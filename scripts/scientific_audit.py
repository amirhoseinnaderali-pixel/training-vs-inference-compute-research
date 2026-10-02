from pathlib import Path
import ast
from compute_research.config import load_config
c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
checks=[
 c.raw["status"]=="frozen",
 [r["condition_id"] for r in c.raw["allocation_matrix"]]==["A0","A1","A2","A3","A4"],
 all(abs(r["training_fraction"]+r["inference_fraction"]-1)<1e-9 for r in c.raw["allocation_matrix"]),
 c.raw["evaluation"]["hidden_results_visible_to_strategy"] is False,
 c.raw["evaluation"]["final_results_used_for_selection"] is False,
 c.raw["execution"]["allow_mock"] is False,
 c.raw["execution"]["fail_closed"] is True,
 c.raw["execution"]["require_credentials"] is False,
 "dataset_manifest_sha256" in c.raw["training"],
 Path("benchmarks/manifests/exp001_v1.json").exists(),
 Path("src/compute_research/runner.py").read_text().find("HuggingFaceSFTAdapter")>=0,
 Path("src/compute_research/runner.py").read_text().find("HuggingFaceInferenceAdapter")>=0,
]
for name,ok in zip(["frozen_matrix","condition_order","allocation_sum","hidden_isolation","final_selection_isolation","mock_blocked","fail_closed","public_hf_credential_policy","dataset_provenance","benchmark_manifest","real_training_adapter","real_inference_adapter","cli_runner","smoke_entrypoint","materialization_gate"],checks): print("PASS" if ok else "FAIL",name)
raise SystemExit(0 if all(checks) else 1)
