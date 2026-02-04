---
categories:
- kubernetes
- jetstream
- jupyterhub
- nbgrader
date: '2026-02-04'
layout: post
title: Deploy nbgrader on Jetstream with ngshare (Kubernetes)
---

This tutorial shows how to deploy **nbgrader** on Jetstream using **ngshare**, a service designed to make nbgrader work on Kubernetes without a shared filesystem exchange. This is the recommended approach for Kubernetes deployments.

We will:

* Deploy `ngshare` via Helm.
* Configure JupyterHub to register the ngshare service.
* Install `ngshare_exchange` and `nbgrader` in the singleuser image (using an existing image).
* Set a placeholder course ID.

## Why ngshare

nbgrader's default exchange assumes a shared filesystem between user pods. Kubernetes does not provide that by default, so ngshare replaces the exchange mechanism with a REST API.

## Prerequisites

* A working Kubernetes cluster on Jetstream (Magnum + Cluster API).
* JupyterHub deployed with the Helm chart.
* `kubectl` and `helm` configured.
* This repository cloned locally.

## Storage sizing for ngshare

ngshare stores **metadata only** (users, courses, submissions metadata), not the actual notebook files.

* Typical classes: **1–5 Gi** is plenty.
* Large classes or many submissions: **10 Gi** is safe.

## Step 1: Install ngshare (Helm)

Add the Helm repo and create a minimal `config.yaml`:

```bash
helm repo add ngshare https://libretexts.github.io/ngshare-helm-repo/
helm repo update
```

Use the template in this repo and edit it:

* `nbgrader/ngshare-config.yaml`

Install into the same namespace as JupyterHub (here `jhub`):

```bash
helm install ngshare ngshare/ngshare \
  --namespace jhub \
  -f nbgrader/ngshare-config.yaml
```

Expected output (truncated):

```
NAME: ngshare
NAMESPACE: jhub
STATUS: deployed
NOTES:
Congrats, ngshare should be installed!
```

At the end of the Helm install, ngshare prints the **exact JupyterHub config snippet** you should add. Keep it; we will use it in the next step.

Verify the pod:

```bash
kubectl -n jhub get pods -l app.kubernetes.io/instance=ngshare
```

Example output:

```
NAME                       READY   STATUS    RESTARTS   AGE
ngshare-57545bf697-rbrcz   1/1     Running   0          37s
```

## Step 2: Register ngshare in JupyterHub

Add the ngshare service snippet to your JupyterHub values:

* `nbgrader/jhub-ngshare-service.yaml`

If you keep your Helm values in `config_standard_storage.yaml`, add the block there.  
Then add the values file to `install_jhub.sh` (just before the last line):

```
--values nbgrader/jhub-ngshare-service.yaml \
```

Re-deploy by running:

```bash
bash install_jhub.sh
```

Verify the ngshare service:

* JupyterHub → Control Panel → Services → **ngshare**
* If you see a 403, try with an admin user (ngshare enforces admin-only access to some endpoints).

## Step 3: Enable nbgrader in the singleuser image

You need `nbgrader` and `ngshare_exchange` inside every user pod.  
This tutorial uses the standard Jupyter Docker Stacks image and installs the packages at startup.

Use the template in this repo:

* `nbgrader/jhub-singleuser-nbgrader.yaml`

Replace `COURSE_ID` with your course (e.g. `course101`).

If you want a custom image instead, see:  
`https://www.zonca.dev/posts/2025-12-01-custom-jupyterhub-docker-image`

After updating the values, add the file to `install_jhub.sh`:

```
--values nbgrader/jhub-singleuser-nbgrader.yaml \
```

Re-deploy:

```bash
bash install_jhub.sh
```

If you forget to add the values file, user pods will not have the packages installed and you will see:

```
WARNING: Package(s) not found: nbgrader, ngshare-exchange
```

## Step 4: Validate in JupyterHub

In a user pod:

```bash
python -m pip show nbgrader ngshare-exchange
nbgrader list
```

Expected output (example):

```
[pip show output truncated]
[ListApp | ERROR] ngshare service returned invalid status code 404.
[ListApp | ERROR] ngshare endpoint /assignments/course101 returned failure: Course not found
[ListApp | ERROR] Failed to get assignments from course course101.
[ListApp | INFO] Released assignments:
```

The 404 "Course not found" is expected until you create the course in the next step.

Note: running `nbgrader list` in a standalone test pod (not a real JupyterHub user pod) can also return a 404 from ngshare. Always validate from an actual user server.

Full `pip show` output is available in this repo at:

* `nbgrader/expected-output/pip-show-nbgrader-ngshare.txt`

## Step 5: Create the course and roster

Use `ngshare-course-management` (installed with `ngshare_exchange`) to create the course and add instructors/students.  
Creating a course requires an **admin** user.

```bash
ngshare-course-management create_course course101 instructor1
ngshare-course-management add_student course101 student1
```

After creating the course:

```
[ListApp | INFO] Released assignments:
```

## Step 6: Create and release a first assignment

Initialize a course directory with example content:

```bash
nbgrader quickstart course101
```

Expected output (example):

