# Compute accounting contract

Every quantity is classified as measured, estimated, derived, or unavailable.

Track training tokens, inference input/output tokens, training/inference/total FLOPs, optimizer steps, model calls, candidates, execution steps, training/inference/total wall-clock, and monetary cost proxy.

Normalized allocation fractions are design coordinates only. They never replace raw compute dimensions.

Budget overruns invalidate a run. Retries consume budget. Unknown pricing stays unavailable. No compute value is fabricated.

## EXP-001 budget envelope

The frozen design uses a 1e15 FLOP estimated envelope with model parameter count 1.54B. Training budget FLOPs are estimated as 6*N*training_tokens; inference budget FLOPs are estimated as 2*N*inference_tokens. These are pre-registered allocation coordinates, not measured hardware FLOPs. Measured training and inference FLOPs remain separate result fields. Each allocation row reserves 10%, 30%, 50%, 70%, or 90% of the estimated envelope for training, with the complement assigned to inference.
