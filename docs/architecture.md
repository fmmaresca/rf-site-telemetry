# Architecture

## Components

- **Edge agent** (`edge-agent/`)
  - Collects metrics (real or simulated)
  - Wraps them in a stable **Telemetry Envelope v1**
  - Sends events to the cloud (HTTP in this repo; MQTT topic design documented)

- **Cloud API** (`cloud-api/`)
  - HTTP ingest endpoint
  - Validates the envelope
  - **Idempotent** insert (dedupe)
  - Query endpoints (devices / latest / series)

- **PostgreSQL**
  - Stores telemetry events (append-only)
  - Stores per-device last seen timestamp

- **Dashboard** (`dashboard/`)
  - Live devices list
  - Per-device latest metrics
  - Time-series charts
  - Online/stale/offline status

- **Simulator** (`tools/simulator/`)
  - Generates realistic signals
  - Optional intermittent outages (drop windows)

## Data flow

`edge-agent / simulator` → `POST /api/v1/ingest` → `cloud-api` → `PostgreSQL` → `dashboard`

## Idempotency model

Every event carries:

- `seq`: monotonic per-device counter
- `msg_id`: string idempotency key (recommended `{device_id}:{seq}`)

On the server, idempotency is enforced with a unique constraint on:

`(tenant, device_id, seq)` (or equivalently `(tenant, msg_id)` if you choose that schema).

Expected behaviour:

- **Duplicate delivery**: accepted, but deduped (no duplicate rows)
- **Out-of-order**: accepted; ordering is based on `ts` for charts

## MQTT topic design (planned)

Topic (design):

`telemetry/v1/{tenant}/{device_id}`

QoS 1 recommended. HTTP remains the canonical ingest path for the public demo.
