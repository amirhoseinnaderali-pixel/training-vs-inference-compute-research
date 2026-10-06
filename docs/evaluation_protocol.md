# Evaluation protocol

The model-facing benchmark contains only prompts and visible assertions. Hidden assertions are materialized into a separate evaluator-only file.

Candidate generation receives no hidden-test content. There is no hidden-informed candidate selection. After all candidates are generated within the inference budget, the independent Docker evaluator runs each candidate against the hidden assertions. Only post-generation evaluator results enter the result artifact.

## Registered primary outcome

The primary estimand is **`any_candidate_passes_hidden`**.

For each task × seed × allocation unit, the primary correctness value is binary:
- `1` if at least one generated candidate passes the hidden evaluator;
- `0` if no generated candidate passes.

Candidate-level hidden correctness is retained only as a secondary descriptive field. Hidden evaluation cannot alter candidate generation, candidate count, generation seeds, or selection because it occurs strictly after generation is complete.

Training validation, inference-visible feedback, and final held-out evaluation remain separate.
