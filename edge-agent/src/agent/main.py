from __future__ import annotations

import argparse
import time

from .collector_sim import SimulatedCollector
from .config import load_config
from .envelope import TelemetryEventV1
from .http_client import HttpIngestClient


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    collector = SimulatedCollector()
    client = HttpIngestClient(cfg.http.base_url, cfg.http.api_key, cfg.http.timeout_s)

    seq = 0
    while True:
        seq += 1
        ev = TelemetryEventV1(
            tenant=cfg.tenant,
            device_id=cfg.device_id,
            ts=TelemetryEventV1.now_utc(),
            seq=seq,
            msg_id=f"{cfg.device_id}:{seq}",
            metrics=collector.read_metrics(),
            status={"fw": "edge-agent/0.1.0"},
        )
        client.ingest(ev)
        time.sleep(cfg.sample_interval_s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/telemetry.example.yaml")
    args = ap.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
