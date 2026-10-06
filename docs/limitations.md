# Limitations

HumanEval is a programming benchmark and does not establish general reasoning capability. Exact zero contamination cannot be claimed. The training dataset is provenance-tracked and its published decontamination procedure is documented, but residual overlap with this specific 100-task benchmark is not independently measured here.

The fixed 1e15 envelope uses token-based FLOP estimates, not hardware-measured FLOPs. Actual hardware FLOPs may differ.

EXP-001 is intentionally expensive because the experimental unit is task x seed x allocation: each unit receives its own training budget before its inference budget. This prevents amortizing one training run across 100 tasks and changing the allocation being tested.

The five allocation conditions sample the allocation surface; they do not prove a global optimum.
