---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2023-09-26'
layout: post
title: Setup HTTPS on Kubernetes with cert-manager

---

**Update March 2024**: the routing issue that force cert-manager pods to run on the control-plane are back, see [this Github issue](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/issues/75), so we had to add back the pinning of cert-manager services on one of the nodes in the control plane.

In this tutorial we will deploy `cert-manager` in Kubernetes to automatically provide SSL certificates to JupyterHub (and other services).

First make sure your payload, for example JupyterHub, is working without HTTPS, so that you check that the ports are open, Ingress is working, and JupyterHub itself can accept connections.

Let's follow the [`cert-manager` documentation](https://cert-manager.io/docs/installation/kubectl/), for convenience I pasted the commands below:

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

Once we have `cert-manager` setup we can create a Cluster Issuer that works for all namespaces (first edit the `yml` and add your email address):

    kubectl create -f setup_https/https_cluster_issuer.yml

After this, we can display all the resources in the `cert-manager` namespace to
check that the services and pods are running:

    kubectl get all --namespace=cert-manager

The result should be something like:

```
NAME                                          READY   STATUS    RESTARTS         AGE
pod/cert-manager-56c667df87-vcj8v             1/1     Running   6 (2d23h ago)    5d
pod/cert-manager-cainjector-8559b6f5d-rpl74   1/1     Running   11 (2d23h ago)   5d
pod/cert-manager-webhook-79f4b558b8-bxc86     1/1     Running   0                5d

NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/cert-manager           ClusterIP   10.233.35.148   <none>        9402/TCP   5d
service/cert-manager-webhook   ClusterIP   10.233.8.95     <none>        443/TCP    5d

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cert-manager              1/1     1            1           5d
deployment.apps/cert-manager-cainjector   1/1     1            1           5d
deployment.apps/cert-manager-webhook      1/1     1            1           5d

NAME                                                DESIRED   CURRENT   READY   AGE
replicaset.apps/cert-manager-56c667df87             1         1         1       5d
replicaset.apps/cert-manager-cainjector-8559b6f5d   1         1         1       5d
replicaset.apps/cert-manager-webhook-79f4b558b8     1         1         1       5d
```

## Bind the pods to the master node

In Jetstream 2 there are routing restrictions which allow Cert Manager to run only from the master node, [see the details on Github](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/issues/75). At least when the nodes do not have floating IPs, if all your Virtual Machines have a floating IP, you can safely skip this step.

Unidata has contributed the script they created to patch the 3 Cert Manager pods to have them run on the master node, we can apply it with:

    cd setup_https
    bash deploymentPatch.sh

Then verify that the pods are redeployed on master:

    kubectl -n cert-manager get pods -o wide

## Setup JupyterHub

Then we modify the JupyterHub ingress configuration to use this Issuer,
modify `secrets.yaml` to:

```
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt"
  hosts:
      - js-XXX-YYY.jetstream-cloud.org
  tls:
      - hosts:
         - js-XXX-YYY.jetstream-cloud.org
        secretName: certmanager-tls-jupyterhub
```

Finally update the JupyterHub deployment rerunning the deployment script (no need to delete it):

    bash install_jhub.sh

After a few minutes we should have a certificate available:

```
kubectl get certificaterequest --all-namespaces
NAMESPACE   NAME                           APPROVED   DENIED   READY   ISSUER        REQUESTOR                                         AGE
jhub        certmanager-tls-jupyterhub-1   True                True    letsencrypt   system:serviceaccount:cert-manager:cert-manager   5d
```

You can also check the state of the certificate with:

```
kubectl -n jhub describe certificate certmanager-tls-jupyterhub
```
