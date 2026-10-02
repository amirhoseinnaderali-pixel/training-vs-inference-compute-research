from pathlib import Path
import json,urllib.request,hashlib
from .benchmark import _split_tests,sha256_file,verify_materialized
SOURCE_URL="https://raw.githubusercontent.com/nerdskingcom/gguf-humaneval-benchmark/7e5a3ceb7b8ab4d94714098fad566ef4c487a605/HumanEval.jsonl"
SOURCE_SHA256="a2891a8b99a91831af37bd5ed618514acc8dfc43dd2347c6e0fa926f18178794"

def materialize(manifest_path:Path,output_path:Path):
    manifest=json.loads(manifest_path.read_text()); raw=urllib.request.urlopen(SOURCE_URL,timeout=60).read()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256: raise RuntimeError("pinned benchmark source hash mismatch")
    source={r["task_id"]:r for r in (json.loads(x) for x in raw.decode().splitlines() if x.strip())}
    rows=[]
    for spec in manifest["tasks"]:
        r=source.get(spec["task_id"])
        if r is None: raise RuntimeError(f"missing frozen task {spec['task_id']}")
        visible,hidden=_split_tests(r["test"])
        rows.append({"task_id":r["task_id"],"prompt":r["prompt"],"entry_point":r["entry_point"],"visible_tests":visible,"task_sha256":spec["task_sha256"],"test_sha256":spec["test_sha256"]})
    output_path.parent.mkdir(parents=True,exist_ok=True); tmp=output_path.with_suffix(".tmp"); tmp.write_text("\n".join(json.dumps(x,sort_keys=True) for x in rows)+"\n"); tmp.replace(output_path)
    hidden_path=output_path.with_name("hidden_tests.jsonl"); htmp=hidden_path.with_suffix(".tmp"); htmp.write_text("\n".join(json.dumps({"task_id":r["task_id"],"hidden_tests":_split_tests(source[r["task_id"]]["test"])[1],"test_sha256":next(s["test_sha256"] for s in manifest["tasks"] if s["task_id"]==r["task_id"])},sort_keys=True) for r in rows)+"\n"); htmp.replace(hidden_path)
    verify_materialized(output_path,hidden_path,manifest_path)
    return sha256_file(output_path)
