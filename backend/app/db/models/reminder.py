from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from app.db.session import Base

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String, index=True)  # e.g., "password_expiry"
    target_identifier = Column(String, index=True)  # e.g., username or user_id
    target_date = Column(DateTime, nullable=False)  # date when password expires
    lead_time_days = Column(Integer, default=7)  # days before target_date to send reminder
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled = Column(Boolean, default=False)
