from pathlib import Path
from compute_research.results import ResultRecord,write_result

def test_no_silent_overwrite(tmp_path:Path):
    r=ResultRecord("EXP-001","run-1","A0","t1",42,"sha","cfg","bench","model",{}, {}, {}, {}, "complete")
    write_result(tmp_path,r)
    try: write_result(tmp_path,r)
    except FileExistsError: return
    assert False
