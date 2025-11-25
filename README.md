# Project: Event-Driven Notification Service

Goal
-----
A small event-driven notification service that lets you publish events and schedule notifications (email/SMS) for future dates (e.g., reminders like password expiry).

Summary
-------
This service provides an end-to-end pipeline for ingesting events, processing them asynchronously, and scheduling delayed notifications. It stores metadata in PostgreSQL, uses Redis + RQ for background jobs and scheduling, and provides a REST API for CRUD operations and monitoring.

Main flows
----------
- Publish events via `POST /api/v1/events` → persist Event to PostgreSQL and enqueue processing job in Redis/RQ.  
- Event worker (RQ consumer) processes events and creates notifications or schedules jobs.  
- Create notifications via `POST /api/v1/notifications` → persisted to PostgreSQL and scheduled using rq-scheduler to run at `target_date - lead_time`.  
- Worker processes scheduled jobs: verifies idempotency (e.g., `sent_at`, `cancelled` flags), sends email/SMS, and marks notifications as sent.

Components
----------
- FastAPI — HTTP API
- PostgreSQL — persistent store for events and notifications
- Redis — RQ broker and scheduler backend
- RQ & rq-scheduler — background jobs and scheduled jobs
- Worker processes — `app.workers.consumer` (worker) and `app.workers.producer` (scheduler)
- Pluggable utilities — email & SMS adapters for sending messages
- Docker Compose + Dockerfile — local development
- Alembic — DB migration scaffolding
- Tests — basic tests in `app/tests/`

What the app does (detailed)
---------------------------
1. Event ingestion
    - Accepts incoming events (e.g., `user.signup`, `payment.failed`), stores them in PostgreSQL, and enqueues event-processing jobs.

2. Event processing worker
    - Runs handlers per event type, extracts metadata (email, phone, `target_date`), creates notification entries in PostgreSQL, and schedules reminder jobs via rq-scheduler.

3. Notification scheduler
    - Schedules reminders at `target_date - lead_time_days`.
    - Adds retry logic and idempotency checks to prevent duplicated sends.

4. Reminder worker
    - Sends email/SMS with retry/backoff logic.
    - Updates notification status in the database.
    - Skips processing if a notification has been sent, canceled, or expired.

5. CRUD API
    - Create or cancel notifications.
    - Query events, notifications, and statuses.

Key capabilities
----------------
- End-to-end event → worker → scheduled job → notification pipeline.
- Job-level retry metadata and dead letter queue (DLQ) support.
- Idempotent worker logic to avoid duplicated notifications.
- Observability through logs.

Problem this solves
-------------------
This system answers the question: “How do you reliably trigger delayed notifications in a distributed system?”

It supports:
- Event-driven pipelines
- Asynchronous background processing
- Delayed execution and scheduling
- Retry policies and failure handling
- Idempotency
- Failure isolation and basic observability

Common use cases:
- Email/SMS reminders
- Billing/subscription notifications
- Password expiry alerts
- HR workflows and SLA alerts

Scalability and limitations
---------------------------
The system is functional for learning and small workloads, but it lacks several production-grade capabilities:

1. Redis & RQ limitations
    - RQ is not horizontally scalable (no partitioning, consumer groups, or replayability).
    - No strong delivery guarantees; Redis restarts could cause job loss unless persistence is configured.

2. Scheduler single point of failure
    - RQ Scheduler is a single process and not distributed.

3. Worker scaling
    - RQ doesn't provide safe auto-scaling or built-in load balancing for many worker replicas.

4. Missing production-grade features
    - Partitioned messaging, consumer groups, replayability, and multi-broker cluster support (consider Kafka or RabbitMQ for production).
    - Advanced durability and failover for Redis-backed jobs.

Why this project is useful for learning
--------------------------------------
This project maps well to multiple learning objectives:

- Goal 1 — End-to-end Kubernetes deployment
  - Practice Deployments, Services, PVs, Redis/Postgres configuration, HPA, ConfigMaps/Secrets, and Ingress.

- Goal 2 — Asynchronous systems, retries, DLQs
  - Practice producer → consumer pipelines, retry/backoff, DLQ, and idempotency.

- Goal 3 — Istio traffic management
  - With multiple services (API, worker, scheduler), you can learn routing, traffic splitting, observability, retry policies, circuit breaking, and mTLS.

- Goal 4 — GitHub Actions CI/CD
  - Practice building Docker images, pushing to GHCR, deploying to Kubernetes, running tests, applying migrations, and rolling updates.

Conclusion
----------
This project is well-suited to learn distributed systems, background processing, and deployment workflows. It’s a working foundation for exploring advanced system architecture but requires upgrades (message brokers, scheduler HA, worker autoscaling, Redis durability) before being production-ready.


