from __future__ import annotations

import requests

from .envelope import TelemetryEventV1


class HttpIngestClient:
    def __init__(self, base_url: str, api_key: str, timeout_s: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def ingest(self, ev: TelemetryEventV1) -> None:
        url = f"{self.base_url}/v1/ingest"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        r = requests.post(url, headers=headers, data=ev.model_dump_json(), timeout=self.timeout_s)
        r.raise_for_status()
