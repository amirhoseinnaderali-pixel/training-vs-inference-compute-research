import json
from pathlib import Path

import pytest

from compute_research.budget import BudgetViolation
from compute_research.checkpoint import validate_checkpoint
from compute_research.real_adapters import _require_step_capacity
from compute_research.stats import paired_differences,summarize

def test_optimizer_step_guard_fails_before_step():
    with pytest.raises(BudgetViolation,match="optimizer_steps"):
        _require_step_capacity(3,3)

def test_checkpoint_provenance_is_bound(tmp_path:Path):
    cp=tmp_path/"checkpoint"
    cp.mkdir()
    data={
        "base_model_id":"model",
        "model_revision":"rev",
        "tokenizer_revision":"rev",
        "training_dataset_id":"dataset",
        "training_dataset_revision":"dataset@rev",
        "dataset_manifest_sha256":"dataset-hash",
        "training_config_hash":"cfg",
        "allocation_condition":"A0",
        "seed":42,
        "git_sha":"git",
        "training_budget":{"tokens":10,"steps_max":2,"estimated_flops":60},
        "realized_compute":{"training_tokens":10,"optimizer_steps":1,"estimated_training_flops":60},
        "training_tokens":10,
        "optimizer_steps":1,
        "estimated_training_flops":60,
        "checkpoint_id":"checkpoint",
    }
    (cp/"provenance.json").write_text(json.dumps(data))
    checked=validate_checkpoint(cp,{
        "allocation_condition":"A0",
        "seed":42,
        "git_sha":"git",
        "training_config_hash":"cfg",
    })
    assert checked["checkpoint_id"]=="checkpoint"
    with pytest.raises(ValueError,match="allocation_condition"):
        validate_checkpoint(cp,{"allocation_condition":"A1"})

def test_analysis_uses_registered_nested_primary_outcome():
    rows=[
        {"condition_id":"A0","task_id":"t","seed":42,
         "final_evaluation":{"primary_outcome":"any_candidate_passes_hidden","primary_outcome_value":True}},
        {"condition_id":"A1","task_id":"t","seed":42,
         "final_evaluation":{"primary_outcome":"any_candidate_passes_hidden","primary_outcome_value":False}},
    ]
    assert summarize(rows)["A0"]["correctness"]==1.0
    assert paired_differences(rows)["A1"]==[-1]
