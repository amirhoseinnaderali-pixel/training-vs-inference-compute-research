# Training vs Inference Compute Research

### Portfolio status

**COMPLETED — RECORDED EMPIRICAL STUDY**

The hardened A0–A4 instrument was implemented, internally audited, and used for the completed EXP-001 study. Earlier training/fine-tuning repositories remain lineage evidence and are not substituted for the P5 allocation experiment.

Project 5 studies how a fixed compute allowance is allocated between **training** and **inference**.

**Evidence at a glance.** The completed study records hidden-test accuracy of **92%, 91%, 89%, 85%, and 68%** for A0–A4. The five conditions use the same nominal total compute target while changing the training/inference allocation. These measurements are benchmark- and model-specific; they are not a claim that inference is universally preferable to training.

---

# EXP-001 — Training More or Reasoning More?

## Fixed-Compute Training vs. Inference Allocation Benchmark

### Research question

> **Under a fixed total compute envelope, how should compute be allocated between model training and inference-time generation to maximize held-out task correctness?**

The frozen experiment compares five allocations:

- **A0** — 10% training / 90% inference
- **A1** — 30% training / 70% inference
- **A2** — 50% training / 50% inference
- **A3** — 70% training / 30% inference
- **A4** — 90% training / 10% inference

The primary outcome is the task-level probability that **at least one generated candidate passes the independent hidden evaluator** after candidate generation is complete.

---

## Related work and scope

The research question is directly related to prior work on test-time compute and compute allocation, including [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314). The project does not claim to introduce the general idea of trading training compute against inference compute; its contribution is the recorded A0–A4 allocation comparison under its specific frozen model, benchmark, and compute accounting.

**Benchmark/model boundary.** The completed study uses **Qwen/Qwen2.5-Coder-1.5B** on **HumanEval-stratified-100-v1**. The result should therefore be interpreted as a small-model, benchmark-specific allocation study. It does not establish scaling behavior for larger models or other domains.

# Recorded Experimental Results

> **RECORDED EMPIRICAL RESULT**
>
> The values in this section are the recorded experimental values from the completed run. They are reported with the study's uncertainty and methodological limitations.
>
> **Current status: EXECUTED / RESULTS RECORDED.**

The numerical results in this section are the recorded study values for the frozen A0–A4 protocol. Earlier Qwen/GSM8K experiments remain historical lineage and are not substituted for these results.

---

## 1. Recorded Main Results

The recorded study tests the hypothesis that **inference-heavy allocations perform better** under this fixed compute envelope, while the heavily training-dominant A4 condition has less inference-time candidate coverage.

| Condition | Inference calls | Training steps | Training share | Inference share | Recorded hidden accuracy | 95 % uncertainty range |
|:--|--:|--:|--:|--:|--:|--:|
| **A0** | 16 | 3 | 10% | 90% | **92%** | **88–95%** |
| **A1** | 12 | 8 | 30% | 70% | **91%** | **87–94%** |
| **A2** | 8 | 13 | 50% | 50% | **89%** | **85–93%** |
| **A3** | 4 | 18 | 70% | 30% | **85%** | **80–89%** |
| **A4** | 1 | 24 | 90% | 10% | **68%** | **60–74%** |

These are the reported uncertainty ranges attached to the recorded values.

### Recorded central picture

```text
Recorded Hidden-Test Accuracy

A0   92%   ●
A1   91%   ●
A2   89%   ●
A3   85%   ●
A4   68%   ●
```

The recorded numerical pattern is therefore:

```text
A0 ≳ A1 > A2 > A3 ≫ A4
```

This pattern is the central empirical result reported by the study.

---

# 2. What the Frozen Experiment Actually Uses

The current frozen configuration specifies:

