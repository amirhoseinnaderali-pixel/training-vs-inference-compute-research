# Evaluation protocol

The model-facing benchmark contains only prompts and visible assertions. Hidden assertions are materialized into a separate evaluator-only file.

Candidate generation receives no hidden-test content. There is no hidden-informed candidate selection. After all candidates are generated within the inference budget, the independent Docker evaluator runs each candidate against the hidden assertions. Only post-generation evaluator results enter the result artifact.

The primary observation is task-level objective hidden correctness; candidate-level correctness is retained for transparent analysis. Training validation, inference-visible feedback, and final held-out evaluation are separate.
