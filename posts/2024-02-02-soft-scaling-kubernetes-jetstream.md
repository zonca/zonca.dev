---
categories:
- kubernetes
- jetstream2
- ana-espinoza
date: '2024-02-02'
layout: post
slug: soft-scaling-kubernetes-jetstream
title: Soft Scaling Kubernetes on Jetstream

---

Work and post contributed by [Ana Espinoza](https://github.com/ana-v-espinoza), only tested and benchmarked by [Andrea Zonca](https://github.com/zonca).

## Summary

To scale down:
```bash
kubectl cordon <node-name>
kubectl drain --ignore-daemonsets <node-name> # --delete-emptydir-data # <-- Flag may be necessary
openstack server shelve <node-name>
```

To scale back up:
```bash
openstack server unshelve <node-name>
kubectl uncordon <node-name>
```

## The Problem

Sometimes,a JupyterHub cluster deployed on top of Kubernetes will receive heavy
intermittent use. For example, a cluster may be deployed with enough
nodes--let's say 10 `m3.mediums`--to serve a regularly held workshop, each with a large
number of participants. However, between workshops, when partipants aren't
expected to be logging into the server, this many nodes are not necessary, and
would be needlessly exhausting Jetstream Service Units (SUs).

## "Hard Scaling" the Cluster (the Slow Way)

To conserve SUs, one might consider [removing the extra
nodes](https://github.com/zonca/jetstream_kubespray/blob/branch_v2.21.0/k8s_remove_node.sh)
from the cluster then re-running Terraform with fewer nodes. When it's time to
run the workshop again, the reverse process is done: run Terraform to re-create
the previously destroyed nodes, then running
[k8s_scale.sh](https://github.com/zonca/jetstream_kubespray/blob/branch_v2.21.0/k8s_scale.sh)
to re-add these nodes to the still existing cluster. 

This however, can be a lengthy process as this involves reinstalling Kubernetes
dependencies on the freshly recreated nodes.

## "Soft Scaling" the Cluster (the Fast Way)

Instead of destorying the excess nodes, we can soft scale the cluster, a
technique first described
[here](https://github.com/Unidata/science-gateway/tree/master/vms/jupyter#soft-scaling-a-cluster).
The technique is simple. To downscale, you "cordon" and "drain" the excess nodes
before finally shelving them via `openstack`, a VM state that conserves SU's.
When you're ready to scale back up, you unshelve the nodes and uncordon them.
The entire scaling process (both downscaling and upscaling) can take as little
as 5 minutes.

### Soft Scaling Down

First, cordon off the nodes you want to scale down. This will ensure that no new
Pods can be scheduled on the node.

```bash
kubectl get nodes # Run to find the node names
kubectl cordon <node-name>
```

Next, drain the node. This will remove any Pods currently running on that node.
Kubernetes will reschedule these Pods on an available node.

```bash
kubectl drain <node-name> --ignore-daemonsets
```

You may get an error that looks like the following:

```
error: unable to drain node "<node>" due to error:cannot delete Pods with local
storage (use --delete-emptydir-data to override):
kube-system/csi-cinder-controllerplugin-xxxxxxxxx, continuing command...
```

This is Kubernetes warning you that the `csi-cinder-controller-plugin` Pod is
storing some temporary data in an "emptyDir" volume mount. This temporary data
is safe to delete and will be recreated once the Pod is rescheduled. Rerun the
drain command with the `--delete-emptydir-data` flag.

Once the node has been successfully drained, you can run a `kubectl get nodes`
and you should see the node status as `Ready,SchedulingDisabled`.

Now run the shelve command:

```bash
openstack server shelve <node-name>
```

One final `kubectl get nodes` should reveal the status of the down scaled node
as `NotReady,SchedulingDisabled`.

### Soft Scaling Back Up

To scale back up, we perform the tasks in reverse.

Unshelve the node:

```bash
openstack server unshelve <node-name>
```

Uncordon the node:

```bash
kubectl uncordon <node-name>
```

Your node's status should now be `Ready,Schedulable`.

### Scaling Many Nodes at Once

Since the node names for worker nodes created using
Kubespray/Jetstream_Kubespray are of the form
`$CLUSTER-k8s-node-<number>`, we can use a `bash` for loop to soft
scale multiple nodes at once.

See the [`k8s_softscale.sh`](https://github.com/zonca/jetstream_kubespray/blob/branch_v2.21.0/k8s_softscale.sh) script in the repository. It is recommended to execute one step at a time and verify that it executed to completion before rerunning the script uncommenting the next step.

## Benchmark

Just as a reference, here are time measurements I took executing the default configuration of the Kubernetes deployment (`m3.medium` instances both for master and for nodes), with no deployed services, just executed once:

* Ansible run for initial deployment of 1 master + 1 worker: 27m
* Terraform run to create other 9 workers: < 1m
* Ansible run to scale the Kubernetes cluster to the 9 extra nodes: 43m
* Cordon 9 nodes: 3s
* Shelve 9 nodes: 3m
* Unshelve 9 nodes: <5m
* Uncordon 9 nodes: 3s

This technique is quite impressive, bring the time needed to scale a cluster from 1 to 10 nodes from 43m down to less than 5m.
