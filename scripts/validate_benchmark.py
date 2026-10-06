from pathlib import Path
from compute_research.benchmark import load_materialized
b=load_materialized(Path("benchmarks/programming/exp001_v1/tasks.jsonl"),Path("benchmarks/programming/exp001_v1/hidden_tests.jsonl"),Path("benchmarks/manifests/exp001_v1.json"))
print("BENCHMARK PASS",len(b.tasks),b.manifest_hash)
