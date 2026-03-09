#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path
from typing import Optional

import psycopg


DEFAULT_CONFIG_FILE = "/etc/rfsite-cloud-api/config.yaml"


def load_config_file(path: str) -> dict:
    """Load configuration from YAML file"""
    import yaml
    
    p = Path(path)
    if not p.exists():
        return {}
    
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load config file {path}: {e}")
        return {}


def resolve_db_dsn(db_dsn: Optional[str], config_file: str) -> str:
    if db_dsn:
        return db_dsn
    
    config = load_config_file(config_file)
    dsn = config.get("db_dsn")
    if not dsn:
        raise SystemExit("db_dsn not found (use --db-dsn or set db_dsn in config file)")
    return dsn


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--device", default=None, help="Optional device_id scope")
    ap.add_argument("--config", default=DEFAULT_CONFIG_FILE, help="Path to config file")
    ap.add_argument("--db-dsn", default=None)
    ap.add_argument("--key", default=None, help="Provide a key instead of generating one")
    args = ap.parse_args()

    dsn = resolve_db_dsn(args.db_dsn, args.config)
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
