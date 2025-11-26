## 0 — High level plan

1. create namespace `event-system`
2. install Istio (demo profile) on minikube
3. label namespace for istio sidecar injection
4. add Helm repos (bitnami)
5. create a Helm chart (umbrella) for your app that:
   * installs backend, worker, scheduler Deployments & Services
   * depends on bitnami/postgresql and bitnami/redis subcharts
6. install the chart in `event-system`
7. create Istio Gateway & VirtualService to expose `backend` externally
8. test with `curl` / your `test-app.py`
9. next steps (monitoring, scaling, k8s configs)

---

## 1 — Prepare minikube & cluster

Start minikube (use Docker driver or your usual driver):

<pre class="overflow-visible!" data-start="1262" data-end="1309"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>minikube start --memory=6g --cpus=2
</span></span></code></div></div></pre>

Enable docker-env if you want to build images inside minikube (optional):

<pre class="overflow-visible!" data-start="1386" data-end="1425"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>eval</span><span> $(minikube docker-env)
</span></span></code></div></div></pre>

Create namespace:

<pre class="overflow-visible!" data-start="1446" data-end="1488"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl create ns event-system
</span></span></code></div></div></pre>

---

## 2 — Install Istio (demo profile, for learning)

If you don't have `istioctl`, install it (Linux/macOS example):

<pre class="overflow-visible!" data-start="1611" data-end="1706"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl -L https://istio.io/downloadIstio | sh -
</span><span>cd</span><span> istio-*
</span><span>export</span><span> PATH=</span><span>$PWD</span><span>/bin:</span><span>$PATH</span><span>
</span></span></code></div></div></pre>

Install Istio (demo is fine for learning):

<pre class="overflow-visible!" data-start="1752" data-end="1802"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>istioctl install --</span><span>set</span><span> profile=demo -y
</span></span></code></div></div></pre>

Label your namespace for automatic sidecar injection:

<pre class="overflow-visible!" data-start="1859" data-end="1931"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl label namespace event-system istio-injection=enabled
</span></span></code></div></div></pre>

Confirm Istio ingressgateway is up:

<pre class="overflow-visible!" data-start="1970" data-end="2014"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get pods -n istio-system
</span></span></code></div></div></pre>

For local access to Istio ingress, you can port-forward:

<pre class="overflow-visible!" data-start="2074" data-end="2212"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80
</span><span># backend will be available at http://localhost:8080/...</span><span>
</span></span></code></div></div></pre>

(Alternative: `minikube tunnel` to expose LoadBalancer but port-forward is easiest.)

---

## 3 — Add Helm repos

<pre class="overflow-visible!" data-start="2328" data-end="2413"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
</span></span></code></div></div></pre>

---

## 4 — Create a Helm chart for your application

You can create a chart or copy these files into a directory `charts/event-backend/`.

I’ll provide the minimum files you need. Create a folder `charts/event-backend/` and add the following.

### `charts/event-backend/Chart.yaml`

<pre class="overflow-visible!" data-start="2698" data-end="3235"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>v2</span><span>
</span><span>name:</span><span></span><span>event-backend</span><span>
</span><span>description:</span><span></span><span>Event</span><span></span><span>Notification</span><span></span><span>Service</span><span></span><span>(backend</span><span></span><span>+</span><span></span><span>worker</span><span></span><span>+</span><span></span><span>scheduler)</span><span>
</span><span>version:</span><span></span><span>0.1</span><span>.0</span><span>
</span><span>appVersion:</span><span></span><span>"1.0.0"</span><span>
</span><span>dependencies:</span><span>
  </span><span>-</span><span></span><span>name:</span><span></span><span>postgresql</span><span>
    </span><span>version:</span><span></span><span>12.11</span><span>.12</span><span></span><span># choose a stable bitnami/postgresql chart version; adjust if needed</span><span>
    </span><span>repository:</span><span></span><span>https://charts.bitnami.com/bitnami</span><span>
    </span><span>condition:</span><span></span><span>postgresql.enabled</span><span>
  </span><span>-</span><span></span><span>name:</span><span></span><span>redis</span><span>
    </span><span>version:</span><span></span><span>19.10</span><span>.7</span><span></span><span># choose a stable bitnami/redis chart version</span><span>
    </span><span>repository:</span><span></span><span>https://charts.bitnami.com/bitnami</span><span>
    </span><span>condition:</span><span></span><span>redis.enabled</span><span>
</span></span></code></div></div></pre>

### `charts/event-backend/values.yaml` (edit as required)

<pre class="overflow-visible!" data-start="3295" data-end="4573"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span># Chart-wide default values</span><span>
</span><span>namespaceOverride:</span><span></span><span>event-system</span><span>

