from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.routes import events, notifications
from backend.app.db.session import engine
from backend.app.core.config import settings
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Run Alembic migrations automatically at app startup.
    Ensures database schema is up-to-date across environments.
    """
    try:
        logger.info("Running Alembic migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to apply migrations: %s", e)
        raise

app = FastAPI(title="Event Notification Service")

# --- CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://task.local",
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
