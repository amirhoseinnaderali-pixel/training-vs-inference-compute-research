# Training vs Inference Compute Research

### Portfolio status

**REGISTERED — EMPIRICAL RESULT NOT RECOVERED FOR THE TARGET QUESTION**

The hardened A0–A4 instrument is implemented and audited, but no real controlled EXP-001 result set was recovered. Earlier training/fine-tuning repositories are lineage evidence, not valid P5 allocation experiments.

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


See [docs/research_report.md](docs/research_report.md) for the historical evidence audit and conclusion.
