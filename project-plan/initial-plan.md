## 🎯 Project Goal

**Build a scalable, event-driven Notification System**
that can schedule and send time-based or event-based notifications (email, SMS, or logs) using **FastAPI, PostgreSQL, Redis, Celery**, deployed on **Kubernetes with Helm**, and progressively enhanced with **Istio**, **Gateway API**, **GitHub Actions**, and **Observability**.

---

## 🧭 Phase Overview

| Phase       | Focus                                   | New Concepts                                 | Deliverable                        |
| ----------- | --------------------------------------- | -------------------------------------------- | ---------------------------------- |
| **Phase 1** | Core system design & local Docker setup | FastAPI tasks + Celery workers + Redis       | Working local version              |
| **Phase 2** | Helm + K8s deployment                   | StatefulSets, ReplicaSets, Network isolation | Running in Minikube                |
| **Phase 3** | Istio & Gateway API integration         | Service mesh, traffic routing                | Traffic management & observability |
| **Phase 4** | CI/CD pipeline                          | GitHub Actions + DockerHub + Helm automation | Automated build-deploy             |
| **Phase 5** | Reliability layer                       | Retry, DLQ, idempotent handling              | Fault-tolerant background jobs     |
| **Phase 6** | Observability                           | Prometheus + Grafana                         | Metrics and dashboards             |
| **Phase 7** | Frontend & UX (optional)                | Next.js dashboard                            | Manage & view notifications        |

---

## 🏗️ Phase 1 — Core System (Local with Docker Compose)

### 🎯 Objective

Recreate the event notification flow locally using Docker Compose — this ensures you understand job queues, scheduling, and async processing before Kubernetes.

### ⚙️ Components

1. **FastAPI App** (REST API)

   * Endpoints:

     * `POST /notify` → create notification
     * `GET /notifications` → list notifications
   * Writes jobs to Redis queue (via Celery)
2. **Worker Service**

   * Celery worker (listening on Redis)
   * Executes scheduled jobs (simulated notifications)
3. **Redis** (Stateful queue broker)
4. **PostgreSQL** (stores notification metadata)

### 🧠 Learnings

* FastAPI + Celery integration
* Task scheduling with Redis backend
* Async job reliability basics
* Docker multi-service networking

### 🧰 Commands

```bash
docker compose up --build
```

✅ Deliverable:
A working FastAPI + Celery + Redis system that queues and processes notifications locally.

---

## ☸️ Phase 2 — Helm + Kubernetes Deployment

### 🎯 Objective

Move from Docker Compose → Kubernetes + Helm deployment.
Replicate architecture using Deployments, Services, StatefulSets.

### ⚙️ Components

| Component        | K8s Resource                | Notes                         |
| ---------------- | --------------------------- | ----------------------------- |
| FastAPI App      | **Deployment** (ReplicaSet) | Scalable web API              |
| Worker           | **Deployment**              | Independent from API replicas |
| Redis            | **StatefulSet**             | Persistent queue storage      |
| Postgres         | **StatefulSet** (Bitnami)   | Persistent DB                 |
| Ingress          | **Ingress / Gateway API**   | Expose FastAPI                |
| Config & Secrets | **ConfigMaps, Secrets**     | Env vars for services         |

### 🧠 Learnings

* StatefulSets vs Deployments
* Managing persistence in Redis/Postgres
* Helm templating for multi-component apps
* Using `.Values` for dynamic configs

### ⚙️ Example Helm command

```bash
helm upgrade --install notifier ./charts/notifier -n notifier
```

✅ Deliverable:
Fully running K8s setup in Minikube with FastAPI, Worker, Redis, Postgres accessible via ingress.

---

## 🌐 Phase 3 — Istio + Gateway API Integration

### 🎯 Objective

Introduce service mesh and fine-grained traffic control.

### ⚙️ Components

* **Istio Gateway**: Entry point instead of NGINX ingress
* **VirtualService**: Routes `/api` → FastAPI service
* **DestinationRule**: Define subsets (v1, v2) for canary/rolling updates

### 🧠 Learnings

* Install Istio (via `istioctl install --set profile=demo`)
* Understand Gateway vs Ingress
* Observe internal traffic flow with `kiali` or `istioctl dashboard`
* Canary rollout with Istio routing rules