</span><span>postgresql:</span><span>
  </span><span>enabled:</span><span></span><span>true</span><span>
  </span><span>global:</span><span>
    </span><span>storageClass:</span><span></span><span>"standard"</span><span>
  </span><span>postgresqlUsername:</span><span></span><span>postgres</span><span>
  </span><span>postgresqlPassword:</span><span></span><span>postgres</span><span>
  </span><span>postgresqlDatabase:</span><span></span><span>notifications</span><span>
  </span><span>primary:</span><span>
    </span><span>persistence:</span><span>
      </span><span>enabled:</span><span></span><span>true</span><span>
      </span><span>size:</span><span></span><span>1Gi</span><span>

</span><span>redis:</span><span>
  </span><span>enabled:</span><span></span><span>true</span><span>
  </span><span>cluster:</span><span>
    </span><span>enabled:</span><span></span><span>false</span><span>
  </span><span>usePassword:</span><span></span><span>false</span><span>

</span><span>image:</span><span>
  </span><span>repository:</span><span></span><span>jayaraj0781/event-backend</span><span>
  </span><span>tag:</span><span></span><span>v1.0.0</span><span>
  </span><span>pullPolicy:</span><span></span><span>IfNotPresent</span><span>

</span><span>replicaCount:</span><span>
  </span><span>backend:</span><span></span><span>1</span><span>
  </span><span>worker:</span><span></span><span>1</span><span>
  </span><span>scheduler:</span><span></span><span>1</span><span>

</span><span>backend:</span><span>
  </span><span>enabled:</span><span></span><span>true</span><span>
  </span><span>image:</span><span>
    </span><span>repository:</span><span></span><span>jayaraj0781/event-backend</span><span>
    </span><span>tag:</span><span></span><span>v1.0.0</span><span>
  </span><span>env:</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>POSTGRES_HOST</span><span>
      </span><span>value:</span><span></span><span>"{{ .Release.Name }}</span><span>-postgresql"   </span><span># bitnami postgresql service name.</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>POSTGRES_USER</span><span>
      </span><span>value:</span><span></span><span>"postgres"</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>POSTGRES_PASSWORD</span><span>
      </span><span>value:</span><span></span><span>"postgres"</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>POSTGRES_DB</span><span>
      </span><span>value:</span><span></span><span>"notifications"</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>REDIS_HOST</span><span>
      </span><span>value:</span><span></span><span>"{{ .Release.Name }}</span><span>-redis-master"  </span><span># bitnami redis service name</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>REDIS_PORT</span><span>
      </span><span>value:</span><span></span><span>"6379"</span><span>
  </span><span>service:</span><span>
    </span><span>type:</span><span></span><span>ClusterIP</span><span>
    </span><span>port:</span><span></span><span>5001</span><span>

</span><span>worker:</span><span>
  </span><span>enabled:</span><span></span><span>true</span><span>
  </span><span>image:</span><span>
    </span><span>repository:</span><span></span><span>jayaraj0781/event-backend</span><span>
    </span><span>tag:</span><span></span><span>v1.0.0</span><span>

</span><span>scheduler:</span><span>
  </span><span>enabled:</span><span></span><span>true</span><span>
  </span><span>image:</span><span>
    </span><span>repository:</span><span></span><span>jayaraj0781/event-backend</span><span>
    </span><span>tag:</span><span></span><span>v1.0.0</span><span>

</span><span>resources:</span><span> {}
</span></span></code></div></div></pre>

> **Note:** the service names for Bitnami charts follow pattern `<release>-postgresql` and `<release>-redis-master`. We’ll use Helm release name to compute hostnames. You can also explicitly set hostnames in values.

---

### Templates

Create a `templates/` directory in the chart and add three Deployment + Service templates. I’ll show one and the rest are similar.

#### `templates/backend-deployment.yaml`

<pre class="overflow-visible!" data-start="4984" data-end="6289"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>{{</span><span>-</span><span></span><span>if</span><span></span><span>.Values.backend.enabled</span><span> }}
</span><span>apiVersion:</span><span></span><span>apps/v1</span><span>
</span><span>kind:</span><span></span><span>Deployment</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
  </span><span>labels:</span><span>
    </span><span>app.kubernetes.io/name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.name"</span><span></span><span>.</span><span> }}
    </span><span>app.kubernetes.io/instance:</span><span> {{ </span><span>.Release.Name</span><span> }}
