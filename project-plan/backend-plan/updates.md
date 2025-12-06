
Replaced this code in main.py:


```python
# def run_migrations():
#     """
#     Run Alembic migrations programmatically.
#     Works inside Docker even if alembic CLI isn't on PATH.
#     """
#     try:
#         base_dir = os.path.dirname(__file__)
#         cfg_path = os.path.abspath(os.path.join(base_dir, "..", "alembic.ini"))
#         logger.info(f"🔍 Alembic config path resolved to: {cfg_path}")
#         logger.info(f"Exists? {os.path.exists(cfg_path)}")

#         versions_dir = os.path.abspath(os.path.join(base_dir, "..", "alembic", "versions"))
#         os.makedirs(versions_dir, exist_ok=True)

#         alembic_cfg = Config(cfg_path)
#         db_url = os.getenv("DATABASE_URL") or (
#             f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
#             f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
#         )
#         logger.info(f"📦 Using DB URL: {db_url}")
#         alembic_cfg.set_main_option("sqlalchemy.url", db_url)

#         logger.info("🚀 Running Alembic migrations...")
#     #     command.upgrade(alembic_cfg, "head")
#     #     logger.info("✅ Migrations applied successfully.")
#     # except Exception as e:
#     #     logger.error(f"❌ Failed to apply migrations: {e}")
#     #     raise

#         try:
#             # Check if any migration file exists
#             alembic_bin = "/app/.venv/bin/alembic"
#             version_files = glob.glob(os.path.join(versions_dir, "*.py"))
#             if not version_files:
#                 logger.info("🧱 No Alembic version found. Generating initial migration...")
#                 run([alembic_bin, "-c", cfg_path, "revision", "--autogenerate", "-m", "initial schema"], check=True)
#             else:
#                 logger.info("✅ Existing Alembic version detected, skipping generation.")

#             logger.info("🚀 Applying migrations...")
#             run([alembic_bin, "-c", cfg_path, "upgrade", "head"], check=True)
#             logger.info("✅ Migrations applied successfully.")

#         except CalledProcessError as e:
#             logger.error(f"❌ Alembic command failed: {e}")
#             raise
#     except Exception as e:
#         logger.error(f"❌ Failed to apply migrations: {e}")
#         raise
```


with the below code:

```
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

        cur.execute("""SELECT version_num FROM alembic_version LIMIT 1;""")
        row = cur.fetchone()

        db_revision = row[0] if row else None
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

```
