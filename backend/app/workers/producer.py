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
from app.db.models.notification import StatusType
from app.db.crud.crud_notification import get_notification, create_notification, mark_notification_sent
from app.utils.email_utils import send_email
from app.utils.sms_utils import send_sms
from app.constants.types import NotificationEventType

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

        if r.status == StatusType.CANCELED:
            logger.info("Reminder %s is cancelled, skipping.", notification_id)
            return

        if r.sent_at:
            logger.info("Reminder %s already sent at %s", notification_id, r.sent_at)
            return

        dt = r.target_date or datetime.now(timezone.utc)
        try:
            when = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M %Z")
        except Exception:
            when = str(dt)

        subject = f"Reminder: {r.notification_type} for {r.entity_id} — due {when}"

        body = (
            f"Hello,\n\n"
            f"This is a friendly reminder about your {r.notification_type.lower()} "
            f"(notification #{r.id}) for {r.entity_id}. It is scheduled for {when}.\n\n"
            "What you need to do:\n"
            "- Review the item and take any required action.\n\n"
            "If you’ve already completed this, please ignore this message.\n\n"
            "If you need help or believe this is an error, reply to this email or check your account for details.\n\n"
            "Thank you,\n"
            "Support Team"
        )

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
    Uses a handler-based approach for clarity and future extensibility.
    """

    db = SessionLocal()
    try:
        event = get_event(db, event_id)
        if not event:
            logger.warning("Event %s not found", event_id)
            return
        
        try:
            event_type: NotificationEventType = NotificationEventType(event.type)
        except ValueError:
            logger.warning(
                "Unknown event type '%s' for event %s. Falling back to CUSTOM.", event.type, event_id)
            event_type = NotificationEventType.CUSTOM

        now_utc = datetime.now(timezone.utc)

        def handle_user_signup(payload):
            return {
                "target_date": now_utc,
                "lead_time_days": 0,
                "entity_id": payload.get("user_id"),
                "email": payload.get("email"),
                "phone": None,  # No SMS
            }

        def handle_payment_failed(payload):
            return {
                "target_date": now_utc,
                "lead_time_days": 0,
                "entity_id": payload.get("user_id"),
                "email": payload.get("email"),
                "phone": None,
            }

        def handle_payment_success(payload):
            return {
                "target_date": now_utc,
                "lead_time_days": 0,
                "entity_id": payload.get("user_id"),
                "email": payload.get("email"),
                "phone": None,
            }

        def handle_password_expiry(payload):
            return {
                "target_date": payload.get("expiry_date"),  # must be UTC datetime
                "lead_time_days": payload.get("lead_days", 7),
                "entity_id": payload.get("user_id"),
                "email": payload.get("email"),
                "phone": None,
            }

        def handle_unsubscribe(payload):
            return {
                "target_date": now_utc,
                "lead_time_days": 0,
                "entity_id": payload.get("user_id"),
                "email": payload.get("email"),
                "phone": None,
            }

        def handle_custom(payload):
            return {
                "target_date": payload.get("target_date") or now_utc,
                "lead_time_days": payload.get("lead_days", 0),
                "entity_id": payload.get("entity_id"),
                "email": payload.get("email"),
                "phone": None,
            }

        handler_map = {
            NotificationEventType.USER_SIGNUP: handle_user_signup,
            NotificationEventType.PAYMENT_FAILED: handle_payment_failed,
            NotificationEventType.PAYMEBT_SUCCESS: handle_payment_success,
            NotificationEventType.PASSWORD_EXPIRY: handle_password_expiry,
            NotificationEventType.USER_UNSUBSCRIBE: handle_unsubscribe,
            NotificationEventType.CUSTOM: handle_custom,
        }

        handler = handler_map.get(event_type, handle_custom)
        params = handler(event.payload or {})

        # Create DB notification
        notification = create_notification(
            db,
            notification_type=event_type.value,
            entity_id=params["entity_id"],
            email=params["email"],
            phone=params["phone"],  # logged only
            target_date=params["target_date"],
            lead_time_days=params["lead_time_days"],
        )

        schedule_notification_job(
            notification.id,
            notification.target_date,
            notification.lead_time_days,
        )

        logger.info(
            "Notification %s created & scheduled for event %s (%s)",
            notification.id,
            event_id,
            event_type.value,
        )

    except Exception as e:
        logger.exception("Error processing event %s: %s", event_id, e)
    finally:
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
