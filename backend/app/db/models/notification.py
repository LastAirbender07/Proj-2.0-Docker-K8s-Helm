from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String, index=True)  # e.g., "password_expiry"
    entity_id = Column(String, index=True)  # e.g., username or user_id
    target_date = Column(DateTime, nullable=False)  # date when password expires
    lead_time_days = Column(Integer, default=7)  # days before target_date to send reminder
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="PENDING")  # (PENDING, SCHEDULED, SENT, FAILED, CANCELLED)