</span><span>spec:</span><span>
  </span><span>replicas:</span><span> {{ </span><span>.Values.replicaCount.backend</span><span></span><span>|</span><span></span><span>default</span><span></span><span>1</span><span> }}
  </span><span>selector:</span><span>
    </span><span>matchLabels:</span><span>
      </span><span>app:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
  </span><span>template:</span><span>
    </span><span>metadata:</span><span>
      </span><span>labels:</span><span>
        </span><span>app:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
    </span><span>spec:</span><span>
      </span><span>containers:</span><span>
        </span><span>-</span><span></span><span>name:</span><span></span><span>backend</span><span>
          </span><span>image:</span><span></span><span>"{{ .Values.backend.image.repository }}</span><span>:</span><span>{{ .Values.backend.image.tag }}</span><span>"
          </span><span>imagePullPolicy:</span><span> {{ </span><span>.Values.image.pullPolicy</span><span> }}
          </span><span>command:</span><span> [</span><span>"/app/.venv/bin/uvicorn"</span><span>]
          </span><span>args:</span><span> [</span><span>"app.main:app"</span><span>, </span><span>"--host"</span><span>, </span><span>"0.0.0.0"</span><span>, </span><span>"--port"</span><span>, </span><span>"5001"</span><span>]
          </span><span>ports:</span><span>
            </span><span>-</span><span></span><span>containerPort:</span><span></span><span>5001</span><span>
          </span><span>env:</span><span>
{{</span><span>-</span><span></span><span>range</span><span></span><span>.Values.backend.env</span><span> }}
            </span><span>-</span><span></span><span>name:</span><span> {{ </span><span>.name</span><span> }}
              </span><span>value:</span><span> {{ </span><span>quote</span><span></span><span>.value</span><span> }}
{{</span><span>-</span><span></span><span>end</span><span> }}
</span><span>---</span><span>
</span><span>apiVersion:</span><span></span><span>v1</span><span>
</span><span>kind:</span><span></span><span>Service</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
</span><span>spec:</span><span>
  </span><span>selector:</span><span>
    </span><span>app:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
  </span><span>ports:</span><span>
    </span><span>-</span><span></span><span>port:</span><span></span><span>5001</span><span>
      </span><span>targetPort:</span><span></span><span>5001</span><span>
      </span><span>protocol:</span><span></span><span>TCP</span><span>
      </span><span>name:</span><span></span><span>http</span><span>
{{</span><span>-</span><span></span><span>end</span><span> }}
</span></span></code></div></div></pre>

Create similar `templates/worker-deployment.yaml` and `templates/scheduler-deployment.yaml` with appropriate command lines:

* worker: `command: ["/app/.venv/bin/python"] args: ["-u", "-m", "app.workers.consumer"]`
* scheduler: `command: ["/app/.venv/bin/python"] args: ["-u", "-m", "app.workers.producer"]`

(You can reuse the same image; separate Deployments.)

---

### Add helper templates

Create `_helpers.tpl` to provide `fullname` function used above:

`templates/_helpers.tpl`

<pre class="overflow-visible!" data-start="6775" data-end="7008"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-gotmpl"><span>{{- define "event-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride -}}
{{- end -}}

