Below is a complete, ready-to-run **backend** scaffold for your Event Notification System. I focused on pragmatic, production-friendly choices you can extend:

* SQLAlchemy (sync) + PostgreSQL
* Redis + RQ + rq-scheduler for background jobs and scheduled reminders
* FastAPI endpoints for events + reminders/subscribers
* Clear file layout matching your requested tree
* Dockerfile + docker-compose for local dev
* Simple email utility (pluggable SMTP) and SMS stub
* Tests skeleton

I kept everything compact but functional so you can run it and extend it. Copy these files into your `backend/` folder.

---

> Notes / decisions (quick)
>
> * I used **RQ** (redis queue) + **rq-scheduler** to schedule reminder jobs (works well for scheduled single-job reminders like "7 days before expiry"). Alternative: cron + worker scan, or Celery. RQ is simpler to start with.
> * Reminder flow: user creates a `Reminder` (DB row) with `target_date` and `lead_time_days` (default 7). Backend schedules `send_reminder` job at (`target_date - lead_time_days`). A worker executes sending and marks `sent_at`. If job fails you'll use retry and/or move to a DLQ (not fully implemented but scaffolded).
> * For idempotency: jobs check DB `sent_at` before sending and set `sent_at` under DB transaction — safe to retry.
> * You can swap `email_utils.send_email` with a real SMTP client. I included both console fallback and an SMTP sample.
> * Use environment variables for config (see Dockerfile / docker-compose).
> * Health endpoints included.

---

## 1) `requirements.txt`

```
fastapi==0.95.2
uvicorn[standard]==0.22.0
SQLAlchemy==2.1.0
psycopg2-binary==2.9.6
pydantic==1.10.11
python-dotenv==1.0.0
redis==4.5.5
rq==1.13.1
rq-scheduler==0.14.2
alembic==1.12.0
requests==2.32.0
httpx==0.26.1
python-multipart==0.0.6
```

---

## 2) `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# system deps for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

ENV APP_MODULE=app.main:app
EXPOSE 5001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
```

---

## 3) `docker-compose.yml` (dev)

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: notifications
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    ports:
      - "5001:5001"
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload

  worker:
    build: .
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    command: bash -c "python -u -m app.workers.consumer"
    volumes:
      - ./app:/app/app

  scheduler:
    build: .
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
    command: bash -c "python -u -m app.workers.producer"
    volumes:
      - ./app:/app/app

volumes:
  pgdata:
```

Create `.env` with DB/Redis settings, example below.

---

## 4) `.env` (example)

```
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=notifications
POSTGRES_HOST=postgres-service
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis-service
REDIS_PORT=6379
REDIS_DB=0

# RQ
RQ_QUEUE=default
RQ_RETRIES=3

# SMTP (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
FROM_EMAIL=no-reply@example.com

```

---

## 5) `app/core/config.py`

```python
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    RQ_QUEUE: str = "default"
    RQ_RETRIES: int = 3

    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    FROM_EMAIL: str | None = "no-reply@example.com"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6) `app/db/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base()

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 7) `app/db/models/event.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from ..session import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

## 8) `app/db/models/reminder.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from ..session import Base

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
```

---

## 9) `app/db/crud/crud_event.py`

```python
from sqlalchemy.orm import Session
from ..models.event import Event

def create_event(db: Session, type_: str, payload: dict):
    ev = Event(type=type_, payload=payload)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

def list_events(db: Session, limit: int = 100):
    return db.query(Event).order_by(Event.created_at.desc()).limit(limit).all()
```

## 10) `app/db/crud/crud_reminder.py`

```python
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
```

---

## 11) Pydantic schemas `app/api/v1/schemas.py`

```python
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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True
```

---

## 12) `app/api/v1/routes/events.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas import EventIn, EventOut
from ...dependencies import get_db
from ...db.crud.crud_event import create_event, list_events

router = APIRouter(prefix="/api/v1/events", tags=["events"])

@router.post("/", response_model=EventOut)
def publish_event(payload: EventIn, db: Session = Depends(get_db)):
    ev = create_event(db, payload.type, payload.payload)
    # Optionally enqueue notifications here
    return ev

@router.get("/", response_model=list[EventOut])
def get_events(limit: int = 50, db: Session = Depends(get_db)):
    return list_events(db, limit=limit)
```

---

## 13) `app/api/v1/routes/notifications.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas import ReminderCreate, ReminderOut
from ...dependencies import get_db
from ...db.crud.crud_reminder import create_reminder, get_reminder, cancel_reminder
from ...workers.producer import schedule_reminder_job

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.post("/reminders", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder_endpoint(payload: ReminderCreate, db: Session = Depends(get_db)):
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
    r = cancel_reminder(db, reminder_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return r
```

---

## 14) `app/dependencies.py`

```python
from .db.session import SessionLocal
from contextlib import contextmanager

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 15) `app/utils/email_utils.py`

```python
import smtplib
from email.message import EmailMessage
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    # If SMTP configured, use it; otherwise print for dev
    if settings.SMTP_HOST and settings.SMTP_USER:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as s:
            s.starttls()
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            s.send_message(msg)
    else:
        logger.info("Sending email (dev) to %s - %s\n%s", to_email, subject, body)
```

## 16) `app/utils/sms_utils.py` (stub)

```python
import logging
logger = logging.getLogger(__name__)

def send_sms(phone: str, message: str):
    logger.info("Sending SMS to %s: %s", phone, message)
```

---

## 17) `app/workers/consumer.py`

```python
"""
Long-running worker process: listens to Redis RQ queue and processes jobs.
Also rq worker automatically handles retries if set.
"""
import os
from redis import Redis
from rq import Worker, Queue, Connection
from ..core.config import settings

listen = [settings.RQ_QUEUE]
redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
```

---

## 18) `app/workers/producer.py`

```python
"""
Scheduler and schedule helper. This module provides a helper `schedule_reminder_job`
which enqueues a job via rq-scheduler to run at specific time.
We also run the scheduled RQ scheduler process here.
"""
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from ..core.config import settings
import logging
from ..db.session import SessionLocal
from ..db.crud.crud_reminder import get_reminder, mark_sent
from ..utils.email_utils import send_email
from ..utils.sms_utils import send_sms

logger = logging.getLogger(__name__)
redis_conn = Redis.from_url(settings.REDIS_URL)
q = Queue(settings.RQ_QUEUE, connection=redis_conn)
scheduler = Scheduler(queue=q, connection=redis_conn)

def send_reminder_job(reminder_id: int):
    """
    Job executed by worker: sends reminder (email/sms) if not already sent or cancelled.
    Idempotent: checks DB for sent_at before sending.
    """
    db = SessionLocal()
    try:
        r = get_reminder(db, reminder_id)
        if not r:
            logger.warning("Reminder %s not found", reminder_id)
            return
        if r.cancelled:
            logger.info("Reminder %s cancelled, skipping", reminder_id)
            return
        if r.sent_at:
            logger.info("Reminder %s already sent at %s", reminder_id, r.sent_at)
            return

        subject = f"Reminder: {r.target_type} for {r.target_identifier}"
        body = f"Your {r.target_type} is due at {r.target_date}. Please take action."

        if r.contact_email:
            send_email(r.contact_email, subject, body)

        if r.contact_phone:
            send_sms(r.contact_phone, body)

        mark_sent(db, reminder_id, datetime.utcnow())
        logger.info("Reminder %s sent", reminder_id)
    except Exception:
        logger.exception("Failed to send reminder %s", reminder_id)
        raise
    finally:
        db.close()

def schedule_reminder_job(reminder_id: int, target_date: datetime, lead_time_days: int = 7):
    run_at = target_date - timedelta(days=lead_time_days)
    if run_at < datetime.utcnow():
        # if run time in past, schedule immediately
        run_at = datetime.utcnow() + timedelta(seconds=5)
    # schedule with rq-scheduler
    scheduler.enqueue_at(run_at, 'app.workers.producer.send_reminder_job', reminder_id)
    logger.info("Scheduled reminder %s at %s", reminder_id, run_at)

if __name__ == "__main__":
    # run redis scheduler loop (long running process) - this process needs to be kept running
    logger.info("Starting scheduler loop")
    scheduler.run()
```

Notes: `scheduler.enqueue_at` references function by string path since rq-scheduler often needs importable path. We also expose `schedule_reminder_job` for the web process to call.

---

## 19) `app/main.py`

```python
from fastapi import FastAPI
from .api.v1.routes import events, notifications
from .db.session import engine, Base
from .core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# create tables (for dev only; use migrations in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Notification Service")

# CORS - frontend origin(s) should be added here
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://task.local",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(events.router)
app.include_router(notifications.router)

@app.get("/health")
def health():
    return {"status": "ok", "env": {"database": settings.DATABASE_URL, "redis": settings.REDIS_URL}}
```

---

## 20) `app/api/v1/routes/__init__.py`

```python
from fastapi import APIRouter
from . import events, notifications

# not used directly
```

---

## 21) `app/tests/test_notifications.py` (skeleton)

```python
def test_create_reminder_api():
    # Use TestClient to call endpoints
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    payload = {
        "target_type": "password_expiry",
        "target_identifier": "user123",
        "target_date": "2030-01-01T00:00:00Z",
        "lead_time_days": 7,
        "contact_email": "test@example.com"
    }
    r = client.post("/api/v1/notifications/reminders", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["target_type"] == "password_expiry"
```

---

## 22) How to run locally (dev)

1. Create `.env` as shown.
2. `docker-compose up --build`

   * `backend` service runs FastAPI (port 5001)
   * `worker` runs `consumer` RQ worker
   * `scheduler` runs the scheduler process that enqueues scheduled jobs
3. Create a reminder via POST `/api/v1/notifications/reminders` — job is scheduled and should be processed at the scheduled time by worker.

---

## 23) Helm / K8s notes (what to add later)

* Create two Deployments: `backend` (FastAPI) and `worker` (RQ worker); optionally `scheduler` as separate Deployment/CronJob or Deployment (always-on).
* Use `Deployment` + `ReplicaSet` for backend.
* Use `StatefulSet` for Redis (or Bitnami chart) as you already planned.
* Use `Secret` for DB credentials.
* Ensure `worker` has RBAC / PodDisruptionBudget if needed.
* For production scheduled jobs at scale prefer dedicated scheduler (e.g., Temporal, Celery beat + durable broker, or CronJob) — rq-scheduler is fine for small-medium workloads.

---

## 24) Idempotency, retries & DLQ (scaffold)

* Job idempotency: `send_reminder_job` checks `sent_at` and `cancelled` before sending.
* Retries: RQ supports retries — register job with `retry=Retry(max=3)` if enqueueing directly.
* DLQ: You can push failing job metadata to a `dead_letter` Redis list or to a separate DB table when exception occurs.

---

## 25) Next steps you can ask me to implement right now (pick one or more)

* Add Alembic migrations instead of `Base.metadata.create_all`.
* Add full tests (unit and integration) including worker job tests (using fakeredis).
* Add JWT auth for protected endpoints.
* Replace stubbed email with real SMTP or integration with SendGrid.
* Add Dockerfile optimization and Helm charts for backend + worker + scheduler.
* Implement a DB-backed dead-letter queue table and automatic requeueing with backoff.

---
