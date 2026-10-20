# Culprit — Stage 1

**Synthetic shared-fault cohort attribution research MVP**

Culprit investigates whether a shared firmware cohort is associated with elevated anomaly rates after accounting for vehicle-model differences. It is a reproducible research prototype, not a production fault-diagnosis system.

## Features

- Deterministic synthetic fleet generation
- Null, shared-fault, and Simpson's paradox scenarios
- Stratified Cochran–Mantel–Haenszel (CMH) testing
- Mantel–Haenszel pooled risk ratio
- Benjamini–Hochberg false discovery rate (FDR) correction
- Unadjusted cohort and naive per-vehicle baselines
- Repeated-seed benchmark and ablation experiments
- Synthetic 24-hour null evaluation
- Automated tests with pytest

## Research results

### Mixed synthetic cohort-attribution benchmark

The benchmark contains 30 runs each of the fault, Simpson, and null scenarios, with 5,000 simulated vehicles per run.

| Metric | Culprit | Unadjusted cohort baseline |
|---|---:|---:|
| True positives | 30 | 30 |
| False positives | 0 | 30 |
| False negatives | 0 | 0 |
| Precision | 1.000 | 0.500 |
| Recall | 1.000 | 1.000 |
| F1 | 1.000 | 0.667 |

**Observed F1 improvement:** +0.333 over the unadjusted cohort baseline.

Across the 60 simulated no-cause runs, Culprit's false-attribution rate was 0%, compared with 50% for the unadjusted cohort baseline.

These are results for the specified synthetic scenarios and seeds. They do not establish real-fleet performance or generalization to unseen fault mechanisms.

### Synthetic 24-hour null evaluation

In a 30-day simulation, each day contains 24 independent hourly snapshots of 5,000 synthetic vehicles.

- Simulated days: 30
- Hourly snapshots: 720
- False incidents observed: 0
- Days exceeding one false incident: 0

All 30 simulated days met the target of at most one false incident per day.

**Important limitation:** these are independent synthetic snapshots, not persistent telemetry or a live 24-hour production test. Zero observed false incidents in this experiment does not establish a real-world false-incident rate.

## Evaluation status

The proposed evaluation gate is:

1. F1 at least 0.20 above **both** baselines.
2. At most one false incident per simulated 24-hour null run.
3. Record seeds, scenarios, configuration, and outputs.

The mixed benchmark exceeds the F1-improvement threshold against the **unadjusted cohort baseline**. The synthetic 24-hour null experiment meets its specified threshold for the tested runs.

**The full gate is not yet demonstrated.** The per-vehicle baseline produces vehicle-level anomaly alerts, while the main benchmark evaluates cohort-level causal attribution. These are different targets, so a comparable second-baseline F1 has not been established. The gate must not be reported as fully passed.

## Limitations and future work

- All data are synthetic.
- CMH testing is a research MVP, not a production detector.
- Exact sparse-table inference and temporal persistence are not implemented.
- Pair-cohort search and greedy excess cover are not implemented.
- Streaming execution is not implemented.
- The experiments do not establish causal effects or real-world fleet reliability.

## Requirements

Python 3.11+ is recommended; compatibility with other versions is not guaranteed.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

If activation is blocked in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Run the experiments

Run a single scenario:

```powershell
python -m culprit.experiments.run --scenario simpson --seed 20261010
```

Run repeated evaluation:

```powershell
python -m culprit.experiments.evaluate --runs 30 --scenario fault
```

Run the mixed synthetic benchmark:

```powershell
python -m culprit.experiments.evaluate_mixed
```

Run the 30-day synthetic null evaluation:

```powershell
python -m culprit.experiments.evaluate_24h --days 30
```

Run ablation experiments:

```powershell
python -m culprit.experiments.ablate --runs 10
```

Save benchmark output:

```powershell
python -m culprit.experiments.evaluate_mixed > mixed-latest.json
```

## Tests

```powershell
python -m pytest -q
```

## Reproducibility

Experiments use explicit seeds and emit scenario-level results. Preserve the seed, scenario, configuration, and output when comparing runs. Benchmark results should be regenerated from the code rather than treated as universal performance guarantees.

## License

No license has been specified yet. All rights reserved by default unless a license is added to this repository.
