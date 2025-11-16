from datetime import datetime, timedelta, timezone
from redis import Redis, RedisError
from rq import Queue
from rq.job import Retry
from rq_scheduler import Scheduler
import logging
import time
import sys

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.crud.crud_event import get_event
from app.db.crud.crud_notification import get_notification, create_notification, mark_notification_sent
from app.utils.email_utils import send_email
from app.utils.sms_utils import send_sms

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def get_redis_connection(retries: int = 5, delay: int = 3) -> Redis | None:
    """
    Lazily create a Redis connection with retries.
    Prevents import-time failure if Redis is unavailable.
    """
    for attempt in range(1, retries + 1):
        try:
            conn = Redis.from_url(settings.REDIS_URL)
            conn.ping()
            logger.info("Connected to Redis (attempt %d)", attempt)
            return conn
        except RedisError as e:
            logger.warning("Redis connection failed (attempt %d/%d): %s", attempt, retries, e)
            time.sleep(delay)
    logger.error("Could not connect to Redis after %d attempts", retries)
    return None


def get_scheduler_components():
    """
    Returns initialized Redis, Queue, DLQ, and Scheduler instances.
    Called lazily within each scheduling operation.
    """
    redis_conn = get_redis_connection()
    if not redis_conn:
        raise RuntimeError("Redis unavailable — cannot schedule jobs")

    q = Queue(settings.RQ_QUEUE, connection=redis_conn)
    dlq = Queue(f"{settings.RQ_QUEUE}_dead", connection=redis_conn)
    scheduler = Scheduler(queue=q, connection=redis_conn)
    return redis_conn, q, dlq, scheduler


def send_reminder_job(notification_id: int):
    """
    Worker job: send reminder if valid and not already sent/cancelled.

    Idempotent:
      - Checks DB before sending (skip if sent/cancelled)
      - Marks as sent after success
    Retries:
      - Handled by RQ Retry policy at enqueue time
    """
    db = SessionLocal()
    try:
        r = get_notification(db, notification_id)
        if not r:
            logger.warning("Reminder %s not found", notification_id)
            return

        if r.cancelled:
            logger.info("Reminder %s cancelled, skipping", notification_id)
            return

        if r.sent_at:
            logger.info("Reminder %s already sent at %s", notification_id, r.sent_at)
            return

        subject = f"Reminder: {r.notification_type} for {r.entity_id}"
        body = f"Your {r.notification_type} is due at {r.target_date}. Please take action."

        if r.email:
            send_email(r.email, subject, body)

        if r.phone:
            send_sms(r.phone, body)

        mark_notification_sent(db, notification_id, datetime.now(timezone.utc))
        logger.info("✅ Reminder %s sent successfully", notification_id)

    except Exception as e:
        logger.exception("❌ Failed to process reminder %s: %s", notification_id, e)
        raise
    finally:
        db.close()


def schedule_notification_job(notification_id: int, target_date: datetime, lead_time_days: int = 7):
    """
    Schedule a reminder for execution at `target_date - lead_time_days`.

    Ensures:
      - Time sanity (future-only scheduling)
      - Retry policy for transient errors
      - Logging for visibility
    """
    run_at = target_date - timedelta(days=lead_time_days)
    now_utc = datetime.now(timezone.utc)

    if run_at < now_utc:
        # Avoid scheduling into the past
        run_at = now_utc + timedelta(seconds=5)
        logger.warning("Adjusted schedule time for reminder %s to %s (was past)", notification_id, run_at)

    retry_policy = Retry(max=3, interval=[30, 60, 120])  # 30s, 1min, 2min

    try:
        _, _, dlq, scheduler = get_scheduler_components()

        scheduler.enqueue_at(
            run_at,
            send_reminder_job,
            notification_id,
            retry=retry_policy,
            # RQ doesn’t directly support on_failure DLQ;
            # you can handle that via a separate monitoring worker later.
        )
        logger.info("🕒 Scheduled reminder %s at %s (lead %d days)", notification_id, run_at, lead_time_days)

    except Exception as e:
        logger.error("Failed to schedule reminder %s: %s", notification_id, e)
        raise

    finally:
        dlq.empty()  # Clear DLQ to prevent buildup

def enqueue_event_processing_job(event_id: int):
    """
    Push an event-processing job onto the Redis queue.
    """
    redis, q, dlq, scheduler = get_scheduler_components()
    q.enqueue(process_event_job, event_id)

def process_event_job(event_id: int):
    """
    Process an incoming event and create/schedule notifications.
    """
    db = SessionLocal()

    event = get_event(db, event_id)
    if not event:
        return

    # === Example business logic ===
    if event.type == "user.signup":
        n = create_notification(
            db,
            notification_type="welcome_email",
            entity_id=event.payload.get("user_id"),
            email=event.payload.get("email"),
            phone=None,
            target_date=None,        # immediate send
            lead_time_days=0         # no lead time
        )
        schedule_notification_job(n.id, n.target_date, n.lead_time_days)

    elif event.type == "payment.failed":
        n = create_notification(
            db,
            notification_type="payment_failure",
            entity_id=event.payload.get("user_id"),
            email=event.payload.get("email"),
            phone=None,
            target_date=None,
            lead_time_days=0
        )
        schedule_notification_job(n.id, n.target_date, n.lead_time_days)

    # Add more event types as needed

    db.close()


if __name__ == "__main__":
    logger.info("🚀 Starting RQ scheduler loop (connected to %s)", settings.REDIS_URL)
    try:
        _, _, _, scheduler = get_scheduler_components()
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error("Scheduler startup failed: %s", e)
