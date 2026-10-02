import sys
from compute_research.config import load_config
p=sys.argv[1] if len(sys.argv)>1 else "configs/experiments/exp001_fixed_allocation.yaml"
c=load_config(p)
print("VALID CONFIG:",c.experiment_id,"hash=",c.config_hash)
