from datetime import datetime, timedelta, timezone
from redis import Redis, RedisError
from rq import Queue
from rq.job import Retry
from rq_scheduler import Scheduler
import logging
import time

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.db.crud.crud_reminder import get_reminder, mark_sent
from backend.app.utils.email_utils import send_email
from backend.app.utils.sms_utils import send_sms

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


def send_reminder_job(reminder_id: int):
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
        r = get_reminder(db, reminder_id)
        if not r:
            logger.warning("Reminder %s not found", reminder_id)
            return

        if r.cancelled:
            logger.info("Reminder %s cancelled, skipping", reminder_id)
            return

        if r.sent_at:
            logger.info("Reminder %s already sent at %s", reminder_id, r.sent_at)
            return

        subject = f"Reminder: {r.target_type} for {r.target_identifier}"
        body = f"Your {r.target_type} is due at {r.target_date}. Please take action."

        if r.contact_email:
            send_email(r.contact_email, subject, body)

        if r.contact_phone:
            send_sms(r.contact_phone, body)

        mark_sent(db, reminder_id, datetime.now(timezone.utc))
        logger.info("✅ Reminder %s sent successfully", reminder_id)

    except Exception as e:
        logger.exception("❌ Failed to process reminder %s: %s", reminder_id, e)
        raise
    finally:
        db.close()


def schedule_reminder_job(reminder_id: int, target_date: datetime, lead_time_days: int = 7):
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
        logger.warning("Adjusted schedule time for reminder %s to %s (was past)", reminder_id, run_at)

    retry_policy = Retry(max=3, interval=[30, 60, 120])  # 30s, 1min, 2min

    try:
        _, _, dlq, scheduler = get_scheduler_components()

        scheduler.enqueue_at(
            run_at,
            send_reminder_job,
            reminder_id,
            retry=retry_policy,
            # RQ doesn’t directly support on_failure DLQ;
            # you can handle that via a separate monitoring worker later.
        )
        logger.info("🕒 Scheduled reminder %s at %s (lead %d days)", reminder_id, run_at, lead_time_days)

    except Exception as e:
        logger.error("Failed to schedule reminder %s: %s", reminder_id, e)
        raise

    finally:
        dlq.empty()  # Clear DLQ to prevent buildup

if __name__ == "__main__":
    logger.info("🚀 Starting RQ scheduler loop (connected to %s)", settings.REDIS_URL)
    try:
        _, _, _, scheduler = get_scheduler_components()
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error("Scheduler startup failed: %s", e)
