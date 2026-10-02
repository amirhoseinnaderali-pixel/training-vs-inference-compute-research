from dataclasses import dataclass
import os, shutil

@dataclass(frozen=True)
class Gate:
    name:str; ok:bool; detail:str

def real_readiness(config,benchmark_present):
    return [
        Gate("benchmark",benchmark_present,"materialized benchmark required"),
        Gate("credentials",bool(os.getenv("OPENAI_API_KEY")),"credential required"),
        Gate("docker",shutil.which("docker") is not None,"docker executable required"),
        Gate("mock_disabled",not config.raw["execution"]["allow_mock"],"mock must be disabled"),
        Gate("validation_disabled",not config.validation_only,"real config required"),
        Gate("model_frozen",config.raw["model"]["model_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION","model must be frozen"),
        Gate("dataset_frozen",config.raw["training"]["dataset_id"]!="TO_BE_FROZEN_BEFORE_EXECUTION","dataset must be frozen")
    ]

def assert_ready(gates):
    bad=[g for g in gates if not g.ok]
    if bad: raise RuntimeError("REAL EXECUTION BLOCKED: "+"; ".join(g.name+": "+g.detail for g in bad))
