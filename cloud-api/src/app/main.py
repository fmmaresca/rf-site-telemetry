from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from . import db
from .models import IngestResult, TelemetryBatchV1, TelemetryEventV1

app = FastAPI(title="RF Site Telemetry Cloud API", version="0.1.0")


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ingest", response_model=IngestResult, status_code=202)
def ingest(payload: Union[TelemetryEventV1, TelemetryBatchV1]) -> IngestResult:
    # Normalize to list of events
    if isinstance(payload, TelemetryEventV1):
        events: List[TelemetryEventV1] = [payload]
        tenant = payload.tenant
        device_id = payload.device_id
    else:
        events = payload.events
        tenant = payload.tenant
        device_id = payload.device_id

    counts = db.IngestCounts()

    try:
        with db.get_conn() as conn:
            conn.autocommit = False
            db.ensure_tenant_and_device(conn, tenant, device_id)

            accepted = deduped = rejected = 0

            for ev in events:
                # Basic consistency guard: batch tenant/device must match
                if ev.tenant != tenant or ev.device_id != device_id:
                    rejected += 1
                    continue

                ts_utc = ev.ts.astimezone(timezone.utc)
                inserted, was_deduped = db.insert_event_idempotent(
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
                elif was_deduped:
                    deduped += 1
                else:
                    rejected += 1

            conn.commit()
            return IngestResult(accepted=accepted, deduped=deduped, rejected=rejected)

    except Exception as e:
        # Keep it simple in commit #1
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/devices")
def list_devices() -> List[Dict[str, Any]]:
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT tenant, device_id, created_at, last_seen_at
              FROM devices
             ORDER BY tenant, device_id
            """
        )
        return list(cur.fetchall())


@app.get("/v1/devices/{device_id}/latest")
def latest(device_id: str, tenant: str = "demo") -> Dict[str, Any]:
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT tenant, device_id, ts, seq, msg_id, metrics, status
              FROM telemetry
             WHERE tenant = %s AND device_id = %s
             ORDER BY ts DESC
             LIMIT 1
            """,
            (tenant, device_id),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="no data")
        return row


@app.get("/v1/devices/{device_id}/series")
def series(
    device_id: str,
    metric: str,
    tenant: str = "demo",
    from_ts: str | None = None,
    to_ts: str | None = None,
    limit: int = 2000,
) -> List[Dict[str, Any]]:
    # MVP: parse ISO timestamps loosely; default last N points
    where = ["tenant = %s", "device_id = %s", "metrics ? %s"]
    params: List[Any] = [tenant, device_id, metric]

    if from_ts:
        where.append("ts >= %s")
        params.append(from_ts)
    if to_ts:
        where.append("ts <= %s")
        params.append(to_ts)

    q = f"""
        SELECT ts, (metrics->>%s)::double precision AS value
          FROM telemetry
         WHERE {" AND ".join(where)}
         ORDER BY ts ASC
         LIMIT %s
    """
    # metric used twice: for select and for "metrics ?"
    # params already has metric for "metrics ? %s"; add first select metric
    params2 = [metric] + params + [limit]

    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(q, params2)
        rows = cur.fetchall()
        return [{"ts": r["ts"], "value": r["value"]} for r in rows]
