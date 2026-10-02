from pathlib import Path
from compute_research.config import load_config

c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
runner=Path("src/compute_research/runner.py").read_text()
results=Path("src/compute_research/results.py").read_text()
checks=[
    c.raw["status"]=="frozen",
    [r["condition_id"] for r in c.raw["allocation_matrix"]]==["A0","A1","A2","A3","A4"],
    all(abs(r["training_fraction"]+r["inference_fraction"]-1)<1e-9 for r in c.raw["allocation_matrix"]),
    c.raw["evaluation"]["primary_outcome"]["estimand"]=="any_candidate_passes_hidden",
    c.raw["evaluation"]["hidden_results_visible_to_strategy"] is False,
    c.raw["evaluation"]["final_results_used_for_selection"] is False,
    c.raw["execution"]["allow_mock"] is False,
    c.raw["execution"]["fail_closed"] is True,
    c.raw["execution"]["require_credentials"] is False,
    "dataset_manifest_sha256" in c.raw["training"],
    Path("benchmarks/manifests/exp001_v1.json").exists(),
    "HuggingFaceSFTAdapter" in runner,
    "HuggingFaceInferenceAdapter" in runner,
    "run_experiment" in Path("scripts/run_experiment.py").read_text(),
    "run_smoke" in Path("scripts/run_smoke_test.py").read_text(),
    "verify_materialized" in runner,
    "eligible_for_analysis" in results,
    "selection_hidden_blind" in runner,
    "evals=[evaluator.evaluate" in runner,
    "optimizer_step" in Path("src/compute_research/real_adapters.py").read_text(),
]
names=[
    "frozen_matrix","condition_order","allocation_sum","primary_estimand",
    "hidden_isolation","final_selection_isolation","mock_blocked","fail_closed",
    "public_hf_credential_policy","dataset_provenance","benchmark_manifest",
    "real_training_adapter","real_inference_adapter","cli_runner","smoke_entrypoint",
    "materialization_gate","result_eligibility","hidden_blind_marker",
    "hidden_evaluation_after_generation","optimizer_step_guard",
]
for name,ok in zip(names,checks):
    print("PASS" if ok else "FAIL",name)
raise SystemExit(0 if all(checks) else 1)
