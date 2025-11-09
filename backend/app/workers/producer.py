"""
Scheduler and schedule helper. This module provides a helper `schedule_reminder_job`
which enqueues a job via rq-scheduler to run at specific time.
We also run the scheduled RQ scheduler process here.
"""
from datetime import datetime, timedelta, timezone
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from ..core.config import settings
import logging
from ..db.session import SessionLocal
from ..db.crud.crud_reminder import get_reminder, mark_sent
from ..utils.email_utils import send_email
from ..utils.sms_utils import send_sms

logger = logging.getLogger(__name__)
redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(settings.RQ_QUEUE, connection=redis_conn)
scheduler = Scheduler(queue=q, connection=redis_conn)

def send_reminder_job(reminder_id: int):
    """
    Job executed by worker: sends reminder (email/sms) if not already sent or cancelled.
    Idempotent: checks DB for sent_at before sending.
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
        logger.info("Reminder %s sent", reminder_id)
    except Exception:
        logger.exception("Failed to send reminder %s", reminder_id)
        raise
    finally:
        db.close()

def schedule_reminder_job(reminder_id: int, target_date: datetime, lead_time_days: int = 7):
    run_at = target_date - timedelta(days=lead_time_days)
    # compare to current UTC time and ensure run_at is not in the past
    now_utc = datetime.now(timezone.utc)
    if run_at < now_utc:
        # if run time is in the past, schedule shortly in the future
        run_at = now_utc + timedelta(seconds=5)
    # schedule with rq-scheduler
    scheduler.enqueue_at(run_at, send_reminder_job, reminder_id)
    logger.info("Scheduled reminder %s at %s", reminder_id, run_at)

if __name__ == "__main__":
    # run redis scheduler loop (long running process) - this process needs to be kept running
    logger.info("Starting scheduler loop")
    scheduler.run()
