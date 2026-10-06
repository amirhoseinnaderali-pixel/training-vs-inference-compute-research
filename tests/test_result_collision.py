from pathlib import Path
from compute_research.results import ResultRecord,write_result

def _record():
    return ResultRecord(
        "EXP-001","run-1","A0","t1",42,"sha","cfg","bench","model","checkpoint",
        {},{}, {},
        {"primary_outcome":"any_candidate_passes_hidden","primary_outcome_value":True},
        "complete",True,
    )

def test_no_silent_overwrite(tmp_path:Path):
    r=_record()
    write_result(tmp_path,r)
    try:
        write_result(tmp_path,r)
    except FileExistsError:
        return
    assert False

def test_result_has_explicit_analysis_eligibility():
    r=_record()
    assert r.eligible_for_analysis is True
    assert r.final_evaluation["primary_outcome"]=="any_candidate_passes_hidden"