{{- define "event-backend.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "event-backend.name" .) -}}
{{- end -}}
</span></code></div></div></pre>

---

## 5 — Install the chart

From the parent directory where `charts/event-backend` lives (or path to chart):

<pre class="overflow-visible!" data-start="7123" data-end="7197"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm install event-system charts/event-backend -n event-system
</span></span></code></div></div></pre>

This will:

* Install Bitnami Postgres and Redis as subcharts
* Create your backend, worker, and scheduler Deployments & Services

If you want to override values from `values.yaml`, use `-f my-values.yaml` or `--set`.

Example using release name `event-system` so Postgres service will be `event-system-postgresql`.

If you used a different release name, adjust env hostnames accordingly.

---

## 6 — Confirm & check pods

<pre class="overflow-visible!" data-start="7622" data-end="7845"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get pods -n event-system
kubectl get svc -n event-system
kubectl logs -n event-system deploy/event-system-event-backend-backend -f
kubectl logs -n event-system deploy/event-system-event-backend-worker -f
</span></span></code></div></div></pre>

---

## 7 — Expose backend via Istio Gateway & VirtualService

Create `istio-gateway.yaml` in the chart `templates/` or apply directly.

`templates/istio-gateway-vs.yaml`

<pre class="overflow-visible!" data-start="8018" data-end="8759"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>networking.istio.io/v1beta1</span><span>
</span><span>kind:</span><span></span><span>Gateway</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>event-backend-gateway</span><span>
  </span><span>namespace:</span><span></span><span>event-system</span><span>
</span><span>spec:</span><span>
  </span><span>selector:</span><span>
    </span><span>istio:</span><span></span><span>ingressgateway</span><span>
  </span><span>servers:</span><span>
    </span><span>-</span><span></span><span>port:</span><span>
        </span><span>number:</span><span></span><span>80</span><span>
        </span><span>name:</span><span></span><span>http</span><span>
        </span><span>protocol:</span><span></span><span>HTTP</span><span>
      </span><span>hosts:</span><span>
        </span><span>-</span><span></span><span>"*"</span><span>
</span><span>---</span><span>
</span><span>apiVersion:</span><span></span><span>networking.istio.io/v1beta1</span><span>
</span><span>kind:</span><span></span><span>VirtualService</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>event-backend-vs</span><span>
  </span><span>namespace:</span><span></span><span>event-system</span><span>
</span><span>spec:</span><span>
  </span><span>hosts:</span><span>
    </span><span>-</span><span></span><span>"*"</span><span>
  </span><span>gateways:</span><span>
    </span><span>-</span><span></span><span>event-backend-gateway</span><span>
  </span><span>http:</span><span>
    </span><span>-</span><span></span><span>match:</span><span>
        </span><span>-</span><span></span><span>uri:</span><span>
            </span><span>prefix:</span><span></span><span>/</span><span>
      </span><span>route:</span><span>
        </span><span>-</span><span></span><span>destination:</span><span>
            </span><span>host:</span><span> {{ </span><span>printf</span><span></span><span>"%s-%s"</span><span></span><span>.Release.Name</span><span></span><span>(include</span><span></span><span>"event-backend.name"</span><span></span><span>.)</span><span> }}</span><span>-backend.event-system.svc.cluster.local</span><span>
            </span><span>port:</span><span>
              </span><span>number:</span><span></span><span>5001</span><span>
</span></span></code></div></div></pre>

If you installed via Helm, apply template or include in chart.

To reach the service locally with Istio port-forward:

<pre class="overflow-visible!" data-start="8880" data-end="9002"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80
</span><span># then</span><span>
curl http://localhost:8080/health
</span></span></code></div></div></pre>

---

## 8 — Secrets & config

* For production, store DB/Redis credentials in Kubernetes Secrets, not in `values.yaml`.
* Use `helm secrets` or Kubernetes `Secret` with `.env` values mounted as envFrom or specific env entries.

Example (apply secret):

<pre class="overflow-visible!" data-start="9257" data-end="9424"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n event-system create secret generic event-backend-secrets \
  --from-literal=POSTGRES_PASSWORD=</span><span>'supersecret'</span><span> \
  --from-literal=REDIS_PASSWORD=</span><span>''</span><span>
</span></span></code></div></div></pre>

Then use `envFrom` in your Deployment to load them.

---

## 9 — Helpful commands

Port forward to test without Istio:

<pre class="overflow-visible!" data-start="9546" data-end="9696"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n event-system port-forward svc/event-system-event-backend-backend 5001:5001
</span><span># now test locally</span><span>
curl http://localhost:5001/health
</span></span></code></div></div></pre>

Check worker logs:

<pre class="overflow-visible!" data-start="9718" data-end="9802"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl logs -n event-system deploy/event-system-event-backend-worker -f
</span></span></code></div></div></pre>

Delete everything:

<pre class="overflow-visible!" data-start="9824" data-end="9910"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm uninstall event-system -n event-system
kubectl delete ns event-system
</span></span></code></div></div></pre>

---

## 10 — Notes, caveats and next steps

* **Local minikube storageclass** : `primary.persistence.size=1Gi` works; minikube provides a default `standard` storageclass.
* **ImagePullPolicy** : If images are local to your machine and you used `eval $(minikube docker-env)`, they will be available in the cluster. Otherwise ensure images are pushed to Docker Hub and reachable.
* **Istio mTLS and Gateway API** : We used Istio Gateway + VirtualService for routing. For Gateway API (Kubernetes Gateway) you can later replace with Gateway resources; Istio supports Gateway API but it’s an additional step.
* **Monitoring** : Add Prometheus + Grafana (or use Istio telemetry) later. You can install the `kube-prometheus-stack` or use Istio add-ons.


# 1) Istio install *profiles* — quick reference

Istio ships with a few opinionated **install profiles** you can choose with `istioctl install --set profile=<name>` (or via the Operator). Common profiles:

* **demo**
  * Purpose: developer learning / demo environments.
  * Contents: lots of add-ons enabled (Prometheus, Grafana, Kiali, Jaeger), permissive defaults, sample certs, permissive mTLS, more permissive resource usage.
  * When to use: local dev, experiments, learning (recommended for you while learning Istio features).
* **default**
  * Purpose: production-ready default configuration.
  * Contents: core control plane + ingress/egress gateways, minimal telemetry (but not all dev addons). More conservative than `demo`.
  * When to use: production clusters or staging that's close to prod.
* **minimal**
  * Purpose: smallest possible Istio (lightweight).
  * Contents: only essential control plane components (istiod, minimal gateways). Less telemetry & addons.
  * When to use: resource-constrained environments or when you want to add exactly what you need.
* **remote**
  * Purpose: used when creating a remote cluster that joins a multi-cluster mesh.
  * Contents: smaller; configured to connect to a central control plane.
  * When to use: multi-cluster topologies.
* **profile customization**
  * You can customize any profile (enable/disable addons, enable Gateway API support, enable mTLS, change telemetry configs etc.) via `istioctl install -f <custom-values.yaml>`.

**Recommendation for you:** start with `demo` to learn traffic management, observability (Grafana/Prometheus), and Kiali. Later switch to `default`/`minimal` when you harden the stack.

---

# 2) Istio components that matter for your project & why

Your app has: API backend (HTTP), worker/scheduler (internal), Redis, Postgres.

Istio brings value in several areas — these are the components we will use:

* **istiod** — control plane (service discovery, config distribution, xDS). Required.
* **sidecar (Envoy) proxies** — injected into your backend/worker pods. Provide L7 routing, telemetry, mTLS, retries, and timeouts.
* **istio-ingressgateway** — entrypoint to the mesh. We’ll route external traffic through it.
* **egressgateway (optional)** — if you want to centralize outbound traffic (e.g., external mail API).
* **Telemetry addons** (Prometheus, Grafana, Kiali, Jaeger) — useful for learning and debugging.
* **Gateway + VirtualService** — Istio resources to route external HTTP traffic to your backend service with features like retries/timeouts/circuit-breakers.

We will enable sidecar injection in the `event-system` namespace so **backend** and **workers** get proxies (workers can remain sidecar-less if you prefer, but sidecar gives better observability and mTLS inside mesh).

---

# 3) How we will use Istio here (concrete features)

* **Ingress Routing & Gateway** : Use Istio `Gateway` + `VirtualService` (or Kubernetes Gateway API later) to expose the backend through the Istio ingressgateway.
* **Traffic management** : implement retries, timeouts, and circuit breakers for backend → external services (or for canary/blue-green).
* **Observability** : collect metrics/traces (via Prometheus, Grafana, Jaeger); use Kiali for service topology.
* **mTLS (optional)** : enable mesh mTLS to secure pod-to-pod traffic and learn auth policies.
* **Fault injection & traffic-splitting** : practice canary deployments by splitting traffic across backend versions.
* **Policy/Rate limiting** : can be added via Istio (or Envoy filters) for advanced exercises.

---

# 4) Istio vs Kubernetes Gateway API — how they relate

* **Istio Gateway / VirtualService** are Istio CRDs (native to Istio). They configure Envoy proxies installed by Istio.
* **Gateway API** is a Kubernetes SIG project that standardizes gateway & route resources across implementations. It defines resources: `GatewayClass`, `Gateway`, `HTTPRoute`, etc.
* **Istio supports the Gateway API** (recent versions). You can choose:
  * Use Istio `Gateway` + `VirtualService` (simpler for Istio-centric deployments).
  * Or use **Gateway API** resources (preferred if you want standardized Kubernetes-native routing). Istio must be configured with Gateway API support.

**Which to choose for learning:** Start with Istio `Gateway` + `VirtualService` (simpler and well documented). Once comfortable, switch to Gateway API to learn vendor-neutral routing; I’ll show how to set both up and how to add templates for Helm.

---

# 5) Practical step-by-step: what files to create and why

Below I give the **exact files** to add to your Helm chart (`charts/event-backend/templates/`) and the  **sequence of commands** . I’ll provide both an **Istio Gateway** option and a **Gateway API** option.

---

## A — Preconditions / commands

1. Install Istio (demo):

<pre class="overflow-visible!" data-start="5540" data-end="5675"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>istioctl install --</span><span>set</span><span> profile=demo -y
kubectl create ns event-system
kubectl label ns event-system istio-injection=enabled
</span></span></code></div></div></pre>

2. Add Helm chart and install your application (as earlier). After Helm deploys, proceed to create routing objects.

---

## B — Files to add to your Helm chart (Istio option)

Place these in `charts/event-backend/templates/`.

### 1) `templates/istio-gateway.yaml` — Istio Gateway + VirtualService + DestinationRule

<pre class="overflow-visible!" data-start="5995" data-end="7573"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>{{</span><span>-</span><span></span><span>if</span><span></span><span>.Values.istio.enableGateway</span><span> }}
</span><span>apiVersion:</span><span></span><span>networking.istio.io/v1beta1</span><span>
</span><span>kind:</span><span></span><span>Gateway</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-gateway</span><span>
  </span><span>namespace:</span><span> {{ </span><span>.Release.Namespace</span><span> }}
</span><span>spec:</span><span>
  </span><span>selector:</span><span>
    </span><span>istio:</span><span></span><span>ingressgateway</span><span>
  </span><span>servers:</span><span>
    </span><span>-</span><span></span><span>port:</span><span>
        </span><span>number:</span><span></span><span>80</span><span>
        </span><span>name:</span><span></span><span>http</span><span>
        </span><span>protocol:</span><span></span><span>HTTP</span><span>
      </span><span>hosts:</span><span>
        </span><span>-</span><span></span><span>"*"</span><span>
</span><span>---</span><span>
</span><span>apiVersion:</span><span></span><span>networking.istio.io/v1beta1</span><span>
</span><span>kind:</span><span></span><span>VirtualService</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-vs</span><span>
  </span><span>namespace:</span><span> {{ </span><span>.Release.Namespace</span><span> }}
</span><span>spec:</span><span>
  </span><span>hosts:</span><span>
    </span><span>-</span><span></span><span>"*"</span><span>
  </span><span>gateways:</span><span>
    </span><span>-</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-gateway</span><span>
  </span><span>http:</span><span>
    </span><span>-</span><span></span><span>match:</span><span>
        </span><span>-</span><span></span><span>uri:</span><span>
            </span><span>prefix:</span><span></span><span>/</span><span>
      </span><span>route:</span><span>
        </span><span>-</span><span></span><span>destination:</span><span>
            </span><span>host:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend.{{</span><span></span><span>.Release.Namespace</span><span></span><span>}}.svc.cluster.local</span><span>
            </span><span>port:</span><span>
              </span><span>number:</span><span></span><span>5001</span><span>
      </span><span>retries:</span><span>
        </span><span>attempts:</span><span></span><span>3</span><span>
        </span><span>perTryTimeout:</span><span></span><span>2s</span><span>
        </span><span>retryOn:</span><span></span><span>gateway-error,connect-failure,refused-stream</span><span>
      </span><span>timeout:</span><span></span><span>15s</span><span>
</span><span>---</span><span>
</span><span>apiVersion:</span><span></span><span>networking.istio.io/v1beta1</span><span>
</span><span>kind:</span><span></span><span>DestinationRule</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-dr</span><span>
  </span><span>namespace:</span><span> {{ </span><span>.Release.Namespace</span><span> }}
</span><span>spec:</span><span>
  </span><span>host:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend.{{</span><span></span><span>.Release.Namespace</span><span></span><span>}}.svc.cluster.local</span><span>
  </span><span>trafficPolicy:</span><span>
    </span><span>connectionPool:</span><span>
      </span><span>tcp:</span><span>
        </span><span>maxConnections:</span><span></span><span>100</span><span>
      </span><span>http:</span><span>
        </span><span>http1MaxPendingRequests:</span><span></span><span>100</span><span>
        </span><span>maxRequestsPerConnection:</span><span></span><span>0</span><span>
    </span><span>outlierDetection:</span><span>
      </span><span>consecutive5xx:</span><span></span><span>5</span><span>
      </span><span>interval:</span><span></span><span>10s</span><span>
      </span><span>baseEjectionTime:</span><span></span><span>30s</span><span>
      </span><span>maxEjectionPercent:</span><span></span><span>50</span><span>
{{</span><span>-</span><span></span><span>end</span><span> }}
</span></span></code></div></div></pre>

**What this does:**

* `Gateway` binds to Istio ingressgateway.
* `VirtualService` routes `/*` to your backend and sets retries/timeouts.
* `DestinationRule` configures connection pools and outlier detection (circuit-breaker behaviour).

Add a toggle in `values.yaml`:

<pre class="overflow-visible!" data-start="7847" data-end="7887"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>istio:</span><span>
  </span><span>enableGateway:</span><span></span><span>true</span><span>
</span></span></code></div></div></pre>

---

## C — Files to add for **Gateway API** (alternative)

If you prefer Gateway API objects, add these templates.

> Note: to use Gateway API with Istio you must enable the Gateway API feature in Istio (Istio versions differ). We will assume Istio supports it; otherwise apply these as straight Gateway resources for a Gateway API controller.

### 1) `templates/gatewayclass.yaml`

<pre class="overflow-visible!" data-start="8272" data-end="8425"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>gateway.networking.k8s.io/v1alpha2</span><span>
</span><span>kind:</span><span></span><span>GatewayClass</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>istio</span><span>
</span><span>spec:</span><span>
  </span><span>controllerName:</span><span></span><span>istio.io/gateway-controller</span><span>
</span></span></code></div></div></pre>

*(some installs create GatewayClass for Istio automatically — check `kubectl get gatewayclass`)*

### 2) `templates/gateway.yaml`

<pre class="overflow-visible!" data-start="8557" data-end="8893"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>gateway.networking.k8s.io/v1alpha2</span><span>
</span><span>kind:</span><span></span><span>Gateway</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-gateway</span><span>
  </span><span>namespace:</span><span> {{ </span><span>.Release.Namespace</span><span> }}
</span><span>spec:</span><span>
  </span><span>gatewayClassName:</span><span></span><span>istio</span><span>
  </span><span>listeners:</span><span>
    </span><span>-</span><span></span><span>name:</span><span></span><span>http</span><span>
      </span><span>protocol:</span><span></span><span>HTTP</span><span>
      </span><span>port:</span><span></span><span>80</span><span>
      </span><span>allowedRoutes:</span><span>
        </span><span>namespaces:</span><span>
          </span><span>from:</span><span></span><span>All</span><span>
</span></span></code></div></div></pre>

### 3) `templates/httproute.yaml`

<pre class="overflow-visible!" data-start="8929" data-end="9425"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>gateway.networking.k8s.io/v1alpha2</span><span>
</span><span>kind:</span><span></span><span>HTTPRoute</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-route</span><span>
  </span><span>namespace:</span><span> {{ </span><span>.Release.Namespace</span><span> }}
</span><span>spec:</span><span>
  </span><span>parentRefs:</span><span>
    </span><span>-</span><span></span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-gateway</span><span>
  </span><span>rules:</span><span>
    </span><span>-</span><span></span><span>matches:</span><span>
        </span><span>-</span><span></span><span>path:</span><span>
            </span><span>type:</span><span></span><span>PathPrefix</span><span>
            </span><span>value:</span><span></span><span>/</span><span>
      </span><span>forwardTo:</span><span>
        </span><span>-</span><span></span><span>service:</span><span>
            </span><span>name:</span><span> {{ </span><span>include</span><span></span><span>"event-backend.fullname"</span><span></span><span>.</span><span> }}</span><span>-backend</span><span>
            </span><span>port:</span><span></span><span>5001</span><span>
          </span><span>weight:</span><span></span><span>100</span><span>
</span></span></code></div></div></pre>

**Notes:**

* Use Gateway API when you want vendor-agnostic routing.
* Istio will consume Gateway API resources if the Istio Gateway API integration is enabled.

---

## D — Helm values toggles

Add options to `values.yaml`:

<pre class="overflow-visible!" data-start="9654" data-end="9717"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>istio:</span><span>
  </span><span>enableGateway:</span><span></span><span>true</span><span>
  </span><span>useGatewayAPI:</span><span></span><span>false</span><span>
</span></span></code></div></div></pre>

And in your chart templates use `{{- if .Values.istio.useGatewayAPI }}` to choose between Gateway API vs Istio CRDs. This allows experimenting without changing charts.

---

## E — Enable Gateways with Helm deployment

When installing:

<pre class="overflow-visible!" data-start="9956" data-end="10139"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm install event-system charts/event-backend -n event-system
</span><span># or</span><span>
helm upgrade --install event-system charts/event-backend -n event-system --</span><span>set</span><span> istio.enableGateway=</span><span>true</span><span>
</span></span></code></div></div></pre>

After installation, forward Istio ingress:

<pre class="overflow-visible!" data-start="10185" data-end="10300"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80
curl http://localhost:8080/health
</span></span></code></div></div></pre>

Or query Gateway API:

<pre class="overflow-visible!" data-start="10325" data-end="10410"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get gateway -n event-system
kubectl get httproute -n event-system
</span></span></code></div></div></pre>

---

# 6) Full explanation of each file you create/modify

* **Chart.yaml / values.yaml** — chart metadata and toggles (image, replicas, DB/Redis config, Istio toggles).
* **templates/backend-deployment.yaml** — Deployment & Service for backend; env vars for Postgres/Redis host; readinessProbe/livenessProbe (you should add).
* **templates/worker-deployment.yaml** — Deployment for worker (command to run consumer).
* **templates/scheduler-deployment.yaml** — Deployment for scheduler (producer).
* **templates/istio-gateway.yaml** — Gateway, VirtualService, DestinationRule (Istio route & traffic policies).
* **templates/gatewayclass.yaml, gateway.yaml, httproute.yaml** — Gateway API equivalents (if using Gateway API).
* **templates/_helpers.tpl** — helper functions (fullname, name).
* **templates/secret.yaml** — (recommended) store DB password and other secret values.
* **templates/configmap.yaml** — (optional) config (e.g., environment overrides).
* **templates/hpa.yaml** — HorizontalPodAutoscaler for backend (later).
* **templates/monitoring/** — optional dashboards/ServiceMonitors for Prometheus.

---

# 7) Traffic management examples (quick copies)

### Retry/Timeout in VirtualService (we included earlier)

<pre class="overflow-visible!" data-start="11638" data-end="11761"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>retries:</span><span>
  </span><span>attempts:</span><span></span><span>3</span><span>
  </span><span>perTryTimeout:</span><span></span><span>2s</span><span>
  </span><span>retryOn:</span><span></span><span>gateway-error,connect-failure,refused-stream</span><span>
</span><span>timeout:</span><span></span><span>15s</span><span>
</span></span></code></div></div></pre>

### Simple traffic-split for canary (VirtualService example)

<pre class="overflow-visible!" data-start="11824" data-end="12054"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>http:</span><span>
</span><span>-</span><span></span><span>route:</span><span>
  </span><span>-</span><span></span><span>destination:</span><span>
      </span><span>host:</span><span></span><span>backend-v1.svc.cluster.local</span><span>
      </span><span>port:</span><span> { </span><span>number:</span><span></span><span>5001</span><span> }
    </span><span>weight:</span><span></span><span>90</span><span>
  </span><span>-</span><span></span><span>destination:</span><span>
      </span><span>host:</span><span></span><span>backend-v2.svc.cluster.local</span><span>
      </span><span>port:</span><span> { </span><span>number:</span><span></span><span>5001</span><span> }
    </span><span>weight:</span><span></span><span>10</span><span>
</span></span></code></div></div></pre>

---

# 8) Sidecar injection & RBAC notes

* Label the namespace to auto-inject sidecars:
  * `kubectl label namespace event-system istio-injection=enabled`
* If using ServiceAccounts & RBAC, ensure the control plane has permissions to inject sidecars and the worker has appropriate permissions to access secrets if you mount them.

---

# 9) Observability & addons (recommended for learning)

With `demo` profile, you get Prometheus, Grafana, Kiali, Jaeger pre-installed. To access:

<pre class="overflow-visible!" data-start="12540" data-end="12663"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl -n istio-system port-forward svc/kiali 20001:20001
</span><span># or use minikube service to open grafana/prometheus</span><span>
</span></span></code></div></div></pre>

Use these to:

* Observe traffic between backend and Redis/Postgres.
* See retries & error rates (via Istio metrics).
* Visualize topology with Kiali.

---

# 10) Testing & validation steps (concrete)

1. `kubectl -n event-system get pods` — ensure pods are `Running`.
2. `kubectl -n event-system port-forward svc/event-system-event-backend-backend 5001:5001` — test API directly.
3. `kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80` — test via Istio ingress: `curl http://localhost:8080/health`.
4. Create an event and validate worker logs: `curl -X POST http://localhost:8080/api/v1/events/ -d '{...}'`.
5. Use Kiali/Grafana to see traffic and retry metrics.
6. Test traffic-split by creating backend v2 (different image tag) and update VirtualService weights.

---

# 11) Production considerations & where to harden

* Use  **default** /customized Istio profile with strict mTLS and more hardened settings for production.
* Use **Kubernetes Secrets** for DB credentials and ensure you do not store passwords in `values.yaml`.
* For high throughput / durability: replace Redis/RQ with **Kafka** + consumer groups. Kafka gives partitioning and replayability.
* Use **Persistent volumes** with proper storage class and backups.
* Set resource requests/limits, HPAs, liveness/readiness probes.
* Set up  **CI/CD** : build image -> push -> `helm upgrade --install` -> run DB migrations with Job.
* Consider **cert-manager** to manage TLS certificates for Gateway.
* Configure **Prometheus** scraping and alerts for job failure rates and queue depth.
* Add **SLOs/alerts** for job retries and failures.

---

# 12) Short checklist — what you need to run now

1. Start minikube; install Istio demo and label namespace.
2. Add the files above to your Helm chart (backend/worker/scheduler deployments, istio-gateway.yaml).
3. `helm install event-system charts/event-backend -n event-system`
4. Port-forward Istio ingress and test API.
5. Open Kiali/Grafana/Prometheus for observability.
