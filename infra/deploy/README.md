# Deploy (systemd + nginx) — rfdemo.fmaresca.com/api

This folder contains a deploy bundle for running the Cloud API behind Nginx on a host that already serves other sites.

Target public URL:
- https://rfdemo.fmaresca.com/api  -> Cloud API (FastAPI/uvicorn)
Future:
- https://rfdemo.fmaresca.com/     -> Dashboard static site (optional)

The API process listens locally:
- 127.0.0.1:8001

---

## 0) Assumptions & requirements

- Debian/Devuan/Ubuntu-like server
- You already manage TLS certificates (Let’s Encrypt / Cloudflare Origin certs / etc.)
- Nginx is installed (or Apache is installed and Nginx will be used as a reverse proxy on this vhost only)
- PostgreSQL reachable from the host (local or remote)

Packages (typical):
- python3, python3-venv
- nginx (if using nginx reverse proxy)
- postgresql-client (psql for migrations)

---

## 1) Directory layout on the server

Recommended paths:
- Repo checkout: `/opt/rfsite/` (read-only-ish)
- Cloud API code: `/opt/rfsite/cloud-api`
- Python venv: `/opt/rfsite/venv`
- Runtime env file: `/etc/rfsite-cloud-api/env`

Create dirs:

```bash
sudo mkdir -p /opt/rfsite
sudo mkdir -p /etc/rfsite-cloud-api
sudo chown -R $USER:$USER /opt/rfsite
```

> Note: This folder is a legacy deployment bundle.
> The current reference deployment docs live in `docs/deployment.md`.


