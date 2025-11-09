from sqlalchemy.orm import Session
from ..models.reminder import Reminder
from datetime import datetime

def create_reminder(db: Session, *, target_type: str, target_identifier: str, target_date: datetime,
                    lead_time_days: int, contact_email: str | None, contact_phone: str | None):
    r = Reminder(
        target_type=target_type,
        target_identifier=target_identifier,
        target_date=target_date,
        lead_time_days=lead_time_days,
        contact_email=contact_email,
        contact_phone=contact_phone,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def get_reminder(db: Session, reminder_id: int):
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()

def cancel_reminder(db: Session, reminder_id: int):
    r = get_reminder(db, reminder_id)
    if not r:
        return None
    r.cancelled = True
    db.commit()
    db.refresh(r)
    return r

def mark_sent(db: Session, reminder_id: int, when):
    r = get_reminder(db, reminder_id)
    if not r:
        return None
    r.sent_at = when
    db.commit()
    db.refresh(r)
    return r
