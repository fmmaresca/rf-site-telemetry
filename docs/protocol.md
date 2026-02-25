# Telemetry Protocol

## Envelope v1 (single event)
Fields:
- `v` (int) = 1
- `tenant` (str)
- `device_id` (str)
- `ts` (RFC3339 UTC, `Z`)
- `seq` (int64, monotonic per device)
- `msg_id` (str, recommended `{device_id}:{seq}`)
- `metrics` (object: numeric values)
- `status` (object, optional)

Example:
```json
{
  "v": 1,
  "tenant": "demo",
  "device_id": "rfsite-001",
  "ts": "2026-02-25T10:12:03Z",
  "seq": 1842,
  "msg_id": "rfsite-001:1842",
  "metrics": {
    "temp_c": 31.4,
    "psu_12v": 12.08,
    "psu_5v": 5.02
  },
  "status": {
    "uptime_s": 92311,
    "fw": "edge-agent/0.1.0"
  }
}
