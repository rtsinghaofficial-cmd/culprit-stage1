### Fair cohort comparison and runtime evaluation

A separate evaluation used 30 runs per scenario (90 runs total), with 5,000 synthetic vehicles per run and seeds starting at 20300000.

| Scenario | Method | TP | FP | FN |
|---|---|---:|---:|---:|
| Fault | Culprit | 30 | 0 | 0 |
| Fault | Unadjusted baseline | 30 | 0 | 0 |
| Simpson | Culprit | 0 | 0 | 0 |
| Simpson | Unadjusted baseline | 0 | 30 | 0 |
| Null | Culprit | 0 | 0 | 0 |
| Null | Unadjusted baseline | 0 | 0 | 0 |

Culprit rejected the misleading firmware association in all 30 Simpson runs. The unadjusted baseline attributed a cohort in all 30 runs.

**Mean runtime per run:**

| Method | Runtime |
|---|---:|
| Culprit | 4.28 ms |
| Unadjusted baseline | 1.71 ms |
| Per-vehicle threshold | 0.51 ms |

The per-vehicle method generates individual vehicle alerts, so its results are reported separately rather than compared using cohort-level F1.

These are synthetic results, not evidence of real-world vehicle fault detection or production performance.

**Reproduce this experiment:**

```powershell
python -m culprit.experiments.evaluate_fair --runs-per-scenario 30 --vehicles 5000
```