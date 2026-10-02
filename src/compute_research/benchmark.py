from dataclasses import dataclass
from .hashing import sha256_json

@dataclass(frozen=True)
class BenchmarkTask:
    task_id:str; prompt:str; visible_tests:tuple[str,...]; hidden_tests:tuple[str,...]; task_sha256:str; test_sha256:str

@dataclass(frozen=True)
class Benchmark:
    benchmark_id:str; version:str; tasks:tuple[BenchmarkTask,...]; manifest_hash:str; contamination_policy:str
    def assert_unique(self):
        ids=[t.task_id for t in self.tasks]
        if len(ids)!=len(set(ids)): raise ValueError("duplicate benchmark task")

def synthetic_validation_benchmark():
    tasks=tuple(BenchmarkTask(f"V{i}",f"task {i}",( "visible",),( "hidden",),"synthetic","synthetic") for i in range(4))
    b=Benchmark("synthetic-4-v1","1.0",tasks,sha256_json([t.__dict__ for t in tasks]),"validation only")
    b.assert_unique(); return b
