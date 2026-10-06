from pathlib import Path
from compute_research.benchmark_materialization import materialize
p=Path("benchmarks/programming/exp001_v1/tasks.jsonl")
print("MATERIALIZED",materialize(Path("benchmarks/manifests/exp001_v1.json"),p),p)
