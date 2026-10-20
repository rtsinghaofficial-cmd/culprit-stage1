# Culprit Reproducible Demo

## 1. Shared-fault scenario

Run:
python -m culprit.experiments.run --scenario fault --seed 20261010 --vehicles 5000

Expected result: Culprit flags firmware=A, the injected synthetic cause.

## 2. Simpson's paradox scenario

Run:
python -m culprit.experiments.run --scenario simpson --seed 20261010 --vehicles 5000

Expected result: Culprit returns no cohort predictions, while the unadjusted baseline flags firmware=A.

## Saved experiment results

- fault-seed-20261010.json
- simpson-seed-20261010.json

## Reproducibility

Both saved outputs matched fresh reruns using the same inputs.

## Limitations

These experiments use synthetic data and do not prove real-world fleet performance. The per-vehicle baseline and cohort-level detector have different output targets, so their scores are not directly comparable without a suitable evaluation design.
