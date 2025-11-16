from sqlalchemy.orm import Session
from app.db.models.notification import Notification
from datetime import datetime

def create_notification(db: Session, *, notification_type: str, entity_id: str, target_date: datetime,
                    lead_time_days: int, email: str | None, phone: str | None):
    r = Notification(
        notification_type=notification_type,
        entity_id=entity_id,
        target_date=target_date,
        lead_time_days=lead_time_days,
        email=email,
        phone=phone,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def get_notification(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def cancel_notification(db: Session, notification_id: int):
    r = get_notification(db, notification_id)
    if not r:
        return None
    r.cancelled = True
    db.commit()
    db.refresh(r)
    return r

def mark_notification_sent(db: Session, notification_id: int, when):
    r = get_notification(db, notification_id)
    if not r:
        return None
    r.sent_at = when
    db.commit()
    db.refresh(r)
    return r
