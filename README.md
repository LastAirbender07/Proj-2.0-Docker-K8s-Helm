jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get pods -n event-system
NAME                                      READY   STATUS    RESTARTS         AGE
event-postgres-postgresql-0               2/2     Running   4 (9m28s ago)    2d22h
event-redis-master-0                      2/2     Running   12 (9m28s ago)   7d22h
event-system-backend-6f79db5d8-sw7dp      2/2     Running   2 (9m29s ago)    35m
event-system-scheduler-846fc758c7-xjvnj   2/2     Running   2 (9m29s ago)    35m
event-system-worker-75c7d65ff5-tv82z      2/2     Running   3 (2m43s ago)    35m
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ k9s
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get pods -n istio-system
NAME                                    READY   STATUS    RESTARTS      AGE
istio-egressgateway-5dcfcd4f76-p6kcf    1/1     Running   7 (11m ago)   8d
istio-ingressgateway-54b44bc89d-crzfb   1/1     Running   7 (11m ago)   8d
istiod-567d49697-4mh7c                  1/1     Running   7 (11m ago)   8d
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get svc -n istio-system istio-ingressgateway
NAME                   TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                                                                      AGE
istio-ingressgateway   LoadBalancer   10.103.152.240   `<pending>`     15021:31137/TCP,80:30174/TCP,443:32320/TCP,31400:30987/TCP,15443:31161/TCP   8d
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
Handling connection for 8080

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ curl -H "Host: api.jayaraj.dev" http://127.0.0.1:8080/health
{"status":"ok","env":{"database":"postgresql://user:supersecretpassword@event-postgres-postgresql:5432/notifications","redis":"redis://event-redis-master:6379/0"}}jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$

root@jayaraj-machine:/home/jayaraj/Desktop# sudo apt install libnss3-tools
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  libnss3-tools
0 upgraded, 1 newly installed, 0 to remove and 36 not upgraded.
Need to get 615 kB of archives.
After this operation, 2,193 kB of additional disk space will be used.
Get:1 http://in.archive.ubuntu.com/ubuntu noble/main amd64 libnss3-tools amd64 2:3.98-1build1 [615 kB]
Fetched 615 kB in 2s (292 kB/s)
Selecting previously unselected package libnss3-tools.
(Reading database ... 194598 files and directories currently installed.)
Preparing to unpack .../libnss3-tools_2%3a3.98-1build1_amd64.deb ...
Unpacking libnss3-tools (2:3.98-1build1) ...
Setting up libnss3-tools (2:3.98-1build1) ...
Processing triggers for man-db (2.12.0-4build2) ...
root@jayaraj-machine:/home/jayaraj/Desktop# curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   111  100   111    0     0     53      0  0:00:02  0:00:02 --:--:--    53
  0     0    0     0    0     0      0      0 --:--:--  0:00:02 --:--:--     0
100 4676k  100 4676k    0     0   983k      0  0:00:04  0:00:04 --:--:-- 3123k
root@jayaraj-machine:/home/jayaraj/Desktop# chmod +x mkcert-v*-linux-amd64
root@jayaraj-machine:/home/jayaraj/Desktop# sudo cp mkcert-v*-linux-amd64 /usr/local/bin/mkcert
root@jayaraj-machine:/home/jayaraj/Desktop# mkcert
Usage of mkcert:

    $ mkcert -install
	Install the local CA in the system trust store.

    $ mkcert example.org
	Generate "example.org.pem" and "example.org-key.pem".

    $ mkcert example.com myapp.dev localhost 127.0.0.1 ::1
	Generate "example.com+4.pem" and "example.com+4-key.pem".

    $ mkcert "*.example.it"
	Generate "_wildcard.example.it.pem" and "_wildcard.example.it-key.pem".

    $ mkcert -uninstall
	Uninstall the local CA (but do not delete it).

root@jayaraj-machine:/home/jayaraj/Desktop# mkcert -install
Created a new local CA 💥
The local CA is now installed in the system trust store! ⚡️
ERROR: no Firefox and/or Chrome/Chromium security databases found

root@jayaraj-machine:/home/jayaraj/Desktop#

jayaraj@jayaraj-machine:~/Desktop$ mkcert api.jayaraj.dev
Created a new local CA 💥
Note: the local CA is not installed in the system trust store.
Note: the local CA is not installed in the Firefox and/or Chrome/Chromium trust store.
Run "mkcert -install" for certificates to be trusted automatically ⚠️

Created a new certificate valid for the following names 📜

