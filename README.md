# Training vs Inference Compute Research

Project 5 studies how a fixed compute allowance is allocated between training and inference.

Scientific question: under a fixed total compute envelope, how does shifting compute between additional training and additional inference-time computation affect objective held-out correctness?

STATUS: PROJECT 5 IMPLEMENTED / VALIDATED / SCIENTIFICALLY AUDITED / NOT EXECUTED.

The real EXP-001 runner now executes the frozen pipeline end-to-end: benchmark integrity gate -> budgeted Hugging Face training -> provenance-validated checkpoint -> budgeted inference -> independent hidden evaluation -> compute accounting -> immutable result artifact.

The allocation contract is enforced at the experimental-unit level (task x seed x condition). Training-token budget is primary; inference input+output token budget is primary. The 1e15 envelope is an estimated-FLOP contract and never substitutes for measured hardware quantities.

CI: GitHub Actions run 55 passed 16 regression tests plus config validation, validation-only execution, and scientific audit.

Real execution remains fail-closed until the frozen 100-task benchmark is materialized and the required Docker + CUDA runtime is available. No empirical result is claimed.
