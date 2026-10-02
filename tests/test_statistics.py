from compute_research.stats import paired_differences,bootstrap_ci

def test_pairing():
    rows=[{"condition_id":"A0","task_id":"t","seed":1,"correct":0},{"condition_id":"A1","task_id":"t","seed":1,"correct":1},{"condition_id":"A1","task_id":"x","seed":2,"correct":1}]
    assert paired_differences(rows)=={"A1":[1]}

def test_empty_ci(): assert bootstrap_ci([])==(None,None)
