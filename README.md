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
