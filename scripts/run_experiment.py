import argparse
from compute_research.config import load_config
from compute_research.runner import run_experiment,run_smoke

def main():
    p=argparse.ArgumentParser(description="Project 5 execution entry point")
    p.add_argument("--config",required=True)
    p.add_argument("--mode",choices=("validation","smoke","real"),default="real")
    a=p.parse_args()
    if a.mode=="validation":
        from run_validation import main as validation_main
        validation_main()
        return
    cfg=load_config(a.config)
    if cfg.validation_only or cfg.raw["execution"]["allow_mock"]:
        raise SystemExit("configuration is validation/mock and cannot enter smoke/real mode")
    if a.mode=="smoke":
        print("SMOKE:",run_smoke(a.config))
        return
    print("EXP-001:",run_experiment(a.config))

if __name__=="__main__":
    main()
