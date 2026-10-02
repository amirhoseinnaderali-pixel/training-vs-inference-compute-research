import random
from collections import defaultdict

def paired_differences(rows,baseline="A0"):
    base={(r["task_id"],r["seed"]):r["correct"] for r in rows if r["condition_id"]==baseline}
    out=defaultdict(list)
    for r in rows:
        k=(r["task_id"],r["seed"])
        if r["condition_id"]!=baseline and k in base: out[r["condition_id"]].append(r["correct"]-base[k])
    return dict(out)

def bootstrap_ci(values,resamples=10000,confidence=.95,seed=0):
    if not values:return(None,None)
    rng=random.Random(seed); n=len(values); means=[]
    for _ in range(resamples): means.append(sum(values[rng.randrange(n)] for _ in range(n))/n)
    means.sort(); lo=int(((1-confidence)/2)*resamples); hi=int((1-(1-confidence)/2)*resamples)-1
    return means[lo],means[hi]

def summarize(rows):
    groups=defaultdict(list)
    for r in rows: groups[r["condition_id"]].append(r)
    return {c:{"n":len(v),"correctness":sum(x["correct"] for x in v)/len(v),"ci95":bootstrap_ci([x["correct"] for x in v])} for c,v in sorted(groups.items())}
