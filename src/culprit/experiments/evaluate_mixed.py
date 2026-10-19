
from __future__ import annotations

import argparse
import json

from culprit.baselines import unadjusted_groupby
from culprit.detector import detect
from culprit.metrics import attribution_scores
from culprit.simulator import generate_fleet


SCENARIO_MIX = {
    "fault": 1,
    "simpson": 1,
    "null": 1,
}


def predicted_labels(incidents: list[dict]) -> list[str]:
    return [
        str(item["cohort"])
        for item in incidents
        if "cohort" in item
    ]


def aggregate_counts(rows: list[dict], method: str) -> dict:
    tp = sum(row[method]["true_positives"] for row in rows)
    fp = sum(row[method]["false_positives"] for row in rows)
    fn = sum(row[method]["false_negatives"] for row in rows)

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-per-scenario", type=int, default=30)
    parser.add_argument("--vehicles", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261010)
    args = parser.parse_args()

    if args.runs_per_scenario < 1:
        parser.error("--runs-per-scenario must be at least 1")
    if args.vehicles < 100:
        parser.error("--vehicles must be at least 100")

    rows = []
    scenario_counts = {}

    for scenario_index, scenario in enumerate(SCENARIO_MIX):
        scenario_counts[scenario] = args.runs_per_scenario

        for run_index in range(args.runs_per_scenario):
            seed = (
                args.seed
                + scenario_index * args.runs_per_scenario
                + run_index
            )

            frame, truth = generate_fleet(
                n=args.vehicles,
                seed=seed,
                scenario=scenario,
            )

            ours = predicted_labels(detect(frame))
            baseline = predicted_labels(unadjusted_groupby(frame))
            actual = truth["true_cause"]

            rows.append({
                "scenario": scenario,
                "seed": seed,
                "true_cause": actual,
                "culprit_predictions": ours,
                "baseline_predictions": baseline,
                "culprit": attribution_scores(ours, actual),
                "baseline": attribution_scores(baseline, actual),
            })

    culprit_scores = aggregate_counts(rows, "culprit")
    baseline_scores = aggregate_counts(rows, "baseline")

    def false_attribution_rate(method: str) -> float:
        no_cause_rows = [
            row for row in rows if row["true_cause"] is None
        ]
        if not no_cause_rows:
            return 0.0
        false_alarms = sum(
            bool(row[f"{method}_predictions"])
            for row in no_cause_rows
        )
        return false_alarms / len(no_cause_rows)

    print(json.dumps({
        "benchmark": "mixed_synthetic_cohort_attribution",
        "runs_per_scenario": args.runs_per_scenario,
        "scenario_counts": scenario_counts,
        "vehicles_per_run": args.vehicles,
        "seed_start": args.seed,
        "culprit_aggregate": culprit_scores,
        "baseline_aggregate": baseline_scores,
        "f1_improvement_over_baseline": (
            culprit_scores["f1"] - baseline_scores["f1"]
        ),
        "culprit_no_cause_false_attribution_rate": (
            false_attribution_rate("culprit")
        ),
        "baseline_no_cause_false_attribution_rate": (
            false_attribution_rate("baseline")
        ),
        "runs_detail": rows,
        "warning": (
            "Synthetic benchmark with equal numbers of fault, Simpson, "
            "and null runs. Aggregate cohort-attribution F1 is reported. "
            "This does not evaluate the per-vehicle baseline and does "
            "not establish real-world performance."
        ),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
