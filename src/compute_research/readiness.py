from dataclasses import dataclass
import os,shutil,subprocess
from pathlib import Path

@dataclass(frozen=True)
class Gate:
    name:str
    ok:bool
    detail:str

def _cuda_available():
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False

def _real_dependencies():
    try:
        import torch,transformers,datasets,accelerate,safetensors
        return True,"torch/transformers/datasets/accelerate/safetensors importable"
    except Exception as e:
        return False,f"real dependency import failed: {e}"

def _docker_ready():
    exe=shutil.which("docker")
    if not exe: return False,"docker executable missing"
    try:
        subprocess.run([exe,"info"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=10)
        return True,"Docker daemon reachable"
    except Exception as e:
        return False,f"Docker daemon unavailable: {e}"

def real_readiness(config,benchmark_present):
    raw=config.raw
    deps_ok,deps_detail=_real_dependencies()
    docker_ok,docker_detail=_docker_ready()
    public_hf=not raw["execution"].get("require_credentials",False)
    return [
      Gate("benchmark",benchmark_present,"materialized benchmark required"),
      Gate("hidden_store",Path("benchmarks/programming/exp001_v1/hidden_tests.jsonl").exists(),"evaluator-only hidden store required"),
      Gate("credentials",public_hf or bool(os.getenv("HF_TOKEN")),"HF credential required only for gated/private resources"),
      Gate("docker",docker_ok,docker_detail),
      Gate("cuda",not raw["execution"].get("require_cuda",False) or _cuda_available(),"CUDA accelerator required by frozen real runtime"),
      Gate("dependencies",deps_ok,deps_detail),
      Gate("mock_disabled",not raw["execution"]["allow_mock"],"mock must be disabled"),
      Gate("validation_disabled",not config.validation_only,"real config required"),
      Gate("model_frozen",raw["model"]["model_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION" and raw["model"]["initialization_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION","model revision must be frozen"),
      Gate("dataset_frozen",raw["training"]["dataset_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION" and raw["training"]["dataset_manifest_sha256"] is not None,"dataset provenance must be frozen"),
      Gate("git",bool(os.getenv("GITHUB_SHA")) or Path(".git").exists(),"git SHA must be resolvable"),
      Gate("fail_closed",raw["execution"]["fail_closed"] is True,"fail_closed must be enabled")
    ]

def assert_ready(gates):
    bad=[g for g in gates if not g.ok]
    if bad: raise RuntimeError("REAL EXECUTION BLOCKED: "+"; ".join(g.name+": "+g.detail for g in bad))
