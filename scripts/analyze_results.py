import argparse,json
from pathlib import Path
from compute_research.stats import summarize,paired_differences

p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args()
rows=[]
for f in Path(a.input).rglob("*.json"):
    if f.name=="MANIFEST.json": continue
    rows.append(json.loads(f.read_text()))
if not rows: raise SystemExit("No scientific result rows found; refusing to fabricate analysis.")
out={"summary":summarize(rows),"paired_differences_vs_A0":paired_differences(rows)}
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True))
print("WROTE",a.output)
