
### `LICENSE`
Poné MIT o Apache-2.0. (Si querés, te paso el texto completo en el próximo commit; para arrancar podés agregarlo desde GitHub template.)

---

## 2) Docs

### `docs/architecture.md`
```md
# Architecture

## Components
- **Edge Agent**: collects metrics, builds Telemetry Envelope v1, sends to cloud (HTTP now, MQTT later). Adds buffering + retries in later milestones.
- **Cloud API**: HTTP ingest + queries. Validates schema, performs idempotent insert, updates device last-seen.
- **PostgreSQL**: stores telemetry events + device registry (seen devices).
- **Dashboard** (later): shows latest + time series.

## Data flow (MVP)
Edge Agent → HTTPS POST `/v1/ingest` → Cloud API → PostgreSQL → Query endpoints → Dashboard

## Idempotency (design)
Primary idempotency key: `(tenant, device_id, seq)` unique constraint.
- Duplicate delivery returns 202 and is counted as `deduped`.
- Collision (same key, different content) returns 409 (later milestone; MVP logs).

## MQTT (design)
Topic: `telemetry/v1/{tenant}/{device_id}` (QoS 1 recommended).
HTTP remains the canonical ingest API for public demo.





---

## 4) Cloud API (FastAPI)

### `cloud-api/pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "rfsite-cloud-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.27",
  "pydantic>=2.6",
  "pydantic-settings>=2.2",
  "psycopg[binary]>=3.1",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]


## 5) Edge Agent (scaffold)

### `edge-agent/pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "rfsite-edge-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.6",
  "pyyaml>=6.0",
  "requests>=2.31",
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]


## 6) Tools stubs

### `tools/simulator/README.md`
```md
# simulator (stub)

Later: generate many devices and push events to /v1/ingest or MQTT.
