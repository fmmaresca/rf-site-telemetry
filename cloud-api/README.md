# cloud-api

FastAPI service providing ingest and query endpoints.

## Run locally

```bash
cd cloud-api
python -m venv .venv && . .venv/bin/activate
pip install -e .

export DB_DSN='postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry'
export AUTH_REQUIRED=0

uvicorn app.main:app --reload --port 8000
```

## OpenAPI

See `openapi.yaml`.