- "api.jayaraj.dev"

The certificate is at "./api.jayaraj.dev.pem" and the key at "./api.jayaraj.dev-key.pem" ✅

It will expire on 7 March 2028 🗓

jayaraj@jayaraj-machine:~/Desktop$ ls
api.jayaraj.dev-key.pem  api.jayaraj.dev.pem  mkcert-v1.4.4-linux-amd64
jayaraj@jayaraj-machine:~/Desktop$ kubectl create secret tls istio-tls-secret   -n event-system   --cert=api.jayaraj.dev.pem   --key=api.jayaraj.dev-key.pem
secret/istio-tls-secret created
jayaraj@jayaraj-machine:~/Desktop$

jayaraj@jayaraj-machine:~/Desktop$ kubectl get secrets -n event-system
NAME                                   TYPE                 DATA   AGE
istio-tls-secret                       kubernetes.io/tls    2      41s
pg-secret                              Opaque               4      3d14h
sh.helm.release.v1.event-postgres.v1   helm.sh/release.v1   1      3d14h
sh.helm.release.v1.event-redis.v1      helm.sh/release.v1   1      8d
sh.helm.release.v1.event-system.v1     helm.sh/release.v1   1      16h
sh.helm.release.v1.event-system.v2     helm.sh/release.v1   1      16h
sh.helm.release.v1.event-system.v3     helm.sh/release.v1   1      15h
jayaraj@jayaraj-machine:~/Desktop$

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ minikube addons disable ingress
🌑  "The 'ingress' addon is disabled
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ minikube tunnel
Status:
        machine: minikube
        pid: 198227
        route: 10.96.0.0/12 -> 192.168.49.2
        minikube: Running
        services: [istio-ingress]
    errors:
                minikube: no errors
                router: no errors
                loadbalancer emulator: no errors

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ curl -vk https://api.jayaraj.dev/health

