# Training vs Inference Compute Research

Project 5 studies how a fixed compute allowance is allocated between training and inference.

## Execution

The repository has one connected, fail-closed execution architecture:

`validation` → synthetic/mock only  
`smoke` → real model + real training + real inference + independent hidden evaluation on one task/seed  
`real` → full frozen EXP-001

Main commands:

```bash
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode validation
python scripts/run_smoke_test.py
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode real
```

Smoke artifacts are stored under `results/smoke/`; scientific evidence is stored under `results/raw/EXP-001/`.

Real execution is fail-closed on benchmark, provenance, Docker, CUDA, dependency, model, dataset, Git, and mock-mode prerequisites.

STATUS: **PROJECT 5 IMPLEMENTED / VALIDATED / SCIENTIFICALLY AUDITED / NOT EXECUTED.**

The frozen A0-A4 allocation matrix is unchanged. No empirical result is claimed.