### ⚙️ Example

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: notifier-api
spec:
  hosts:
    - "*"
  gateways:
    - notifier-gateway
  http:
    - route:
        - destination:
            host: notifier-backend
            subset: v1
```

✅ Deliverable:
Service mesh–enabled FastAPI backend accessible through Istio Gateway with routing rules.

---

## ⚙️ Phase 4 — CI/CD (GitHub Actions)

### 🎯 Objective

Automate build, test, push, and Helm deploy pipeline.

### 🧰 Steps

1. Create `.github/workflows/deploy.yml`
2. Trigger on push to `main`
3. Actions:

   * Build backend image
   * Push to DockerHub
   * Run `helm upgrade --install`
   * Optionally deploy to Minikube via SSH or ngrok tunnel

### 🧠 Learnings

* Build caching in CI
* Image versioning (Semantic tagging)
* Helm automation in pipelines

✅ Deliverable:
Automated workflow that deploys every push.

---

## 🔁 Phase 5 — Reliability Layer

### 🎯 Objective

Add resilience and robustness to message handling.

### 🧩 Techniques

* **Retry logic**: Celery built-in exponential backoff
* **Dead Letter Queue**: Failed messages sent to a separate Redis queue
* **Idempotent Jobs**: Prevent duplicate executions using job hash in DB
* **Logging & Alerts**: Track failed notifications

### 🧠 Learnings

* Production-grade queue management
* Designing fault-tolerant systems
* Using Redis Streams for DLQs

✅ Deliverable:
A resilient backend that can retry and recover failed tasks automatically.

---

## 📊 Phase 6 — Observability (Prometheus + Grafana)

### 🎯 Objective

Monitor notification throughput, failures, queue size, etc.

### ⚙️ Components

* **Prometheus Operator**: Collect metrics
* **Grafana Dashboard**: Visualize Celery queue size, task durations
* **Istio telemetry**: Add request tracing between API ↔ Worker

### 🧠 Learnings

* ServiceMonitor CRDs
* Custom metrics exposure in FastAPI
* Grafana dashboards from Helm charts

✅ Deliverable:
Real-time monitoring dashboard for your system.

---

## 🧑‍💻 Phase 7 — Frontend (Next.js Dashboard)

### 🎯 Objective

Add a professional UI to view and schedule notifications.

### ⚙️ Features

* View all scheduled & executed notifications
* Create new notifications (POST → API)
* Show metrics (via Prometheus APIs or FastAPI)

### 🧠 Learnings

* Next.js API integration
* Deployment as separate Helm release
* Exposing via Istio Gateway (same host, different path)

✅ Deliverable:
Full-stack event notification platform with observability and CI/CD.

---

## 🌈 Project Milestones Recap

| Phase | Focus               | Outcome                         |
| ----- | ------------------- | ------------------------------- |
| 1     | Local system        | Basic event processing          |
| 2     | Kubernetes + Helm   | Deployable cluster setup        |
| 3     | Istio + Gateway API | Mesh routing + canary control   |
| 4     | CI/CD               | Automated build + deploy        |
| 5     | Reliability         | Fault-tolerant, idempotent jobs |
| 6     | Observability       | Monitoring & metrics dashboards |
| 7     | Frontend            | Dashboard UI for management     |

---

## 🧩 Technology Stack Summary

| Layer                | Tools                                      |
| -------------------- | ------------------------------------------ |
| **Backend**          | FastAPI, Celery                            |
| **Queue**            | Redis (StatefulSet)                        |
| **Database**         | PostgreSQL (Bitnami Helm chart)            |
| **Deployment**       | Kubernetes + Helm                          |
| **Service Mesh**     | Istio + Gateway API                        |
| **CI/CD**            | GitHub Actions + DockerHub                 |
| **Monitoring**       | Prometheus + Grafana                       |
| **Frontend (later)** | Next.js                                    |
| **Access**           | ngrok / free hosting (for testing ingress) |

---

## 🏁 Learning Outcomes

By completing this project, you’ll:

* Master **end-to-end Kubernetes deployment** patterns.
* Understand **asynchronous systems, retries, and DLQs**.
* Learn **Istio traffic management** and **Gateway API routing**.
* Gain experience in **CI/CD automation** using GitHub Actions.
* Develop a **production-grade microservice** architecture.
* Achieve fluency in **debugging, monitoring, and scaling cloud-native systems**.

---
