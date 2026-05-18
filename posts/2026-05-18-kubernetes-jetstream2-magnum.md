     1|---
     2|categories:
     3|- kubernetes
     4|- jetstream
     5|date: '2026-05-18 08:00:00'
     6|layout: post
     7|slug: kubernetes-jetstream2-magnum
     8|title: Deploy Kubernetes on Jetstream2 with Magnum and Cluster API (1 of 4)
     9|---
    10|
    11|This post is part of a series on deploying JupyterHub on Jetstream2:
    12|
    13|1. **Deploy Kubernetes on Jetstream2**
    14|2. [Install Traefik Ingress Controller](/posts/2026-05-18-kubernetes-jetstream2-traefik)
    15|3. [Deploy JupyterHub](/posts/2026-05-18-kubernetes-jetstream2-jupyterhub)
    16|4. [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager)
    17|
    18|Jetstream2 uses the Cluster API as the backend for Magnum, making it faster and more straightforward to launch Kubernetes clusters. This guide walks through creating a cluster, configuring autoscaling, and verifying the deployment.
    19|
    20|## Advantages of Magnum-Based Deployments
    21|
    22|Magnum-based clusters offer several benefits over [Kubespray](/posts/kubernetes-jetstream2-kubespray):
    23|
    24|- **Faster Deployment**: Instead of using Ansible to configure each VM, Magnum uses pre-prepared images. Clusters typically deploy in about 10 minutes, and workers can scale up in around 5 minutes.
    25|- **Load Balancer Integration**: The OpenStack load balancer service provides easy support for multiple master nodes, ensuring high availability.
    26|- **Autoscaling**: The Cluster Autoscaler can automatically add or remove worker nodes based on workload.
    27|
    28|## Prerequisites
    29|
    30|1. **Install OpenStack and Magnum Clients**:
    31|   ```bash
    32|   pip install python-openstackclient python-magnumclient python-octaviaclient python-designateclient
    33|   ```
    34|
    35|   The OpenStack client creates and manages the cluster, the Magnum client manages cluster templates, the Octavia client manages load balancers, and the Designate client manages DNS records.
    36|
    37|   This tutorial used python-openstackclient 9.0.0, python-magnumclient 4.8.1, python-octaviaclient 3.14.0, and python-designateclient 6.3.0.
    38|
    39|2. **Create an App Credential**:
    40|   Create an application credential through [Horizon](https://js2.jetstream-cloud.org/) under [Identity → Application credentials](https://js2.jetstream-cloud.org/identity/application_credentials/).
    41|   Choose "Unrestricted" and include all permissions, notably "loadbalancer", in the project where you will create the cluster. Download the `openrc` file and source it:
    42|
    43|   ```bash
    44|   source app-cred-XXXX-openrc.sh
    45|   ```
    46|
    47|3. **Install Kubernetes Tooling**:
    48|   Once the cluster is launched, manage it using standard Kubernetes tools:
    49|   - `kubectl`: see <https://kubernetes.io/docs/tasks/tools/>, this tutorial used 1.35.
    50|   - `helm`: see <https://helm.sh/docs/intro/install/>, this tutorial used 3.18.
    51|
    52|## Create the Cluster with Magnum
    53|
    54|Check the available cluster templates:
    55|
    56|```bash
    57|openstack coe cluster template list
    58|```
    59|
    60|Clone the repository with all the configuration files:
    61|
    62|```bash
    63|git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
    64|cd jupyterhub-deploy-kubernetes-jetstream/kubernetes_magnum
    65|```
    66|
    67|Create a cluster:
    68|
    69|```bash
    70|export K8S_CLUSTER_NAME=k8s
    71|bash create_cluster.sh
    72|```
    73|
    74|The script uses the `kubernetes-1-33-jammy-fixed-labels` template, creates 1 control-plane node and 1 worker (both `m3.small` flavor), enables autoscaling with min 1 / max 5 workers, and polls until the cluster status is `CREATE_COMPLETE`. Cluster creation typically takes about 10 minutes.
    75|
    76|> **Template choice**: We use the `kubernetes-1-33-jammy-fixed-labels` template rather than `kubernetes-1-33-jammy`. The default template deploys a Kubernetes dashboard app that is now defunct, which causes Magnum's post-create bookkeeping to get stuck at `CREATE_IN_PROGRESS` even though the cluster is fully functional. The `-fixed-labels` template omits the dashboard and completes cleanly. Alternatively, you can use any template with `--labels kube_dashboard_enabled=false`.
    77|
    78|> **Note**: The first time you create a cluster (or after a long period of inactivity), deployment can take 2–2.5 hours, likely because the images are not cached in OpenStack. After that, clusters should deploy in about 10 minutes.
    79|
    80|In case of errors, check the error message with:
    81|
    82|```bash
    83|openstack coe cluster show $K8S_CLUSTER_NAME -f json | jq '.status_reason'
    84|```
    85|
    86|The cluster consumes resources when active. To delete it:
    87|
    88|```bash
    89|bash delete_cluster.sh
    90|```
    91|
    92|**Warning**: This deletes all Jetstream virtual machines and any data stored in JupyterHub.
    93|
    94|Once the nodes are ready, retrieve the Kubernetes config file:
    95|
    96|```bash
    97|openstack coe cluster config $K8S_CLUSTER_NAME --force
    98|export KUBECONFIG=$(pwd)/config
    99|chmod 600 config
   100|```
   101|
   102|Verify that `kubectl` commands work:
   103|
   104|```bash
   105|kubectl get nodes
   106|```
   107|
   108|You should see output like:
   109|
   110|```
   111|NAME                                          STATUS   ROLES           AGE     VERSION
   112|k8s-wamiv264xiet-control-plane-p2zj6          Ready    control-plane   8m22s   v1.33.2
   113|k8s-wamiv264xiet-default-worker-x8cxp-vj9db   Ready    <none>          5m45s   v1.33.2
   114|```
   115|
   116|Check storage classes (Magnum provides Cinder-backed persistent volumes by default):
   117|
   118|```bash
   119|kubectl get storageclass
   120|```
   121|
   122|```
   123|NAME                PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
   124|default (default)   cinder.csi.openstack.org   Retain          WaitForFirstConsumer   true                   12m
   125|replicated-hdd      cinder.csi.openstack.org   Retain          WaitForFirstConsumer   true                   12m
   126|```
   127|
   128|## Autoscaling
   129|
   130|The `create_cluster.sh` script creates the cluster with the label `auto_scaling_enabled=true` and `max_node_count=5`, which activates the Cluster Autoscaler. You can override the maximum before creating the cluster:
   131|
   132|```bash
   133|export MAX_NODE_COUNT=10
   134|bash create_cluster.sh
   135|```
   136|
   137|After the cluster is created, verify the label on the nodegroup:
   138|
   139|```bash
   140|openstack coe nodegroup show $K8S_CLUSTER_NAME default-worker -c labels -c min_node_count -c max_node_count
   141|```
   142|
   143|```
   144|| Field          | Value                                                                          |
   145|+----------------+--------------------------------------------------------------------------------+
   146|| labels         | {'auto_scaling_enabled': 'true', 'min_node_count': '1', 'max_node_count': '5'} |
   147|| max_node_count | None                                                                           |
   148|| min_node_count | 1                                                                              |
   149|```
   150|
   151|Note that `max_node_count` on the nodegroup shows `None` even though the label is set to 5. This is a Magnum quirk — the nodegroup field and the label are separate. **The autoscaler reads the label value**, not the nodegroup field, so it is active and capped at 5 regardless. This means there is no need to run `openstack coe nodegroup update` to set `max_node_count` — the label set at cluster creation time is sufficient. To change the maximum, set `MAX_NODE_COUNT` before running `create_cluster.sh`.
   152|
   153|### Test Scale Up
   154|
   155|Create a deployment that requests enough memory to trigger the autoscaler:
   156|
   157|```bash
   158|kubectl create -f high_mem_dep.yaml
   159|kubectl scale deployment high-memory-deployment --replicas=6
   160|```
   161|
   162|Each replica requests 4 GB of memory, so 6 replicas cannot fit on a single `m3.small` worker. The autoscaler detects the pending pods and adds nodes. Check the scale-up event:
   163|
   164|```bash
   165|kubectl get events --field-selector reason=TriggeredScaleUp
   166|```
   167|
   168|```
   169|LAST SEEN   TYPE     REASON             OBJECT                                        MESSAGE
   170|2m19s       Normal   TriggeredScaleUp   pod/high-memory-deployment-844964899f-ngldm   pod triggered scale-up: [{MachineDeployment/.../k8s-...-default-worker 1->5 (max: 5)}]
   171|```
   172|
   173|Within a few minutes, new worker nodes appear:
   174|
   175|```bash
   176|kubectl get nodes
   177|```
   178|
   179|```
   180|NAME                                          STATUS   ROLES           AGE     VERSION
   181|k8s-2yo5qznljser-control-plane-g7nk4          Ready    control-plane   15m     v1.33.2
   182|k8s-2yo5qznljser-default-worker-m2pp7-2mq6z   Ready    <none>          2m40s   v1.33.2
   183|k8s-2yo5qznljser-default-worker-m2pp7-bc6jv   Ready    <none>          2m37s   v1.33.2
   184|k8s-2yo5qznljser-default-worker-m2pp7-kp28n   Ready    <none>          2m30s   v1.33.2
   185|k8s-2yo5qznljser-default-worker-m2pp7-t2nsg   Ready    <none>          15m     v1.33.2
   186|k8s-2yo5qznljser-default-worker-m2pp7-tzjdn   Ready    <none>          2m31s   v1.33.2
   187|```
   188|
   189|The autoscaler scaled from 1 to 5 workers (the maximum set in the label). One pod remains pending because all 6 replicas cannot fit within the 5-worker limit.
   190|
   191|### Clean Up and Observe Scale Down
   192|
   193|Delete the test deployment so the autoscaler can return the worker pool to its minimum size:
   194|
   195|```bash
   196|kubectl delete deployment high-memory-deployment
   197|```
   198|
   199|The autoscaler takes several minutes to identify idle nodes, drain them, and terminate them. Watch the node count drop:
   200|
   201|```bash
   202|kubectl get nodes -w
   203|```
   204|
   205|You can inspect the autoscaler's internal status to see whether a scale-down is in progress:
   206|
   207|```bash
   208|kubectl -n kube-system get configmap cluster-autoscaler-status -o jsonpath='{.data.status}'
   209|```
   210|
   211|When `scaleDown.status` shows `CandidatesPresent`, the autoscaler has identified idle nodes and is draining them. Once the process completes, the cluster returns to 1 worker node.
   212|
   213|## Scale Manually
   214|
   215|If you prefer not to use the autoscaler, you can scale the worker pool manually. Resize the nodegroup:
   216|
   217|```bash
   218|openstack coe cluster resize --nodegroup default-worker $K8S_CLUSTER_NAME 3
   219|```
   220|
   221|Confirm the change:
   222|
   223|```bash
   224|kubectl get nodes
   225|```
   226|
## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.

**Next**: [Install Traefik Ingress Controller](/posts/2026-05-18-kubernetes-jetstream2-traefik)
   230|