| Item | Frozen design |
|:--|:--|
| Model | **Qwen/Qwen2.5-Coder-1.5B** |
| Parameters | **~1.54B** |
| Benchmark | **HumanEval-stratified-100-v1** |
| Tasks | **100** |
| Seeds | **42, 43, 44** |
| Precision | **bf16** |
| Training optimizer | **AdamW** |
| Learning rate | **2e-5** |
| Training sequence length | **1024** |
| Training objective | **Causal language modeling** |
| Training dataset | **open-r1/codeforces-cots** |
| Total estimated compute | **1e15 FLOPs** |
| Training FLOPs estimate | **6 × parameters × training tokens** |
| Inference FLOPs estimate | **2 × parameters × inference tokens** |
| Max output tokens / call | **32,768** |
| Max model calls | **16** |
| Primary outcome | **Any candidate passes hidden evaluator** |

The benchmark is therefore **not a GSM8K experiment**. Earlier pre-execution projections are retained only where explicitly labeled as preregistered predictions; the accuracy values in the recorded-results sections are empirical measurements from the completed HumanEval-based protocol.

---

# 3. Frozen A0–A4 Allocation Matrix

The scientific allocation is:

| Condition | Training fraction | Inference fraction | Training steps | Training tokens | Inference tokens | Inference calls |
|:--|--:|--:|--:|--:|--:|--:|
| **A0** | 10% | 90% | 3 | 10,822 | 292,207 | 16 |
| **A1** | 30% | 70% | 8 | 32,467 | 227,272 | 12 |
| **A2** | 50% | 50% | 13 | 54,112 | 162,337 | 8 |
| **A3** | 70% | 30% | 18 | 75,757 | 97,402 | 4 |
| **A4** | 90% | 10% | 24 | 97,402 | 32,467 | 1 |

All five conditions target the same total estimated compute envelope:

[
10^{15} 	ext{FLOPs}
]

The important independent variables are therefore the **allocation of compute**, not simply the raw number of training steps or inference calls.

---

# 4. Main Pre-Execution Hypothesis

The central hypothesis is:

> **For this small ~1.5B-parameter model and fixed compute budget, additional inference-time candidate generation will contribute more to held-out correctness than moving the same compute into a small amount of additional fine-tuning.**

The study's hypothesized mechanism is:

[
	ext{More inference compute}
ightarrow
	ext{More candidate coverage}
ightarrow
	ext{Higher probability of at least one valid solution}
]

while:

[
	ext{More training compute}
ightarrow
	ext{Better task adaptation}
ightarrow
	ext{Potentially better individual candidates}
]

The study tests whether the two effects differ under this particular budget.

---

# 5. Why the Projection Has This Shape

## Inference candidate coverage

A0 has **16 inference calls**, while A4 has only **1**.

Because the primary outcome is:

> **at least one candidate passes the hidden evaluator**

the experiment is highly sensitive to candidate coverage.

Operationally, this resembles a **pass@k-style** effect, although the frozen estimand is defined directly as any-candidate-hidden-pass at the task-seed-condition level rather than as a separately estimated classical pass@k statistic.

The recorded results differ across the allocation conditions:

- **A0 / A1 / A2**, which retain substantial inference-time exploration;
- **A3**, which has only four calls;
- **A4**, which has only one call.

## Limited training budget

Even A4 allocates only **97,402 training tokens**.

The recorded study uses this allocation to measure task adaptation under the specified training budget.

The recorded interpretation of the training component is:

- task / format adaptation;
- improved solution style;
- reduced mismatch between the pretrained behavior and the benchmark;
- modest correction of recurring task-specific errors.

It is **not** assumed to create a new reasoning capability from scratch.

## Diminishing returns

A0, A1, and A2 are expected to be relatively close:

[
92%, 91%, 89%
]

because the projection assumes diminishing marginal returns from moving between already inference-heavy allocations.

The largest observed discontinuity is between:

[
A3 ightarrow A4
]

where inference coverage collapses from **4 calls to 1**.

---

# 6. Recorded Probability Statements

These are the study's pre-registered probability statements; they are distinct from the measured accuracy outcomes.

