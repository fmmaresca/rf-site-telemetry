
### `docs/api.md`
```md
# Cloud API (v1)

Auth (MVP):
- `Authorization: Bearer <api_key>` (optional enforcement in later milestone; scaffolding only in commit #1)

## Endpoints
- `GET /healthz`
- `POST /v1/ingest`
- `GET /v1/devices`
- `GET /v1/devices/{device_id}/latest`
- `GET /v1/devices/{device_id}/series?metric=...&from=...&to=...&limit=...`
