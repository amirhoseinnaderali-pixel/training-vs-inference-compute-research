from pathlib import Path
import os,time,uuid,json,subprocess
from .config import load_config
from .benchmark import load_model_tasks,verify_materialized,sha256_file
from .readiness import real_readiness,assert_ready
from .real_adapters import HuggingFaceSFTAdapter,HuggingFaceInferenceAdapter,RealDependencyError
from .inference_budget import InferenceAccount
from .evaluator import DockerHiddenEvaluator
from .results import ResultRecord,write_result
from .checkpoint import validate_checkpoint
from .budget import BudgetViolation

PRIMARY_ESTIMAND = "any_candidate_passes_hidden"

def git_sha():
    v=os.getenv("GITHUB_SHA")
    if v:
        return v
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception as e:
        raise RuntimeError("git SHA unavailable") from e

def _condition(cfg,condition_id):
    for row in cfg.raw["allocation_matrix"]:
        if row["condition_id"]==condition_id:
            return row
    raise ValueError(condition_id)

def _result_budget(cond):
    return {
        "training":{
            "planned_tokens":cond["training_tokens"],
            "planned_steps_max":cond["training_budget_steps"],
            "planned_flops":cond["training_estimated_flops"],
        },
        "inference":{
            "planned_tokens":cond["inference_tokens"],
            "planned_calls":cond["inference_model_calls"],
        },
    }

def _failure_status(exc):
    if isinstance(exc,BudgetViolation):
        return "ineligible_budget"
    if isinstance(exc,RealDependencyError):
        return "runtime_failure"
    name=type(exc).__name__.lower()
    if "evaluat" in name or "docker" in str(exc).lower():
        return "evaluation_failure"
    if "config" in name or "benchmark" in str(exc).lower() or "provenance" in str(exc).lower():
        return "configuration_failure"
    if "model" in name or "token" in name.lower() or "model" in str(exc).lower():
        return "model_failure"
    return "runtime_failure"

def run_one(config_path,condition_id,seed,task_limit=None,results_root=None,smoke=False):
    cfg=load_config(config_path)
    if cfg.validation_only or cfg.raw["execution"]["allow_mock"]:
        raise RuntimeError("real runner refuses validation/mock configuration")
    root=Path(".")
    bench_path=root/"benchmarks/programming/exp001_v1/tasks.jsonl"
    hidden_path=root/"benchmarks/programming/exp001_v1/hidden_tests.jsonl"
    manifest=root/"benchmarks/manifests/exp001_v1.json"
    if not bench_path.exists() or not hidden_path.exists():
        raise RuntimeError("real execution blocked: materialized benchmark and hidden store are required")
    verify_materialized(bench_path,hidden_path,manifest)
    tasks_all=load_model_tasks(bench_path,manifest)
    assert_ready(real_readiness(cfg,True))
    cond=_condition(cfg,condition_id)
    if abs(cond["training_fraction"]+cond["inference_fraction"]-1)>1e-9:
        raise ValueError("allocation fractions do not sum to one")
    run_id=f"{condition_id}-seed{seed}-{uuid.uuid4().hex[:10]}"
    out_root=Path(results_root) if results_root else root/"results/raw"
    tasks=tasks_all if task_limit is None else tasks_all[:task_limit]
    if not tasks:
        raise ValueError("no benchmark tasks selected")
    evaluator=DockerHiddenEvaluator(hidden_path)

    for task in tasks:
        started=time.perf_counter()
        checkpoint_id=""
        status="complete"
        eligible=False
        compute={}
        final_eval={
            "primary_outcome":PRIMARY_ESTIMAND,
            "primary_outcome_value":None,
            "hidden_correct":None,
            "hidden_exposed":False,
            "selection_hidden_blind":True,
        }
        try:
            train_dir=root/("results/smoke/checkpoints" if smoke else "results/checkpoints")/cfg.experiment_id/run_id/task.task_id.replace("/","_")
            train=HuggingFaceSFTAdapter().train(
                model_id=cfg.raw["model"]["model_id"],
                revision=cfg.raw["model"]["initialization_id"],
                dataset_id=cfg.raw["training"]["dataset_id"],
                dataset_revision=cfg.raw["training"]["dataset_version"].split("@")[-1],
                dataset_config="solutions_py_decontaminated",
                output_dir=str(train_dir),
                token_budget=cond["training_tokens"],
                max_steps=cond["training_budget_steps"],
                batch_size=cfg.raw["training"]["batch_size"],
                gradient_accumulation=cfg.raw["training"]["gradient_accumulation"],
                sequence_length=cfg.raw["training"]["sequence_length"],
                learning_rate=cfg.raw["training"]["learning_rate"],
                seed=seed,
                max_flops=cond["training_estimated_flops"],
                max_wall_seconds=cfg.raw["training"]["max_wall_seconds"],
                provenance={
                    "base_model_id":cfg.raw["model"]["model_id"],
                    "model_revision":cfg.raw["model"]["initialization_id"],
                    "tokenizer_revision":cfg.raw["model"]["initialization_id"],
                    "training_dataset_id":cfg.raw["training"]["dataset_id"],
                    "training_dataset_revision":cfg.raw["training"]["dataset_version"],
                    "dataset_manifest_sha256":cfg.raw["training"]["dataset_manifest_sha256"],
                    "training_config_hash":cfg.config_hash,
                    "allocation_condition":condition_id,
                    "seed":seed,
                    "git_sha":git_sha(),
                    "training_budget":{
                        "tokens":cond["training_tokens"],
                        "steps_max":cond["training_budget_steps"],
                        "estimated_flops":cond["training_estimated_flops"],
                    },
                    "realized_compute":{},
                },
            )
            expected_checkpoint={
                "base_model_id":cfg.raw["model"]["model_id"],
                "model_revision":cfg.raw["model"]["initialization_id"],
                "tokenizer_revision":cfg.raw["model"]["initialization_id"],
                "training_dataset_id":cfg.raw["training"]["dataset_id"],
                "training_dataset_revision":cfg.raw["training"]["dataset_version"],
                "dataset_manifest_sha256":cfg.raw["training"]["dataset_manifest_sha256"],
                "training_config_hash":cfg.config_hash,
                "allocation_condition":condition_id,
                "seed":seed,
                "git_sha":git_sha(),
                "training_budget":{
                    "tokens":cond["training_tokens"],
                    "steps_max":cond["training_budget_steps"],
                    "estimated_flops":cond["training_estimated_flops"],
                },
            }
            cp=validate_checkpoint(Path(train["checkpoint"]),expected_checkpoint)
            checkpoint_id=cp["checkpoint_id"]

            model=HuggingFaceInferenceAdapter(
                cfg.raw["model"]["model_id"],
                cfg.raw["model"]["initialization_id"],
                train["checkpoint"],
            )
            input_n=model.count_input_tokens(task.prompt)
            calls=cond["inference_model_calls"]
            if input_n*calls>=cond["inference_tokens"]:
                raise BudgetViolation("inference","input_tokens",input_n*calls,cond["inference_tokens"]-1)
            remaining_output=cond["inference_tokens"]-input_n*calls
            account=InferenceAccount(
                cond["inference_tokens"],
                calls,
                calls,
                calls,
                cfg.raw["inference"]["max_wall_seconds"],
            )
            candidates=[]
            # Candidate generation is completed before any hidden evaluation.
            for i in range(calls):
                quota=remaining_output//(calls-i)
                if quota<1:
                    raise BudgetViolation("inference","output_quota",quota,1)
                if quota>cfg.raw["inference"]["max_output_tokens_per_call"]:
                    raise BudgetViolation(
                        "inference",
                        "max_output_tokens_per_call",
                        quota,
                        cfg.raw["inference"]["max_output_tokens_per_call"],
                    )
                if input_n+quota>cfg.raw["inference"]["max_input_tokens_per_call"]+cfg.raw["inference"]["max_output_tokens_per_call"]:
                    raise BudgetViolation(
                        "inference",
                        "per_call_context",
                        input_n+quota,
                        cfg.raw["inference"]["max_input_tokens_per_call"]+cfg.raw["inference"]["max_output_tokens_per_call"],
                    )
                out=model.generate(task.prompt,quota,seed+i)
                if out["input_tokens"]+out["output_tokens"]!=input_n+quota:
                    raise BudgetViolation(
                        "inference",
                        "generation_token_realization",
                        out["input_tokens"]+out["output_tokens"],
                        input_n+quota,
                    )
                account.reserve(
                    out["input_tokens"],
                    out["output_tokens"],
                    1,
                    1,
                    out["wall_seconds"],
                )
                candidates.append(out)
                remaining_output-=out["output_tokens"]

            if account.calls!=calls or account.candidates!=calls or account.total_tokens!=cond["inference_tokens"]:
                raise BudgetViolation(
                    "inference",
                    "allocation_accounting",
                    account.total_tokens,
                    cond["inference_tokens"],
                )

            # Hidden evaluation is strictly downstream of candidate generation.
            evals=[evaluator.evaluate(task,out["text"]) for out in candidates]
            correct=sum(e.hidden_score for e in evals)
            primary_value=correct>0
            final_eval={
                "primary_outcome":PRIMARY_ESTIMAND,
                "primary_outcome_value":primary_value,
                "hidden_correct":primary_value,
                "candidate_correctness":[e.hidden_score for e in evals],
                "candidate_count":len(evals),
                "selection_hidden_blind":True,
                "evaluator_id":"independent_hidden_executor_v1",
            }
            compute={
                "training_tokens":train["training_tokens"],
                "inference_input_tokens":account.input_tokens,
                "inference_output_tokens":account.output_tokens,
                "training_flops":{"value":train["estimated_training_flops"],"status":"estimated"},
                "inference_flops":{
                    "value":2*cfg.raw["model"]["parameter_count"]*account.total_tokens,
                    "status":"estimated",
                },
                "total_flops":{
                    "value":train["estimated_training_flops"]+2*cfg.raw["model"]["parameter_count"]*account.total_tokens,
                    "status":"derived",
                },
                "optimizer_steps":train["optimizer_steps"],
                "model_calls":account.calls,
                "candidates":account.candidates,
                "execution_steps":{"value":None,"status":"unavailable"},
                "training_wall_seconds":train["training_wall_seconds"],
                "inference_wall_seconds":account.wall_seconds,
                "total_wall_seconds":time.perf_counter()-started,
                "monetary_cost_proxy":{"value":None,"status":"unavailable"},
            }
            eligible=True
        except Exception as exc:
            status=_failure_status(exc)
            compute={
                "failure":str(exc),
                "failure_type":type(exc).__name__,
                "total_wall_seconds":time.perf_counter()-started,
            }
            final_eval={
                "primary_outcome":PRIMARY_ESTIMAND,
                "primary_outcome_value":None,
                "hidden_correct":None,
                "hidden_exposed":False,
                "selection_hidden_blind":True,
            }

        record=ResultRecord(
            cfg.experiment_id,run_id,condition_id,task.task_id,seed,git_sha(),
            cfg.config_hash,sha256_file(manifest),
            cfg.raw["model"]["initialization_id"],checkpoint_id,
            _result_budget(cond)["training"],_result_budget(cond)["inference"],
            compute,final_eval,status,eligible
        )
        write_result(out_root,record)
    return run_id

def run_experiment(config_path):
    cfg=load_config(config_path)
    if cfg.validation_only or cfg.raw["execution"]["allow_mock"]:
        raise RuntimeError("real experiment requires validation_only=false and allow_mock=false")
    run_ids=[]
    for cond in cfg.raw["allocation_matrix"]:
        for seed in cfg.raw["seeds"]:
            run_ids.append(run_one(config_path,cond["condition_id"],seed))
    return run_ids

def run_smoke(config_path,condition_id="A0",seed=42):
    return run_one(
        config_path,condition_id,seed,task_limit=1,
        results_root="results/smoke",smoke=True
    )
