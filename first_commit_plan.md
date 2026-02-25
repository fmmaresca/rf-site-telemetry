
---

## Primer commit plan (archivos + contenido mínimo)

**Objetivo del primer commit:** que el repo “nazca” con contrato, arquitectura y scaffolding Python + migrations, sin todavía implementar lógica compleja.

### 1) Root
- `README.md`
  - qué es el proyecto, features, quickstart (vacío pero con placeholders)
  - link a docs
- `LICENSE` (MIT o Apache-2.0; yo usaría Apache-2.0 si querés vibe más “enterprise”)
- `.gitignore` (Python, Node si dashboard después, env, etc.)

### 2) Docs
- `docs/architecture.md`
  - diagrama ASCII simple + explicación de componentes
- `docs/protocol.md`
  - Envelope v1 + topics MQTT + batch + ejemplos JSON
- `docs/api.md`
  - endpoints con ejemplos (derivado de OpenAPI)
- `docs/provisioning.md` (stub)
- `docs/threat-model.md` (stub: assets, threats, mitigations)

### 3) Cloud API (scaffold)
- `cloud-api/pyproject.toml` (FastAPI + uvicorn + pydantic + asyncpg/psycopg)
- `cloud-api/src/app/main.py`
  - FastAPI app + `/healthz`
  - routers vacíos
- `cloud-api/src/app/models.py`
  - Pydantic models para Envelope v1 + batch
- `cloud-api/openapi.yaml`
  - spec inicial (ingest + query stubs)
- `cloud-api/README.md`
  - cómo correr local

### 4) DB / migrations
- `infra/migrations/001_init.sql`
  - tablas `tenants`, `devices`, `telemetry` + índices + unique
- `infra/docker-compose.dev.yml`
  - postgres local + cloud-api (opcional)
- `infra/README.md`

### 5) Edge agent (scaffold)
- `edge-agent/pyproject.toml`
- `edge-agent/src/agent/main.py`
  - loop con collector simulado + build envelope + print (sin enviar aún)
- `edge-agent/config/telemetry.example.yaml`
- `edge-agent/systemd/rfsite-telemetry.service` (unit básica)
- `edge-agent/README.md`

### 6) Tools
- `tools/simulator/README.md` (stub)
- `tools/scripts/` (vacío por ahora)

---
