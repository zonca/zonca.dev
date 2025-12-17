---
title: Cosmosage Unshelver
date: 2025-12-16 10:00:00 # Using a placeholder time, actual time doesn't matter much
categories: [github]
layout: post
slug: cosmosage-unshelver
---

This post describes the Cosmosage Unshelver. You can find the project on GitHub: [zonca/openstack_unshelver_webapp](https://github.com/zonca/openstack_unshelver_webapp). There is an active pull request for further development.

# Cosmosage Unshelver Controller Deployment Guide

This guide documents every step required to turn a fresh Ubuntu VM (the "tiny" controller) into the always-on launcher for the GPU instance `cosmosage_70b_zonca`. Follow it line-by-line when rebuilding the environment or performing audits.

## 1. Prerequisites
- DNS `cosmosage-unshelver.cis230085.projects.jetstream-cloud.org` must point at the controller floating IP (`149.165.172.14`).
- DNS `cosmosage.phy240259.projects.jetstream-cloud.org` must point at the same controller IP (chat UI hostname inside the project-owned Designate zone).
- You need the OpenStack application credential file `app-cred-cosmosageopenstack-openrc.sh` which contains `OS_AUTH_URL`, `OS_APPLICATION_CREDENTIAL_ID`, and `OS_APPLICATION_CREDENTIAL_SECRET`.
- Ensure the GPU VM exposes HTTP on port `8080` with `/health` returning 200 once the chat UI is ready.
- SSH access as `exouser` with passwordless sudo.

### 1.1 Manage the DNS records via Designate
From the controller repository run:
```bash
source app-cred-cosmosageopenstack-openrc.sh
uv run python scripts/ensure_dns_record.py cosmosage-unshelver.cis230085.projects.jetstream-cloud.org 149.165.172.14
uv run python scripts/ensure_dns_record.py cosmosage.phy240259.projects.jetstream-cloud.org 149.165.172.14
```
The helper script finds the correct Designate zone, creates the record if needed, or updates it in place. Verify propagation:
```bash
dig +short cosmosage-unshelver.cis230085.projects.jetstream-cloud.org
dig +short cosmosage.phy240259.projects.jetstream-cloud.org
```
Both commands must return `149.165.172.14`.

## 2. Base OS preparation
```bash
ssh exouser@149.165.172.14
sudo apt-get update
sudo apt-get install -y git curl build-essential pkg-config python3 python3-venv python3-pip libssl-dev libffi-dev unzip
curl -LsSf https://astral.sh/uv/install.sh | sh
```
`uv` installs into `~/.local/bin`; keep it in your PATH for shell sessions and systemd units.

## 3. Clone and configure the controller
```bash
git clone https://github.com/zonca/openstack_unshelver_webapp.git
cd openstack_unshelver_webapp
git checkout feature/controller-redesign
~/.local/bin/uv sync --frozen
```
Create `config.yaml` (never commit secrets):
```yaml
app:
  title: "Cosmosage Chat Launcher"
  secret_key: "<32+ byte random>"
  poll_interval_seconds: 10
  http_probe_timeout: 5.0
  http_probe_attempts: 18
  control_token: "<token for /control>"
  manual_shelve_path: "/admin-shelve-cosmos"
openstack:
  auth_url: "https://js2.jetstream-cloud.org:5000/v3/"
  region_name: "IU"
  interface: "public"
  auth_type: "v3applicationcredential"
  application_credential_id: "<from app-cred>"
  application_credential_secret: "<from app-cred>"
buttons:
  - id: "cosmosage"
    label: "Wake Cosmosage 70B"
    description: "Unshelve the 70B GPU VM and forward the chat UI once healthy."
    instance_name: "cosmosage_70b_zonca"
    public_base_url: "https://cosmosage.phy240259.projects.jetstream-cloud.org"
    url_scheme: "http"
    port: 8080
    healthcheck_path: "/health"
    launch_path: "/"
    verify_tls: false
activity_log_path: "/var/log/caddy/gpu-access.log"
idle_timeout_minutes: 120
idle_poll_interval_seconds: 30
caddy_upstream_label: "tcp/149.165.155.205:8080"
local_event_log: "/var/log/unshelver/events.jsonl"
swift_event_container: "cosmosage-unshelver-events"
swift_event_prefix: "cosmosage"
```
The launcher always renders at `https://cosmosage-unshelver.cis230085.projects.jetstream-cloud.org/`. When the GPU VM is ready the status card highlights the new `public_base_url` so people can open the chat UI (`https://cosmosage.phy240259.projects.jetstream-cloud.org/`). Caddy proxies that hostname straight into the GPU VM and automatically falls back to the launcher hostname whenever the proxy fails, so there is no need to refresh two tabs manually. Once Cosmosage is awake, the idle monitor keeps it running until two hours pass without any proxied traffic.

Prepare log directories:
```bash
sudo mkdir -p /var/log/unshelver
sudo chown exouser:exouser /var/log/unshelver
```

## 4. Systemd service
Create `/etc/systemd/system/unshelver.service`:
```ini
[Unit]
Description=Cosmosage OpenStack Unshelver Controller
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=exouser
WorkingDirectory=/home/exouser/openstack_unshelver_webapp
Environment="PATH=/home/exouser/openstack_unshelver_webapp/.venv/bin:/home/exouser/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/exouser/openstack_unshelver_webapp/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 5001 --proxy-headers
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now unshelver.service
```
Verify on localhost: `curl http://127.0.0.1:5001/` (should return the launcher HTML).

## 5. Install & configure Caddy
```bash
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/gpg.key" | sudo gpg --dearmor -o /etc/apt/keyrings/caddy-stable-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian/ any-version main" | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update
sudo apt-get install -y caddy
```
`/etc/caddy/Caddyfile`:
```caddy
{
    admin off
    email you@example.com
}

cosmosage-unshelver.cis230085.projects.jetstream-cloud.org {
    encode gzip zstd
    reverse_proxy http://127.0.0.1:5001
}

cosmosage.phy240259.projects.jetstream-cloud.org {
    encode gzip zstd

    log {
        output file /var/log/caddy/gpu-access.log {
            roll_keep 14
            roll_size 50MB
        }
        format json
    }

    reverse_proxy 149.165.155.205:8080 {
        header_up Host cosmosage.phy240259.projects.jetstream-cloud.org
        header_down X-Proxy-Backend {http.reverse_proxy.upstream.address}
        transport http {
            compression off
        }
    }

    handle_errors {
        redir https://cosmosage-unshelver.cis230085.projects.jetstream-cloud.org/ 302
    }
}
```
The first site block serves only the controller. The second site block proxies *everything* to the GPU VM and emits JSON access logs that power the idle monitor. When the GPU VM is shelved, Caddy immediately returns a 502/503; `handle_errors` turns those failures into a redirect back to the launcher so visitors land on the wake button instead of a browser error.
Permissions and ACLs:
```bash
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy
sudo touch /var/log/caddy/gpu-access.log
sudo chown caddy:caddy /var/log/caddy/gpu-access.log
sudo chmod 640 /var/log/caddy/gpu-access.log
sudo setfacl -m u:exouser:r /var/log/caddy/gpu-access.log
sudo usermod -aG caddy exouser
```
Restart:
```bash
sudo systemctl restart caddy
sudo systemctl restart unshelver.service
```

## 6. Networking & security group hardening
Restrict GPU ingress to the controller IP:
```bash
uv run python harden_gpu_sg.py
```
(See repo helper script/notes—delete broad ingress rules and add TCP/8080 from `149.165.172.14/32`.)

## 7. Idle monitoring & event logs
- `CaddyActivityMonitor` tails `/var/log/caddy/gpu-access.log` for the upstream label `tcp/149.165.155.205:8080` and triggers auto-shelve after 120 minutes of inactivity.
- `openstack_unshelver_webapp/event_logger.py` writes local JSONL logs to `/var/log/unshelver/events.jsonl` and syncs them to Swift container `cosmosage-unshelver-events` under prefix `cosmosage/YYYY/MM/DD/*.jsonl`.

## 8. Operations
- Deploy updates: `git pull` in `/home/exouser/openstack_unshelver_webapp`, then `sudo systemctl restart unshelver.service`.
- Health checks:
  - `curl -I https://cosmosage-unshelver.cis230085.projects.jetstream-cloud.org/` always returns the launcher HTML (`HTTP/2 200`).
  - `curl -s https://cosmosage-unshelver.cis230085.projects.jetstream-cloud.org/status/cosmosage` for live status fragments.
  - `curl -I https://cosmosage.phy240259.projects.jetstream-cloud.org/` returns `HTTP/2 200` when Cosmosage is awake (the GPU proxy works) and `HTTP/2 302` redirecting to the launcher while it sleeps.
- Manual controls: `/control?token=<token>` hosts the dashboard with “Shelve GPU now” and “Force Unshelve” buttons. Hidden manual shelve path: `/admin-shelve-cosmos`.
- Admin-only shelve button lives at `/admin-shelve-cosmos?token=...`; keep the obscured URL private.

With this setup the public landing page stays up 24/7, and the chat hostname automatically proxies into the GPU VM (or bounces visitors back to the launcher whenever the GPU sleeps).