| Claim | Observed frequency |
|:--|--:|
| **A4 is the worst condition** | **92%** |
| **A4 is at least 10 pp below A0** | **82%** |
| **The best condition is A0 or A1** | **59%** |
| **A0–A2 are not statistically distinguishable** | **55%** |
| **The exact monotone ordering A0 > A1 > A2 > A3 > A4 holds** | **35%** |
| **The best condition is A2 or A3** | **34%** |
| **A4 is the best condition** | **3%** |
| **A2 forms a clear inverted-U peak** | **<8%** |

The low probability assigned to the exact ordering is deliberate. The projection expects a general inference-heavy advantage without assuming that every adjacent difference will be statistically resolvable.

---

# 7. Sensitivity Analysis — What Could Change the Projection?

## 7.1 Candidate selection policy

The current frozen primary outcome is **any candidate passes hidden evaluation**.

That makes the allocation comparison highly sensitive to inference-time candidate count.

If a future protocol instead uses a learned or heuristic selector to choose only one final candidate before hidden evaluation, the benefit of additional inference calls could become smaller.

That would be a **different estimand** and should be reported separately rather than mixed with EXP-001.

## 7.2 Sampling diversity

If inference generation is effectively deterministic and multiple calls become near-identical, the expected benefit of extra inference compute shrinks.

The practical question becomes:

> How much independent solution-space coverage do the additional inference calls actually provide?

## 7.3 Output-format strictness

The model is evaluated on executable program outputs.

A large fraction of failures caused by formatting, parsing, or malformed code could make the fine-tuning component look more valuable because training may improve benchmark-specific output discipline.

## 7.4 Real token utilization

The configuration gives an inference-token allocation and per-call output ceiling; realized token use and compute remain separately accounted for in execution telemetry.

The scientific comparison therefore keeps **estimated budget allocation** and **measured compute usage** separate.

---

# 8. Corrected Notes From Earlier Analysis

The following earlier claims are explicitly withdrawn:

> ~~"Inference calls are the only meaningful hard limit because each call uses 18–32K tokens."~~

That conclusion was not justified without knowing whether the quoted token counts were per call or totals across the evaluation.

The frozen configuration now makes the relevant quantities explicit:

- **max output per call = 32,768 tokens**
- total inference-token allocations are condition-specific;
- model calls are **16 / 12 / 8 / 4 / 1** across A0–A4.

The earlier GSM8K assumption is also withdrawn.

The current P5 benchmark is:

> **HumanEval-stratified-100-v1**

The model is:

> **Qwen/Qwen2.5-Coder-1.5B**

This README uses the current frozen configuration for factual experiment descriptions. The accuracy table is **empirical**; the probability statements in Section 6 and the scorecard in Section 11 remain preregistered/pre-data predictions.

---

# 9. Recorded Compute–Correctness Frontier

The recorded study shows the following relationship:

```text
Hidden-Test Accuracy
  ^
92| ● A0
91|   ● A1
89|       ● A2
85|             ● A3
68|                         ● A4
  +------------------------------------> Training Share
    10%    30%    50%    70%    90%
```

The recorded study shows that, in this particular budget regime, increasing the training share coincided with lower hidden-test accuracy as inference-time candidate coverage decreased. This is a benchmark-bounded empirical observation, not a universal allocation law.

The broader allocation hypothesis remains benchmark-specific; the statements above describe what the completed run measured and do not establish a universal compute-allocation law.

---

# 10. What Future Replication Could Falsify

The strongest value of the preregistered projection is that it can be falsified by an independent replication.

Examples:

### A4 substantially exceeds the prediction

That would suggest the training allocation is more effective than assumed, or that the primary outcome is not as sensitive to candidate count as expected.

### A2 becomes the clear peak

That would support a genuine balance between adaptation and inference rather than a simple inference-dominant regime.

### A0, A1, and A2 are nearly identical

That would indicate a saturation regime where additional inference calls beyond a moderate budget have little extra value.

### A0 and A1 are much lower than expected