* Host api.jayaraj.dev:443 was resolved.
* IPv6: (none)
* IPv4: 192.168.49.2, 10.108.114.66
* Trying 192.168.49.2:443...
* connect to 192.168.49.2 port 443 from 192.168.49.1 port 56412 failed: Connection refused
* Trying 10.108.114.66:443...
* Connected to api.jayaraj.dev (10.108.114.66) port 443
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / RSASSA-PSS
* ALPN: server accepted h2
* Server certificate:
* subject: O=mkcert development certificate; OU=jayaraj@jayaraj-machine
* start date: Dec  7 16:15:53 2025 GMT
* expire date: Mar  7 16:15:53 2028 GMT
* issuer: O=mkcert development CA; OU=jayaraj@jayaraj-machine; CN=mkcert jayaraj@jayaraj-machine
* SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
* Certificate level 0: Public key type RSA (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://api.jayaraj.dev/health
* [HTTP/2] [1] [:method: GET]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: api.jayaraj.dev]
* [HTTP/2] [1] [:path: /health]
* [HTTP/2] [1] [user-agent: curl/8.5.0]
* [HTTP/2] [1] [accept: */*]

> GET /health HTTP/2
> Host: api.jayaraj.dev
> User-Agent: curl/8.5.0
> Accept: */*

* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* old SSL session ID is stale, removing
  < HTTP/2 200
  < date: Sun, 07 Dec 2025 16:47:15 GMT
  < server: istio-envoy
  < content-length: 163
  < content-type: application/json
  < x-envoy-upstream-service-time: 9
  <
* Connection #0 to host api.jayaraj.dev left intact
  {"status":"ok","env":{"database":"postgresql://user:supersecretpassword@event-postgres-postgresql:5432/notifications","redis":"redis://event-redis-master:6379/0"}}jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$


# Event-System Helm + Istio Setup with HTTPS (mkcert) – Comprehensive Documentation

## Table of Contents

1. [Overview]()
2. [Environment &amp; Prerequisites]()
3. [Objective]()
4. [Steps Taken]()
   * 4.1 [Helm Deployment of Event-System]()
   * 4.2 [Istio Ingress Setup]()
   * 4.3 [Creating TLS Certificates with mkcert]()
   * 4.4 [Creating TLS Secret in Kubernetes]()
   * 4.5 [Gateway &amp; VirtualService Configuration]()
5. [Errors Faced]()
6. [Investigation &amp; Root Cause]()
7. [Resolution]()
8. [Final Verification]()
9. [Lessons Learned]()

---

## Overview

We deployed an **Event-System application** in a Kubernetes cluster using **Helm** and exposed it externally via  **Istio Ingress** . The goal was to enable HTTPS access locally using a self-signed certificate generated by  **mkcert** .

---

## Environment & Prerequisites

* **Kubernetes** : Minikube
* **Helm** : For application deployment
* **Istio** : For ingress traffic management
* **mkcert** : For generating local trusted TLS certificates
* **Tools** : `kubectl`, `curl`

Namespaces used:

* `event-system` – Application namespace
* `istio-system` – Default Istio installation namespace

---

## Objective

1. Deploy `event-system` backend + Redis + PostgreSQL using Helm.
2. Expose backend via  **Istio Ingress Gateway** .
3. Configure HTTPS using  **mkcert certificates** .
4. Enable local access to `https://api.jayaraj.dev/health`.

---

## Steps Taken

### 4.1 Helm Deployment of Event-System

* Helm charts installed:

<pre class="overflow-visible!" data-start="2019" data-end="2113"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm install event-system ./charts/event-system -n event-system --create-namespace
</span></span></code></div></div></pre>

* Pods verified:

<pre class="overflow-visible!" data-start="2133" data-end="2177"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get pods -n event-system
</span></span></code></div></div></pre>

* Services verified:

<pre class="overflow-visible!" data-start="2201" data-end="2244"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get svc -n event-system
</span></span></code></div></div></pre>

---

### 4.2 Istio Ingress Setup

* Installed Istio ingress gateway in `event-system` namespace:

<pre class="overflow-visible!" data-start="2344" data-end="2412"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>helm install istio-ingress istio/gateway -n event-system
</span></span></code></div></div></pre>

* Verified pod labels:

<pre class="overflow-visible!" data-start="2438" data-end="2496"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl get pods -n event-system --show-labels
</span></span></code></div></div></pre>

* Key label used for Gateway selector: `istio=ingress`

---

### 4.3 Creating TLS Certificates with mkcert

* Installed mkcert and local CA:

<pre class="overflow-visible!" data-start="2640" data-end="2667"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>mkcert -install
</span></span></code></div></div></pre>

* Generated certificate for `api.jayaraj.dev`:

<pre class="overflow-visible!" data-start="2717" data-end="2819"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>mkcert api.jayaraj.dev
</span><span>mv</span><span> api.jayaraj.dev.pem cert.crt
</span><span>mv</span><span> api.jayaraj.dev-key.pem cert.key
</span></span></code></div></div></pre>

---

### 4.4 Creating TLS Secret in Kubernetes

* Initially, secret was created in `istio-system`:

<pre class="overflow-visible!" data-start="2921" data-end="3020"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl create secret tls api-tls-secret -n istio-system --cert=cert.crt --key=cert.key
</span></span></code></div></div></pre>

* This caused HTTPS failures because the  **Gateway was in `event-system` namespace** .
* Correct solution: Create secret in `event-system` namespace:

<pre class="overflow-visible!" data-start="3175" data-end="3274"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl create secret tls api-tls-secret -n event-system --cert=cert.crt --key=cert.key
</span></span></code></div></div></pre>

---

### 4.5 Gateway & VirtualService Configuration

**Gateway YAML:**

<pre class="overflow-visible!" data-start="3348" data-end="3785"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>networking.istio.io/v1</span><span>
</span><span>kind:</span><span></span><span>Gateway</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>event-system-gateway</span><span>
  </span><span>namespace:</span><span></span><span>event-system</span><span>
</span><span>spec:</span><span>
  </span><span>selector:</span><span>
    </span><span>istio:</span><span></span><span>ingress</span><span>
  </span><span>servers:</span><span>
  </span><span>-</span><span></span><span>port:</span><span>
      </span><span>number:</span><span></span><span>80</span><span>
      </span><span>name:</span><span></span><span>http</span><span>
      </span><span>protocol:</span><span></span><span>HTTP</span><span>
    </span><span>hosts:</span><span>
    </span><span>-</span><span></span><span>api.jayaraj.dev</span><span>
  </span><span>-</span><span></span><span>port:</span><span>
      </span><span>number:</span><span></span><span>443</span><span>
      </span><span>name:</span><span></span><span>https</span><span>
      </span><span>protocol:</span><span></span><span>HTTPS</span><span>
    </span><span>hosts:</span><span>
    </span><span>-</span><span></span><span>api.jayaraj.dev</span><span>
    </span><span>tls:</span><span>
      </span><span>mode:</span><span></span><span>SIMPLE</span><span>
      </span><span>credentialName:</span><span></span><span>api-tls-secret</span><span>
</span></span></code></div></div></pre>

**VirtualService YAML:**

<pre class="overflow-visible!" data-start="3813" data-end="4201"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>apiVersion:</span><span></span><span>networking.istio.io/v1</span><span>
</span><span>kind:</span><span></span><span>VirtualService</span><span>
</span><span>metadata:</span><span>
  </span><span>name:</span><span></span><span>event-system-backend-vs</span><span>
  </span><span>namespace:</span><span></span><span>event-system</span><span>
</span><span>spec:</span><span>
  </span><span>gateways:</span><span>
  </span><span>-</span><span></span><span>event-system-gateway</span><span>
  </span><span>hosts:</span><span>
  </span><span>-</span><span></span><span>api.jayaraj.dev</span><span>
  </span><span>http:</span><span>
  </span><span>-</span><span></span><span>match:</span><span>
    </span><span>-</span><span></span><span>uri:</span><span>
        </span><span>prefix:</span><span></span><span>/</span><span>
    </span><span>route:</span><span>
    </span><span>-</span><span></span><span>destination:</span><span>
        </span><span>host:</span><span></span><span>event-system-backend.event-system.svc.cluster.local</span><span>
        </span><span>port:</span><span>
          </span><span>number:</span><span></span><span>5001</span><span>
</span></span></code></div></div></pre>

---

## Errors Faced

1. **HTTPS connection failure** :

<pre class="overflow-visible!" data-start="4259" data-end="4337"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl -vk https://api.jayaraj.dev/health
</span><span># Connection reset by peer</span><span>
</span></span></code></div></div></pre>

2. **Browser TLS errors** :

* Chrome/Firefox showed self-signed certificate warnings initially.
* After mkcert, certificates were trusted locally but HTTPS still failed.

---

## Investigation & Root Cause

* Istio ingress logs showed  **TLS handshake failure** .
* `kubectl get secret -n istio-system` showed secret existed, but  **Gateway is in `event-system` namespace** .
* Istio requires TLS secrets to be  **in the same namespace as the Gateway** .

**Root cause:** Secret namespace mismatch.

---

## Resolution

1. Move TLS secret to `event-system` namespace.

<pre class="overflow-visible!" data-start="4910" data-end="5062"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>kubectl delete secret api-tls-secret -n istio-system
kubectl create secret tls api-tls-secret -n event-system --cert=cert.crt --key=cert.key
</span></span></code></div></div></pre>

2. Ensure Gateway selector matches ingress pod label: `istio=ingress`.
3. Use `minikube tunnel` to expose LoadBalancer IP locally.
4. Update `/etc/hosts`:

<pre class="overflow-visible!" data-start="5224" data-end="5265"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-text"><span><span>10.108.114.66 api.jayaraj.dev
</span></span></code></div></div></pre>

5. Test HTTP & HTTPS endpoints:

<pre class="overflow-visible!" data-start="5300" data-end="5386"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl http://api.jayaraj.dev/health
curl -vk https://api.jayaraj.dev/health
</span></span></code></div></div></pre>

---

## Final Verification

* HTTP ✅ returns backend health JSON:

<pre class="overflow-visible!" data-start="5455" data-end="5630"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>"status"</span><span>:</span><span>"ok"</span><span>,</span><span>"env"</span><span>:</span><span>{</span><span>"database"</span><span>:</span><span>"postgresql://user:supersecretpassword@event-postgres-postgresql:5432/notifications"</span><span>,</span><span>"redis"</span><span>:</span><span>"redis://event-redis-master:6379/0"</span><span>}</span><span>}</span><span>
</span></span></code></div></div></pre>

* HTTPS ✅ works in browser without errors.
* Istio ingress shows pod running in `event-system` namespace.
* Gateway and VirtualService route traffic correctly.

---

## Lessons Learned

1. **TLS Secret Namespace Matters** – secret must be in the same namespace as the Gateway.
2. **Gateway Selector** must match ingress pod label.
3. `mkcert` is an easy way to generate trusted local TLS certs for development.
4. `minikube tunnel` exposes LoadBalancer services with real IPs for local testing.
5. Always check `kubectl describe gateway/virtualservice` and ingress logs for TLS errors.

---

**Outcome:**

We successfully configured **Helm + Istio + HTTPS** using mkcert, and `api.jayaraj.dev` is now fully accessible via both HTTP and HTTPS locally.
