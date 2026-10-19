
from __future__ import annotations

import argparse
import json

from culprit.simulator import generate_fleet
from culprit.detector import detect
from culprit.baselines import unadjusted_groupby
from culprit.metrics import attribution_scores


def predicted_labels(incidents: list[dict]) -> list[str]:
    return [
        str(item["cohort"])
        for item in incidents
        if "cohort" in item
    ]


def correct_decision(predictions: list[str], actual: str | None) -> bool:
    if actual is None:
        return len(predictions) == 0

    return actual in predictions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument(
        "--scenario",
        choices=["null", "fault", "simpson"],
        default="fault",
    )
    parser.add_argument("--vehicles", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261010)
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.vehicles < 100:
        parser.error("--vehicles must be at least 100")

    rows = []

    for i in range(args.runs):
        seed = args.seed + i
        frame, truth = generate_fleet(
            n=args.vehicles,
            seed=seed,
            scenario=args.scenario,
        )

        ours = predicted_labels(detect(frame))
        naive = predicted_labels(unadjusted_groupby(frame))
        actual = truth["true_cause"]

        ours_scores = attribution_scores(ours, actual)
        naive_scores = attribution_scores(naive, actual)

        rows.append({
            "seed": seed,
            "scenario": args.scenario,
            "true_cause": actual,
            "culprit_predictions": ours,
            "baseline_predictions": naive,
            "culprit": ours_scores,
            "baseline": naive_scores,
            "culprit_correct_decision": correct_decision(ours, actual),
            "baseline_correct_decision": correct_decision(naive, actual),
        })

    def mean_score(method: str, metric: str) -> float:
        return sum(row[method][metric] for row in rows) / len(rows)

    def rate(key: str) -> float:
        return sum(bool(row[key]) for row in rows) / len(rows)

    def false_attribution_rate(method: str) -> float:
        null_rows = [row for row in rows if row["true_cause"] is None]
        if not null_rows:
            return 0.0

        false_attributions = sum(
            bool(row[f"{method}_predictions"]) for row in null_rows
        )
        return false_attributions / len(null_rows)

    print(json.dumps({
        "scenario": args.scenario,
        "runs": args.runs,
        "vehicles_per_run": args.vehicles,
        "seed_start": args.seed,
        "culprit_mean_precision": mean_score("culprit", "precision"),
        "culprit_mean_recall": mean_score("culprit", "recall"),
        "culprit_mean_f1": mean_score("culprit", "f1"),
        "baseline_mean_precision": mean_score("baseline", "precision"),
        "baseline_mean_recall": mean_score("baseline", "recall"),
        "baseline_mean_f1": mean_score("baseline", "f1"),
        "culprit_correct_decision_rate": rate("culprit_correct_decision"),
        "baseline_correct_decision_rate": rate("baseline_correct_decision"),
        "culprit_no_cause_false_attribution_rate": false_attribution_rate("culprit"),
        "baseline_no_cause_false_attribution_rate": false_attribution_rate("baseline"),
        "runs_detail": rows,
        "warning": (
            "Single-window synthetic evaluation. "
            "Correct-decision rate is not cohort-attribution F1. "
            "Does not establish 24-hour false-incident performance."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
