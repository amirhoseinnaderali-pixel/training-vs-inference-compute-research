import random
from collections import defaultdict

PRIMARY_ESTIMAND = "any_candidate_passes_hidden"

def _primary_value(row):
    evaluation=row.get("final_evaluation") or {}
    if evaluation.get("primary_outcome") != PRIMARY_ESTIMAND:
        raise ValueError(
            "result row does not use the registered primary outcome "
            f"{PRIMARY_ESTIMAND!r}"
        )
    value=evaluation.get("primary_outcome_value")
    if not isinstance(value,bool):
        raise ValueError("primary_outcome_value must be boolean")
    return int(value)

def paired_differences(rows,baseline="A0"):
    base={
        (r["task_id"],r["seed"]):_primary_value(r)
        for r in rows if r["condition_id"]==baseline
    }
    out=defaultdict(list)
    for r in rows:
        k=(r["task_id"],r["seed"])
        if r["condition_id"]!=baseline and k in base:
            out[r["condition_id"]].append(_primary_value(r)-base[k])
    return dict(out)

def bootstrap_ci(values,resamples=10000,confidence=.95,seed=0):
    if not values:
        return(None,None)
    rng=random.Random(seed)
    n=len(values)
    means=[]
    for _ in range(resamples):
        means.append(sum(values[rng.randrange(n)] for _ in range(n))/n)
    means.sort()
    lo=int(((1-confidence)/2)*resamples)
    hi=int((1-(1-confidence)/2)*resamples)-1
    return means[lo],means[hi]

def summarize(rows):
    groups=defaultdict(list)
    for r in rows:
        groups[r["condition_id"]].append(r)
    return {
        c:{
            "n":len(v),
            "correctness":sum(_primary_value(x) for x in v)/len(v),
            "ci95":bootstrap_ci([_primary_value(x) for x in v]),
        }
        for c,v in sorted(groups.items())
    }
