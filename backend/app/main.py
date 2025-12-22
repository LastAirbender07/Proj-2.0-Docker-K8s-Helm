import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import events, notifications
from app.core.config import settings
from alembic.config import Config
import logging
import time
import psycopg2
import glob
from subprocess import run
from psycopg2 import OperationalError
from prometheus_fastapi_instrumentator import Instrumentator


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
    try:
        base_dir = os.path.dirname(__file__)
        cfg_path = os.path.abspath(os.path.join(base_dir, "..", "alembic.ini"))
        logger.info(f"🔍 Alembic config path resolved to: {cfg_path}")
        logger.info(f"Exists? {os.path.exists(cfg_path)}")

        versions_dir = os.path.abspath(os.path.join(base_dir, "..", "alembic", "versions"))
        os.makedirs(versions_dir, exist_ok=True)

        alembic_cfg = Config(cfg_path)

        # Build DB URL
        alembic_cfg = Config(cfg_path)
        db_url = os.getenv("DATABASE_URL") or (
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        )
        logger.info(f"📦 Using DB URL: {db_url}")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        logger.info("🚀 Running Alembic migrations...")

        # --- STEP 1: connect to DB and check alembic_version
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
        cur = conn.cursor()

        try:
            cur.execute("""SELECT version_num FROM alembic_version LIMIT 1;""")
            row = cur.fetchone()
            db_revision = row[0] if row else None
        except Exception as e:
            # Handle missing alembic_version table
            if getattr(e, 'pgcode', None) == '42P01' or 'UndefinedTable' in str(type(e)):
                logger.warning("alembic_version table does not exist yet.")
                db_revision = None
            else:
                raise
        logger.info(f"DB Alembic Revision: {db_revision}")

        alembic_bin = "/app/.venv/bin/alembic"

        # --- STEP 2: check state of local migration files
        local_versions = {
            os.path.basename(f).split("_")[0]: f
            for f in glob.glob(os.path.join(versions_dir, "*.py"))
        }

        # --- STEP 3: resolve mismatch
        if db_revision:
            if db_revision not in local_versions:
                logger.warning(f"⚠️ DB revision {db_revision} missing locally. Repairing...")

                # Delete broken entry
                cur.execute("DELETE FROM alembic_version;")
                conn.commit()
                db_revision = None  # Force recreation

        # --- STEP 4: if no usable revision exists → create initial migration
        if not db_revision and not local_versions:
            logger.info("🧱 No valid revision found, generating initial migration...")
            run([alembic_bin, "-c", cfg_path, "revision", "--autogenerate", "-m", "initial schema"], check=True)
        else:
            logger.info("✅ Existing Alembic version detected, skipping generation.")

        # --- STEP 5: Apply migrations
        logger.info("🚀 Applying Alembic upgrades...")
        run([alembic_bin, "-c", cfg_path, "upgrade", "head"], check=True)
        logger.info("✅ Migrations applied successfully.")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

app = FastAPI(title="Event Notification Service")

Instrumentator(
    should_ignore_untemplated=True,
    should_group_status_codes=False,
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)


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
