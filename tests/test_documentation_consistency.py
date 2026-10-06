from pathlib import Path
import re,yaml

def test_exp001_readme_matches_matrix():
    c=yaml.safe_load(Path("configs/experiments/exp001_fixed_allocation.yaml").read_text())
    t=Path("experiments/EXP-001/README.md").read_text()
    for r in c["allocation_matrix"]:
        expected=f"| {r['condition_id']} | {r['training_fraction']:.0%} | {r['inference_fraction']:.0%} | {r['training_tokens']:,} | {r['training_budget_steps']} | {r['inference_tokens']:,} | {r['inference_model_calls']} |"
        assert expected in t
