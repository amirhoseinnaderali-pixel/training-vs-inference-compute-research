# Training vs Inference Compute — Historical Evidence Report

## Research question

Under a fixed total compute allowance, how should compute be allocated between training and inference to maximize objective performance?

## Portfolio status

COMPLETED — RECORDED EMPIRICAL STUDY

The current repository contains a hardened controlled instrument and the recorded EXP-001 empirical study for the training-vs-inference allocation question.

## Evidence audit

The current project defines a fixed allocation matrix (A0–A4) and a connected real-training/real-inference execution architecture. The repository status is explicitly: PROJECT 5 IMPLEMENTED / VALIDATED / INTERNALLY AUDITED / EXECUTED / RESULTS RECORDED.

The recorded EXP-001 empirical result set is used for the study.

### Historical lineage checked

Related earlier repositories include DistillLlama-Curriculum, Phi-to-Qwen-Knowledge-Distillation, Phi-4-to-Qwen-Knowledge-Distillation, and qwen-math-reasoning.

These repositories contain genuine training executions and/or evaluation artifacts, but they do not implement the P5 research design of comparing multiple training/inference allocations under one fixed total compute budget.

For example, qwen-math-reasoning preserves a real Qwen2.5-3B LoRA training run on GSM8K and separate base/fine-tuned evaluation outputs. That is valid historical training evidence, but it is not a controlled A0–A4 compute-allocation comparison.

Similarly, the curriculum/distillation repositories vary training procedures, datasets, models, or distillation objectives without holding total training-plus-inference compute fixed across allocation conditions.

## What can be claimed

The portfolio can honestly claim that:

- the fixed-allocation research question was formalized;
- A0–A4 allocation conditions were implemented;
- real training and real inference adapters were integrated;
- benchmark/provenance/statistical safeguards were added;
- the execution architecture was validated and internally audited.

## What cannot be claimed

The recorded study values are the A0–A4 results documented in the project record. They should be interpreted only within the evaluated benchmark and fixed-compute budget regime; they do not by themselves establish broad generalization.

## Conclusion

P5 is a completed empirical study of the target question, with explicit scope and reproducibility limitations.

The older training projects are useful lineage and evidence that real training work was performed, but using their results as P5 findings would change the research question. They are therefore not promoted into P5 empirical results.

## Reproducibility boundary

The current P5 repository is the authoritative implementation of the target experiment. The recorded A0–A4 numerical results are preserved in the project documentation; future replications should use raw A0–A4 result files generated under the frozen budget and provenance controls.