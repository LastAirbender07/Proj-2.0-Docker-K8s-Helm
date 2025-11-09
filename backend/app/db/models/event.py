from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from ..session import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
