from __future__ import annotations

import argparse
import json
import time

from culprit.baselines import unadjusted_groupby, per_vehicle_threshold
from culprit.detector import detect
from culprit.metrics import attribution_scores
from culprit.simulator import generate_fleet


SCENARIOS = ("fault", "simpson", "null")


def summarize(rows: list[dict], method: str) -> dict:
    tp = sum(row[method]["true_positives"] for row in rows)
    fp = sum(row[method]["false_positives"] for row in rows)
    fn = sum(row[method]["false_negatives"] for row in rows)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0

    no_cause = [row for row in rows if row["true_cause"] is None]
    false_attributions = sum(
        bool(row["culprit_predictions" if method == "culprit" else "baseline_predictions"]) for row in no_cause
    )

    return {
        "runs": len(rows),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "no_cause_false_attribution_rate": (
            false_attributions / len(no_cause) if no_cause else None
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fair cohort-level comparison on synthetic fleet scenarios."
    )
    parser.add_argument("--runs-per-scenario", type=int, default=30)
    parser.add_argument("--vehicles", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20300000)
    args = parser.parse_args()

    if args.runs_per_scenario < 1:
        parser.error("--runs-per-scenario must be at least 1")
    if args.vehicles < 100:
        parser.error("--vehicles must be at least 100")

    rows = []
    next_seed = args.seed

    for scenario in SCENARIOS:
        for _ in range(args.runs_per_scenario):
            seed = next_seed
            next_seed += 1

            frame, truth = generate_fleet(
                n=args.vehicles,
                seed=seed,
                scenario=scenario,
            )

            start = time.perf_counter()
            culprit_predictions = [
                item["cohort"] for item in detect(frame)
            ]
            culprit_seconds = time.perf_counter() - start

            start = time.perf_counter()
            baseline_predictions = [
                item["cohort"] for item in unadjusted_groupby(frame)
            ]
            baseline_seconds = time.perf_counter() - start

            start = time.perf_counter()
            vehicle_alerts = per_vehicle_threshold(frame)
            vehicle_seconds = time.perf_counter() - start

            actual = truth["true_cause"]

            rows.append({
                "scenario": scenario,
                "seed": seed,
                "true_cause": actual,
                "culprit_predictions": culprit_predictions,
                "baseline_predictions": baseline_predictions,
                "culprit": attribution_scores(culprit_predictions, actual),
                "unadjusted_baseline": attribution_scores(
                    baseline_predictions, actual
                ),
                "vehicle_alert_count": len(vehicle_alerts),
                "vehicle_alert_rate": len(vehicle_alerts) / args.vehicles,
                "runtime_seconds": {
                    "culprit": culprit_seconds,
                    "unadjusted_baseline": baseline_seconds,
                    "per_vehicle_threshold": vehicle_seconds,
                },
            })

    output = {
        "benchmark": "fair_synthetic_cohort_evaluation",
        "vehicles_per_run": args.vehicles,
        "runs_per_scenario": args.runs_per_scenario,
        "seed_start": args.seed,
        "methods": {
            "culprit": "Stratified CMH cohort detector",
            "unadjusted_baseline": "Unadjusted cohort association",
            "per_vehicle_threshold": (
                "Individual anomaly alerts; descriptive metrics only"
            ),
        },
        "thresholds": {
            "culprit_q": 0.01,
            "minimum_lift": 1.5,
            "minimum_flagged": 5,
        },
        "scenario_results": {},
        "runtime_mean_seconds": {},
        "warning": (
            "Synthetic data only. Cohort-level metrics compare Culprit "
            "and the unadjusted cohort baseline. Per-vehicle alerts are "
            "reported descriptively, not as comparable cohort F1. "
            "Thresholds are fixed, not calibrated on these runs."
        ),
    }

    for scenario in SCENARIOS:
        subset = [row for row in rows if row["scenario"] == scenario]
        output["scenario_results"][scenario] = {
            "culprit": summarize(subset, "culprit"),
            "unadjusted_baseline": summarize(
                subset, "unadjusted_baseline"
            ),
            "mean_vehicle_alert_count": (
                sum(row["vehicle_alert_count"] for row in subset)
                / len(subset)
            ),
            "mean_vehicle_alert_rate": (
                sum(row["vehicle_alert_rate"] for row in subset)
                / len(subset)
            ),
        }

    for method in (
        "culprit",
        "unadjusted_baseline",
        "per_vehicle_threshold",
    ):
        output["runtime_mean_seconds"][method] = (
            sum(row["runtime_seconds"][method] for row in rows)
            / len(rows)
        )

    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

