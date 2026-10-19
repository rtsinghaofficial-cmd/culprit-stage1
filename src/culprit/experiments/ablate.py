
from __future__ import annotations

import argparse
import json

from culprit.simulator import generate_fleet
from culprit.detector import detect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--vehicles", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261010)
    parser.add_argument(
        "--scenario",
        choices=["null", "fault", "simpson"],
        default="fault",
    )
    args = parser.parse_args()

    variants = [
        ("full", True, True),
        ("no_stratification", False, True),
        ("no_fdr", True, False),
        ("no_stratification_no_fdr", False, False),
    ]

    results = []

    for name, stratified, fdr in variants:
        emitted = 0
        correct = 0
        false_attributions = 0
        missed_faults = 0
        correct_decisions = 0

        for i in range(args.runs):
            seed = args.seed + i
            frame, truth = generate_fleet(
                args.vehicles, seed, args.scenario
            )
            predictions = detect(
                frame, stratified=stratified, fdr=fdr
            )

            emitted += bool(predictions)

            if truth["true_cause"] is not None:
                is_correct = any(
                    prediction.get("cohort") == truth["true_cause"]
                    for prediction in predictions
                )

                if is_correct:
                    correct += 1
                    correct_decisions += 1
                else:
                    missed_faults += 1
            else:
                if predictions:
                    false_attributions += 1
                else:
                    correct_decisions += 1

        results.append({
            "variant": name,
            "runs": args.runs,
            "scenario": args.scenario,
            "detection_rate": emitted / args.runs,
            "correct_attribution_rate": correct / args.runs,
            "correct_decision_rate": correct_decisions / args.runs,
            "false_attribution_rate": false_attributions / args.runs,
            "miss_rate": missed_faults / args.runs,
        })

    print(json.dumps({
        "seed_start": args.seed,
        "vehicles_per_run": args.vehicles,
        "ablations": results,
        "note": (
            "Synthetic single-window metrics only. "
            "No 24-hour incident-rate claim is made."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
