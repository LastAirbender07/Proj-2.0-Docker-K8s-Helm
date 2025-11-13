import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import events, notifications
from app.core.config import settings
from alembic.config import Config
from alembic import command
import logging
import time
import psycopg2
import glob
from subprocess import run, CalledProcessError
from psycopg2 import OperationalError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def wait_for_db():
    db_url = settings.DATABASE_URL
    max_retries = 10
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            logger.info("Database is available.")
            return
        except OperationalError:
            logger.warning(f"Database not available, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    logger.error("Could not connect to the database after several attempts.")
    raise Exception("Database connection failed.")

def run_migrations():
    """
    Run Alembic migrations programmatically.
    Works inside Docker even if alembic CLI isn't on PATH.
    """
    try:
        base_dir = os.path.dirname(__file__)
        cfg_path = os.path.abspath(os.path.join(base_dir, "..", "alembic.ini"))
        logger.info(f"🔍 Alembic config path resolved to: {cfg_path}")
        logger.info(f"Exists? {os.path.exists(cfg_path)}")

        versions_dir = os.path.abspath(os.path.join(base_dir, "..", "alembic", "versions"))
        os.makedirs(versions_dir, exist_ok=True)

        alembic_cfg = Config(cfg_path)
        db_url = os.getenv("DATABASE_URL") or (
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        )
        logger.info(f"📦 Using DB URL: {db_url}")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        logger.info("🚀 Running Alembic migrations...")
    #     command.upgrade(alembic_cfg, "head")
    #     logger.info("✅ Migrations applied successfully.")
    # except Exception as e:
    #     logger.error(f"❌ Failed to apply migrations: {e}")
    #     raise

        try:
            # Check if any migration file exists
            alembic_bin = "/app/.venv/bin/alembic"
            version_files = glob.glob(os.path.join(versions_dir, "*.py"))
            if not version_files:
                logger.info("🧱 No Alembic version found. Generating initial migration...")
                run([alembic_bin, "-c", cfg_path, "revision", "--autogenerate", "-m", "initial schema"], check=True)
            else:
                logger.info("✅ Existing Alembic version detected, skipping generation.")

            logger.info("🚀 Applying migrations...")
            run([alembic_bin, "-c", cfg_path, "upgrade", "head"], check=True)
            logger.info("✅ Migrations applied successfully.")

        except CalledProcessError as e:
            logger.error(f"❌ Alembic command failed: {e}")
            raise
    except Exception as e:
        logger.error(f"❌ Failed to apply migrations: {e}")
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
    wait_for_db()
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
