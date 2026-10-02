from dataclasses import dataclass
from pathlib import Path
import hashlib,json,ast

@dataclass(frozen=True)
class ModelTask:
    task_id:str; prompt:str; entry_point:str; visible_tests:str; task_sha256:str; test_sha256:str

@dataclass(frozen=True)
class BenchmarkTask:
    task_id:str; prompt:str; entry_point:str; visible_tests:str; hidden_tests:str; task_sha256:str; test_sha256:str

@dataclass(frozen=True)
class Benchmark:
    benchmark_id:str; version:str; tasks:tuple[BenchmarkTask,...]; manifest_hash:str; source_archive_sha256:str; contamination_policy:str
    def assert_integrity(self,expected_count:int):
        if len(self.tasks)!=expected_count: raise ValueError(f"benchmark task count {len(self.tasks)} != {expected_count}")
        ids=[t.task_id for t in self.tasks]
        if len(ids)!=len(set(ids)): raise ValueError("duplicate benchmark task")
        if any(not t.hidden_tests.strip() or not t.visible_tests.strip() for t in self.tasks): raise ValueError("evaluation split missing")

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def _split_tests(test_source:str):
    tree=ast.parse(test_source); fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="check"),None)
    if fn is None: raise ValueError("HumanEval task has no check(candidate)")
    asserts=[n for n in fn.body if isinstance(n,ast.Assert)]
    if len(asserts)<2: raise ValueError("task has fewer than two top-level asserts")
    visible_n=(len(asserts)+1)//2; lines=test_source.splitlines(); prefix="\n".join(lines[:fn.lineno-1])
    def block(nodes): return "\n".join("\n".join(lines[n.lineno-1:n.end_lineno]) for n in nodes)
    def wrap(nodes): return prefix+"\n\ndef check(candidate):\n    "+block(nodes).replace("\n","\n    ")
    return wrap(asserts[:visible_n]),wrap(asserts[visible_n:])

def load_model_tasks(path:Path,manifest_path:Path)->tuple[ModelTask,...]:
    manifest=json.loads(manifest_path.read_text()); rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    expected={t["task_id"]:t for t in manifest["tasks"]}
    if list(expected)!=[r["task_id"] for r in rows]: raise ValueError("benchmark ordering/task selection differs from frozen manifest")
    out=[]
    for r in rows:
        if "hidden_tests" in r: raise ValueError("hidden tests must not be present in model-facing benchmark")
        e=expected[r["task_id"]]
        if r.get("task_sha256")!=e["task_sha256"] or r.get("test_sha256")!=e["test_sha256"]: raise ValueError(f"{r['task_id']}: frozen hash mismatch")
        out.append(ModelTask(r["task_id"],r["prompt"],r["entry_point"],r["visible_tests"],r["task_sha256"],r["test_sha256"]))
    if len(out)!=manifest["task_count"]: raise ValueError("task count mismatch")
    return tuple(out)

def load_materialized(path:Path,hidden_path:Path,manifest_path:Path)->Benchmark:
    model=load_model_tasks(path,manifest_path); hidden={json.loads(x)["task_id"]:json.loads(x) for x in hidden_path.read_text().splitlines() if x.strip()}
    tasks=[]
    for t in model:
        h=hidden.get(t.task_id)
        if not h or h.get("test_sha256")!=t.test_sha256 or not h.get("hidden_tests","").strip(): raise ValueError(f"hidden store mismatch: {t.task_id}")
        tasks.append(BenchmarkTask(t.task_id,t.prompt,t.entry_point,t.visible_tests,h["hidden_tests"],t.task_sha256,t.test_sha256))
    m=json.loads(manifest_path.read_text())
    b=Benchmark(m["benchmark_id"],m["version"],tuple(tasks),sha256_file(manifest_path),m["provenance"]["source_archive_sha256"],"provenance documented; exact zero contamination is not claimed")
    b.assert_integrity(m["task_count"]); return b


def synthetic_validation_benchmark():
    tasks=tuple(BenchmarkTask(f"V{i}",f"validation task {i}","f","def check(candidate):\n    assert candidate()==1","def check(candidate):\n    assert candidate()==1","synthetic","synthetic") for i in range(4))
    b=Benchmark("synthetic-4-v1","1.0",tasks,"synthetic-manifest","synthetic-source","validation only")
    b.assert_integrity(4)
    return b


def verify_materialized(path:Path, hidden_path:Path, manifest_path:Path)->None:
    manifest=json.loads(manifest_path.read_text())
    rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    hidden_rows=[json.loads(x) for x in hidden_path.read_text().splitlines() if x.strip()]
    expected=manifest["tasks"]
    if len(rows)!=manifest["task_count"] or len(hidden_rows)!=manifest["task_count"]:
        raise ValueError("materialized benchmark/hidden store count mismatch")
    if [r.get("task_id") for r in rows] != [e["task_id"] for e in expected]:
        raise ValueError("materialized benchmark ordering differs from frozen manifest")
    if [r.get("task_id") for r in hidden_rows] != [e["task_id"] for e in expected]:
        raise ValueError("hidden store ordering differs from frozen manifest")
    hmap={r["task_id"]:r for r in hidden_rows}
    for row,spec in zip(rows,expected):
        if "hidden_tests" in row:
            raise ValueError("hidden tests leaked into model-facing benchmark")
        if row.get("task_sha256")!=spec["task_sha256"] or row.get("test_sha256")!=spec["test_sha256"]:
            raise ValueError(f"{row['task_id']}: model-facing hash mismatch")
        h=hmap[row["task_id"]]
        if h.get("test_sha256")!=spec["test_sha256"] or not h.get("hidden_tests","").strip():
            raise ValueError(f"{row['task_id']}: hidden-test provenance mismatch")
    if manifest["provenance"]["canonical_source"]!="openai/human-eval":
        raise ValueError("unexpected canonical benchmark source")
    if manifest["provenance"]["source_commit"]!="6d43fb980f9fee3c892a914eda09951f772ad10d":
        raise ValueError("unexpected canonical source commit")
    mirror=manifest["provenance"]["acquisition_mirror"]
    if mirror["repository"]!="nerdskingcom/gguf-humaneval-benchmark" or mirror["branch_sha"]!="7e5a3ceb7b8ab4d94714098fad566ef4c487a605":
        raise ValueError("unexpected pinned acquisition mirror")
    if manifest.get("selection_policy",{}).get("type")!="stratified_source_order":
        raise ValueError("selection policy differs from Project 3 frozen benchmark")
    split=manifest.get("evaluation_split_policy",{})
    if split.get("type")!="deterministic_assertion_split" or split.get("visible_rule")!="first ceil(n/2) top-level assert statements" or split.get("hidden_rule")!="remaining top-level assert statements":
        raise ValueError("evaluation split policy differs from Project 3 frozen benchmark")
    if manifest.get("integrity",{}).get("manifest_content_sha256")!="b14dc4fbe6b8dd0a31764cc66cb9446473cf942f676a24205fbd9965c481a798":
        raise ValueError("Project 3 benchmark manifest identity mismatch")
