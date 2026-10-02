from dataclasses import dataclass
from pathlib import Path
import subprocess,tempfile

@dataclass(frozen=True)
class EvaluationResult:
    task_id:str; visible_score:float|None; hidden_score:float; evaluator_id:str; hidden_exposed:bool=False

class DockerHiddenEvaluator:
    def __init__(self,timeout_seconds:int=30): self.timeout_seconds=timeout_seconds
    def evaluate_task(self,task,candidate:str)->EvaluationResult:
        if task.hidden_tests.strip()=="" or task.visible_tests.strip()=="": raise ValueError("evaluation split missing")
        script="import resource\n"+candidate+"\n"+task.hidden_tests+f"\ncheck({task.entry_point})\n"
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"eval.py"; p.write_text(script)
            cmd=["docker","run","--rm","--network","none","--cpus","1","--memory","512m","--pids-limit","64","-v",f"{d}:/work:ro","python:3.12-slim","python","/work/eval.py"]
            try: r=subprocess.run(cmd,capture_output=True,text=True,timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired: return EvaluationResult(task.task_id,None,0.0,"independent_hidden_executor_v1",False)
            return EvaluationResult(task.task_id,None,1.0 if r.returncode==0 else 0.0,"independent_hidden_executor_v1",False)
