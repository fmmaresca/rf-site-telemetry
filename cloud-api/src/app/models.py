from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TelemetryEventV1(BaseModel):
    v: int = Field(1, ge=1, le=1)
    tenant: str = Field(min_length=1, max_length=64)
    device_id: str = Field(min_length=1, max_length=128)
    ts: datetime
    seq: int = Field(ge=0)
    msg_id: str = Field(min_length=1, max_length=256)
    metrics: Dict[str, float]
    status: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("ts")
    @classmethod
    def ts_must_be_utc(cls, v: datetime) -> datetime:
        # Normalize: require timezone-aware; convert to UTC
        if v.tzinfo is None:
            raise ValueError("ts must be timezone-aware (UTC)")
        return v.astimezone(timezone.utc)

    @field_validator("metrics")
    @classmethod
    def metrics_numeric(cls, v: Dict[str, float]) -> Dict[str, float]:
        # pydantic will coerce ints to floats; ensure non-empty
        if not v:
            raise ValueError("metrics must not be empty")
        return v


class TelemetryBatchV1(BaseModel):
    v: int = Field(1, ge=1, le=1)
    tenant: str = Field(min_length=1, max_length=64)
    device_id: str = Field(min_length=1, max_length=128)
    events: List[TelemetryEventV1]

    @field_validator("events")
    @classmethod
    def events_non_empty(cls, v: List[TelemetryEventV1]) -> List[TelemetryEventV1]:
        if not v:
            raise ValueError("events must not be empty")
        return v


class IngestResult(BaseModel):
    accepted: int
    deduped: int
    rejected: int
