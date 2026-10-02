from dataclasses import dataclass
from pathlib import Path
import subprocess,tempfile,json

@dataclass(frozen=True)
class EvaluationResult:
    task_id:str; hidden_score:float; evaluator_id:str; hidden_exposed:bool=False

class DockerHiddenEvaluator:
    def __init__(self,hidden_store:Path,timeout_seconds:int=30):
        self.hidden_store=hidden_store; self.timeout_seconds=timeout_seconds
    def _hidden(self,task_id):
        for line in self.hidden_store.read_text().splitlines():
            if line.strip():
                row=json.loads(line)
                if row["task_id"]==task_id: return row["hidden_tests"]
        raise KeyError(task_id)
    def evaluate(self,task,candidate:str)->EvaluationResult:
        hidden=self._hidden(task.task_id)
        script="import resource\n"+candidate+"\n"+hidden+f"\ncheck({task.entry_point})\n"
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"eval.py"; p.write_text(script)
            cmd=["docker","run","--rm","--network","none","--cpus","1","--memory","512m","--pids-limit","64","-v",f"{d}:/work:ro","python:3.12-slim","python","/work/eval.py"]
            try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:return EvaluationResult(task.task_id,0.0,"independent_hidden_executor_v1",False)
            return EvaluationResult(task.task_id,1.0 if r.returncode==0 else 0.0,"independent_hidden_executor_v1",False)
