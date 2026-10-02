import argparse
from compute_research.runner import run_smoke

def main():
    p=argparse.ArgumentParser(description="Real one-task/one-seed Project 5 smoke test")
    p.add_argument("--config",default="configs/experiments/exp001_fixed_allocation.yaml")
    p.add_argument("--condition",default="A0")
    p.add_argument("--seed",type=int,default=42)
    a=p.parse_args()
    print("REAL SMOKE:",run_smoke(a.config,a.condition,a.seed))

if __name__=="__main__":
    main()
