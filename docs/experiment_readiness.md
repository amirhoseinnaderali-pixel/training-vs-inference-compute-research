# EXP-001 readiness

The frozen experiment is executable in software but real execution is currently blocked until runtime prerequisites exist.

Required gates:
1. Materialized benchmark exists and matches the vendored Project 3 manifest.
2. Hidden assertions exist in a separate evaluator-only file.
3. Docker is available for independent hidden evaluation.
4. The exact frozen Qwen model/tokenizer revision is available.
5. The exact frozen open-r1 dataset revision and provenance manifest are available.
6. A reproducible Git SHA is available.
7. Mock execution remains disabled in real mode.

The frozen model and dataset are public Hugging Face resources, so no provider credential is required. A credential would become required only if the frozen resources were changed to gated/private resources; that would invalidate the frozen experiment.

No real training, inference, or hidden evaluation is claimed until these gates pass.
