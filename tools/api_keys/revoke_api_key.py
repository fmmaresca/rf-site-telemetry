#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psycopg


DEFAULT_ENV_FILE = "/etc/rfsite-cloud-api/env"


def load_env_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def resolve_db_dsn(db_dsn: Optional[str], env_file: str) -> str:
    if db_dsn:
        return db_dsn
    load_env_file(env_file)
    dsn = os.getenv("DB_DSN")
    if not dsn:
        raise SystemExit("DB_DSN not set (use --db-dsn or set DB_DSN or provide --env-file)")
    return dsn


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("api_key")
    ap.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    ap.add_argument("--db-dsn", default=None)
    args = ap.parse_args()

    dsn = resolve_db_dsn(args.db_dsn, args.env_file)
    now = datetime.now(timezone.utc)

    with psycopg.connect(dsn) as conn:
        cur = conn.execute(
            """
            UPDATE api_keys
               SET revoked_at = %s
             WHERE api_key = %s
               AND revoked_at IS NULL
            RETURNING tenant, device_id
            """,
            (now, args.api_key),
        )
        row = cur.fetchone()
        conn.commit()

    if not row:
        print("No active key found (already revoked or missing).")
        raise SystemExit(2)

    print(f"Revoked key for tenant={row[0]} device={row[1]}")


if __name__ == "__main__":
    main()
