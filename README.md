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
