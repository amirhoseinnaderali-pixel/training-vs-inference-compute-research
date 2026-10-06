# EXP-001 readiness

The main CLI is connected to the real runner. Execution modes are explicit:

- `--mode validation`: synthetic/mock only; never scientific evidence.
- `--mode smoke`: real model, real training, real inference, and independent hidden evaluation on one task/seed; artifacts go under `results/smoke/`.
- `--mode real`: full frozen EXP-001; artifacts go under `results/raw/EXP-001/`.

Real execution is fail-closed. Required gates are: materialized benchmark, benchmark/manifest integrity, evaluator-only hidden store, frozen model and tokenizer revisions, frozen dataset/provenance, Docker daemon, CUDA, real runtime dependencies, reproducible Git SHA, fail_closed=true, and mock disabled.

The frozen model and dataset are public Hugging Face resources, so no provider credential is required. A credential would become required only for a gated/private resource.

The benchmark manifest is cross-checked against the Project 3 frozen identity: HumanEval source commit, acquisition mirror, selection policy, deterministic assertion split, task ordering, task hashes, and test hashes.

No real training, inference, hidden evaluation, or empirical evidence is claimed unless the corresponding mode actually completes.
