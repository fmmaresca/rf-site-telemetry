
This provides:

- Logical isolation
- Simple query patterns
- Straightforward API authorization

---

## 9. API Design Goals

- Simple and explicit
- Read/write separation
- Stateless
- Environment-driven configuration

The API exposes:

- Ingest endpoint (write path)
- Latest value endpoint
- Time-series endpoint
- Device list endpoint

---

## 10. Simulator

The simulator exists to:

- Generate realistic telemetry
- Produce duplicates
- Produce intermittent outages
- Demonstrate liveness transitions

It models real operational behavior, not just data generation.

---

## 11. Deployment Model

Designed for:

- Single VM deployment
- systemd process supervision
- Reverse proxy TLS termination

This keeps the operational footprint minimal while remaining
production-realistic.

---

## 12. Configuration

All runtime configuration is environment-driven:

- Database DSN
- Authentication mode
- API keys

No secrets are stored in the repository.

---

## 13. Observability

Minimal but sufficient:

- Health endpoint
- Structured logs
- Database as system of record

Metrics systems are intentionally out of scope.

---

## 14. Failure Modes Considered

- Network loss between edge and cloud
- Duplicate delivery
- Out-of-order delivery
- Temporary device silence
- Cloud API restart

All of these are safe and do not require manual intervention.

---

## 15. Future Extensions

Possible evolutions:

- MQTT ingest path
- Downlink channel
- Time-series partitioning
- Per-tenant API keys
- WebSocket live updates

---

## 16. Non-Goals

This project deliberately avoids:

- Vendor-specific cloud services
- Complex orchestration
- Large framework dependencies

The focus is on clarity of the data path and delivery semantics.

---

## 17. Intended Use

This repository is:

- A reference implementation
- A portfolio project
- A discussion artifact for edge-to-cloud architecture

It is not a turnkey product.
