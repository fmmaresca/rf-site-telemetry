from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Tuple

import psycopg
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
) -> Tuple[bool, bool]:
    """
    Returns (inserted, deduped).
    Deduped means primary key (tenant, device_id, seq) already existed.
    """
    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO telemetry(tenant, device_id, ts, seq, msg_id, metrics, status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                """,
                (tenant, device_id, ts_utc, seq, msg_id, json.dumps(metrics), json.dumps(status)),
            )
            return True, False
        except psycopg.errors.UniqueViolation:
            conn.rollback()
            return False, True
