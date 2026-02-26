# edge-agent

Python edge agent scaffold.

## Run locally

```bash
cd edge-agent
python -m venv .venv && . .venv/bin/activate
pip install -e .

python -m agent.main --config config/telemetry.example.yaml
```
