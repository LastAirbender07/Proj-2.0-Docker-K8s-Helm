from sqlalchemy.orm import Session
from app.db.models.event import Event

def create_event(db: Session, type_: str, payload: dict):
    ev = Event(type=type_, payload=payload)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

def list_events(db: Session, limit: int = 100):
    return db.query(Event).order_by(Event.created_at.desc()).limit(limit).all()

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()