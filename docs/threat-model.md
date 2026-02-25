# Threat Model (stub)

Assets:
- Device identity (tenant/device_id)
- API keys
- Telemetry integrity

Threats (high level):
- Replay / duplicates
- Forged device identity
- Data tampering in transit

Mitigations (planned):
- HTTPS, API key, rate limiting
- Idempotency keys + collision detection
- Optional payload signatures
