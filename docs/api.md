

# Cloud API (v1)

Auth:
- `Authorization: Bearer <api_key>`

## Endpoints
- `GET /healthz`
- `GET /readyz`
- `POST /v1/ingest`

Tenant-scoped:
- `GET /v1/tenants/{tenant}/devices`
- `GET /v1/tenants/{tenant}/devices/{device_id}/latest`
- `GET /v1/tenants/{tenant}/devices/{device_id}/series?metric=&from_ts=&to_ts=&limit=`
