import pytest
from compute_research.config import load_config
from compute_research.budget import TrainingBudget,InferenceBudget,BudgetViolation
from compute_research.accounting import Quantity,ComputeRecord

def test_frozen_allocation():
    c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
    assert c.raw["status"]=="frozen"
    assert all(abs(r["training_fraction"]+r["inference_fraction"]-1)<1e-9 for r in c.raw["allocation_matrix"])

def test_training_budget():
    b=TrainingBudget(1,10,100,10); b.add(1,10,100)
    with pytest.raises(BudgetViolation): b.add(1)

def test_inference_retry_budget():
    b=InferenceBudget(2,100,100,2,2,0,10); b.add(calls=1,candidates=1); b.add(calls=1,candidates=1)
    with pytest.raises(BudgetViolation): b.add(calls=1)

def test_unavailable():
    with pytest.raises(ValueError): Quantity(1,"unavailable")

def test_total_flops():
    q=lambda v,s: Quantity(v,s)
    r=ComputeRecord(q(1,"measured"),q(1,"measured"),q(1,"measured"),q(100,"estimated"),q(50,"estimated"),q(150,"derived"),q(1,"measured"),q(1,"measured"),q(1,"measured"),q(0,"measured"),q(1,"measured"),q(1,"measured"),q(2,"derived"),q(None,"unavailable"))
    r.validate()
