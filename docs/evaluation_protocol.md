# Evaluation protocol

The benchmark uses a deterministic visible/hidden split. Visible feedback may be used only where the frozen condition permits it. Hidden tests are never passed to strategy selection, training, checkpoint selection, hyperparameter tuning, or inference strategy selection.

Final correctness is produced by an independent evaluator after selection. Validation data and final held-out evaluation are separate.
