
---
categories:
- jetstream2
- jupyterhub
- singularity
- kubernetes
layout: post
date: '2023-03-07'
title: Run Singularity inside Kubernetes

---

In this tutorial we will be running a container capable of running [Singularity containers](https://docs.sylabs.io/guides/latest/user-guide/) inside Kubernetes,
then we will use it to deploy a Singularity-powered Jupyter Notebooks in JupyterHub. In my application, I have a pre-built Singularity container and I want to use it as a "Single-User container" in JupyterHub.

The other solution would be to entirely drop `ContainerD` and [run Kubernetes on top of Singularity](https://docs.sylabs.io/guides/cri/1.0/user-guide/k8s.html), however this is not supported by Kubespray which is my current deploying strategy.


## Test a privileged container running Singularity

The first step is straightforward, just by running a privileged container inside Kubernetes, we can allow it to execute Singularity commands, save this file as `privileged-pod.yaml`:

```
apiVersion: v1
kind: Pod
metadata:
  name: singularity
  namespace: default
spec:
  containers:
  - name: singularity
    image: quay.io/singularity/singularity:v3.11.0
    command: ['sh', '-c', 'sleep 999']
    securityContext:
       privileged: true
       allowPrivilegeEscalation: true
```

Then launch it:

    kubectl create -f privileged-pod.yaml

and connect to it with:

    kubectl exec -it singularity -- /bin/sh

Now we can pull a Docker image into a Singularity image file:

    singularity pull jupyterhub_singleuser.sif docker://jupyterhub/singleuser:3.1.0

## Build a Docker container with the JupyterHub Singleuser server

We now assume that `jupyterhub_singleuser.sif` is our "Production" software image that includes all the software environment that we want to offer to the users in our JupyterHub deployment.

We extract the Singularity image from the container with:

    kubectl cp default/singularity:/go/jupyterhub_singleuser.sif jupyterhub_singleuser.sif

Next we build a different Docker container based again on the Singularity Alpine image, but that when called executes `jupyterhub-singleuser` from the embedded Singularity image.

For testing purposes, you could use the container I have already built (tag `2023.03.7`):

<https://hub.docker.com/repository/docker/zonca/singularity_jupyterhub/>

To build instead, see the repository <https://github.com/zonca/singularity_jupyterhub> on Github,
then (replace `nerdctl` with `docker` if necessary):

```
# set DockerHub username
export DU=

gh repo clone zonca/singularity_jupyterhub
mv jupyterhub_singleuser.sif singularity_jupyterhub/
sudo nerdctl build -t $DU/singularity_jupyterhub singularity_jupyterhub/
```

Test it:

    sudo nerdctl run -d --privileged $DU/singularity_jupyterhub
    sudo nerdctl logs xxxxxxxxxxxxxxxxxxxxxxxxxxxx

or interactively:

    sudo nerdctl run -it --entrypoint /bin/sh $DU/singularity_jupyterhub:latest 

This should fail with this error message, which is a sign that we just need to configure the environment right but the container is working:

    JUPYTERHUB_API_TOKEN env is required to run jupyterhub-singleuser. Did you launch it manually?                            

Publish it:

    sudo nerdctl login
    sudo nerdctl push $DU/singularity_jupyterhub

### Built the image on a Kubernetes node

If you do not have Docker locally, you can use one of the nodes of your Kubernetes deployments to build the container.

Find the IP address and connect to it:

    openstack server list
    export IPN=xxx.xxx.xxx.xxx
    ssh ubuntu@$IPN

Then we need to install `buildkit`:

    <https://github.com/moby/buildkit/releases>

Unpack and install:

    sudo cp bin/buildkitd bin/buildctl /usr/local/bin/

Finally launch the daemon:

```
sudo /usr/local/bin/buildkitd &
```

## Build a Docker container with the JupyterHub Singleuser server
