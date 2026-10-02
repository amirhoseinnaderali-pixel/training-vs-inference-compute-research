from compute_research.config import load_config
from compute_research.readiness import real_readiness

def test_concrete_model_and_dataset_are_frozen():
    c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
    assert c.raw["model"]["model_id"].startswith("Qwen/")
    assert c.raw["training"]["dataset_id"]=="open-r1/codeforces-cots"
    assert c.raw["training"]["dataset_version"].endswith("387653d830af3c298723ce21826c39877b50b783")

def test_missing_benchmark_blocks_real():
    c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
    assert any(g.name=="benchmark" and not g.ok for g in real_readiness(c,False))
