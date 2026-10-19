"""Simple comparison baselines for the Stage 1 experiment."""
from __future__ import annotations
import pandas as pd
from .statistics import unadjusted_test


def unadjusted_groupby(frame: pd.DataFrame, q: float = 0.01, min_lift: float = 1.5) -> list[dict]:
    r = unadjusted_test(frame, "firmware")
    if r["rate_ratio"] is None or r["rate_ratio"] < min_lift or r["p_value"] > q:
        return []
    return [{"cohort": "firmware=A", **r}]


def per_vehicle_threshold(frame: pd.DataFrame) -> list[dict]:
    """A deliberately simple baseline: each anomalous vehicle emits its own alert."""
    rows = frame[frame["anomaly"] == 1]
    return [{"cohort": f"vehicle:{v}", "vehicle_id": v} for v in rows["vehicle_id"]]
