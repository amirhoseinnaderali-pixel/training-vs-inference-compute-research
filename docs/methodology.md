# Methodology

Experimental unit: one task, seed, and allocation condition.

Independent variable: frozen training/inference allocation.
Dependent variables: hidden correctness plus separate compute dimensions.
Controls: model family, tokenizer, initialization, objective, training data, benchmark, prompts, evaluator, seeds, precision, and runtime policy.

Each condition trains an identifiable checkpoint within its declared training budget and then performs inference within its separate inference budget. Hidden evaluation happens only after selection.

Failure taxonomy: CONFIG_INVALID, BENCHMARK_MISSING, CONTAMINATION_UNRESOLVED, TRAINING_BUDGET_EXCEEDED, INFERENCE_BUDGET_EXCEEDED, RUNTIME_MISSING, CREDENTIAL_MISSING, EXECUTION_TIMEOUT, MODEL_ERROR, EVALUATION_ERROR, RESULT_COLLISION.
