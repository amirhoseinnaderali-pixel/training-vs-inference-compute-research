from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from .hashing import sha256_json

@dataclass(frozen=True)
class Config:
    raw: dict[str, Any]
    config_hash: str
    @property
    def experiment_id(self): return self.raw["experiment_id"]
    @property
    def validation_only(self): return bool(self.raw["execution"]["validation_only"])

def load_config(path: str) -> Config:
    raw = yaml.safe_load(Path(path).read_text())
    validate_config(raw)
    return Config(raw, sha256_json(raw))

def validate_config(c: dict[str, Any]) -> None:
    required={"experiment_id","model","benchmark","training","inference","allocation_matrix","seeds","execution"}
    missing=required-set(c)
    if missing: raise ValueError(f"missing sections: {sorted(missing)}")
    if not c["seeds"]: raise ValueError("at least one seed is required")
    seen=set()
    for r in c["allocation_matrix"]:
        cid=r["condition_id"]
        if cid in seen: raise ValueError(f"duplicate condition: {cid}")
        seen.add(cid)
        if abs(float(r["training_fraction"])+float(r["inference_fraction"])-1.0)>1e-9: raise ValueError(f"{cid}: fractions must sum to 1")
        if r["training_budget_steps"]<0 or r["inference_model_calls"]<1: raise ValueError(f"{cid}: invalid budget")
    if c["execution"]["validation_only"] and c["experiment_id"].startswith("EXP-"): raise ValueError("scientific experiment cannot be validation_only")
    if not c["execution"]["validation_only"] and c["execution"]["allow_mock"]: raise ValueError("real config cannot allow mock")
