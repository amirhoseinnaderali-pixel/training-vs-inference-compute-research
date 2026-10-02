# Reproducibility contract

Every empirical run records experiment ID, unique run ID, Git SHA, configuration hash, benchmark manifest hash, training-data provenance hash, model/revision, tokenizer revision, seed, allocation condition, training/inference budgets, realized compute, runtime environment, checkpoint provenance, and timestamps.

Checkpoint provenance is mandatory. A checkpoint without provenance.json containing frozen model/data/config/allocation metadata is not scientific evidence.

Result directories are unique and refuse overwrite.
