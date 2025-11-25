Alembic Migration Issue Summary
# Alembic Migration Issue Summary

## Alembic Migration Issue

### Root Cause
- Alembic was not initialized and no migration versions existed.
- The backend could not locate the Alembic configuration or migration scripts due to incorrect container file paths.
- The database URL was not set for Alembic, so it had no valid connection.
- Even after initialization, no versioned migration files were present, preventing upgrades.

### Detailed Explanation
- Missing Alembic setup: The project initially lacked the Alembic directory and configuration (alembic.ini and the /alembic folder), preventing migrations from running.
- Incorrect path configuration: The backend attempted to run Alembic with a relative or invalid path, causing silent failures.
- Database URL not set: sqlalchemy.url in alembic.ini was not dynamically configured, so Alembic could not connect to the Postgres DB.
- No migration versions: With no files under /alembic/versions, Alembic could not detect or apply migrations, effectively blocking schema changes.

### Resolution
- Proper initialization: Added alembic.ini and the /alembic directory to the backend container.
- Dynamic config path: Resolved Alembic config path dynamically:
    ```python
    cfg_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
    ```
    and logged the absolute path for visibility.
- Dynamic DB URL: Programmatically set:
    ```python
    config.set_main_option("sqlalchemy.url", db_url)
    ```
    to ensure Alembic connects to the correct Postgres instance.
- Automatic revision and upgrade: When no versions existed, the system generated an initial migration automatically:
    ```
    alembic revision --autogenerate -m "initial schema"
    ```
    and applied migrations:
    ```
    alembic upgrade head
    ```

### Verification
- Confirmed Alembic created an initial version file (583d8889edde_initial_schema.py).
- Confirmed expected tables (events, reminders, etc.) were created in the database.

### Outcome
- Alembic migrations are now initialized, versioned, and automatically applied at backend startup.
- The system connects to Postgres, detects schema changes, and applies them without manual intervention, improving containerized deployment and schema consistency across environments.

---

# Retry Logic Issue

## Affected Components
- Retry behavior for background jobs (process_event_job and send_reminder_job)
- Failure handling for scheduled jobs via RQ Scheduler
- Dead Letter Queue (DLQ) behavior
- Reliability of the event → notification → reminder pipeline

## Root Cause
- Retry logic was applied at the worker level instead of at enqueue time.
- RQ does not honor worker-level retry configuration; job retry metadata must be set when enqueuing.
- Scheduler-created jobs did not include retry metadata and were not retried.
- A dlq.empty() call unintentionally purged failed jobs, removing failure visibility.

## Design Intent and the Problem
- Initial intent: centralize retry logic in the worker to simplify enqueue code.
    ```python
    worker = Worker(..., retry=Retry(...))
    ```
- Problem: RQ requires retry metadata per job at enqueue—workers cannot globally enforce retries. The scheduler ignores worker retry settings. Clearing the DLQ removed diagnostics.

## Fix Implemented
- Set retry policy when enqueuing jobs:
    ```python
    q.enqueue(
            process_event_job,
            args=(event_id,),
            retry=Retry(max=3, interval=[30, 60, 120])
    )
    ```
- Set retry policy for scheduled jobs:
    ```python
    scheduler.enqueue_at(
            run_at,
            send_reminder_job,
            notification_id,
            retry=Retry(max=3, interval=[30, 60, 120])
    )
    ```
- Remove dangerous DLQ clearing (removed dlq.empty()).
- Leave workers in default mode and rely on job-level retry metadata.

## Lessons Learned
- RQ retry logic is job-based; the worker cannot override it.
- All jobs (including scheduled ones) must include retry metadata at enqueue.
- Never automatically clear the DLQ—it's essential for diagnosing failures.
- Scheduler jobs behave differently and require explicit retry settings.

