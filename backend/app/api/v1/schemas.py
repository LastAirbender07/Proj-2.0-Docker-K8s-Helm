from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.constants.types import NotificationEventType

class EventIn(BaseModel):
    type: str
    payload: dict

class EventOut(BaseModel):
    id: int
    type: str
    payload: dict
    created_at: datetime

    model_config = { "from_attributes": True }

class NotificationCreate(BaseModel):
    notification_type: NotificationEventType
    entity_id: str
    target_date: datetime
    lead_time_days: int = 7
    email: EmailStr | None = None
    phone: str | None = None

class NotificationOut(BaseModel):
    id: int
    notification_type: NotificationEventType
    entity_id: str
    target_date: datetime
    lead_time_days: int
    email: EmailStr | None
    phone: str | None
    sent_at: datetime | None
    created_at: datetime | None
    status: str | None # default as "PENDING"

    model_config = { "from_attributes": True }
