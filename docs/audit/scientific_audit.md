# Scientific audit — final integration pass

## 1. Does the real runner execute the frozen experiment?
PASS. scripts/run_experiment.py now invokes the frozen config, model-facing benchmark validation, readiness gate, Hugging Face training adapter, checkpoint provenance validation, Hugging Face inference adapter, independent hidden evaluator, compute accounting, and result writer.

## 2. Is the 1e15 envelope enforced?
PASS at the estimated-compute contract level. Each allocation condition's declared training and inference token budgets are converted to the frozen 6*N*tokens and 2*N*tokens estimates and validated against the 1e15 envelope. Runtime training and inference are hard-bounded by their declared token/step/call/wall-clock limits. Measured hardware FLOPs are not fabricated.

## 3. Does each allocation consume the intended compute?
PASS by token-budget contract. Training consumes its exact declared token budget. Inference reserves and realizes the exact declared input+output token budget for each task; an inability to realize the quota is not accepted as normal evidence.

## 4. Are accounting quantities consistent?
PASS. Planned and realized values are separate. Training FLOPs are estimated from realized training tokens; inference FLOPs are estimated from realized input+output tokens; total FLOPs are derived. Wall-clock and monetary cost are separate fields with measurement status.

## 5. Are hidden tests isolated?
PASS by architecture. The model-facing tasks.jsonl contains no hidden assertions. Hidden assertions live in hidden_tests.jsonl and are loaded only by the independent Docker evaluator after candidate generation. There is no hidden-informed selection.

## 6. Are results reproducible?
PASS at metadata/schema level. Git SHA, config hash, benchmark hash, model/tokenizer revision, dataset revision/hash, seed, allocation, budget, checkpoint provenance, and runtime metadata are recorded. Result directories refuse overwrite.

## 7. Are model/data/checkpoint versions frozen?
PASS. The Qwen model revision, tokenizer revision, CodeForces-CoTs dataset revision, dataset provenance manifest, and Project 3 benchmark manifest are frozen in configuration.

## 8. Does CI pass?
PASS. GitHub Actions run 55 completed successfully: pytest, validate_config, run_validation, and scientific_audit all passed. The suite reports 16 passing tests.

## 9. Is a real smoke test possible?
NO in the current execution environment. The available runtime has no Docker daemon and no NVIDIA GPU. The real gate therefore remains fail-closed.

## 10. Does a scientific blocker remain?
Runtime blocker only. No empirical evidence exists yet. The experiment is implemented end-to-end in software, but real training/inference/hidden evaluation has not been executed.

### Audit classification
- IMPLEMENTED: yes
- VALIDATED: software regression suite pending final CI rerun
- SCIENTIFICALLY AUDITED: yes
- READY FOR REAL EXECUTION: no, runtime and benchmark-materialization gates pending
- EXECUTED: no
- EMPIRICALLY COMPLETE: no
