from compute_research.config import load_config
from compute_research.benchmark import synthetic_validation_benchmark
from compute_research.training import TrainingConfig,MockTrainingAdapter
from compute_research.inference import InferenceConfig,MockInferenceAdapter
from compute_research.budget import TrainingBudget,InferenceBudget

cfg=load_config("configs/validation.yaml")
assert cfg.validation_only
bench=synthetic_validation_benchmark()
for row in cfg.raw["allocation_matrix"]:
    tb=TrainingBudget(4,128,1000000,999)
    ib=InferenceBudget(4,128,128,4,2,0,999)
    if row["training_budget_steps"]:
        MockTrainingAdapter().train(TrainingConfig("mock-tiny","v1",1000,"synthetic-validation","v1",None,1,1,"SGD",None,"constant","fp32",42),tb)
    MockInferenceAdapter().generate("validation prompt",InferenceConfig("mock-tiny",16,min(2,row["inference_model_calls"]),1,42),ib)
print("VALIDATION ONLY PASS:",len(bench.tasks),"synthetic tasks; no scientific results created.")
