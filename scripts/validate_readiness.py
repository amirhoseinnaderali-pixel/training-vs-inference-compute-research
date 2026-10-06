from pathlib import Path
from compute_research.config import load_config
from compute_research.readiness import real_readiness,assert_ready
cfg=load_config("configs/experiments/exp001_fixed_allocation.yaml")
gates=real_readiness(cfg,Path("benchmarks/programming/exp001_v1/tasks.jsonl").exists())
for g in gates: print("PASS" if g.ok else "BLOCKED",g.name,g.detail)
assert_ready(gates)
print("REAL EXECUTION READY")
