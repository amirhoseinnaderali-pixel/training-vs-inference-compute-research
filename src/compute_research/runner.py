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
from .budget import BudgetViolation

def git_sha():
    v=os.getenv("GITHUB_SHA")
    if v:return v
    try:return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception as e: raise RuntimeError("git SHA unavailable") from e

def run_one(config_path,condition_id,seed,task_limit=None):
    cfg=load_config(config_path); raw=cfg.raw; root=Path(".")
    bench_path=root/"benchmarks/programming/exp001_v1/tasks.jsonl"; manifest=root/"benchmarks/manifests/exp001_v1.json"
    if not bench_path.exists(): raise RuntimeError("real execution blocked: materialized benchmark missing")
    benchmark=load_materialized(bench_path,manifest); assert_ready(real_readiness(cfg,True))
    cond=next((x for x in raw["allocation_matrix"] if x["condition_id"]==condition_id),None)
    if cond is None: raise ValueError(condition_id)
    if abs(cond["training_fraction"]+cond["inference_fraction"]-1)>1e-9: raise ValueError("allocation fractions do not sum to one")
    run_id=f"{condition_id}-seed{seed}-{uuid.uuid4().hex[:10]}"; results_root=root/"results/raw"
    tasks=benchmark.tasks if task_limit is None else benchmark.tasks[:task_limit]
    evaluator=DockerHiddenEvaluator()
    for task in tasks:
        started=time.time(); checkpoint_id=""; status="complete"
        try:
            train_dir=root/"results/checkpoints"/raw["experiment_id"]/run_id/task.task_id.replace("/","_")
            train=HuggingFaceSFTAdapter().train(
              model_id=raw["model"]["model_id"],revision=raw["model"]["initialization_id"],dataset_id=raw["training"]["dataset_id"],
              dataset_revision=raw["training"]["dataset_version"].split("@")[-1],dataset_config="solutions_py_decontaminated",output_dir=str(train_dir),
              token_budget=cond["training_tokens"],max_steps=cond["training_budget_steps"],batch_size=raw["training"]["batch_size"],
              gradient_accumulation=raw["training"]["gradient_accumulation"],sequence_length=raw["training"]["sequence_length"],learning_rate=raw["training"]["learning_rate"],seed=seed,
              max_flops=cond["training_estimated_flops"],max_wall_seconds=raw["training"]["max_wall_seconds"],
              provenance={"base_model_id":raw["model"]["model_id"],"model_revision":raw["model"]["initialization_id"],"tokenizer_revision":raw["model"]["initialization_id"],"training_dataset_id":raw["training"]["dataset_id"],"training_dataset_revision":raw["training"]["dataset_version"],"dataset_manifest_sha256":raw["training"]["dataset_manifest_sha256"],"training_config_hash":cfg.config_hash,"allocation_condition":condition_id,"seed":seed,"git_sha":git_sha(),"training_budget":{"tokens":cond["training_tokens"],"steps_max":cond["training_budget_steps"],"estimated_flops":cond["training_estimated_flops"]},"realized_compute":{}}
            )
            cp=validate_checkpoint(Path(train["checkpoint"])); checkpoint_id=cp["checkpoint_id"]
            model=HuggingFaceInferenceAdapter(raw["model"]["model_id"],raw["model"]["initialization_id"],train["checkpoint"])
            account=InferenceAccount(cond["inference_tokens"],cond["inference_model_calls"],cond["inference_model_calls"],raw["inference"]["max_reasoning_rounds"],raw["inference"]["max_wall_seconds"])
            input_n=model.count_input_tokens(task.prompt)
            total_input=input_n*cond["inference_model_calls"]
            if total_input>=cond["inference_tokens"]: raise BudgetViolation("inference","input_tokens",total_input,cond["inference_tokens"]-1)
            remaining_output=cond["inference_tokens"]-total_input
            candidate_texts=[]; evals=[]
            for i in range(cond["inference_model_calls"]):
                quota=remaining_output//(cond["inference_model_calls"]-i)
                if quota<=0: raise BudgetViolation("inference","output_quota",quota,1)
                out=model.generate(task.prompt,min(quota,raw["inference"]["max_output_tokens_per_call"]),seed+i)
                if out["input_tokens"]+out["output_tokens"] != input_n+quota: raise RuntimeError("generation did not realize declared token quota")
                account.reserve(out["input_tokens"],out["output_tokens"],1,1,out["wall_seconds"]); candidate_texts.append(out["text"])
                evals.append(evaluator.evaluate_task(task,out["text"]))
                remaining_output-=out["output_tokens"]
            if account.total_tokens!=cond["inference_tokens"]: raise BudgetViolation("inference","token_budget_not_fully_consumed",account.total_tokens,cond["inference_tokens"])
            correct=sum(e.hidden_score for e in evals)
            final_eval={"hidden_correct":correct>0,"candidate_correctness":[e.hidden_score for e in evals],"candidate_count":len(evals),"selection_hidden_blind":True,"evaluator_id":"independent_hidden_executor_v1"}
            compute={"training_tokens":train["training_tokens"],"inference_input_tokens":account.input_tokens,"inference_output_tokens":account.output_tokens,"training_flops":{"value":train["estimated_training_flops"],"status":"estimated"},"inference_flops":{"value":2*raw["model"]["parameter_count"]*account.total_tokens,"status":"estimated"},"total_flops":{"value":train["estimated_training_flops"]+2*raw["model"]["parameter_count"]*account.total_tokens,"status":"derived"},"optimizer_steps":train["optimizer_steps"],"model_calls":account.calls,"candidates":account.candidates,"execution_steps":0,"training_wall_seconds":train["training_wall_seconds"],"inference_wall_seconds":account.wall_seconds,"total_wall_seconds":time.time()-started,"monetary_cost_proxy":{"value":None,"status":"unavailable"}}
        except BudgetViolation as e:
            status="ineligible_budget"; compute={"budget_violation":str(e)}; final_eval={"hidden_correct":None,"hidden_exposed":False}
            train={"training_tokens":0,"optimizer_steps":0,"estimated_training_flops":0,"training_wall_seconds":0}
        record=ResultRecord(raw["experiment_id"],run_id,condition_id,task.task_id,seed,git_sha(),cfg.config_hash,benchmark.manifest_hash,raw["model"]["initialization_id"],checkpoint_id,{"planned_tokens":cond["training_tokens"],"planned_steps_max":cond["training_budget_steps"],"planned_flops":cond["training_estimated_flops"]},{"planned_tokens":cond["inference_tokens"],"planned_calls":cond["inference_model_calls"]},compute,final_eval,status)
        write_result(results_root,record)
    return run_id
