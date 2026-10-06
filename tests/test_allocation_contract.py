from compute_research.config import load_config

def test_every_allocation_stays_within_envelope():
    c=load_config("configs/experiments/exp001_fixed_allocation.yaml"); N=c.raw["model"]["parameter_count"]; E=c.raw["compute_budget"]["total_target_estimated_flops"]
    assert [x["condition_id"] for x in c.raw["allocation_matrix"]]==["A0","A1","A2","A3","A4"]
    for r in c.raw["allocation_matrix"]:
        assert abs(r["training_fraction"]+r["inference_fraction"]-1)<1e-9
        assert 6*N*r["training_tokens"]+2*N*r["inference_tokens"]<=E
