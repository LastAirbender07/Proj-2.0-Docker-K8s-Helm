from pydantic import BaseModel, EmailStr
from datetime import datetime

class EventIn(BaseModel):
    type: str
    payload: dict

class EventOut(BaseModel):
    id: int
    type: str
    payload: dict
    created_at: datetime

    model_config = { "from_attributes": True }

class ReminderCreate(BaseModel):
    target_type: str
    target_identifier: str
    target_date: datetime
    lead_time_days: int = 7
    contact_email: EmailStr | None = None
    contact_phone: str | None = None

class ReminderOut(BaseModel):
    id: int
    target_type: str
    target_identifier: str
    target_date: datetime
    lead_time_days: int
    contact_email: EmailStr | None
    contact_phone: str | None
    sent_at: datetime | None
    cancelled: bool

    model_config = { "from_attributes": True }
