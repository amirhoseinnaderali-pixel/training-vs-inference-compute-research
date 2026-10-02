import argparse,json
from collections import Counter
from pathlib import Path
from compute_research.stats import summarize,paired_differences,PRIMARY_ESTIMAND

p=argparse.ArgumentParser()
p.add_argument("--input",required=True)
p.add_argument("--output",required=True)
a=p.parse_args()

all_rows=[]
for f in Path(a.input).rglob("*.json"):
    if f.name=="MANIFEST.json":
        continue
    all_rows.append(json.loads(f.read_text()))

eligible=[
    r for r in all_rows
    if r.get("status")=="complete" and r.get("eligible_for_analysis") is True
]
excluded=Counter(r.get("status","missing") for r in all_rows if r not in eligible)

if not eligible:
    raise SystemExit("No eligible scientific result rows found; refusing to fabricate analysis.")

for row in eligible:
    evaluation=row.get("final_evaluation") or {}
    if evaluation.get("primary_outcome")!=PRIMARY_ESTIMAND:
        raise SystemExit(f"Result row {row.get('run_id')} does not match registered primary estimand.")
    if not isinstance(evaluation.get("primary_outcome_value"),bool):
        raise SystemExit(f"Result row {row.get('run_id')} has no valid primary outcome value.")

out={
    "primary_estimand":PRIMARY_ESTIMAND,
    "eligible_rows":len(eligible),
    "excluded_rows":len(all_rows)-len(eligible),
    "excluded_status_counts":dict(sorted(excluded.items())),
    "summary":summarize(eligible),
    "paired_differences_vs_A0":paired_differences(eligible),
}
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True))
print("WROTE",a.output)
