jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl create ns event-system
namespace/event-system created
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ curl -L https://istio.io/downloadIstio | sh -
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   101  100   101    0     0    212      0 --:--:-- --:--:-- --:--:--   212
100  5124  100  5124    0     0   5246      0 --:--:-- --:--:-- --:--:--     0

Downloading istio-1.28.0 from https://github.com/istio/istio/releases/download/1.28.0/istio-1.28.0-linux-amd64.tar.gz ...

Istio 1.28.0 download complete!

The Istio release archive has been downloaded to the istio-1.28.0 directory.

To configure the istioctl client tool for your workstation,
add the /home/jayaraj/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0/bin directory to your environment path variable with:
         export PATH="$PATH:/home/jayaraj/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0/bin"

Begin the Istio pre-installation check by running:
         istioctl x precheck 

Try Istio in ambient mode
        https://istio.io/latest/docs/ambient/getting-started/
Try Istio in sidecar mode
        https://istio.io/latest/docs/setup/getting-started/
Install guides for ambient mode
        https://istio.io/latest/docs/ambient/install/
Install guides for sidecar mode
        https://istio.io/latest/docs/setup/install/

Need more information? Visit https://istio.io/latest/docs/ 
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ cd istio-1.28.0/
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ export PATH=$PWD/bin:$PATH
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ echo $PATH
/home/jayaraj/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0/bin:/home/jayaraj/.config/Code/User/globalStorage/github.copilot-chat/debugCommand:/home/jayaraj/.config/Code/User/globalStorage/github.copilot-chat/copilotCli:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/jayaraj/.vscode/extensions/ms-python.debugpy-2025.16.0-linux-x64/bundled/scripts/noConfigScripts
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ istioctl install --set profile=demo -y
        |\          
        | \         
        |  \        
        |   \       
      /||    \      
     / ||     \     
    /  ||      \    
   /   ||       \   
  /    ||        \  
 /     ||         \ 
/______||__________\
____________________
  \__       _____/  
     \_____/        

✔ Istio core installed ⛵️                                                                                                                                         
✔ Istiod installed 🧠                                                                                                                                             
✔ Egress gateways installed 🛫                                                                                                                                    
✔ Ingress gateways installed 🛬                                                                                                                                   
✔ Installation complete                                                                                                                                           
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ kubectl label namespace event-system istio-injection=enabled
namespace/event-system labeled
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ kubectl get pods -n istio-system
NAME                                    READY   STATUS    RESTARTS   AGE
istio-egressgateway-5dcfcd4f76-p6kcf    1/1     Running   0          89s
istio-ingressgateway-54b44bc89d-crzfb   1/1     Running   0          88s
istiod-567d49697-4mh7c                  1/1     Running   0          107s
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ kubectl -n istio-system port-forward svc/istio-ingressgateway 8080:80
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
^Cjayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" already exists with the same configuration, skipping
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm/istio-1.28.0$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