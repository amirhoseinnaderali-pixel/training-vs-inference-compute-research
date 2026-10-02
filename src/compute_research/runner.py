from pathlib import Path
import os,time,uuid,json,subprocess
from .config import load_config
from .benchmark import load_materialized
from .readiness import real_readiness,assert_ready
from .real_adapters import HuggingFaceSFTAdapter,HuggingFaceInferenceAdapter
from .inference_budget import InferenceAccount
from .evaluator import DockerHiddenEvaluator
from .results import ResultRecord,write_result
from .checkpoint import validate_checkpoint
from .hashing import sha256_json

def git_sha():
    v=os.getenv("GITHUB_SHA")
    if v: return v
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception: raise RuntimeError("git SHA unavailable")

def run_one(config_path,condition_id,seed,task_limit=None):
    cfg=load_config(config_path); raw=cfg.raw; root=Path(".")
    bench_path=root/"benchmarks/programming/exp001_v1/tasks.jsonl"; manifest=root/"benchmarks/manifests/exp001_v1.json"
    benchmark=load_materialized(bench_path,manifest)
    assert_ready(real_readiness(cfg,True))
    cond=next(x for x in raw["allocation_matrix"] if x["condition_id"]==condition_id)
    run_id=f"{condition_id}-seed{seed}-{uuid.uuid4().hex[:10]}"; started=time.time(); results=[]
    train_dir=root/"results/checkpoints"/raw["experiment_id"]/run_id
    train=HuggingFaceSFTAdapter().train(
      model_id=raw["model"]["model_id"],revision=raw["model"]["initialization_id"],dataset_id=raw["training"]["dataset_id"],
      dataset_revision=raw["training"]["dataset_version"].split("@")[-1],dataset_config="solutions_py_decontaminated",output_dir=str(train_dir),
      token_budget=cond["training_tokens"],max_steps=cond["training_budget_steps"],batch_size=raw["training"]["batch_size"],
      gradient_accumulation=raw["training"]["gradient_accumulation"],sequence_length=raw["training"]["sequence_length"],learning_rate=raw["training"]["learning_rate"],seed=seed,
      max_flops=cond["training_estimated_flops"],max_wall_seconds=raw["training"]["max_wall_seconds"],
      provenance={"base_model_id":raw["model"]["model_id"],"model_revision":raw["model"]["initialization_id"],"tokenizer_revision":raw["model"]["initialization_id"],"training_dataset_id":raw["training"]["dataset_id"],"training_dataset_revision":raw["training"]["dataset_version"],"dataset_manifest_sha256":raw["training"]["dataset_manifest_sha256"],"training_config_hash":cfg.config_hash,"allocation_condition":condition_id,"seed":seed,"git_sha":git_sha(),"training_budget":{"tokens":cond["training_tokens"],"steps":cond["training_budget_steps"],"estimated_flops":cond["training_estimated_flops"]},"realized_compute":{}}
    )
    validate_checkpoint(Path(train["checkpoint"]))
    model=HuggingFaceInferenceAdapter(raw["model"]["model_id"],raw["model"]["initialization_id"],train["checkpoint"])
    account=InferenceAccount(cond["inference_tokens"],cond["inference_model_calls"],raw["inference"]["max_candidates"],raw["inference"]["max_reasoning_rounds"],raw["inference"]["max_wall_seconds"])
    evaluator=DockerHiddenEvaluator()
    tasks=benchmark.tasks if task_limit is None else benchmark.tasks[:task_limit]
    for task in tasks:
        candidates=[]
        for _ in range(cond["inference_model_calls"]):
            out=model.generate(task.prompt,raw["inference"]["max_output_tokens_per_call"],seed)
            account.reserve(out["input_tokens"],out["output_tokens"],1,1,out["wall_seconds"])
            candidates.append(out["text"])
        # Candidate selection is deterministic and hidden-blind: choose the first generated candidate.
        ev=evaluator.evaluate_task(task,candidates[0])
        results.append(ResultRecord(raw["experiment_id"],run_id,condition_id,task.task_id,seed,git_sha(),cfg.config_hash,benchmark.manifest_hash,raw["model"]["initialization_id"],{"planned_tokens":cond["training_tokens"],"planned_steps":cond["training_budget_steps"]},{"planned_tokens":cond["inference_tokens"],"planned_calls":cond["inference_model_calls"]},{"training_tokens":train["training_tokens"],"inference_input_tokens":account.input_tokens,"inference_output_tokens":account.output_tokens,"total_flops":{"value":train["estimated_training_flops"]+2*raw["model"]["parameter_count"]*account.total_tokens,"status":"estimated"},"optimizer_steps":train["optimizer_steps"],"model_calls":account.calls,"candidates":account.candidates,"execution_steps":0,"training_wall_seconds":train["training_wall_seconds"],"inference_wall_seconds":account.wall_seconds,"total_wall_seconds":time.time()-started,"monetary_cost_proxy":{"value":None,"status":"unavailable"}}, {"hidden_correct":ev.hidden_score,"evaluator_id":ev.evaluator_id,"hidden_exposed":False},"complete"))
    for r in results: write_result(root/"results/raw",r)
    return results
