from dataclasses import dataclass
from pathlib import Path
import hashlib, json, ast

@dataclass(frozen=True)
class BenchmarkTask:
    task_id:str; prompt:str; entry_point:str; visible_tests:str; hidden_tests:str; task_sha256:str; test_sha256:str

@dataclass(frozen=True)
class Benchmark:
    benchmark_id:str; version:str; tasks:tuple[BenchmarkTask,...]; manifest_hash:str; source_archive_sha256:str; contamination_policy:str
    def assert_integrity(self, expected_count:int):
        if len(self.tasks)!=expected_count: raise ValueError(f"benchmark task count {len(self.tasks)} != {expected_count}")
        ids=[t.task_id for t in self.tasks]
        if len(ids)!=len(set(ids)): raise ValueError("duplicate benchmark task")
        if any(not t.hidden_tests.strip() for t in self.tasks): raise ValueError("hidden evaluation missing")
        if any(not t.visible_tests.strip() for t in self.tasks): raise ValueError("visible evaluation missing")

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def _split_tests(test_source:str):
    tree=ast.parse(test_source)
    fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="check"),None)
    if fn is None: raise ValueError("HumanEval task has no check(candidate)")
    asserts=[n for n in fn.body if isinstance(n,ast.Assert)]
    if len(asserts)<2: raise ValueError("task has fewer than two top-level asserts")
    visible_n=(len(asserts)+1)//2
    lines=test_source.splitlines()
    prefix="\n".join(lines[:fn.lineno-1])
    def block(nodes):
        return "\n".join("\n".join(lines[n.lineno-1:n.end_lineno]) for n in nodes)
    def wrap(nodes): return prefix+"\n\ndef check(candidate):\n    "+block(nodes).replace("\n","\n    ")
    return wrap(asserts[:visible_n]),wrap(asserts[visible_n:])

def load_materialized(path:Path,manifest_path:Path)->Benchmark:
    manifest=json.loads(manifest_path.read_text())
    rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    expected={t["task_id"]:t for t in manifest["tasks"]}
    if list(expected)!=[r["task_id"] for r in rows]: raise ValueError("benchmark ordering/task selection differs from frozen manifest")
    tasks=[]
    for r in rows:
        e=expected[r["task_id"]]
        if r.get("task_sha256")!=e["task_sha256"] or r.get("test_sha256")!=e["test_sha256"]: raise ValueError(f"{r['task_id']}: frozen task/test hash mismatch")
        tasks.append(BenchmarkTask(r["task_id"],r["prompt"],r["entry_point"],r["visible_tests"],r["hidden_tests"],r["task_sha256"],r["test_sha256"]))
    b=Benchmark(manifest["benchmark_id"],manifest["version"],tuple(tasks),sha256_file(manifest_path),manifest["provenance"]["source_archive_sha256"],"provenance documented; exact zero contamination is not claimed")
    b.assert_integrity(manifest["task_count"]); return b
