# Methods

Project 5 tests compute allocation rather than assuming a universal training/inference trade-off. Task and seed are paired across five pre-registered allocation conditions.

Training is bounded by steps, tokens, FLOPs when available, and wall-clock. Inference is bounded by calls, input/output tokens, candidates, reasoning rounds, verifier calls, and wall-clock. Retries consume budget.

Final correctness is measured by an independent hidden evaluator. Hidden results cannot influence optimization, checkpoint selection, inference strategy, or budget allocation.

All compute quantities carry a measurement status. No unavailable quantity is imputed silently.
