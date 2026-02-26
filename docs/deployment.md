# Deployment (reference)

This repo is designed to be deployable on a small VM using systemd + a reverse proxy.

## Cloud API

### Environment

Example env file (do **not** commit secrets):

```bash
DB_DSN='postgresql://rftelemetry:***@localhost:5432/rftelemetry'
AUTH_REQUIRED=1
PUBLIC_READONLY_TENANT=demo
PUBLIC_READONLY_API_KEY='***'
```

### systemd unit

```ini
[Unit]
Description=RF Site Cloud API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rfdemo
Group=nogroup
WorkingDirectory=/opt/rfsite/cloud-api
EnvironmentFile=/etc/rfsite-cloud-api/env
ExecStart=/opt/rfsite/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

## Reverse proxy

The public site serves the dashboard at `/` and proxies the API under `/api/`.

Apache vhost key points:

- `ProxyPass /api/ http://127.0.0.1:8001/`
- SPA fallback must **exclude** `/api/` and `/assets/`

## Cloudflare caching

If you use Cloudflare in front, ensure that `/api/*` is **not cached**.

Recommended:

- Cache rule: *Bypass cache* for `URI path starts with /api/`
- Cache rule: *Cache* for `/assets/*` (hashed assets)
