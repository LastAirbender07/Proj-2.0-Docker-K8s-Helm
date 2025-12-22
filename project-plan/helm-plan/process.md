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

---

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

 kubectl create secret generic pg-secret   -n event-system   --from-literal=postgres-password="postgres"   --from-literal=app-username="postgres"   --from-literal=app-password="supersecretpassword"
secret/pg-secret created
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm install event-postgres bitnami/postgresql 
  -n event-system 
  --set auth.existingSecret=pg-secret 
  --set auth.postgresPasswordKey=postgres-password 
  --set auth.username=postgres 
  --set auth.passwordKey=app-password 
  --set auth.database=notifications 
  --set primary.persistence.size=1Gi
NAME: event-postgres
LAST DEPLOYED: Fri Nov 28 21:21:51 2025
NAMESPACE: event-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: postgresql
CHART VERSION: 18.1.13
APP VERSION: 18.1.0

⚠ WARNING: Since August 28th, 2025, only a limited subset of images/charts are available for free.
    Subscribe to Bitnami Secure Images to receive continued support and security updates.
    More info at https://bitnami.com and https://github.com/bitnami/containers/issues/83267

** Please be patient while the chart is being deployed **

WARNING: PostgreSQL has been configured without authentication, this is not recommended for production environments.

PostgreSQL can be accessed via port 5432 on the following DNS names from within your cluster:

    event-postgres-postgresql.event-system.svc.cluster.local - Read/Write connection

To get the password for "postgres" run:

    export POSTGRES_PASSWORD=$(kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.postgres-password}" | base64 -d)

To connect to your database run the following command:

    kubectl run event-postgres-postgresql-client --rm --tty -i --restart='Never' --namespace event-system --image registry-1.docker.io/bitnami/postgresql:latest
    --command -- psql --host event-postgres-postgresql -d notifications -p 5432

    > NOTE: If you access the container using bash, make sure that you execute "/opt/bitnami/scripts/postgresql/entrypoint.sh /bin/bash" in order to avoid the error "psql: local user with ID 1001} does not exist"

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace event-system svc/event-postgres-postgresql 5432:5432 &
    psql --host 127.0.0.1 -d notifications -p 5432

