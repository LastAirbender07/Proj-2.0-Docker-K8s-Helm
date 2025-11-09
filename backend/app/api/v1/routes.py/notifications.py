from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas import ReminderCreate, ReminderOut
from ...dependencies import get_db
from ...db.crud.crud_reminder import create_reminder, get_reminder, cancel_reminder
from ...workers.producer import schedule_reminder_job

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.post("/reminders", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder_endpoint(payload: ReminderCreate, db: Session = Depends(get_db)):
    """
    Create a reminder to send at target_date - lead_time_days.

    Args:
        payload (ReminderCreate): reminder metadata
        db (Session): database session

    Returns:
        ReminderOut: created reminder metadata
    """
    r = create_reminder(
        db,
        target_type=payload.target_type,
        target_identifier=payload.target_identifier,
        target_date=payload.target_date,
        lead_time_days=payload.lead_time_days,
        contact_email=str(payload.contact_email) if payload.contact_email else None,
        contact_phone=payload.contact_phone,
    )
    # schedule RQ job
    schedule_reminder_job(r.id, r.target_date, r.lead_time_days)
    return r

@router.delete("/reminders/{reminder_id}", response_model=ReminderOut)
def delete_reminder_endpoint(reminder_id: int, db: Session = Depends(get_db)):
    """
    Cancel a reminder to prevent sending it.

    Args:
        reminder_id (int): id of the reminder to cancel
        db (Session): database session

    Returns:
        ReminderOut: cancelled reminder metadata

    Raises:
        HTTPException: reminder not found
    """
    r = cancel_reminder(db, reminder_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return r
