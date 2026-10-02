# Training vs Inference Compute Research

Project 5 studies how a fixed compute allowance is allocated between training and inference.

Scientific question: under a fixed total compute envelope, how does shifting compute between additional training and additional inference-time computation affect objective held-out correctness?

STATUS: PROJECT 5 IMPLEMENTED / NOT EXECUTED.

The repository contains a frozen EXP-001 design, explicit training/inference accounting, benchmark provenance, hidden-evaluation isolation, validation-only execution, fail-closed readiness checks, statistical analysis, and scientific invariant tests. No empirical result is claimed.

Validation: `python -m pytest -q`, `python scripts/validate_config.py`, `python scripts/run_validation.py`, `python scripts/scientific_audit.py`.
