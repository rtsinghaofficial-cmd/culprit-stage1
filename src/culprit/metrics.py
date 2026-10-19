
"""Ground-truth-aware evaluation helpers."""
from __future__ import annotations


def binary_f1(predicted: bool, actual: bool) -> float:
    """F1 for one scenario-level cause-present/cause-absent decision."""
    tp = int(predicted and actual)
    fp = int(predicted and not actual)
    fn = int(not predicted and actual)
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom else 1.0


def incident_counts(incidents: list[dict]) -> dict:
    return {"incident_count": len(incidents)}


def attribution_scores(predicted: list[str], actual: str | None) -> dict:
    """Score exact cohort labels for a single simulated window.

    A correct cause is one exact cohort label, e.g. 'firmware=A'.
    A null scenario has no expected label.
    """
    predicted_set = set(predicted)
    actual_set = {actual} if actual is not None else set()

    tp = len(predicted_set & actual_set)
    fp = len(predicted_set - actual_set)
    fn = len(actual_set - predicted_set)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    denom = 2 * tp + fp + fn
    f1 = 2 * tp / denom if denom else 0.0   
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
