# Culprit — Stage 1 ready-to-run proof of insight

This repository implements a local synthetic experiment for shared-fault cohort attribution.
It includes:
- deterministic synthetic fleet generation
- null, shared-fault, and Simpson-trap scenarios
- a stratified CMH score and Mantel–Haenszel rate ratio
- Benjamini–Hochberg FDR correction
- naive per-vehicle and unadjusted cohort baselines
- repeated-seed evaluation and simple ablation runs
- pytest unit tests

**Research honesty:** all data are synthetic. Results are not evidence of real-fleet performance.
The CMH implementation here is a research MVP, not a production detector. Exact sparse-table
inference, temporal persistence, pair-cohort search, greedy excess cover, and streaming execution
remain future work and must not be represented as implemented.

## Install (Python 3.11+ recommended; compatibility is an ESTIMATE)

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

If PowerShell activation is blocked:
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

## Run

```bash
python -m culprit.experiments.run --scenario simpson --seed 20261010
python -m culprit.experiments.evaluate --runs 30 --scenario fault
python -m culprit.experiments.ablate --runs 10
```

Outputs are JSON to stdout. To save one:
```bash
python -m culprit.experiments.evaluate --runs 30 --scenario fault > results/fault-eval.json
```

## Gate

The proposed gate is:
1. F1 at least 0.20 above **both** baselines.
2. At most 1 false incident per simulated 24-hour null run.
3. Record seed, scenario, config and output.

This code does not declare the gate passed automatically. Review the measured synthetic outputs.
The current simulation is window-level; 24-hour false-incident extrapolation is not claimed.
