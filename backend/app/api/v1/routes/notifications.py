from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging
import sys

from app.api.v1.schemas import NotificationCreate, NotificationOut
from app.dependencies import get_db
from app.db.crud.crud_notification import create_notification, cancel_notification
from app.workers.producer import schedule_notification_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification_endpoint(
    payload: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a reminder and schedule a notification job.

    Design:
    - Creates reminder in DB immediately.
    - Schedules background job asynchronously to avoid blocking HTTP request.
    - Logs scheduling failure but does not affect API response.
    """
    # Step 1: Create reminder entry in DB
    r = create_notification(
        db,
        notification_type=payload.notification_type,
        entity_id=payload.entity_id,
        target_date=payload.target_date,
        lead_time_days=payload.lead_time_days,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
    )

    # Step 2: Schedule asynchronously
    def safe_schedule():
        try:
            schedule_notification_job(r.id, r.target_date, r.lead_time_days)
            logger.info(f"Scheduled reminder job for ID={r.id}")
        except Exception as e:
            logger.error(f"Failed to schedule reminder job (ID={r.id}): {e}")

    background_tasks.add_task(safe_schedule)

    return r


@router.delete("/{notification_id}", response_model=NotificationOut)
def delete_notification_endpoint(notification_id: int, db: Session = Depends(get_db)):
    """
    Cancel a reminder to prevent future notification.
    """
    r = cancel_notification(db, notification_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return r
