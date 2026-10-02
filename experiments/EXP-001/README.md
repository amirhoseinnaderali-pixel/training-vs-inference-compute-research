# EXP-001

STATUS: FROZEN / NOT EXECUTED

Authoritative configuration: `configs/experiments/exp001_fixed_allocation.yaml`.

Experimental unit: one benchmark task × one seed × one allocation condition. Training is performed from the same frozen base model for each unit, then inference is performed on that task. This makes the fixed compute envelope apply to the unit being compared.

Seeds: 42, 43, 44.

| Condition | Training fraction | Inference fraction | Training token budget | Max optimizer steps | Inference token budget | Model calls |
|---|---:|---:|---:|---:|---:|---:|
| A0 | 10% | 90% | 10,822 | 3 | 292,207 | 16 |
| A1 | 30% | 70% | 32,467 | 8 | 227,272 | 12 |
| A2 | 50% | 50% | 54,112 | 13 | 162,337 | 8 |
| A3 | 70% | 30% | 75,757 | 18 | 97,402 | 4 |
| A4 | 90% | 10% | 97,402 | 24 | 32,467 | 1 |

The fractions are the frozen allocation coordinates. Integer token budgets produce a small rounding remainder below the 1e15 estimated-FLOP envelope. Training token budget is primary; optimizer steps are a hard maximum. Training uses a token stream and consumes the exact declared token budget before checkpointing. Inference consumes the exact declared total input+output token budget, subject to the frozen per-call safety caps.

Registered primary outcome: `any_candidate_passes_hidden`. For each task × seed × condition, it is 1 iff at least one generated candidate passes the independent hidden evaluator after all candidate generation is complete. Candidate-level correctness is retained only as a secondary field.

Hidden evaluation occurs only after candidate generation and never influences selection. No empirical result is claimed by this repository state.