```
[QuickStartApp | INFO] Creating directory '/home/jovyan/course101'...
[QuickStartApp | INFO] Copying example from the user guide...
[QuickStartApp | INFO] Generating example config file...
[QuickStartApp | INFO] Done! The course files are located in '/home/jovyan/course101'.
```

Generate the assignment and release it to ngshare:

```bash
cd /home/jovyan/course101
nbgrader generate_assignment ps1
nbgrader release_assignment ps1
```

If you want ready-made test notebooks, this repo includes a minimal set at:

* `nbgrader/quickstart-source/ps1/problem1.ipynb`
* `nbgrader/quickstart-source/ps1/problem2.ipynb`

Copy them into your course source before generating:

```bash
cp -r /path/to/jupyterhub-deploy-kubernetes-jetstream/nbgrader/quickstart-source/ps1 /home/jovyan/course101/source/
```

Expected output (example):

```
[GenerateAssignmentApp | INFO] Updating/creating assignment 'ps1': {}
[GenerateAssignmentApp | INFO] Converting notebook /home/jovyan/course101/source/./ps1/problem1.ipynb
[GenerateAssignmentApp | INFO] Converting notebook /home/jovyan/course101/source/./ps1/problem2.ipynb
[ReleaseAssignmentApp | INFO] Successfully released ps1
```

If `nbgrader generate_assignment` fails with an “old nbgrader metadata format” error, run:

```bash
cd /home/jovyan/course101
nbgrader update .
```

Then re-run `nbgrader generate_assignment ps1 --force`.

If you re-run the release, add `--force`:

```bash
nbgrader release_assignment ps1 --force
```

Verify it shows up:

```
[ListApp | INFO] Released assignments:
[ListApp | INFO] course101 ps1
```

## Step 7: Student workflow (fetch + submit)

Make sure the student is added to the course:

```bash
ngshare-course-management add_student course101 student1
```

If a student is not added, they will see:

```
[ListApp | ERROR] ngshare service returned invalid status code 403.
[ListApp | ERROR] ngshare endpoint /assignments/course101 returned failure: Permission denied
```

As the student, list available assignments:

```bash
nbgrader list
```

Expected output (example):

```
[ListApp | INFO] Released assignments:
[ListApp | INFO] course101 ps1
```

Fetch the assignment:

```bash
nbgrader fetch_assignment ps1
```

Expected output (example):

```
[FetchAssignmentApp | INFO] Successfully fetched ps1. Will try to decode
[FetchAssignmentApp | INFO] Decoding: /home/jovyan/ps1/problem2.ipynb
[FetchAssignmentApp | INFO] Decoding: /home/jovyan/ps1/problem1.ipynb
[FetchAssignmentApp | INFO] Successfully decoded ps1.
```

Submit the assignment:

```bash
nbgrader submit ps1
```

Expected output (example):

```
[SubmitApp | INFO] Source: /home/jovyan/ps1
[SubmitApp | INFO] Encoding: problem1.ipynb
[SubmitApp | INFO] Encoding: problem2.ipynb
[SubmitApp | INFO] Submitted as: course101 ps1 2026-02-04 03:03:39.734930
```

## Step 8: Instructor workflow (collect + autograde)

As the instructor:

```bash
cd /home/jovyan/course101
nbgrader collect ps1
```

Expected output (example):

```
[CollectApp | INFO] Processing 1 submissions of "ps1" for course "course101"
[CollectApp | INFO] Collecting submission: student1 ps1
[CollectApp | INFO] Decoding: /home/jovyan/course101/submitted/student1/ps1/problem1.ipynb
[CollectApp | INFO] Decoding: /home/jovyan/course101/submitted/student1/ps1/problem2.ipynb
```

Autograde:

```bash
nbgrader autograde ps1
```

Expected output (example):

```
[AutogradeApp | INFO] SubmittedAssignment<ps1 for student1> submitted at 2026-02-04 03:03:39.734930
[AutogradeApp | INFO] Autograding /home/jovyan/course101/autograded/student1/ps1/problem1.ipynb
[AutogradeApp | INFO] Autograding /home/jovyan/course101/autograded/student1/ps1/problem2.ipynb
```

You may see `SAWarning` lines from SQLAlchemy during autograde. These are warnings (not failures) and can be ignored for this workflow.

## Notes

* Use **ngshare** for nbgrader exchange on Kubernetes.
* Use a dedicated course ID per class (set in `nbgrader_config.py`).
* To manage students and instructors, use the `ngshare-course-management` CLI installed with `ngshare_exchange` rather than the formgrader UI.

## Troubleshooting

If ngshare starts with:

```
sqlite3.OperationalError: unable to open database file
```

Your storage backend likely doesn't honor `fsGroup`.  
Fix it by uncommenting the `deployment.initContainers` block in `nbgrader/ngshare-config.yaml` and re-install:

```bash
helm upgrade ngshare ngshare/ngshare \
  --namespace jhub \
  -f nbgrader/ngshare-config.yaml
```

Then restart the pod:

```bash
kubectl -n jhub delete pod -l app.kubernetes.io/instance=ngshare
```

If you see:

```
KeyError: 'USER'
```

you are likely running outside a real JupyterHub user environment. Run the validation inside a spawned JupyterHub user server.