WARNING: The configured password will be ignored on new installation in case when previous PostgreSQL release was deleted through the helm command. In that case, old PVC will have an old password, and setting it through helm won't take effect. Deleting persistent volumes (PVs) will solve the issue.
WARNING: Rolling tag detected (bitnami/postgresql:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/os-shell:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:

- primary.resources
- readReplicas.resources
  +info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
  jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm install event-redis bitnami/redis 
  -n event-system 
  --set architecture=standalone 
  --set auth.enabled=false 
  --set usePassword=false 
  --set master.persistence.size=500Mi
  NAME: event-redis
  LAST DEPLOYED: Fri Nov 28 21:22:58 2025
  NAMESPACE: event-system
  STATUS: deployed
  REVISION: 1
  TEST SUITE: None
  NOTES:
  CHART NAME: redis
  CHART VERSION: 24.0.0
  APP VERSION: 8.4.0

⚠ WARNING: Since August 28th, 2025, only a limited subset of images/charts are available for free.
    Subscribe to Bitnami Secure Images to receive continued support and security updates.
    More info at https://bitnami.com and https://github.com/bitnami/containers/issues/83267

** Please be patient while the chart is being deployed **

Redis&reg; can be accessed via port 6379 on the following DNS name from within your cluster:

    event-redis-master.event-system.svc.cluster.local

To connect to your Redis&reg; server:

1. Run a Redis&reg; pod that you can use as a client:

   kubectl run --namespace event-system redis-client --restart='Never'  --image registry-1.docker.io/bitnami/redis:latest --command -- sleep infinity

   Use the following command to attach to the pod:

   kubectl exec --tty -i redis-client --namespace event-system -- bash
2. Connect using the Redis&reg; CLI:
   redis-cli -h event-redis-master

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace event-system svc/event-redis-master 6379:6379 &
    redis-cli -h 127.0.0.1 -p 6379
WARNING: Rolling tag detected (bitnami/redis:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/redis-sentinel:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/redis-exporter:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/os-shell:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/os-shell:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:

- replica.resources
- master.resources
  +info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get pods -n event-system
NAME                          READY   STATUS    RESTARTS   AGE
event-postgres-postgresql-0   2/2     Running   0          2m48s
event-redis-master-0          2/2     Running   0          101s
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$

ayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl create secret generic pg-secret -n event-system   --from-literal=postgres-username=postgresUser   --from-literal=postgres-password=supersecretpassword   --from-literal=postgres-database=notifications
secret/pg-secret created
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get secrets -n event-system
NAME                                TYPE                 DATA   AGE
pg-secret                           Opaque               3      9s
sh.helm.release.v1.event-redis.v1   helm.sh/release.v1   1      3d
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl get secret pg-secret -n event-system -o yaml
apiVersion: v1
data:
  postgres-database: bm90aWZpY2F0aW9ucw==
  postgres-password: c3VwZXJzZWNyZXRwYXNzd29yZA==
  postgres-username: cG9zdGdyZXNVc2Vy
kind: Secret
metadata:
  creationTimestamp: "2025-12-01T16:21:00Z"
  name: pg-secret
  namespace: event-system
  resourceVersion: "77681"
  uid: 1df8869b-dc75-4ecc-ab87-042a261cadcb
type: Opaque
jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm install event-postgres bitnami/postgresql 
  -n event-system 
  --set auth.existingSecret=pg-secret 
  --set auth.secretKeys.userKey=postgres-username 
  --set auth.secretKeys.passwordKey=postgres-password 
  --set auth.secretKeys.databaseKey=postgres-database 
  --set volumePermissions.enabled=true 
  --set persistence.size=1Gi
NAME: event-postgres
LAST DEPLOYED: Mon Dec  1 21:52:34 2025
NAMESPACE: event-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: postgresql
CHART VERSION: 18.1.13
APP VERSION: 18.1.0

⚠ WARNING: Since August 28th, 2025, only a limited subset of images/charts are available for free.
    Subscribe to Bitnami Secure Images to receive continued support and security updates.
    More info at https://bitnami.com and https://github.com/bitnami/containers/issues/83267

** Please be patient while the chart is being deployed **

WARNING: PostgreSQL has been configured without authentication, this is not recommended for production environments.

PostgreSQL can be accessed via port 5432 on the following DNS names from within your cluster:

    event-postgres-postgresql.event-system.svc.cluster.local - Read/Write connection

To get the password for "postgres" run:

    export POSTGRES_PASSWORD=$(kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.postgres-password}" | base64 -d)

To connect to your database run the following command:

    kubectl run event-postgres-postgresql-client --rm --tty -i --restart='Never' --namespace event-system --image registry-1.docker.io/bitnami/postgresql:latest
    --command -- psql --host event-postgres-postgresql -d postgres -p 5432

    > NOTE: If you access the container using bash, make sure that you execute "/opt/bitnami/scripts/postgresql/entrypoint.sh /bin/bash" in order to avoid the error "psql: local user with ID 1001} does not exist"

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace event-system svc/event-postgres-postgresql 5432:5432 &
    psql --host 127.0.0.1 -d postgres -p 5432

WARNING: The configured password will be ignored on new installation in case when previous PostgreSQL release was deleted through the helm command. In that case, old PVC will have an old password, and setting it through helm won't take effect. Deleting persistent volumes (PVs) will solve the issue.
WARNING: Rolling tag detected (bitnami/postgresql:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/os-shell:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:

- primary.resources
- readReplicas.resources
- volumePermissions.resources
  +info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
  jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$

secret.yml:

apiVersion: v1
kind: Secret
metadata:
  name: pg-secret
  namespace: event-system
type: Opaque
stringData:
  postgres-password: supersecretpassword   # admin password
  password: supersecretpassword            # app user password
  username: user                           # app DB user
  database: notifications                  # app DB name

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ helm install event-postgres bitnami/postgresql 
  --namespace event-system 
  --set auth.existingSecret=pg-secret 
  --set auth.username=user 
  --set auth.secretKeys.adminPasswordKey=postgres-password 
  --set auth.secretKeys.userPasswordKey=password 
  --set auth.database=notifications
  --set volumePermissions.enabled=true 
  --set persistence.size=1Gi
NAME: event-postgres
LAST DEPLOYED: Wed Dec  3 21:06:51 2025
NAMESPACE: event-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: postgresql
CHART VERSION: 18.1.13
APP VERSION: 18.1.0

⚠ WARNING: Since August 28th, 2025, only a limited subset of images/charts are available for free.
    Subscribe to Bitnami Secure Images to receive continued support and security updates.
    More info at https://bitnami.com and https://github.com/bitnami/containers/issues/83267

** Please be patient while the chart is being deployed **

WARNING: PostgreSQL has been configured without authentication, this is not recommended for production environments.

PostgreSQL can be accessed via port 5432 on the following DNS names from within your cluster:

    event-postgres-postgresql.event-system.svc.cluster.local - Read/Write connection

To get the password for "postgres" run:

    export POSTGRES_ADMIN_PASSWORD=$(kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.postgres-password}" | base64 -d)

To get the password for "user" run:

    export POSTGRES_PASSWORD=$(kubectl get secret --namespace event-system pg-secret -o jsonpath="{.data.password}" | base64 -d)

To connect to your database run the following command:

    kubectl run event-postgres-postgresql-client --rm --tty -i --restart='Never' --namespace event-system --image registry-1.docker.io/bitnami/postgresql:latest
    --command -- psql --host event-postgres-postgresql -d notifications -p 5432

    > NOTE: If you access the container using bash, make sure that you execute "/opt/bitnami/scripts/postgresql/entrypoint.sh /bin/bash" in order to avoid the error "psql: local user with ID 1001} does not exist"

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace event-system svc/event-postgres-postgresql 5432:5432 &
    psql --host 127.0.0.1 -d notifications -p 5432

WARNING: The configured password will be ignored on new installation in case when previous PostgreSQL release was deleted through the helm command. In that case, old PVC will have an old password, and setting it through helm won't take effect. Deleting persistent volumes (PVs) will solve the issue.
WARNING: Rolling tag detected (bitnami/postgresql:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html
WARNING: Rolling tag detected (bitnami/os-shell:latest), please note that it is strongly recommended to avoid using rolling tags in a production environment.
+info https://techdocs.broadcom.com/us/en/vmware-tanzu/application-catalog/tanzu-application-catalog/services/tac-doc/apps-tutorials-understand-rolling-tags-containers-index.html

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:

- primary.resources
- readReplicas.resources
  +info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
  --set: command not found
  jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$

jayaraj@jayaraj-machine:~/Learnings/Proj-2.0-Docker-K8s-Helm$ kubectl run psql-test --rm -it --namespace event-system 
  --image registry-1.docker.io/bitnami/postgresql:latest 
  -- bash
If you don't see a command prompt, try pressing enter.

postgresql 15:38:54.20 INFO  ==>
postgresql 15:38:54.20 INFO  ==> Welcome to the Bitnami postgresql container
postgresql 15:38:54.20 INFO  ==> Subscribe to project updates by watching https://github.com/bitnami/containers
postgresql 15:38:54.20 INFO  ==> NOTICE: Starting August 28th, 2025, only a limited subset of images/charts will remain available for free. Backup will be available for some time at the 'Bitnami Legacy' repository. More info at https://github.com/bitnami/containers/issues/83267
postgresql 15:38:54.21 INFO  ==>

postgres [ / ]$
postgres [ / ]$
postgres [ / ]$ psql -h event-postgres-postgresql -U user -d notifications
Password for user user:
psql (18.1)
Type "help" for help.

notifications=> \du
                             List of roles
 Role name |                         Attributes
-----------+------------------------------------------------------------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
 user      | Create DB

notifications=> \l
                                                       List of databases
     Name      |  Owner   | Encoding | Locale Provider |   Collate   |    Ctype    | Locale | ICU Rules
 |   Access privileges
---------------+----------+----------+-----------------+-------------+-------------+--------+----------
-+-----------------------
 notifications | user     | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |
 | =Tc/user             +
               |          |          |                 |             |             |        |
 | user=CTc/user
 postgres      | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |
 |
 template0     | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |
 | =c/postgres          +
               |          |          |                 |             |             |        |
 | postgres=CTc/postgres
 template1     | postgres | UTF8     | libc            | en_US.UTF-8 | en_US.UTF-8 |        |
 | =c/postgres          +
               |          |          |                 |             |             |        |
 | postgres=CTc/postgres
(4 rows)
