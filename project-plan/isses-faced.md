Alembic Migration Issue Summary
1. Root Cause

The backend container initially failed to apply database migrations during startup because Alembic was not initialized and no migration versions existed. Additionally, the application could not locate the Alembic configuration or migration scripts correctly due to incorrect file paths in the container environment.

2. Detailed Explanation

Missing Alembic setup: The project did not include the Alembic directory or configuration initially (alembic.ini and /alembic folder), preventing migrations from running.

Incorrect configuration path: The backend attempted to execute Alembic commands using a relative or invalid path, resulting in silent failures.

Database URL not set: The sqlalchemy.url parameter inside alembic.ini was not dynamically configured, so Alembic had no valid database connection.

No migration versions: Even after Alembic initialization, there were no versioned migration files in /alembic/versions, causing Alembic to hang when attempting upgrades.

These issues collectively prevented the backend from generating or applying schema migrations to the PostgreSQL database, blocking the application’s startup flow.

3. Resolution

Initialized Alembic properly: Added the alembic.ini file and /alembic directory within the backend container.

Dynamic configuration path: Updated the code to resolve Alembic’s configuration path dynamically using:

cfg_path = os.path.join(os.path.dirname(__file__), "alembic.ini")


and logged the absolute path for visibility.

Dynamic database URL: Programmatically set config.set_main_option("sqlalchemy.url", db_url) to ensure Alembic connected to the correct Postgres instance.

Automatic revision and upgrade: Added logic to detect missing versions, generate the initial migration dynamically using:

alembic revision --autogenerate -m "initial schema"


and then apply migrations with:

alembic upgrade head


Verification: Confirmed Alembic successfully generated the initial version (583d8889edde_initial_schema.py) and created all expected tables (events, reminders, etc.) in the database.

4. Outcome

Alembic migrations are now automatically initialized, versioned, and applied at backend startup.
The system successfully connects to PostgreSQL, detects schema changes, and applies them without manual intervention — ensuring smooth containerized deployment and schema consistency across environments.