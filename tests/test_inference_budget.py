import pytest
from compute_research.inference_budget import InferenceAccount
from compute_research.budget import BudgetViolation

def test_hard_inference_limits():
    a=InferenceAccount(10,2,2,2,10); a.reserve(2,3)
    a.reserve(2,3)
    with pytest.raises(BudgetViolation): a.reserve(1,1)
    assert a.total_tokens==10
