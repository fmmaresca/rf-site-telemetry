# HTTP Simulator

Generates telemetry for many devices and sends to `/v1/ingest`.

## Run (local)
```bash
python3 tools/simulator/sim_http.py \
  --base-url http://localhost:8000 \
  --api-key dev-key \
  --tenant demo \
  --devices 25 \
  --interval-s 5


/opt/rfsite/venv/bin/python /opt/rfsite/tools/simulator/sim_http.py \
  --base-url https://rfdemo.fmaresca.com/api \
  --api-key <TENANT_WIDE_KEY> \
  --tenant demo \
  --devices 50 \
  --interval-s 5


