#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
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
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    ap.add_argument("--db-dsn", default=None)
    ap.add_argument("--all", action="store_true", help="Include revoked keys")
    args = ap.parse_args()

    dsn = resolve_db_dsn(args.db_dsn, args.env_file)

    where = "tenant = %s"
    if not args.all:
        where += " AND revoked_at IS NULL"

    with psycopg.connect(dsn) as conn:
        cur = conn.execute(
            f"""
            SELECT api_key, tenant, device_id, created_at, revoked_at
              FROM api_keys
             WHERE {where}
             ORDER BY created_at DESC
            """,
            (args.tenant,),
        )
        rows = cur.fetchall()

    for r in rows:
        print(f"{r[0]}  tenant={r[1]}  device={r[2]}  created={r[3]}  revoked={r[4]}")


if __name__ == "__main__":
    main()
