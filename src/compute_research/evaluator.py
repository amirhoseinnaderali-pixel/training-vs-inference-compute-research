from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class EvaluationResult:
    task_id:str; visible_score:float|None; hidden_score:float|None; evaluator_id:str; hidden_exposed:bool=False

def evaluate_hidden(task_id,candidate,hidden_tests,executor:Callable[[str,list[str]],float]):
    return EvaluationResult(task_id,None,executor(candidate,hidden_tests),"independent_hidden_executor_v1",False)
