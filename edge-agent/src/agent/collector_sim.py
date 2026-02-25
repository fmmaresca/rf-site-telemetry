from __future__ import annotations

import math
import random
import time
from typing import Dict


class SimulatedCollector:
    def __init__(self) -> None:
        self.t0 = time.time()

    def read_metrics(self) -> Dict[str, float]:
        t = time.time() - self.t0
        temp = 30.0 + 3.0 * math.sin(t / 60.0) + random.uniform(-0.2, 0.2)
        v12 = 12.0 + 0.08 * math.sin(t / 15.0) + random.uniform(-0.02, 0.02)
        v5 = 5.0 + 0.03 * math.sin(t / 20.0) + random.uniform(-0.01, 0.01)
        return {"temp_c": float(temp), "psu_12v": float(v12), "psu_5v": float(v5)}
