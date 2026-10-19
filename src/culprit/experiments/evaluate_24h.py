
from __future__ import annotations

import argparse
import json

from culprit.simulator import generate_fleet
from culprit.detector import detect


def evaluate_day(
    seed: int,
    vehicles: int = 5000,
    hours: int = 24,
) -> dict:
    """Evaluate false cohort attributions across synthetic null windows."""
    false_incidents = 0
    hourly_results = []

    for hour in range(hours):
        window_seed = seed + hour
        frame, truth = generate_fleet(
            n=vehicles,
            seed=window_seed,
            scenario="null",
        )

        predictions = detect(frame)
        false_attribution = (
            truth["true_cause"] is None and bool(predictions)
        )

        if false_attribution:
            false_incidents += 1

        hourly_results.append({
            "hour": hour,
            "seed": window_seed,
            "false_attribution": false_attribution,
            "predictions": [
                item.get("cohort")
                for item in predictions
            ],
        })

    return {
        "day_seed": seed,
        "hours": hours,
        "vehicles_per_window": vehicles,
        "false_incidents": false_incidents,
        "within_one_false_incident": false_incidents <= 1,
        "hourly_results": hourly_results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--vehicles", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261010)
    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days must be at least 1")
    if args.vehicles < 100:
        parser.error("--vehicles must be at least 100")

    days = [
        evaluate_day(
            seed=args.seed + day * 24,
            vehicles=args.vehicles,
        )
        for day in range(args.days)
    ]

    total_incidents = sum(day["false_incidents"] for day in days)
    days_over_limit = sum(
        day["false_incidents"] > 1 for day in days
    )

    print(json.dumps({
        "scenario": "null",
        "days_simulated": args.days,
        "hours_per_day": 24,
        "vehicles_per_window": args.vehicles,
        "seed_start": args.seed,
        "total_false_incidents": total_incidents,
        "mean_false_incidents_per_day": total_incidents / args.days,
        "days_with_at_most_one_false_incident": (
            args.days - days_over_limit
        ),
        "days_over_one_false_incident": days_over_limit,
        "fraction_of_days_over_limit": days_over_limit / args.days,
        "days": days,
        "warning": (
            "Synthetic independent snapshots, not persistent telemetry. "
            "Results do not establish real-world 24-hour reliability."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
