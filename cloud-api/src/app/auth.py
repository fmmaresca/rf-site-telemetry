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

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import db
from .settings import settings


@dataclass(frozen=True)
class Principal:
    tenant: str
    device_id: Optional[str]  # if set, key is scoped to a single device
    is_public_readonly: bool = False


bearer = HTTPBearer(auto_error=False)


def get_principal(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    """
    Auth rules:
    - POST /v1/ingest: always requires Bearer token (handled in route)
    - GET tenant-scoped endpoints:
        - if Bearer token present -> validate normally
        - else allow ONLY if PUBLIC_READONLY_TENANT matches the requested tenant
    """
    if not settings.auth_required:
        return Principal(tenant="demo", device_id=None, is_public_readonly=True)

    # If token is provided, validate it
    if creds is not None and creds.scheme.lower() == "bearer" and creds.credentials:
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
        return Principal(tenant=row["tenant"], device_id=row["device_id"], is_public_readonly=False)

    # No token: allow read-only access ONLY for a configured public tenant
    public_tenant = settings.public_readonly_tenant
    if not public_tenant:
        raise HTTPException(status_code=401, detail="missing bearer token")

    # Tenant is in URL: /v1/tenants/{tenant}/...
    path_params = request.path_params or {}
    requested_tenant = path_params.get("tenant")
    if request.method == "GET" and requested_tenant == public_tenant:
        return Principal(tenant=public_tenant, device_id=None, is_public_readonly=True)

    raise HTTPException(status_code=401, detail="missing bearer token")
def Xget_principal(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
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
