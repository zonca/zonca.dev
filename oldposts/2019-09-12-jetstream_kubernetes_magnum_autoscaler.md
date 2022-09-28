---
layout: post
title: Deploy Cluster Autoscaler for Kubernetes on Jetstream
date: 2019-09-12 12:00
categories: [kubernetes, openstack, jetstream, jupyterhub]
slug: kubernetes-jetstream-autoscaler
---

The [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler) is a service
that runs within a Kubernetes cluster and when there are not enough resources to accomodate
the pods that are queued to run, it contacts the API of the cloud provider to create
more Virtual Machines to join the Kubernetes Cluster.

Initially the Cluster Autoscaler only supported commercial cloud provides, but back in
March 2019 [a user contributed Openstack support based on Magnum](https://github.com/kubernetes/autoscaler/pull/1690).

First step you should have a Magnum-based deployment running on Jetstream,
see [my recent tutorial about that](https://zonca.github.io/2019/06/kubernetes-jupyterhub-jetstream-magnum.html).

Therefore you should also have already a copy of the repository of all configuration
files checked out on your local machine that you are using to interact with the openstack API,
if not:

    git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git

and enter the folder dedicated to the autoscaler:

    cd jupyterhub-deploy-kubernetes-jetstream/kubernetes_magnum/autoscaler

## Setup credentials

We first create the service account needed by the autoscaler to interact with the Kubernetes API:

```bash
kubectl create -f cluster-autoscaler-svcaccount.yaml 
```

Then we need to provide all connection details for the autoscaler to interact with the Openstack API,
those are contained in the `cloud-config` of our cluster available in the master node and setup
by Magnum.
Get the `IP` of your master node from:

```bash
openstack server list
IP=xxx.xxx.xxx.xxx
```

Now ssh into the master node and access the `cloud-config` file:

```bash
ssh fedora@$IP
cat /etc/kubernetes/cloud-config 
```

now copy the `[Global]` section at the end of `cluster-autoscaler-secret.yaml` on the local machine.
Also remove the line of `ca-file`

```bash
kubectl create -f cluster-autoscaler-secret.yaml
```

## Launch the Autoscaler deployment

Create the Autoscaler deployment:

```bash
kubectl create -f cluster-autoscaler-deployment-master.yaml
```

Alternatively, I also added a version for a cluster where we are not deploying pods on master `cluster-autoscaler-deployment.yaml`.

Check that the deployment is active:

```bash
kubectl -n kube-system get pods
NAME                   DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
cluster-autoscaler     1         1         1            0           10s
```

And check its logs:

```bash
kubectl -n kube-system logs cluster-autoscaler-59f4cf4f4-4k4p2

I0905 05:29:21.589062       1 leaderelection.go:217] attempting to acquire leader lease  kube-system/cluster-autoscaler...
I0905 05:29:39.412449       1 leaderelection.go:227] successfully acquired lease kube-system/cluster-autoscaler
I0905 05:29:43.896557       1 magnum_manager_heat.go:293] For stack ID 17ab3ae7-1a81-43e6-98ec-b6ffd04f91d3, stack name is k8s-lu3bksbwsln3
I0905 05:29:44.146319       1 magnum_manager_heat.go:310] Found nested kube_minions stack: name k8s-lu3bksbwsln3-kube_minions-r4lhlv5xuwu3, ID d0590824-cc70-4da5-b9ff-8581d99c666b
```

If you redeploy the cluster and keep a older authentication, you'll see "Authentication failed" in the logs of the autoscaler pod, you need to update the secret every time you redeploy the cluster.

## Test the autoscaler

Now we need to produce a significant load on the cluster so that the autoscaler is triggered to request Openstack Magnum to create more Virtual Machines.

We can create a deployment of the NGINX container (any other would work for this test):

```bash
kubectl create deployment autoscaler-demo --image=nginx
```

And then create a large number of replicas:

```bash
kubectl scale deployment autoscaler-demo --replicas=300
```

We are using 2 nodes with a large amount of memory and CPU, so they can accommodate more then 200 of those pods. The rest remains in the queue:

```bash
kubectl get deployment autoscaler-demo
NAME              DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
autoscaler-demo   300       300       300          213         18m
```

And this triggers the autoscaler:

```bash
kubectl -n kube-system logs cluster-autoscaler-59f4cf4f4-4k4p2

I0905 05:34:47.401149       1 scale_up.go:689] Scale-up: setting group DefaultNodeGroup size to 2
I0905 05:34:49.267280       1 magnum_nodegroup.go:101] Increasing size by 1, 1->2
I0905 05:35:22.222387       1 magnum_nodegroup.go:67] Waited for cluster UPDATE_IN_PROGRESS status
```

Check also in the Openstack API:

```bash
openstack coe cluster list
+------+------+---------+------------+--------------+--------------------+
| uuid | name | keypair | node_count | master_count | status             |
+------+------+---------+------------+--------------+--------------------+
| 09fcf| k8s  | comet   |          2 |            1 | UPDATE_IN_PROGRESS |
+------+------+---------+------------+--------------+--------------------+
```

It takes about 4 minutes for a new VM to boot, be configured by Magnum and join the Kubernetes cluster.

Checking the logs again should show another line:

```bash
I0912 17:18:28.290987       1 magnum_nodegroup.go:67] Waited for cluster UPDATE_COMPLETE status
```
Then you should have all 3 nodes available:

```bash
kubectl get nodes
NAME                        STATUS   ROLES    AGE   VERSION
k8s-6bawhy45wr5t-master-0   Ready    master   38m   v1.11.1
k8s-6bawhy45wr5t-minion-0   Ready    <none>   38m   v1.11.1
k8s-6bawhy45wr5t-minion-1   Ready    <none>   30m   v1.11.1
```

and all 300 NGINX containers deployed:

```bash
kubectl get deployments
NAME              DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
autoscaler-demo   300       300       300          300         35m
```

You can also test scaling down by scaling back the number of NGINX containers to only a few and check in the logs
of the autoscaler that this process triggers the scale-down process.

In `cluster-autoscaler-deployment-master.yaml` I have configured the scale down process to trigger just after 1 minute, to simplify testing. For production, better increase this to 10 minutes or more. Check the [documentation of Cluster Autoscaler 1.14](https://github.com/zonca/autoscaler/blob/cluster-autoscaler-1.14-magnum/cluster-autoscaler/FAQ.md) for all other available options.

## Note about the Cluster Autoscaler container

The Magnum provider was added in Cluster Autoscaler 1.15, however this version is not compatible with Kubernetes 1.11 which is currently available on Jetstream. Therefore I have taken the development version of Cluster Autoscaler 1.14 and compiled it myself. I also noticed that the scale down process was not working due to incompatible IDs when the Cloud Provider tried to lookup the ID of a Minion in the Stack. I am now directly using the MachineID instead of going through these indices. This version is available in [my fork of `autoscaler`](https://github.com/zonca/autoscaler/tree/cluster-autoscaler-1.14-magnum) and it is built into docker containers on the [`zonca/k8s-cluster-autoscaler-jetstream` repository on Docker Hub](https://cloud.docker.com/repository/docker/zonca/k8s-cluster-autoscaler-jetstream).
The image tags are the short version of the repository git commit hash.

I build the container using the `run_gobuilder.sh` and `run_build_autoscaler_container.sh` scripts included in the repository.

## Note about images used by Magnum

I have tested this deployment using the `Fedora-Atomic-27-20180419` image on Jetstream at Indiana University.
The Fedora Atomic 28 image had a long hang-up during boot and took more than 10 minutes to start and that caused timeout in the autoscaler and anyway it would have been too long for a user waiting to start a notebook.

I also tried updating the Fedora Atomic 28 image with `sudo atomic host upgrade` and while this fixed the slow startup issue, it generated a broken Kubernetes installation, i.e. the Kubernetes services didn't detect the master node as part of the cluster, `kubectl get nodes` only showed the minion.
