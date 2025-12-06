📝 Migration Issue – Root Cause & Fix
1. What Was the Problem?

When deploying the backend service in Kubernetes, Alembic failed with the error:

Can't locate revision identified by 'dff470803ce4'


This happened even though my code was explicitly written to:

detect missing migration files

generate a fresh initial migration

then upgrade to head

But Alembic still attempted to upgrade using a revision ID that did not exist anywhere.
This ID (dff470803ce4) was neither:

present in my alembic/versions/ folder, nor

valid in the local filesystem

Yet it did exist inside the PostgreSQL "alembic_version" table.

So the database believed that a migration existed — but the filesystem (inside the container) did not.

This mismatch caused the entire Alembic upgrade process to fail.

2. Why Did This Happen? (Root Cause)
Root Cause: DB state and container state were out of sync

At some earlier point during local development or a previous failed container run:

Alembic generated a migration: dff470803ce4_initial_schema.py

That revision ID was written into the Postgres database (alembic_version table)

Later, I deleted or replaced the migration files

But the DB still contained the old revision ID

So when my Kubernetes workload started:

Alembic checked the DB and saw revision dff470803ce4

Alembic checked the filesystem and did not find the matching file

This created a broken migration state

Even though my code tried to create a new revision when no files existed, Alembic still failed because the database was pointing to a revision that no longer lived inside the container.

This is a classic Alembic problem:
Version table in DB and filesystem got out of sync.

3. What I Changed (Fix & Logic)

I updated the migration logic to make it fully self-healing.

✔ Final Migration Logic Implemented

Check if Alembic version table contains a revision

Check if the corresponding file exists

If the DB has a revision but the file does not, then:

Delete the invalid DB entry

Treat it as a fresh initialization

If no migration files exist:

Generate a new initial migration (revision --autogenerate)

Finally, run:

alembic upgrade head

✔ Result of Fix

On the next deployment:

Alembic detected no valid version present

It generated a fresh new migration (bde182d93568_initial_schema.py)

Upgraded successfully:

Running upgrade -> bde182d93568


Application started without issues

The migration system is now:

Deterministic

Self-healing

Safe for repeated pod restarts

Resilient to mismatches between DB and container

4. Personal Learning / What I Must Remember

Alembic tracks revision state inside the database, not just in files.

If I delete or modify alembic/versions/ without cleaning the DB, migrations will break.

Kubernetes pods restarting can expose this problem because each pod uses fresh container filesystem, but the DB state persists.

A robust production system must:

Detect mismatched revision state

Repair DB revision table

Auto-generate initial migrations when needed

My updated implementation now does exactly that.

5. Future Recommendation

For long-term stability, I should eventually move Alembic migrations to one of these patterns:

Option A — Kubernetes Job (preferred)

A “migration job” that runs before backend pods start.

Option B — Acquire DB-level locks

To prevent multiple pods from attempting migrations simultaneously.

Both ensure cleaner separation between application startup and schema management.