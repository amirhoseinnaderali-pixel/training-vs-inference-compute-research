# Scientific audit — final defect closure

## A. Does the main CLI actually run the experiment?
**YES.** `scripts/run_experiment.py --mode real` invokes `compute_research.runner.run_experiment`, which iterates the frozen A0-A4 conditions and seeds and executes training, checkpoint provenance validation, inference, hidden evaluation, accounting, and result writing.

## B. Does the smoke test perform real training?
**YES, when runtime gates pass.** `scripts/run_smoke_test.py` invokes the same Hugging Face training adapter with one task and one seed. It never uses the mock adapter.

## C. Does it perform real inference?
**YES, when runtime gates pass.** The smoke path invokes the real Hugging Face inference adapter.

## D. Does it perform independent hidden evaluation?
**YES, when runtime gates pass.** Candidate generation is completed before the first hidden evaluator call. Hidden tests are loaded only by the Docker evaluator. The primary outcome is explicitly `any_candidate_passes_hidden`.

## E. Is the allocation contract enforced at runtime?
**YES.** Training-token budgets, the optimizer-step ceiling, estimated FLOP ceilings, and wall-clock ceilings are fail-closed. The optimizer-step guard checks capacity before calling `optimizer.step()`. Inference model-call, candidate, reasoning-round, total-token, per-call output, and wall-clock ceilings are enforced. Exact realized training tokens and inference input+output tokens must match the frozen allocation.

## F. Is checkpoint provenance bound to the experimental unit?
**YES.** Checkpoints record and are validated against model revision, tokenizer revision, training dataset revision and manifest hash, config hash, allocation condition, seed, Git SHA, declared training budget, and realized training compute.

## G. Is result eligibility explicit?
**YES.** Every result record has `eligible_for_analysis`. Complete records are eligible only after successful exact-budget execution and post-generation hidden evaluation. Budget/runtime/configuration/model/evaluation failures remain raw but are excluded from analysis.

## H. Is CI green?
**YES.** The latest GitHub Actions validation run for the current main HEAD is run #84 on commit `6f11a38019fa7fcc09312f249764383f3a0aea6e`; it completed successfully and executed pytest, config validation, validation-only execution, and the scientific audit.

## I. Is full EXP-001 executed?
**NO.** No full scientific benchmark run has been performed.

## J. Is a real smoke run executed?
**NO.** The current repository state does not contain a completed real smoke artifact, and this audit does not treat CI as empirical execution.

### Final classification

- IMPLEMENTED: **YES**
- VALIDATED: **YES**
- SCIENTIFICALLY AUDITED: **YES**
- REAL SMOKE EXECUTED: **NO**
- READY FOR REAL EXECUTION: **EXTERNAL-RUNTIME-BLOCKED** until materialized benchmark, Docker daemon, CUDA, and required runtime resources are supplied
- EXECUTED: **NO**
- EMPIRICALLY COMPLETE: **NO**

No empirical results are present or claimed.
