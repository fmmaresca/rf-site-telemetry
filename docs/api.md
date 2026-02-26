# Cloud API (v1)

Base path in the public deployment:

- `/api` (reverse proxy)

So the ingest endpoint is:

- `POST /api/v1/ingest`

## Auth

Requests may require:

- `Authorization: Bearer <api_key>`

In local dev you can disable auth via `AUTH_REQUIRED=0`.

## Endpoints

Health:

- `GET /healthz`
- `GET /readyz`

Ingest:

- `POST /v1/ingest`

Tenant-scoped queries:

- `GET /v1/tenants/{tenant}/devices`
- `GET /v1/tenants/{tenant}/devices/{device_id}/latest`
- `GET /v1/tenants/{tenant}/devices/{device_id}/series?metric=&from_ts=&to_ts=&limit=`
