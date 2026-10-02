from dataclasses import dataclass
import os,shutil
from pathlib import Path
@dataclass(frozen=True)
class Gate:
    name:str; ok:bool; detail:str
def real_readiness(config,benchmark_present):
    raw=config.raw
    public_hf=not raw["execution"].get("require_credentials",False)
    return [
      Gate("benchmark",benchmark_present,"materialized benchmark required"),
      Gate("hidden_store",Path("benchmarks/programming/exp001_v1/hidden_tests.jsonl").exists(),"evaluator-only hidden store required"),
      Gate("credentials",public_hf or bool(os.getenv("HF_TOKEN")),"HF credential required only for gated/private resources"),
      Gate("docker",shutil.which("docker") is not None,"Docker sandbox required for hidden execution"),
      Gate("mock_disabled",not raw["execution"]["allow_mock"],"mock must be disabled"),
      Gate("validation_disabled",not config.validation_only,"real config required"),
      Gate("model_frozen",raw["model"]["model_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION" and raw["model"]["initialization_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION","model revision must be frozen"),
      Gate("dataset_frozen",raw["training"]["dataset_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION" and raw["training"]["dataset_manifest_sha256"] is not None,"dataset provenance must be frozen"),
      Gate("git",bool(os.getenv("GITHUB_SHA")) or Path(".git").exists(),"git SHA must be resolvable")
    ]
def assert_ready(gates):
    bad=[g for g in gates if not g.ok]
    if bad: raise RuntimeError("REAL EXECUTION BLOCKED: "+"; ".join(g.name+": "+g.detail for g in bad))
