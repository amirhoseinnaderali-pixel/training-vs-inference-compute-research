import sys
from pathlib import Path
import importlib.util
import pytest

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"src"))

def _load_script(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/"scripts"/f"{name}.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_cli_real_mode_is_connected_to_runner(monkeypatch):
    cli=_load_script("run_experiment")
    seen=[]
    monkeypatch.setattr(cli,"run_experiment",lambda config: seen.append(config) or ["run"])
    monkeypatch.setattr(sys,"argv",[
        "run_experiment.py","--config",
        "configs/experiments/exp001_fixed_allocation.yaml","--mode","real"
    ])
    cli.main()
    assert seen==["configs/experiments/exp001_fixed_allocation.yaml"]

def test_cli_validation_mode_uses_requested_validation_config(monkeypatch):
    cli=_load_script("run_experiment")
    seen=[]
    monkeypatch.setitem(
        sys.modules,
        "run_validation",
        type("M",(),{"main":lambda path: seen.append(path)})(),
    )
    monkeypatch.setattr(sys,"argv",[
        "run_experiment.py","--config","configs/validation.yaml","--mode","validation"
    ])
    cli.main()
    assert seen==["configs/validation.yaml"]

def test_smoke_entrypoint_is_real_runner(monkeypatch):
    smoke=_load_script("run_smoke_test")
    seen=[]
    monkeypatch.setattr(
        smoke,"run_smoke",
        lambda config,condition,seed: seen.append((config,condition,seed)) or "ok",
    )
    monkeypatch.setattr(sys,"argv",["run_smoke_test.py"])
    smoke.main()
    assert seen==[("configs/experiments/exp001_fixed_allocation.yaml","A0",42)]

def test_real_runner_requires_materialized_benchmark(monkeypatch):
    from compute_research.runner import run_one
    monkeypatch.chdir(ROOT)
    with pytest.raises(RuntimeError,match="materialized benchmark"):
        run_one("configs/experiments/exp001_fixed_allocation.yaml","A0",42)

def test_failure_taxonomy_is_not_incorrect_answer():
    from compute_research.runner import _failure_status
    from compute_research.budget import BudgetViolation
    assert _failure_status(BudgetViolation("inference","tokens",11,10))=="ineligible_budget"
    assert _failure_status(RuntimeError("Docker daemon unavailable"))=="evaluation_failure"
    assert _failure_status(RuntimeError("model load failed"))=="model_failure"

def test_hidden_store_never_enters_model_facing_rows():
    from compute_research.benchmark import load_model_tasks
    bench=ROOT/"benchmarks/programming/exp001_v1/tasks.jsonl"
    manifest=ROOT/"benchmarks/manifests/exp001_v1.json"
    if not bench.exists():
        pytest.skip("materialized benchmark intentionally absent in repository")
    rows=load_model_tasks(bench,manifest)
    assert all(not hasattr(t,"hidden_tests") for t in rows)
