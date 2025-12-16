What we need ?

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get ns
NAME              STATUS   AGE
default           Active   5d
event-system      Active   4d23h
kube-node-lease   Active   5d
kube-public       Active   5d
kube-system       Active   5d
monitoring        Active   2m4s

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm repo list
NAME                    URL                                                
bitnami                 https://charts.bitnami.com/bitnami                 
istio                   https://istio-release.storage.googleapis.com/charts
prometheus-community    https://prometheus-community.github.io/helm-charts 
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ 

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl expose service kube-prometheus-stack-grafana  --type=NodePort --target-port=3000 --name=grafana-ext -n=monitoring
service/grafana-ext exposed
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ minikube service grafana-ext

❌  Exiting due to SVC_NOT_FOUND: Service 'grafana-ext' was not found in 'default' namespace.
You may select another namespace by using 'minikube service grafana-ext -n <namespace>'. Or list out all the services using 'minikube service list'

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ minikube service grafana-ext -n monitoring
|------------|-------------|-------------|---------------------------|
| NAMESPACE  |    NAME     | TARGET PORT |            URL            |
|------------|-------------|-------------|---------------------------|
| monitoring | grafana-ext |          80 | http://192.168.49.2:30956 |
|------------|-------------|-------------|---------------------------|
🎉  Opening service monitoring/grafana-ext in default browser...

Now install the helm charts and other dependencies

