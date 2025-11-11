from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.schemas import EventIn, EventOut
from app.dependencies import get_db
from app.db.crud.crud_event import create_event, list_events

router = APIRouter(prefix="/api/v1/events", tags=["events"])

@router.post("/", response_model=EventOut)
def publish_event(payload: EventIn, db: Session = Depends(get_db)):
    """
    Publish a new event.
    Args:
        payload: EventIn
    Returns:
        EventOut
    """
    ev = create_event(db, payload.type, payload.payload)
    # Optionally enqueue notifications here
    return ev

@router.get("/", response_model=list[EventOut])
def get_events(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get a list of events.
    Args:
        limit: int, number of events to return (default=50)
    Returns:
        list[EventOut]
    """
    return list_events(db, limit=limit)
