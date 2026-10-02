from compute_research.config import load_config
from compute_research.evaluator import evaluate_hidden

def test_validation_is_separate():
    v=load_config("configs/validation.yaml"); r=load_config("configs/experiments/exp001_fixed_allocation.yaml")
    assert v.validation_only and v.raw["execution"]["allow_mock"]
    assert not r.validation_only and not r.raw["execution"]["allow_mock"]

def test_hidden_not_visible():
    seen={}
    def executor(candidate,tests): seen["tests"]=tests; return 1.0
    x=evaluate_hidden("t","candidate",["hidden"],executor)
    assert x.visible_score is None and x.hidden_exposed is False and seen["tests"]==["hidden"]
