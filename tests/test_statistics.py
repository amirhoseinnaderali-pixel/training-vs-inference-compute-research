from compute_research.stats import paired_differences,bootstrap_ci

def _row(condition_id,task_id,seed,value):
    return {
        "condition_id":condition_id,
        "task_id":task_id,
        "seed":seed,
        "final_evaluation":{
            "primary_outcome":"any_candidate_passes_hidden",
            "primary_outcome_value":value,
        },
    }

def test_pairing():
    rows=[
        _row("A0","t",1,False),
        _row("A1","t",1,True),
        _row("A1","x",2,True),
    ]
    assert paired_differences(rows)=={"A1":[1]}

def test_empty_ci(): assert bootstrap_ci([])==(None,None)
