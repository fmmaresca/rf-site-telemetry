from __future__ import annotations

from datetime import timezone
from typing import Any, Dict, List, Union

from fastapi import Depends, FastAPI, HTTPException

from . import db
from .auth import Principal, get_principal
from .models import IngestResult, TelemetryBatchV1, TelemetryEventV1
from .settings import settings, initialize_settings

# Initialize settings with default config if not already initialized
if settings is None:
    initialize_settings()

app = FastAPI(title="RF Site Telemetry Cloud API", version="0.2.0")


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> Dict[str, str]:
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            cur.fetchone()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db not ready: {e}")


def _enforce_scope(principal: Principal, tenant: str, device_id: str | None = None) -> None:
    if principal.tenant != tenant:
        raise HTTPException(status_code=403, detail="tenant forbidden")
    if principal.device_id is not None and device_id is not None and principal.device_id != device_id:
        raise HTTPException(status_code=403, detail="device forbidden")


@app.post("/v1/ingest", response_model=IngestResult, status_code=202)
def ingest(
    payload: Union[TelemetryEventV1, TelemetryBatchV1],
    principal: Principal = Depends(get_principal),
) -> IngestResult:
    # Normalize to list of events
    if isinstance(payload, TelemetryEventV1):
        events = [payload]
        tenant = payload.tenant
        device_id = payload.device_id
    else:
        events = payload.events
        tenant = payload.tenant
        device_id = payload.device_id

    _enforce_scope(principal, tenant, device_id)

    accepted = deduped = rejected = 0

    try:
        with db.get_conn() as conn:
            conn.autocommit = False
            db.ensure_tenant_and_device(conn, tenant, device_id)

            for ev in events:
                # Batch consistency guard
                if ev.tenant != tenant or ev.device_id != device_id:
                    rejected += 1
                    continue

                ts_utc = ev.ts.astimezone(timezone.utc)

                inserted = db.insert_event_idempotent(
                    conn=conn,
                    tenant=tenant,
                    device_id=device_id,
                    ts_utc=ts_utc,
                    seq=ev.seq,
                    msg_id=ev.msg_id,
                    metrics=ev.metrics,
                    status=ev.status,
                )
                if inserted:
                    accepted += 1
                    db.upsert_last_seen(conn, tenant, device_id, ts_utc)
                else:
                    deduped += 1

            conn.commit()

        return IngestResult(accepted=accepted, deduped=deduped, rejected=rejected)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/tenants/{tenant}/devices")
def list_devices(
    tenant: str,
    principal: Principal = Depends(get_principal),
) -> List[Dict[str, Any]]:
    _enforce_scope(principal, tenant)
    with db.get_conn() as conn:
        return db.list_devices(conn, tenant)


@app.get("/v1/tenants/{tenant}/devices/{device_id}/latest")
def latest(
    tenant: str,
    device_id: str,
    principal: Principal = Depends(get_principal),
) -> Dict[str, Any]:
    _enforce_scope(principal, tenant, device_id)
    with db.get_conn() as conn:
        row = db.get_latest(conn, tenant, device_id)
        if not row:
            raise HTTPException(status_code=404, detail="no data")
        return row


@app.get("/v1/tenants/{tenant}/devices/{device_id}/series")
def series(
    tenant: str,
    device_id: str,
    metric: str,
    from_ts: str | None = None,
    to_ts: str | None = None,
    limit: int = 2000,
    principal: Principal = Depends(get_principal),
) -> List[Dict[str, Any]]:
    _enforce_scope(principal, tenant, device_id)
    limit = max(1, min(limit, 10000))
    with db.get_conn() as conn:
        return db.get_series(conn, tenant, device_id, metric, from_ts, to_ts, limit)
