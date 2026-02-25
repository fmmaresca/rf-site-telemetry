# cloud-api

Run locally:
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
