# Compute accounting contract

Every quantity is classified as measured, estimated, derived, or unavailable.

Tracked quantities include training tokens, inference input/output tokens, training/inference/total FLOPs, optimizer steps, model calls, candidates, execution steps, training/inference/total wall-clock, and monetary cost proxy.

## EXP-001 allocation contract

The fixed envelope is 1e15 estimated FLOPs per experimental unit (one task x seed x allocation condition). The frozen estimates use:

- training: `6 * parameter_count * training_tokens`
- inference: `2 * parameter_count * (input_tokens + output_tokens)`

The allocation matrix supplies exact token budgets. Integer token rounding leaves a small remainder below the envelope; no condition exceeds 1e15 estimated FLOPs.

## Training

Training-token budget is primary. The runner consumes the exact declared token budget from a token stream. Optimizer steps are a hard upper bound, not the primary compute coordinate. Actual optimizer steps and realized tokens are recorded separately.

## Inference

Inference-token budget is primary. For every task, the runner reserves the full declared input+output token budget across the declared model-call count. Generation is forced to the reserved output quota; retries consume the same budget.

## Measurement status

Estimated FLOPs are never relabeled as measured hardware FLOPs. Wall-clock and hardware counters are recorded as measured when available. Monetary cost remains unavailable unless a documented price source and usage measurement are supplied.
