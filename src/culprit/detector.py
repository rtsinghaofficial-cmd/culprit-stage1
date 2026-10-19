"""Candidate cohort scoring and FDR-controlled incident selection."""
from __future__ import annotations
import pandas as pd
from .statistics import bh_adjust, cmh_test, unadjusted_test


def detect(frame: pd.DataFrame, stratified: bool = True, fdr: bool = True,
           q: float = 0.01, min_flagged: int = 5, min_lift: float = 1.5) -> list[dict]:
    """Test firmware A as a candidate cohort. One row = one vehicle/window."""
    flagged = frame.groupby("firmware")["anomaly"].sum()
    if int(flagged.get("A", 0)) < min_flagged:
        return []
    result = (cmh_test(frame, "firmware", "model") if stratified
              else unadjusted_test(frame, "firmware"))
    if result["rate_ratio"] is None or result["rate_ratio"] < min_lift:
        return []
    adjusted = bh_adjust([result["p_value"]])[0] if fdr else result["p_value"]
    if adjusted > q:
        return []
    return [{
        "cohort": "firmware=A",
        **result,
        "q_value": adjusted,
        "flagged_exposed": int(flagged.get("A", 0)),
        "vehicles_exposed": int((frame["firmware"] == "A").sum()),
    }]
