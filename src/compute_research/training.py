from dataclasses import dataclass
from .budget import TrainingBudget

@dataclass(frozen=True)
class TrainingConfig:
    base_model:str; model_version:str; parameter_count:int|None
    dataset_id:str; dataset_version:str; dataset_sha256:str|None
    batch_size:int|None; gradient_accumulation:int|None; optimizer:str
    learning_rate:float|None; scheduler:str; precision:str; seed:int

@dataclass
class TrainingRun:
    checkpoint_id:str; budget:TrainingBudget; mode:str

class TrainingAdapter:
    def train(self,cfg,budget): raise NotImplementedError

class MockTrainingAdapter(TrainingAdapter):
    def train(self,cfg:TrainingConfig,budget:TrainingBudget):
        if cfg.dataset_id!="synthetic-validation": raise ValueError("mock training requires validation dataset")
        budget.add(steps=budget.max_steps,tokens=min(budget.max_tokens,budget.max_steps*32),flops=min(budget.max_flops,budget.max_steps*1000))
        return TrainingRun(f"mock-{cfg.seed}-{budget.steps}",budget,"validation")
