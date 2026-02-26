from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Optional

import yaml


Transport = Literal["http"]


@dataclass
class HttpConfig:
    base_url: str
    api_key: str
    timeout_s: float = 5.0


@dataclass
class AgentConfig:
    tenant: str
    device_id: str
    transport: Transport
    sample_interval_s: float
    http: HttpConfig


def load_config(path: str) -> AgentConfig:
    data: Dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    http = data["http"]
    return AgentConfig(
        tenant=data["tenant"],
        device_id=data["device_id"],
        transport=data.get("transport", "http"),
        sample_interval_s=float(data.get("sample_interval_s", 5)),
        http=HttpConfig(
            base_url=http["base_url"].rstrip("/"),
            api_key=http["api_key"],
            timeout_s=float(http.get("timeout_s", 5.0)),
        ),
    )
