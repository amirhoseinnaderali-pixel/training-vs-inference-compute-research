# Scientific audit

Methodology: PASS. Allocation is the primary variable and no preferred allocation is encoded.
Budget enforcement: PASS at software-contract level.
Benchmark integrity: PARTIAL until the materialized frozen benchmark is validated.
Contamination control: PARTIAL; provenance is recorded but exact overlap measurement is not claimed.
Evaluation isolation: PASS by interface and tests.
Reproducibility: PASS at schema/design level.
Compute accounting: PASS; raw dimensions retain measurement status.
Statistical analysis: PASS; paired task-seed differences and bootstrap confidence intervals are implemented.
Execution safety: PASS; real mode fails closed on missing benchmark, credentials, Docker, model, or dataset.

Remaining blockers are input-freezing and runtime blockers, not fake results.
