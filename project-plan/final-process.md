
## 📣 Event Notification Service API

### Overview

The **Event Notification Service API** is a backend, machine-oriented service designed to ingest events and schedule time-based notifications in a reliable and asynchronous manner.

This API is  **not intended for direct human consumption** . Instead, it is meant to be integrated into **automated systems (M2M)** such as backend services, workflows, schedulers, and event-driven pipelines.

---

## 🎯 Intended Consumers

* Backend services
* Event producers
* Automation workflows
* Job schedulers
* Machine-to-machine (M2M) integrations

Human users are expected to interact with this service  **indirectly** , through applications or automation layers built on top of it.

---

## 🧩 Problem It Solves

Modern systems frequently need to:

* React to domain events (e.g., user signup, payment status changes)
* Schedule notifications relative to a future date
* Execute reminders asynchronously without blocking request flows
* Decouple event production from notification delivery

This service provides a centralized solution for  **event ingestion, notification persistence, and time-based orchestration** .

---

## ✅ Key Use Cases

### Event-driven notifications

* User signup notifications
* Payment success or failure alerts
* Subscription or password expiry reminders

### Scheduled reminders

* Notify users *N days before* a target date
* Schedule follow-ups or compliance reminders
* Time-based alerts triggered from system events

### Automation workflows

* A system publishes an event
* A notification is scheduled asynchronously
* Delivery is handled independently by background workers

---

## 🔌 API Capabilities

### Events API

Used to publish and retrieve system events.

* `POST /api/v1/events/` – Publish an event
* `GET /api/v1/events/` – Retrieve events

Events act as  **signals** , not delivery mechanisms.

### Notifications API

Used to create, manage, and cancel scheduled notifications.

* `POST /api/v1/notifications/` – Create a notification
* `DELETE /api/v1/notifications/{notification_id}` – Cancel a scheduled notification

**Design principles:**

* Notification is persisted immediately
* Scheduling happens asynchronously
* Scheduling failures are logged but do not block API responses

### Health API

Used for infrastructure and automation checks.

* `GET /health`

Provides service liveness and dependency visibility (database, Redis).

---

## ⚠️ Current Scope & Limitations

* Notification delivery channels are pluggable
* No human-facing UI is provided
* Focus is on scheduling, orchestration, and reliability
* Delivery providers (email, SMS, webhooks) are intentionally decoupled

---

## 🚀 Future Enhancements

* Email delivery provider integration
* SMS / webhook notification channels
* Delivery retry & dead-letter handling
* Notification status tracking
* Admin and observability dashboards

---

## 📌 Get started with setting up the application

To solve kubectl TLS handshake issue, try increasing the resource allocation for your local Kubernetes cluster.

`minikube start --cpus=4 --memory=8192` with `colima start --cpu 6 --memory 12`

This allocates more CPU and memory to the cluster, which can help resolve TLS handshake problems.

<!-- Required helm repos -->

```
Proj-2.0-Docker-K8s-Helm % helm repo list
NAME                    URL
prometheus-community    https://prometheus-community.github.io/helm-charts
bitnami                 https://charts.bitnami.com/bitnami
istio                   https://istio-release.storage.googleapis.com/charts
```

<!-- Required namespaces -->

```
Proj-2.0-Docker-K8s-Helm % kubectl create ns event-system
namespace/event-system created
Proj-2.0-Docker-K8s-Helm % kubectl create ns istio-system
namespace/istio-system created
Proj-2.0-Docker-K8s-Helm % kubectl create ns monitoring
namespace/monitoring created
```

<!-- Configure mkcert -->

```
brew install mkcert
mkcert -install

Proj-2.0-Docker-K8s-Helm % mv api.jayaraj.dev.pem cert.crt
Proj-2.0-Docker-K8s-Helm % mv api.jayaraj.dev-key.pem cert.key
```

<!-- Install Istio -->

```
Proj-2.0-Docker-K8s-Helm % helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace

NAME: istio-base
LAST DEPLOYED: Sun Dec 21 19:42:36 2025
NAMESPACE: istio-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Istio base successfully installed!

To learn more about the release, try:
  $ helm status istio-base -n istio-system
  $ helm get all istio-base -n istio-system

```

```
Proj-2.0-Docker-K8s-Helm % helm install istiod istio/istiod -n istio-system --wait


NAME: istiod
LAST DEPLOYED: Sun Dec 21 19:43:11 2025
NAMESPACE: istio-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
"istiod" successfully installed!

To learn more about the release, try:
  $ helm status istiod -n istio-system
  $ helm get all istiod -n istio-system

Next steps:
  * Deploy a Gateway: https://istio.io/latest/docs/setup/additional-setup/gateway/
  * Try out our tasks to get started on common configurations:
    * https://istio.io/latest/docs/tasks/traffic-management
    * https://istio.io/latest/docs/tasks/security/
    * https://istio.io/latest/docs/tasks/policy-enforcement/
  * Review the list of actively supported releases, CVE publications and our hardening guide:
    * https://istio.io/latest/docs/releases/supported-releases/
    * https://istio.io/latest/news/security/
    * https://istio.io/latest/docs/ops/best-practices/security/

For further documentation see https://istio.io website
Proj-2.0-Docker-K8s-Helm % helm ls -n istio-system
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART           APP VERSION
istio-base      istio-system    1               2025-12-21 19:42:36.554245 +0530 IST    deployed        base-1.28.1     1.28.1   
istiod          istio-system    1               2025-12-21 19:43:11.914933 +0530 IST    deployed        istiod-1.28.1   1.28.1   
Proj-2.0-Docker-K8s-Helm % 
```

```
Proj-2.0-Docker-K8s-Helm % helm install istio-ingress istio/gateway -n event-system


NAME: istio-ingress
LAST DEPLOYED: Sun Dec 21 19:45:17 2025
NAMESPACE: event-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
"istio-ingress" successfully installed!

To learn more about the release, try:
  $ helm status istio-ingress -n event-system
  $ helm get all istio-ingress -n event-system

Next steps:
  * Deploy an HTTP Gateway: https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/
  * Deploy an HTTPS Gateway: https://istio.io/latest/docs/tasks/traffic-management/ingress/secure-ingress/
Proj-2.0-Docker-K8s-Helm % 
```

```
Proj-2.0-Docker-K8s-Helm % kubectl create secret tls api-tls-secret -n event-system --cert=cert.crt --key=cert.key
secret/api-tls-secret created

```

<!-- Install postgress and redis -->

```
Proj-2.0-Docker-K8s-Helm % kubectl create secret generic pg-secret -n event-system  --from-literal=username=user --from-literal=password=supersecretpassword --from-literal=postgres-password=supersecretpassword --from-literal=database=notifications

Proj-2.0-Docker-K8s-Helm % helm install event-postgres bitnami/postgresql 
  --namespace event-system 
  --set auth.existingSecret=pg-secret 
  --set auth.username=user 
  --set auth.secretKeys.adminPasswordKey=postgres-password 
  --set auth.secretKeys.userPasswordKey=password 
  --set auth.database=notifications 
  --set volumePermissions.enabled=true 
  --set persistence.size=1Gi

Proj-2.0-Docker-K8s-Helm %  helm install event-redis bitnami/redis 
-n event-system 
--set architecture=standalone 
--set auth.enabled=false 
--set usePassword=false 
--set master.persistence.size=500Mi


i750332@GR2F96R7YN Proj-2.0-Docker-K8s-Helm % kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.postgres-password}" | base64 -d; echo
supersecretpassword

i750332@GR2F96R7YN Proj-2.0-Docker-K8s-Helm % kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.password}" | base64 -d; echo
supersecretpassword

Proj-2.0-Docker-K8s-Helm % kubectl run psql-test --rm -it --namespace event-system --image registry-1.docker.io/bitnami/postgresql:latest -- bash

in the terminal run below command to connect to the db
/opt/bitnami/scripts/postgresql/entrypoint.sh /bin/bash

psql -h event-postgres-postgresql -U user -d notifications
```

<!-- Install event-system -->

```
Proj-2.0-Docker-K8s-Helm % helm upgrade --install event-system event-system/. -n event-system

NAME: event-system
LAST DEPLOYED: Sun Dec 21 19:56:09 2025
NAMESPACE: event-system
STATUS: deployed
REVISION: 1
TEST SUITE: None

```

<!-- Install prometheus + grafana -->

```
Proj-2.0-Docker-K8s-Helm % helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring


NAME: kube-prometheus-stack
LAST DEPLOYED: Sun Dec 21 18:58:12 2025
NAMESPACE: monitoring
STATUS: deployed
REVISION: 1
NOTES:
kube-prometheus-stack has been installed. Check its status by running:
  kubectl --namespace monitoring get pods -l "release=kube-prometheus-stack"

Get Grafana 'admin' user password by running:

  kubectl --namespace monitoring get secrets kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo

Access Grafana local instance:

  export POD_NAME=$(kubectl --namespace monitoring get pod -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=kube-prometheus-stack" -oname)
  kubectl --namespace monitoring port-forward $POD_NAME 3000

Get your grafana admin user password by running:

  kubectl get secret --namespace monitoring -l app.kubernetes.io/component=admin-secret -o jsonpath="{.items[0].data.admin-password}" | base64 --decode ; echo


Visit https://github.com/prometheus-operator/kube-prometheus for instructions on how to create & configure Alertmanager and Prometheus instances using the Operator.
```

```
Proj-2.0-Docker-K8s-Helm % kubectl get all -n monitoring
NAME                                                       READY   STATUS            RESTARTS   AGE
alertmanager-kube-prometheus-stack-alertmanager-0          2/2     Running           0          50s
kube-prometheus-stack-grafana-59b75df58c-k9mmp             3/3     Running           0          2m58s
kube-prometheus-stack-kube-state-metrics-669dcf4b9-pr9np   1/1     Running           0          2m58s
kube-prometheus-stack-operator-6b677dd94f-b9dnt            1/1     Running           0          2m58s
kube-prometheus-stack-prometheus-node-exporter-vgxf8       1/1     Running           0          2m58s
prometheus-kube-prometheus-stack-prometheus-0              0/2     PodInitializing   0          50s
Proj-2.0-Docker-K8s-Helm % kubectl get pods -n monitoring
NAME                                                       READY   STATUS    RESTARTS   AGE
alertmanager-kube-prometheus-stack-alertmanager-0          2/2     Running   0          105s
kube-prometheus-stack-grafana-59b75df58c-k9mmp             3/3     Running   0          3m53s
kube-prometheus-stack-kube-state-metrics-669dcf4b9-pr9np   1/1     Running   0          3m53s
kube-prometheus-stack-operator-6b677dd94f-b9dnt            1/1     Running   0          3m53s
kube-prometheus-stack-prometheus-node-exporter-vgxf8       1/1     Running   0          3m53s
prometheus-kube-prometheus-stack-prometheus-0              2/2     Running   0          105s
Proj-2.0-Docker-K8s-Helm % clear
Proj-2.0-Docker-K8s-Helm % kubectl get all -n monitoring
NAME                                                           READY   STATUS    RESTARTS   AGE
pod/alertmanager-kube-prometheus-stack-alertmanager-0          2/2     Running   0          2m42s
pod/kube-prometheus-stack-grafana-59b75df58c-k9mmp             3/3     Running   0          4m50s
pod/kube-prometheus-stack-kube-state-metrics-669dcf4b9-pr9np   1/1     Running   0          4m50s
pod/kube-prometheus-stack-operator-6b677dd94f-b9dnt            1/1     Running   0          4m50s
pod/kube-prometheus-stack-prometheus-node-exporter-vgxf8       1/1     Running   0          4m50s
pod/prometheus-kube-prometheus-stack-prometheus-0              2/2     Running   0          2m42s

NAME                                                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
service/alertmanager-operated                            ClusterIP   None             <none>        9093/TCP,9094/TCP,9094/UDP   2m42s
service/kube-prometheus-stack-alertmanager               ClusterIP   10.105.116.124   <none>        9093/TCP,8080/TCP            4m50s
service/kube-prometheus-stack-grafana                    ClusterIP   10.104.124.186   <none>        80/TCP                       4m50s
service/kube-prometheus-stack-kube-state-metrics         ClusterIP   10.96.185.158    <none>        8080/TCP                     4m50s
service/kube-prometheus-stack-operator                   ClusterIP   10.106.151.191   <none>        443/TCP                      4m50s
service/kube-prometheus-stack-prometheus                 ClusterIP   10.110.72.212    <none>        9090/TCP,8080/TCP            4m50s
service/kube-prometheus-stack-prometheus-node-exporter   ClusterIP   10.107.195.126   <none>        9100/TCP                     4m50s
service/prometheus-operated                              ClusterIP   None             <none>        9090/TCP                     2m42s

NAME                                                            DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
daemonset.apps/kube-prometheus-stack-prometheus-node-exporter   1         1         1       1            1           kubernetes.io/os=linux   4m50s

NAME                                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/kube-prometheus-stack-grafana              1/1     1            1           4m50s
deployment.apps/kube-prometheus-stack-kube-state-metrics   1/1     1            1           4m50s
deployment.apps/kube-prometheus-stack-operator             1/1     1            1           4m50s

NAME                                                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/kube-prometheus-stack-grafana-59b75df58c             1         1         1       4m50s
replicaset.apps/kube-prometheus-stack-kube-state-metrics-669dcf4b9   1         1         1       4m50s
replicaset.apps/kube-prometheus-stack-operator-6b677dd94f            1         1         1       4m50s

NAME                                                               READY   AGE
statefulset.apps/alertmanager-kube-prometheus-stack-alertmanager   1/1     2m42s
statefulset.apps/prometheus-kube-prometheus-stack-prometheus       1/1     2m42s

```

```
Proj-2.0-Docker-K8s-Helm % sudo nano /etc/hosts

Add `127.0.0.1   api.jayaraj.dev`

Proj-2.0-Docker-K8s-Helm % kubectl port-forward -n event-system svc/istio-ingress 8443:443

Forwarding from 127.0.0.1:8443 -> 443
Forwarding from [::1]:8443 -> 443

Proj-2.0-Docker-K8s-Helm % curl https://api.jayaraj.dev:8443/
{"message":"Welcome to the Event Notification Service API","docs":"/docs"}%  

Go to: `https://api.jayaraj.dev:8443/metrics` to see fast-api metrics

kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090

Use "up" to check logs

Proj-2.0-Docker-K8s-Helm % kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80

create a Fast API Dashboard using an already available dashboard ID

now the dashboard is ready!

Test the deployed application using the test-deployed-backend.py script

```

<!-- K9s after deplopyment -->

![1766498318381](image/README/1766498318381.png)

![1766498372293](image/README/1766498372293.png)

<!-- Swagger UI for backend -->

![1766500594057](image/README/1766500594057.png)

<!-- Prometheus Logs -->

![1766500182632](image/README/1766500182632.png)

<!-- Grafana Dashboard -->

![1766500526458](image/README/1766500526458.png)
