"""Stratified CMH and effect-size calculations for binary vehicle flags."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import StratifiedTable


def bh_adjust(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values, preserving input order."""
    p = np.asarray(p_values, dtype=float)
    if p.size == 0:
        return []
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be finite and in [0, 1]")
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty_like(ranked)
    adjusted[order] = np.minimum(ranked, 1.0)
    return adjusted.tolist()


def _tables(frame: pd.DataFrame, cohort_col: str, strata_col: str) -> list[np.ndarray]:
    tables = []
    for _, group in frame.groupby(strata_col, observed=True):
        # rows = exposed/unexposed, cols = anomalous/not anomalous
        exp = group[group[cohort_col] == 1]["anomaly"]
        unexp = group[group[cohort_col] == 0]["anomaly"]
        if len(exp) == 0 or len(unexp) == 0:
            continue
        tables.append(np.array([
            [int(exp.sum()), int(len(exp) - exp.sum())],
            [int(unexp.sum()), int(len(unexp) - unexp.sum())],
        ], dtype=float))
    return tables



def cmh_test(frame: pd.DataFrame, cohort_col: str, strata_col: str = "model") -> dict:
    """CMH association test with a pooled stratified risk ratio."""
    data = frame.copy()
    values = data[cohort_col]

    if values.dtype == object or pd.api.types.is_string_dtype(values.dtype):
        data["_exposed"] = (values == "A").astype(int)
    else:
        data["_exposed"] = values.astype(int)

    tables = _tables(data, "_exposed", strata_col)

    if not tables:
        return {
            "p_value": 1.0,
            "rate_ratio": None,
            "ci_low": None,
            "ci_high": None,
            "strata_used": 0,
        }

    try:
        st = StratifiedTable(tables)
        p_value = float(st.test_null_odds().pvalue)
        rr = float(st.riskratio_pooled)

        if not np.isfinite(rr) or rr <= 0:
            rr = None

        return {
            "p_value": p_value,
            "rate_ratio": rr,
            "ci_low": None,
            "ci_high": None,
            "strata_used": len(tables),
        }
    except (ValueError, ZeroDivisionError, FloatingPointError):
        return {
            "p_value": 1.0,
            "rate_ratio": None,
            "ci_low": None,
            "ci_high": None,
            "strata_used": len(tables),
        }


def unadjusted_test(frame: pd.DataFrame, cohort_col: str) -> dict:
    exposed = frame[frame[cohort_col] == "A"]["anomaly"]
    control = frame[frame[cohort_col] != "A"]["anomaly"]
    if exposed.empty or control.empty:
        return {"p_value": 1.0, "rate_ratio": None}
    table = np.array([
        [int(exposed.sum()), int(len(exposed) - exposed.sum())],
        [int(control.sum()), int(len(control) - control.sum())],
    ])
    _, p, _, _ = chi2_contingency(table, correction=False)
    er, cr = exposed.mean(), control.mean()
    return {"p_value": float(p), "rate_ratio": float(er / cr) if cr > 0 else None}
