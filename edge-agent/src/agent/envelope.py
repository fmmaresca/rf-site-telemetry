from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field


class TelemetryEventV1(BaseModel):
    v: int = Field(1)
    tenant: str
    device_id: str
    ts: datetime
    seq: int = Field(ge=0)
    msg_id: str
    metrics: Dict[str, float]
    status: Dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