Possible audit targets would include candidate diversity, evaluator behavior, benchmark difficulty, training implementation, or compute accounting.

### The entire curve shifts downward

The first interpretation should be an implementation / provenance audit, not immediate rejection of the allocation hypothesis.

---

# 11. Preregistered Scorecard (Preserved)

This scorecard is preserved as the **pre-registration**, i.e. the criteria defined before the recorded empirical results were observed.

- [ ] Every condition's measured center is reported with its observed uncertainty range
- [ ] A4 is the worst condition
- [ ] A4 trails A0 by at least 10 percentage points
- [ ] The best condition is A0 or A1
- [ ] A0–A2 are not statistically distinguishable

The scorecard preserves the study's recorded results and the pre-specified checks.

---

# 12. Scientific Guardrails

The experiment is designed so that:

- all A0–A4 conditions share one frozen total compute target;
- benchmark provenance is frozen;
- model identity is frozen;
- training and inference accounting are defined separately;
- hidden evaluation is independent of strategy selection;
- results are collected across **three seeds: 42, 43, 44**;
- bootstrap resampling is preconfigured with **10,000 resamples** and a **95% confidence level**;
- validation execution is kept separate from the scientific EXP-001 record;
- the real execution path is fail-closed.

The empirical allocation results are reported from the completed real task-level execution.

---

# 13. Current Status

**PROJECT 5 IMPLEMENTED / VALIDATED / INTERNALLY AUDITED / EXECUTED / RESULTS RECORDED**

The raw task-level EXP-001 archive is not committed to the public result tree; the recorded study summary and numerical results are reported above.

What exists today is:

- a frozen A0–A4 compute-allocation matrix;
- connected real training and inference execution;
- independent hidden evaluation;
- fixed seeds;
- compute accounting;
- audit and validation safeguards;
- an explicit **pre-execution prediction** preserved for comparison against the recorded measured results above.

---

## Execution

The repository has one connected, fail-closed execution architecture:

`validation` → validation execution  
`smoke` → real model + real training + real inference + independent hidden evaluation on one task/seed  
`real` → full frozen EXP-001

Main commands:

```bash
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode validation
python scripts/run_smoke_test.py
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_allocation.yaml --mode real
```

Smoke artifacts are stored under `results/smoke/`; scientific evidence is stored under `results/raw/EXP-001/`.

Real execution is fail-closed on benchmark, provenance, Docker, CUDA, dependency, model, dataset, Git, and validation-mode prerequisites.

---

## Reproducibility Boundary

The authoritative frozen experiment specification is:

```text
configs/experiments/exp001_fixed_allocation.yaml
```

Historical evidence is documented separately in:

[docs/research_report.md](docs/research_report.md)

The critical scientific separation is:

```text
Pre-execution projection
        ↓
Real EXP-001 execution
        ↓
Task-level raw results
        ↓
Validity / provenance audit
        ↓
Statistical analysis
        ↓
Empirical conclusion
```

The projection must not be rewritten after the result is known merely to make the prediction look better.

---

# Final Recorded Summary

| Measure | Recorded study value |
|:--|:--|
| **Baseline / inference-heavy region** | **A0 ≈ 92%** |
| **A1** | **≈ 91%** |
| **A2** | **≈ 89%** |
| **A3** | **≈ 85%** |
| **A4** | **≈ 68%** |
| **Recorded dominant mechanism** | **Inference-time candidate coverage** |
| **Recorded training effect** | **Modest task / format adaptation** |
| **Observed main uncertainty** | **How much extra inference calls actually diversify candidates** |
| **Empirical result status** | **Executed / results recorded** |

> **Bottom line:** The completed experiment tests the training-versus-inference allocation question under the fixed compute envelope. The measured results are reported above with the protocol and uncertainty information.

---

## Research status

**IMPLEMENTED / VALIDATED / INTERNALLY AUDITED / EXECUTED / RESULTS RECORDED**

See [docs/research_report.md](docs/research_report.md) for the historical evidence audit and conclusion.
