#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests


@dataclass
class DeviceState:
    tenant: str
    device_id: str
    seq: int
    t0: float
    v12_base: float = 12.0
    v5_base: float = 5.0
    temp_base: float = 30.0


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def gen_metrics(ds: DeviceState) -> Dict[str, float]:
    t = time.time() - ds.t0
    # simple "physical-ish" signals
    temp = ds.temp_base + 3.0 * (random.random() - 0.5) + 2.0 * (0.5 - 0.5 * (1.0 + random.random())) + 2.0 * (0.0)
    temp += 2.0 * (0.0)  # placeholder for later: diurnal/long wave
    temp += 1.5 * (random.random() - 0.5)

    v12 = ds.v12_base + 0.08 * (random.random() - 0.5) + 0.05 * (random.random() - 0.5)
    v5 = ds.v5_base + 0.03 * (random.random() - 0.5) + 0.02 * (random.random() - 0.5)

    # occasional droops / spikes
    if random.random() < 0.01:
        v12 -= random.uniform(0.2, 0.7)
    if random.random() < 0.01:
        temp += random.uniform(3.0, 8.0)

    return {
        "temp_c": round(float(temp), 2),
        "psu_12v": round(float(v12), 3),
        "psu_5v": round(float(v5), 3),
    }


def build_event(ds: DeviceState) -> Dict:
    ds.seq += 1
    msg_id = f"{ds.device_id}:{ds.seq}"
    return {
        "v": 1,
        "tenant": ds.tenant,
        "device_id": ds.device_id,
        "ts": now_utc_iso(),
        "seq": ds.seq,
        "msg_id": msg_id,
        "metrics": gen_metrics(ds),
        "status": {
            "fw": "simulator/0.1.0",
            "uptime_s": int(time.time() - ds.t0),
        },
    }


def post_event(base_url: str, api_key: str, ev: Dict, timeout_s: float) -> Tuple[bool, int, str]:
    url = base_url.rstrip("/") + "/v1/ingest"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(url, headers=headers, json=ev, timeout=timeout_s)
        return r.ok, r.status_code, r.text[:200]
    except Exception as e:
        return False, 0, str(e)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="e.g. https://rfdemo.fmaresca.com/api")
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--tenant", default="demo")
    ap.add_argument("--devices", type=int, default=10)
    ap.add_argument("--interval-s", type=float, default=5.0, help="per-device sample interval")
    ap.add_argument("--jitter-s", type=float, default=0.5)
    ap.add_argument("--timeout-s", type=float, default=5.0)
    ap.add_argument("--duplicate-rate", type=float, default=0.02, help="send duplicate of a prior seq with this probability")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    base = args.base_url.rstrip("/")
    states: List[DeviceState] = []
    for i in range(args.devices):
        device_id = f"rfsite-{i+1:03d}"
        states.append(DeviceState(tenant=args.tenant, device_id=device_id, seq=0, t0=time.time()))

    print(f"Simulator running: tenant={args.tenant} devices={args.devices} -> {base}/v1/ingest")

    # simple scheduler: round-robin devices
    idx = 0
    while True:
        ds = states[idx]
        idx = (idx + 1) % len(states)

        ev = build_event(ds)

        ok, status, detail = post_event(base, args.api_key, ev, args.timeout_s)
        if not ok:
            print(f"[ERR] {ds.device_id} seq={ev['seq']} status={status} detail={detail}")
        else:
            # optional duplicates to test idempotency
            if args.duplicate_rate > 0 and random.random() < args.duplicate_rate:
                ok2, status2, detail2 = post_event(base, args.api_key, ev, args.timeout_s)
                if not ok2:
                    print(f"[DUP-ERR] {ds.device_id} seq={ev['seq']} status={status2} detail={detail2}")

        # pacing: since we're round-robin, divide interval by number of devices
        target_sleep = max(0.01, (args.interval_s / max(1, args.devices)) + random.uniform(-args.jitter_s, args.jitter_s) / max(1, args.devices))
        time.sleep(target_sleep)


if __name__ == "__main__":
    main()
