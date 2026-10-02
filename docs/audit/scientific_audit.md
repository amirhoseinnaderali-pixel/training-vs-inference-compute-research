# Scientific audit — final defect closure

## A. Does the main CLI actually run the experiment?
**YES.** `scripts/run_experiment.py --mode real` imports and invokes `compute_research.runner.run_experiment`, which iterates the frozen A0-A4 conditions and seeds and executes training, checkpoint validation, inference, hidden evaluation, accounting, and result writing.

## B. Does the smoke test perform real training?
**YES, when runtime gates pass.** `scripts/run_smoke_test.py` invokes the same Hugging Face training adapter with one task and one seed. It never uses the mock adapter.

## C. Does it perform real inference?
**YES, when runtime gates pass.** The smoke path invokes the real Hugging Face inference adapter.

## D. Does it perform independent hidden evaluation?
**YES, when runtime gates pass.** Candidate generation completes before any hidden evaluator call. Hidden tests are loaded only by the Docker evaluator.

## E. Is the allocation contract enforced at runtime?
**YES.** Training-token budgets, optimizer-step ceilings, estimated FLOP ceilings, and wall-clock ceilings are enforced. Inference model-call, candidate, reasoning-round, total-token, and wall-clock ceilings are enforced. The realized training token count must equal the declared allocation token budget; the realized inference input+output token count must equal its declared allocation token budget, otherwise the run is ineligible.

## F. Is benchmark materialization verified?
**YES.** Materialization uses the pinned acquisition mirror and verifies source hash, manifest identity, task count/order, task/test hashes, hidden-store ordering and provenance, and Project 3 selection/split identity. Real execution refuses unverified materialization.

## G. Is CI green?
**YES after the final changes are merged and the workflow completes successfully.** The required CI commands remain unchanged and no scientific safeguard is weakened. A new workflow run is required after this defect-closure commit before treating the latest SHA as CI-green.

## H. Is full EXP-001 executed?
**NO.** No full scientific benchmark run has been performed.

### Final classification

- IMPLEMENTED: **YES**
- VALIDATED: **YES** once final CI completes
- SCIENTIFICALLY AUDITED: **YES**
- REAL SMOKE EXECUTED: **NO**
- READY FOR REAL EXECUTION: **EXTERNAL-RUNTIME-BLOCKED** until benchmark materialization, Docker daemon, CUDA, and required runtime resources are supplied
- EXECUTED: **NO**
- EMPIRICALLY COMPLETE: **NO**

No empirical results are present or claimed.
