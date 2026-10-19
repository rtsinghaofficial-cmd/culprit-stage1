"""Deterministic synthetic fleet scenarios; ground truth is returned separately."""
from __future__ import annotations
import numpy as np
import pandas as pd


def generate_fleet(n: int = 5000, seed: int = 20261010, scenario: str = "fault") -> tuple[pd.DataFrame, dict]:
    """Return one row per vehicle plus separate ground truth metadata.

    Scenarios:
      null: no injected cohort fault
      fault: firmware A increases anomaly probability in each model stratum
      simpson: firmware A is concentrated in a high-baseline-risk model; within-model
               risk is equal across firmware, while unadjusted rates can mislead by design.
    """
    if n < 100:
        raise ValueError("n must be >= 100 for meaningful synthetic strata")
    if scenario not in {"null", "fault", "simpson"}:
        raise ValueError(f"unknown scenario: {scenario}")
    rng = np.random.default_rng(seed)
    model = rng.choice(["M1", "M2"], size=n, p=[0.65, 0.35])
    # Firmware allocation differs sharply in Simpson scenario.
    if scenario == "simpson":
        p_a = np.where(model == "M1", 0.15, 0.85)
    else:
        p_a = np.full(n, 0.5)
    firmware = np.where(rng.random(n) < p_a, "A", "B")

    # Baseline model risk: M2 has naturally higher anomaly risk.
    baseline = np.where(model == "M1", 0.025, 0.22)
    if scenario == "fault":
        prob = np.where(firmware == "A", np.minimum(baseline * 2.5, 0.95), baseline)
        true_cause = "firmware=A"
    elif scenario == "simpson":
        prob = baseline.copy()
        true_cause = None
    else:
        prob = baseline.copy()
        true_cause = None
    anomaly = rng.random(n) < prob

    frame = pd.DataFrame({
        "vehicle_id": [f"veh-{i:06d}" for i in range(n)],
        "firmware": firmware,
        "model": model,
        "anomaly": anomaly.astype(int),
    })
    # Do not pass this object into detection functions.
    truth = {
        "scenario": scenario,
        "seed": int(seed),
        "n_vehicles": int(n),
        "true_cause": true_cause,
        "fault_injected": scenario == "fault",
    }
    return frame, truth
