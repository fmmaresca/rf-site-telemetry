from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import db
from .settings import settings


@dataclass(frozen=True)
class Principal:
    tenant: str
    device_id: Optional[str]  # if set, key is scoped to a single device


bearer = HTTPBearer(auto_error=False)


def get_principal(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    if not settings.auth_required:
        # Dev fallback: allow demo tenant, unscoped
        return Principal(tenant="demo", device_id=None)

    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise HTTPException(status_code=401, detail="missing bearer token")

    api_key = creds.credentials

    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT tenant, device_id
              FROM api_keys
             WHERE api_key = %s
               AND revoked_at IS NULL
            """,
            (api_key,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="invalid api key")

    return Principal(tenant=row["tenant"], device_id=row["device_id"])
