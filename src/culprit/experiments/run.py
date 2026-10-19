from __future__ import annotations
import argparse, json
from culprit.simulator import generate_fleet
from culprit.detector import detect
from culprit.baselines import unadjusted_groupby, per_vehicle_threshold


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=["null", "fault", "simpson"], default="simpson")
    p.add_argument("--seed", type=int, default=20261010)
    p.add_argument("--vehicles", type=int, default=5000)
    args = p.parse_args()
    frame, truth = generate_fleet(args.vehicles, args.seed, args.scenario)
    # Truth is only read after detector outputs have been computed.
    culprit = detect(frame)
    naive = unadjusted_groupby(frame)
    threshold = per_vehicle_threshold(frame)
    output = {
        "truth": truth,
        "culprit": culprit,
        "unadjusted_groupby": naive,
        "per_vehicle_threshold_alert_count": len(threshold),
        "note": "Synthetic single-window result; not a production benchmark."
    }
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
