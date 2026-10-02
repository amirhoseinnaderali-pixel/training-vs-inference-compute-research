from dataclasses import dataclass,asdict
from pathlib import Path
import json
from .hashing import sha256_json

@dataclass(frozen=True)
class ResultRecord:
    experiment_id:str; run_id:str; condition_id:str; task_id:str; seed:int
    git_sha:str; config_hash:str; benchmark_hash:str; model_version:str
    training_budget:dict; inference_budget:dict; compute:dict; final_evaluation:dict; status:str

def write_result(root:Path,record:ResultRecord):
    out=root/record.experiment_id/record.run_id
    out.mkdir(parents=True,exist_ok=False)
    payload=asdict(record); payload["result_hash"]=sha256_json(payload)
    name=f"{record.condition_id}__{record.task_id}__seed{record.seed}.json"
    (out/name).write_text(json.dumps(payload,indent=2,sort_keys=True))
