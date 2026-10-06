# Methods

Project 5 tests compute allocation rather than assuming a universal training/inference trade-off. Task and seed are paired across five pre-registered allocation conditions.

Training is bounded by steps, tokens, FLOPs when available, and wall-clock. Inference is bounded by calls, input/output tokens, candidates, reasoning rounds, verifier calls, and wall-clock. Retries consume budget.

Final correctness is measured by an independent hidden evaluator. Hidden results cannot influence optimization, checkpoint selection, inference strategy, or budget allocation.

All compute quantities carry a measurement status. No unavailable quantity is imputed silently.


## Execution modes

The repository exposes three explicit modes. Validation uses only synthetic/mock components and cannot write scientific evidence. Smoke mode uses the real Hugging Face model, real training, real inference, and the independent hidden evaluator on one task/seed, with artifacts isolated under `results/smoke/`. Real mode executes the complete frozen EXP-001 matrix. All real modes are fail-closed on benchmark, provenance, runtime, CUDA, Docker, dependency, Git, and mock-policy gates.
