# Statistical analysis

The primary unit is a paired task-seed observation. Aggregate correctness is the mean of binary hidden correctness across observations.

For each non-baseline allocation, paired differences against A0 are retained by exact task and seed. Confidence intervals are bootstrap intervals over the paired observations or, for descriptive condition summaries, over correctness observations.

Analysis reports the full frontier: allocation coordinates, raw compute dimensions, correctness, latency, and cost proxy. No scalar score or significance threshold is used to select a winner in advance. Statistical tests are descriptive unless a pre-specified inferential analysis is added before execution.
