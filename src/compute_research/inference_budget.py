from dataclasses import dataclass
from .budget import BudgetViolation

@dataclass
class InferenceAccount:
    token_budget:int
    max_calls:int
    max_candidates:int
    max_rounds:int
    max_wall_seconds:float
    input_tokens:int=0
    output_tokens:int=0
    calls:int=0
    candidates:int=0
    rounds:int=0
    wall_seconds:float=0.0

    def reserve(self,input_tokens,output_tokens,candidates=1,rounds=1,wall_seconds=0):
        total=self.input_tokens+self.output_tokens+input_tokens+output_tokens
        if self.calls+1>self.max_calls:
            raise BudgetViolation("inference","model_calls",self.calls+1,self.max_calls)
        if total>self.token_budget:
            raise BudgetViolation("inference","total_tokens",total,self.token_budget)
        if self.candidates+candidates>self.max_candidates:
            raise BudgetViolation("inference","candidates",self.candidates+candidates,self.max_candidates)
        if self.rounds+rounds>self.max_rounds:
            raise BudgetViolation("inference","reasoning_rounds",self.rounds+rounds,self.max_rounds)
        if self.wall_seconds+wall_seconds>self.max_wall_seconds:
            raise BudgetViolation("inference","wall_seconds",self.wall_seconds+wall_seconds,self.max_wall_seconds)
        self.input_tokens+=input_tokens
        self.output_tokens+=output_tokens
        self.calls+=1
        self.candidates+=candidates
        self.rounds+=rounds
        self.wall_seconds+=wall_seconds

    @property
    def total_tokens(self): return self.input_tokens+self.output_tokens
