#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import secrets
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
    ap.add_argument("--device", default=None, help="Optional device_id scope")
    ap.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    ap.add_argument("--db-dsn", default=None)
    ap.add_argument("--key", default=None, help="Provide a key instead of generating one")
    args = ap.parse_args()

    dsn = resolve_db_dsn(args.db_dsn, args.env_file)
    api_key = args.key or secrets.token_urlsafe(32)

    with psycopg.connect(dsn) as conn:
        conn.execute("INSERT INTO tenants(tenant) VALUES (%s) ON CONFLICT DO NOTHING", (args.tenant,))
        conn.execute(
            """
            INSERT INTO api_keys(api_key, tenant, device_id)
            VALUES (%s, %s, %s)
            """,
            (api_key, args.tenant, args.device),
        )
        conn.commit()

    scope = f"tenant={args.tenant}" + (f" device={args.device}" if args.device else " (tenant-wide)")
    print(api_key)
    print(f"Created API key: {scope}")


if __name__ == "__main__":
    main()
