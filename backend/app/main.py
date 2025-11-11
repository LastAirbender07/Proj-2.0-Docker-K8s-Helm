import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import events, notifications
from app.core.config import settings
from alembic.config import Config
from alembic import command
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Run Alembic migrations programmatically.
    Works inside Docker even if alembic CLI isn't on PATH.
    """
    try:
        logger.info("Running Alembic migrations...")
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply migrations: {e}")
        raise

app = FastAPI(title="Event Notification Service")

# --- CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Routes ---
app.include_router(events.router)
app.include_router(notifications.router)

# --- Startup Event: Run Migrations ---
@app.on_event("startup")
def startup_event():
    run_migrations()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": {
            "database": settings.DATABASE_URL,
            "redis": settings.REDIS_URL,
        },
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Event Notification Service API",
        "docs": "/docs",
    }
