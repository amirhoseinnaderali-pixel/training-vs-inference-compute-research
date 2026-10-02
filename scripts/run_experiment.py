import argparse
from pathlib import Path
from compute_research.config import load_config
from compute_research.readiness import real_readiness,assert_ready
p=argparse.ArgumentParser(); p.add_argument("--config",required=True); a=p.parse_args()
cfg=load_config(a.config)
if cfg.validation_only: raise SystemExit("Validation-only config cannot run scientific experiment")
assert_ready(real_readiness(cfg,Path("benchmarks/programming/exp001_v1/tasks.jsonl").exists()))
raise SystemExit("Readiness passed. Real model/training adapters are an explicit integration boundary; no model inference is performed by repository validation.")
