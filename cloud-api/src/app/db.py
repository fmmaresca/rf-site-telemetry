from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import psycopg:
from psycopg.rows import dict_row

from .settings import settings


@dataclass(frozen=True)
class IngestCounts:
    accepted: int = 0
    deduped: int = 0
    rejected: int = 0


def get_conn() -> psycopg.Connection:
    return psycopg.connect(settings.db_dsn, row_factory=dict_row)


def ensure_tenant_and_device(conn: psycopg.Connection, tenant: str, device_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tenants(tenant) VALUES (%s) ON CONFLICT DO NOTHING",
            (tenant,),
        )
        cur.execute(
            """
            INSERT INTO devices(tenant, device_id) VALUES (%s, %s)
            ON CONFLICT (tenant, device_id) DO NOTHING
            """,
            (tenant, device_id),
        )


def upsert_last_seen(conn: psycopg.Connection, tenant: str, device_id: str, ts_utc) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE devices
               SET last_seen_at = GREATEST(COALESCE(last_seen_at, %s), %s)
             WHERE tenant = %s AND device_id = %s
            """,
            (ts_utc, ts_utc, tenant, device_id),
        )


def insert_event_idempotent(
    conn: psycopg.Connection,
    tenant: str,
    device_id: str,
    ts_utc,
    seq: int,
    msg_id: str,
    metrics: dict[str, Any],
    status: dict[str, Any],
) -> bool:
    """
    Returns True if inserted, False if deduped (already existed).
    Uses ON CONFLICT DO NOTHING to avoid exceptions / rollbacks.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO telemetry(tenant, device_id, ts, seq, msg_id, metrics, status)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            ON CONFLICT (tenant, device_id, seq) DO NOTHING
            RETURNING 1
            """,
            (tenant, device_id, ts_utc, seq, msg_id, json.dumps(metrics), json.dumps(status)),
        )
        row = cur.fetchone()
        return row is not None


def list_devices(conn: psycopg.Connection, tenant: str) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tenant, device_id, created_at, last_seen_at
              FROM devices
             WHERE tenant = %s
             ORDER BY device_id
            """,
            (tenant,),
        )
        return list(cur.fetchall())


def get_latest(conn: psycopg.Connection, tenant: str, device_id: str) -> Optional[dict[str, Any]]:
    with conn.cursor() as cur:
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
        return cur.fetchone()


def get_series(
    conn: psycopg.Connection,
    tenant: str,
    device_id: str,
    metric: str,
    from_ts: Optional[str],
    to_ts: Optional[str],
    limit: int,
) -> list[dict[str, Any]]:
    where = ["tenant = %s", "device_id = %s", "metrics ? %s"]
    params: list[Any] = [tenant, device_id, metric]

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
    params2 = [metric] + params + [limit]

    with conn.cursor() as cur:
        cur.execute(q, params2)
        rows = cur.fetchall()
        return [{"ts": r["ts"], "value": r["value"]} for r in rows]
