# RF Site Telemetry (Edge → Cloud)

Portfolio project: production-style telemetry pipeline from edge devices to cloud.

## What it demonstrates
- Stable telemetry envelope (v1)
- HTTP ingest (FastAPI) + PostgreSQL persistence
- Query endpoints: devices, latest, series
- Edge agent scaffold (Python) generating envelope events
- MQTT topic design (docs) — implementation in later milestone

## Repo layout
- `docs/` architecture + protocol + API
- `cloud-api/` FastAPI service
- `edge-agent/` Python edge agent
- `infra/` postgres + migrations

## Quickstart (dev)
1) Start Postgres:
```bash
docker compose -f infra/docker-compose.dev.yml up -d db
