from pathlib import Path
import json
REQUIRED={"base_model_id","model_revision","tokenizer_revision","training_dataset_id","training_dataset_revision","dataset_manifest_sha256","training_config_hash","allocation_condition","seed","git_sha","training_budget","realized_compute"}
def validate_checkpoint(path:Path):
    p=path/"provenance.json"
    if not p.exists(): raise ValueError("checkpoint provenance missing")
    data=json.loads(p.read_text()); missing=REQUIRED-set(data)
    if missing: raise ValueError(f"checkpoint provenance missing: {sorted(missing)}")
    return data
