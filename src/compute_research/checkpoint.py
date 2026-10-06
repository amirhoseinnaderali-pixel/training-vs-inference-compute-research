from pathlib import Path
import json

REQUIRED = {
    "base_model_id","model_revision","tokenizer_revision","training_dataset_id",
    "training_dataset_revision","dataset_manifest_sha256","training_config_hash",
    "allocation_condition","seed","git_sha","training_budget","realized_compute",
}

def validate_checkpoint(path: Path, expected: dict | None = None):
    provenance_path = path / "provenance.json"
    if not provenance_path.exists():
        raise ValueError("checkpoint provenance missing")
    data = json.loads(provenance_path.read_text())
    missing = REQUIRED - set(data)
    if missing:
        raise ValueError(f"checkpoint provenance missing: {sorted(missing)}")

    if expected:
        for key, expected_value in expected.items():
            if data.get(key) != expected_value:
                raise ValueError(
                    f"checkpoint provenance mismatch for {key}: "
                    f"{data.get(key)!r} != {expected_value!r}"
                )

    realized = data.get("realized_compute") or {}
    budget = data.get("training_budget") or {}
    if realized.get("training_tokens") != data.get("training_tokens"):
        raise ValueError("checkpoint realized token provenance is inconsistent")
    if realized.get("optimizer_steps") != data.get("optimizer_steps"):
        raise ValueError("checkpoint realized step provenance is inconsistent")
    if realized.get("estimated_training_flops") != data.get("estimated_training_flops"):
        raise ValueError("checkpoint realized FLOP provenance is inconsistent")
    if budget.get("tokens") != data.get("training_tokens"):
        raise ValueError("checkpoint token provenance conflicts with declared training budget")
    return data
