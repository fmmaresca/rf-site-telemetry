# RF Site Telemetry (Edge → Cloud)

Production-style telemetry pipeline from edge devices to a cloud API, backed by PostgreSQL, with a live dashboard.

**Live demo:** https://rfdemo.fmaresca.com

## What this demonstrates

- **Stable telemetry envelope (v1)** with tenant + device identity
- **HTTP ingest** (FastAPI) + PostgreSQL persistence
- **Idempotency / dedupe** via `msg_id` / `(tenant, device_id, seq)`
- **Query APIs**: devices, latest, time-series
- **Operational UX**: online / stale / offline device state
- **Simulator** that generates realistic signals + intermittent outages

## Architecture

High level:

`edge-agent / simulator` → **HTTPS** `POST /api/v1/ingest` → `cloud-api` → `PostgreSQL` → `dashboard`

Docs:

- `docs/architecture.md`
- `docs/protocol.md`
- `docs/api.md`
- `docs/deployment.md`

## Repo layout

- `cloud-api/` – FastAPI service (ingest + queries)
- `edge-agent/` – Python agent scaffold (local metrics → envelope)
- `tools/` – simulator + helpers
- `dashboard/` – Vite + React dashboard
- `infra/` – dev docker compose (Postgres)
- `docs/` – reference docs

## Quickstart (local dev)

### 1) Start Postgres

```bash
docker compose -f infra/docker-compose.dev.yml up -d db
```

### 2) Run cloud API

```bash
cd cloud-api
python -m venv .venv && . .venv/bin/activate
pip install -e .
export DB_DSN='postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry'
export AUTH_REQUIRED=0
export LOGGING__FILE_PATH='./logs/cloud-api.log'
mkdir -p logs
uvicorn app.main:app --reload --port 8001
```

Health check:

```bash
curl -s http://127.0.0.1:8001/healthz
```

### 3) Send telemetry (simulator)

```bash
python3 tools/simulator/sim_http.py \
  --base-url http://127.0.0.1:8001 \
  --tenant demo \
  --devices 5 \
  --interval-s 5
```

### 4) Run dashboard

```bash
cd dashboard
npm install
VITE_API_BASE=http://127.0.0.1:8001 npm run dev
```

Open http://127.0.0.1:5173

## License

MIT (see `LICENSE`).
