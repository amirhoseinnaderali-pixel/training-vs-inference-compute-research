# Statistical analysis

The primary unit is a paired task-seed observation. Aggregate primary correctness is the mean of the binary `any_candidate_passes_hidden` outcome across eligible observations.

For each non-baseline allocation, paired differences against A0 are retained by exact task and seed. Confidence intervals are bootstrap intervals over the paired observations or, for descriptive condition summaries, over primary correctness observations.

Only result records with `status == "complete"` and `eligible_for_analysis == true` enter scientific aggregation. Budget violations, runtime failures, configuration failures, model failures, evaluation failures, and other incomplete records remain in the raw artifact set but are excluded from scientific estimates.

Analysis reports the full frontier: allocation coordinates, raw compute dimensions, correctness, latency, and cost proxy. No scalar score or significance threshold is used to select a winner in advance. Statistical tests are descriptive unless a pre-specified inferential analysis is added before execution.
