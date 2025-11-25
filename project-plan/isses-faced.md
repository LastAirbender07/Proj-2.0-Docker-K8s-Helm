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


Retry Logic Issue – 
1. What Was Affected

The following components of the notification system were affected:

Retry behavior for background jobs (process_event_job and send_reminder_job)

Failure handling for scheduled jobs submitted via RQ Scheduler

Dead Letter Queue (DLQ) behavior

Reliability of event → notification → reminder pipeline

Failures inside jobs were not being retried correctly, which could lead to:

Lost event-processing jobs

Lost scheduled reminder jobs

Jobs incorrectly ending up in DLQ

Inconsistent or missing notifications

2. What Was the Issue (Root Cause)

The retry logic was initially misconfigured due to a misunderstanding of how RQ applies retries.

Specifically:

Retry configuration was being applied at the worker level rather than at the job enqueue level.

RQ does not honor worker-level retry configuration for individual jobs.

Instead, each job must explicitly include a Retry(...) policy at enqueue time.

This caused:

Jobs enqueued without retry metadata

Worker default behavior:

If a job failed → mark as failed

No retry → optionally go to DLQ

Scheduled jobs from rq-scheduler had no retry metadata, causing silent failures

Additionally, a dlq.empty() call inside the scheduling process was unintentionally purging failed jobs.

3. Why It Was Designed That Way & What Was the Problem
Initial Intent

The design attempted to:

Centralize retry logic inside the worker:

worker = Worker(..., retry=Retry(...))


Simplify enqueue code by not requiring retry parameters everywhere.

Allow the worker to govern failure and retry behavior globally.

Problem with This Design

RQ explicitly does not work this way.

Workers cannot globally apply retry policies.

Only job-level retry metadata matters.

Scheduler-created jobs ignore worker retry settings entirely.

DLQ clearing (dlq.empty()) removed visibility into real failures.

Thus, jobs that should have retried were:

Never retried

Directly failing

Or silently disappearing

4. What Was the Fix – What Did We Learn?
Fix Implemented

We corrected the implementation to follow RQ’s actual design:

✔ Add retry policy per job at enqueue
q.enqueue(
    process_event_job,
    args=(event_id,),
    retry=Retry(max=3, interval=[30, 60, 120])
)

✔ Add retry policy for scheduled jobs
scheduler.enqueue_at(
    run_at,
    send_reminder_job,
    notification_id,
    retry=Retry(max=3, interval=[30, 60, 120])
)

✔ Remove dangerous DLQ clearing

dlq.empty() was removed to prevent loss of failure information.

✔ Worker left in default mode

Workers now process jobs without attempting to override retry logic.

Lessons Learned
1. RQ retry logic is purely job-based

Workers do not control retry behavior.

Every job must be enqueued with explicit retry metadata.

Scheduled jobs also require retry config.

2. Never clear DLQs automatically

DLQ is critical for diagnosing failures.

Automatic clearing hides real issues.

3. Scheduler jobs behave differently

RQ Scheduler does not infer retry settings.

Must be explicitly set on each scheduled job.