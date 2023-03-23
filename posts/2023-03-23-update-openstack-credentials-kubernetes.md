---
categories:
- kubernetes
- jetstream
date: '2023-03-23'
layout: post
title: Update Openstack credentials in Kubernetes

---

If you are deploying Kubernetes on top of Openstack, the Openstack External cloud provider stores the ID and Secret necessary to authenticate with the cloud infrastructure in a Secret.

Let's see how to replece those credentials, for example if they expired.

First dump the base64 encoded secret to the terminal:
 
```
kubectl get secret -n kube-system external-openstack-cloud-config -o jsonpath='{.data}'
```

Then copy-paste just the encoded part:

echo xxxxxx | base64 --decode > cloud.conf

Now we can edit it to replace the credentials

Set the new `OS_APPLICATION_CREDENTIAL_ID` in `application-credential-id` and `application-credential-name`.
Set the value of `OS_APPLICATION_CREDENTIAL_SECRET` in `application-credential-secret`.

Finally encode the content of the file again (`-w0` gives the output in 1 line without wrapping):

    cat cloud.conf | base64 -w0

and overwrite the `cloud.conf` value in the secret:

    kubectl edit secret -n kube-system external-openstack-cloud-config

Now repeat the process with the `cloud-config` secret, which is used by Cinder CSI, you can copy the 3 relevant lines from the previous file.

Finally we need to restart the affected pods, however, to make it easier I just rebooted all the nodes via `openstack server reboot`.
