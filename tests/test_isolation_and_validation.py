import json
from pathlib import Path
from compute_research.config import load_config
from compute_research.benchmark import load_model_tasks
from compute_research.evaluator import DockerHiddenEvaluator

def test_validation_is_separate():
    v=load_config("configs/validation.yaml"); r=load_config("configs/experiments/exp001_fixed_allocation.yaml")
    assert v.validation_only and v.raw["execution"]["allow_mock"]
    assert not r.validation_only and not r.raw["execution"]["allow_mock"]

def test_model_facing_benchmark_contains_no_hidden_tests(tmp_path:Path):
    p=tmp_path/"tasks.jsonl"; p.write_text(json.dumps({"task_id":"t","prompt":"x","entry_point":"f","visible_tests":"v","task_sha256":"a","test_sha256":"b"})+"\n")
    m=tmp_path/"manifest.json"; m.write_text(json.dumps({"task_count":1,"tasks":[{"task_id":"t","task_sha256":"a","test_sha256":"b"}]}))
    tasks=load_model_tasks(p,m)
    assert not hasattr(tasks[0],"hidden_tests")

def test_hidden_store_is_only_loaded_by_evaluator(tmp_path:Path):
    h=tmp_path/"hidden.jsonl"; h.write_text(json.dumps({"task_id":"t","hidden_tests":"def check(candidate):\n    assert candidate()==1","test_sha256":"b"})+"\n")
    ev=DockerHiddenEvaluator(h)
    assert ev._hidden("t").startswith("def check")
