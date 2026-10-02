from dataclasses import dataclass
from .budget import InferenceBudget

@dataclass(frozen=True)
class InferenceConfig:
    model_id:str; max_output_tokens:int; candidates:int; reasoning_rounds:int; seed:int

@dataclass
class InferenceRun:
    outputs:list[str]; budget:InferenceBudget; mode:str

class InferenceAdapter:
    def generate(self,prompt,cfg,budget): raise NotImplementedError

class MockInferenceAdapter(InferenceAdapter):
    def generate(self,prompt,cfg:InferenceConfig,budget:InferenceBudget):
        n=min(cfg.candidates,budget.max_candidates)
        budget.add(calls=n,input_tokens=len(prompt.split())*n,output_tokens=4*n,candidates=n,rounds=min(cfg.reasoning_rounds,n))
        return InferenceRun([f"validation-output-{cfg.seed}-{i}" for i in range(n)],budget,"validation")
