# ------------------------------------------------------------

# 🚀 Phase 5 — Prometheus + Grafana for Event-System

# ------------------------------------------------------------

# 1. **What Prometheus Is**

Prometheus is a:

* **time-series metrics collector**
* **pull-based system**
* **purpose-built for microservices + Kubernetes**
* **de facto monitoring standard**

### Prometheus collects:

* CPU, RAM, Disk usage
* Response time, request counts
* Custom FastAPI metrics
* Istio request traces
* Redis/Postgres health
* Celery queue size, task rate, failures

---

# 2. **What Problem Prometheus Solves**

Modern microservices have  **too many moving parts** :

* worker
* scheduler
* API
* Redis
* PostgreSQL
* Istio ingress

Without monitoring:

❌ You don’t know if tasks are slow

❌ You don’t know queue size

❌ You don’t know API latency

❌ You don’t know traffic spikes

❌ You don’t know bottlenecks

**Prometheus solves this.**

---

# 3. **What Grafana Is**

Grafana is a:

* **dashboard visualization tool**
* **connects to Prometheus datasources**
* **creates graphs, alerts, heatmaps, KPIs**

With Grafana dashboards, you will see:

* API response latency
* Request throughput
* Worker queue size
* Celery task failures
* Redis saturation
* Database connection errors
* Istio inbound/outbound traffic

---

# 4. **Why Companies Use Them**

Because:

* They integrate natively with **Kubernetes**
* They are part of CNCF (Cloud Native Foundation)
* They scale extremely well
* They are **industry standard**

Used in:

Netflix, Uber, Stripe, Cloudflare, DoorDash, etc.

---

# 5. **Future of Prometheus + Grafana**

They remain the **industry standard** even in 2025 and beyond.

Grafana is even moving toward:

* LLM-based anomaly detection
* Auto-dashboards
* Grafana Cloud AI

Prometheus ecosystem is expanding with:

* OpenTelemetry
* Tempo (tracing)
* Loki (logging)

Their adoption will  **increase** , not decrease.

---

# ------------------------------------------------------------

# 🚀 How to Install Prometheus + Grafana in *Your Exact Cluster*

# ------------------------------------------------------------

You have:

<pre class="overflow-visible!" data-start="6637" data-end="6670"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>istio-</span><span>system</span><span>
event-</span><span>system</span><span>
</span></span></code></div></div></pre>

Best practice:

Install Prometheus stack in its own namespace:

<pre class="overflow-visible!" data-start="6737" data-end="6773"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>kubectl </span><span>create</span><span> ns monitoring
</span></span></code></div></div></pre>

### Install using Helm chart (recommended for production)

<pre class="overflow-visible!" data-start="6834" data-end="7037"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>helm repo add prometheus-community https:</span><span>//prometheus-community.github.io/helm-charts</span><span>
helm repo update

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
</span></span></code></div></div></pre>

This installs:

* Prometheus
* Grafana
* Alertmanager
* Node exporters
* ServiceMonitor CRDs

---

# 1. **Expose Grafana locally**

<pre class="overflow-visible!" data-start="7181" data-end="7265"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring </span><span>3000</span><span>:</span><span>80</span><span>
</span></span></code></div></div></pre>

Open:

<pre class="overflow-visible!" data-start="7274" data-end="7303"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>http:</span><span>//localhost:3000</span><span>
</span></span></code></div></div></pre>

Default login:

<pre class="overflow-visible!" data-start="7321" data-end="7364"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>user</span><span>: </span><span>admin</span><span>
</span><span>password</span><span>: prom-</span><span>operator</span><span>
</span></span></code></div></div></pre>

---

# 2. **Enable Istio Telemetry**

Istio automatically emits metrics.

The Prometheus chart automatically scrapes them.

To confirm:

<pre class="overflow-visible!" data-start="7504" data-end="7544"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>kubectl </span><span>get</span><span> pods </span><span>-</span><span>n istio</span><span>-</span><span>system</span><span>
</span></span></code></div></div></pre>

You should see labels:

<pre class="overflow-visible!" data-start="7570" data-end="7606"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>prometheus.io/scrape: </span><span>"true"</span><span>
</span></span></code></div></div></pre>

---

# 3. **Add ServiceMonitor for Event-System Backend**

Create:

<pre class="overflow-visible!" data-start="7676" data-end="7712"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>event-system/monitoring.yaml
</span></span></code></div></div></pre>

Add to your Helm chart later.

<pre class="overflow-visible!" data-start="7745" data-end="8073"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>monitoring.coreos.com/v1</span><span>
</span><span>kind:</span><span></span><span>ServiceMonitor</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>event-system-backend</span><span>
  </span><span>namespace:</span><span></span><span>monitoring</span><span>
</span><span>spec:</span><span>
  </span><span>selector:</span><span>
    </span><span>matchLabels:</span><span>
      </span><span>app:</span><span></span><span>event-system-backend</span><span>
  </span><span>namespaceSelector:</span><span>
    </span><span>matchNames:</span><span>
      </span><span>-</span><span></span><span>event-system</span><span>
  </span><span>endpoints:</span><span>
    </span><span>-</span><span></span><span>port:</span><span></span><span>http</span><span>
      </span><span>path:</span><span></span><span>/metrics</span><span>
      </span><span>interval:</span><span></span><span>15s</span><span>
</span></span></code></div></div></pre>

Your FastAPI must expose:

<pre class="overflow-visible!" data-start="8102" data-end="8118"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>/metrics
</span></span></code></div></div></pre>

You can add:

<pre class="overflow-visible!" data-start="8134" data-end="8253"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>from</span><span> prometheus_fastapi_instrumentator </span><span>import</span><span> Instrumentator
Instrumentator().instrument(app).expose(app)
</span></span></code></div></div></pre>

---

# 4. **Grafana Dashboards**

Grafana →

**Import Dashboard → ID**

Useful IDs:

| Dashboard            | ID                      |
| -------------------- | ----------------------- |
| Kubernetes Cluster   | 315                     |
| Istio Control Plane  | 7645                    |
| Istio Mesh Dashboard | 7639                    |
| Redis                | 11835                   |
| PostgreSQL           | 9628                    |
| Celery               | custom, small yaml file |

You will now visualize your entire system.



# Installation of Prometheus and Grafana using Helm

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "istio" chart repository
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
NAME: kube-prometheus-stack
LAST DEPLOYED: Thu Dec 11 20:53:46 2025
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
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ 