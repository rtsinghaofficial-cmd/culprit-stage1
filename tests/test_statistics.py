import pandas as pd
from culprit.statistics import bh_adjust, cmh_test


def test_bh_is_monotonic_in_sorted_p_values():
    adjusted = bh_adjust([0.03, 0.001, 0.02])
    assert len(adjusted) == 3
    assert all(0 <= x <= 1 for x in adjusted)


def test_cmh_detects_clear_stratified_association():
    rows = []
    for model in ["M1", "M2"]:
        for exposed, n, events in [(1, 500, 100), (0, 500, 30)]:
            rows.extend([{"firmware": "A" if exposed else "B", "model": model, "anomaly": 1}] * events)
            rows.extend([{"firmware": "A" if exposed else "B", "model": model, "anomaly": 0}] * (n-events))
    result = cmh_test(pd.DataFrame(rows), "firmware", "model")
    assert result["p_value"] < 0.001
    assert result["rate_ratio"] > 1
