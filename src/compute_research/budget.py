from dataclasses import dataclass

@dataclass
class BudgetViolation(Exception):
    scope: str; metric: str; observed: float; limit: float
    def __str__(self): return f"{self.scope} budget exceeded: {self.metric}={self.observed} > {self.limit}"

@dataclass
class TrainingBudget:
    max_steps:int; max_tokens:int; max_flops:int; max_wall_seconds:float
    steps:int=0; tokens:int=0; flops:int=0; wall_seconds:float=0
    def add(self, steps=0,tokens=0,flops=0,wall_seconds=0):
        new=(self.steps+steps,self.tokens+tokens,self.flops+flops,self.wall_seconds+wall_seconds)
        for n,v,l in zip(("steps","tokens","flops","wall_seconds"),new,(self.max_steps,self.max_tokens,self.max_flops,self.max_wall_seconds)):
            if v>l: raise BudgetViolation("training",n,v,l)
        self.steps,self.tokens,self.flops,self.wall_seconds=new

@dataclass
class InferenceBudget:
    max_calls:int; max_input_tokens:int; max_output_tokens:int; max_candidates:int; max_rounds:int; max_verifier_calls:int; max_wall_seconds:float
    calls:int=0; input_tokens:int=0; output_tokens:int=0; candidates:int=0; rounds:int=0; verifier_calls:int=0; wall_seconds:float=0
    def add(self,calls=0,input_tokens=0,output_tokens=0,candidates=0,rounds=0,verifier_calls=0,wall_seconds=0):
        new=(self.calls+calls,self.input_tokens+input_tokens,self.output_tokens+output_tokens,self.candidates+candidates,self.rounds+rounds,self.verifier_calls+verifier_calls,self.wall_seconds+wall_seconds)
        limits=(self.max_calls,self.max_input_tokens,self.max_output_tokens,self.max_candidates,self.max_rounds,self.max_verifier_calls,self.max_wall_seconds)
        for n,v,l in zip(("calls","input_tokens","output_tokens","candidates","rounds","verifier_calls","wall_seconds"),new,limits):
            if v>l: raise BudgetViolation("inference",n,v,l)
        self.calls,self.input_tokens,self.output_tokens,self.candidates,self.rounds,self.verifier_calls,self.wall_seconds=new
