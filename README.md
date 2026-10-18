# Training vs Inference Compute Research

**EXP-001 — Fixed-compute training vs. inference allocation**

This project investigates how a fixed compute budget should be split between fine-tuning a language model and generating multiple candidate solutions at inference time.

## Research question

Under the same **estimated total compute budget**, does spending more on training or on inference-time candidate generation improve held-out code correctness?

## Experimental setup

| Item | Configuration |
|---|---|
| Base model | `Qwen/Qwen2.5-Coder-1.5B` (~1.54B parameters) |
| Benchmark | `HumanEval-stratified-100-v1` (100 Python tasks) |
| Training data | `open-r1/codeforces-cots` |
| Fine-tuning | Full fine-tuning; causal language modeling with AdamW |
| Training settings | BF16, learning rate `2e-5`, sequence length 1024, batch size 1 |
| Seeds | 42, 43, 44 |
| Compute target | `1e15` **estimated FLOPs** per task × seed × condition |

FLOPs are estimated from token counts, not measured directly from hardware.

## Allocation conditions and recorded results

Each condition starts from the same frozen base model, fine-tunes within its assigned training-token budget, generates the allocated number of candidates, and evaluates them with hidden tests after generation is complete.

| Condition | Training / inference | Training tokens | Inference tokens | Calls per task | Recorded hidden accuracy (95% uncertainty range) |
|---|---:|---:|---:|---:|---:|
| **A0** | 10% / 90% | 10,822 | 292,207 | 16 | **92%** (88–95%) |
| **A1** | 30% / 70% | 32,467 | 227,272 | 12 | **91%** (87–94%) |
| **A2** | 50% / 50% | 54,112 | 162,337 | 8 | **89%** (85–93%) |
| **A3** | 70% / 30% | 75,757 | 97,402 | 4 | **85%** (80–89%) |
| **A4** | 90% / 10% | 97,402 | 32,467 | 1 | **68%** (60–74%) |

The primary outcome is **whether at least one candidate passes the independent hidden evaluator** for a task, seed, and condition. The recorded results favor inference-heavy allocations in this setup, with a substantial drop for A4. The overlapping uncertainty ranges mean the small differences among A0–A2 should not be treated as definitive.

**Evidence note:** these values are reported in the study record. Task-level raw result files are not committed in the public repository, so the aggregate figures cannot currently be independently recomputed from this repository alone.

## How the experiment works

1. **Allocate compute:** freeze the A0–A4 training/inference budgets.
2. **Fine-tune:** train a separate checkpoint for each task × seed × condition, starting from the frozen base model.
3. **Generate candidates:** use the remaining inference budget for the condition's allotted model calls.
4. **Evaluate:** run hidden tests only after all candidates have been generated.
5. **Analyze:** compare task-level correctness and uncertainty across allocations; exclude incomplete or budget-violating runs.

## Important limitations

- Results apply to this 1.5B code model, this 100-task HumanEval-derived benchmark, and this budget range; they do not establish a universal training-versus-inference rule.
- The five allocations sample part of the compute-allocation space; they do not identify a global optimum.
- The total-compute target is based on token-based FLOP estimates, not hardware-measured FLOPs.
- Public task-level run artifacts are needed for independent reproduction of the reported aggregates.

## Run

Install the real-execution dependencies:

```bash
pip install -e ".[real]"
python scripts/materialize_benchmark.py
```

Run a one-task smoke test or the full frozen experiment (requires the configured CUDA/Docker environment):

```bash
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode smoke
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode real
```

The real runner is designed to stop if its required environment, benchmark, or provenance checks fail. Validation/mock outputs are not scientific results.

## Key files

- `configs/experiments/exp001_fixed_allocation.yaml` — frozen experiment and allocation matrix
- `src/compute_research/real_adapters.py` — full fine-tuning and inference adapters
- `src/compute_research/runner.py` — experiment execution and budget enforcement
- `src/compute_research/evaluator.py` — independent hidden-test evaluation
- `src/compute_research/stats.py` — summary statistics and confidence intervals
- `docs/` — methodology, reproducibility, and limitations
