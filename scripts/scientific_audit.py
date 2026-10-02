from compute_research.config import load_config
c=load_config("configs/experiments/exp001_fixed_allocation.yaml")
checks=[c.raw["status"]=="frozen",len(c.raw["seeds"])>=2,c.raw["evaluation"]["hidden_results_visible_to_strategy"] is False,c.raw["evaluation"]["final_results_used_for_selection"] is False,c.raw["execution"]["allow_mock"] is False,c.raw["execution"]["fail_closed"] is True]
for name,ok in zip(["frozen_matrix","paired_seeds","hidden_isolation","final_selection_isolation","mock_blocked","fail_closed"],checks): print("PASS" if ok else "FAIL",name)
raise SystemExit(0 if all(checks) else 1)
