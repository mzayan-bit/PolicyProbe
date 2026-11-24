"""Execute the frozen pilot and export observed outcomes."""

import argparse
import json
from pathlib import Path

from .baselines import METHODS
from .benchmark import load_scenarios, verify_dataset
from .benchmark_metrics import summarize
from .benchmark_run import run_scenario
from .benchmark_shop import BenchmarkShop
from .local_model import LocalModel


def suite(folder, split, method="boundary", client=None):
    runs = []
    for scenario in load_scenarios(folder, split):
        for broken in (False, True):
            target = BenchmarkShop(scenario, broken)
            run = run_scenario(folder, scenario, method, target, client)
            run["target"] = "seeded" if broken else "clean"
            run["seeded_defect"] = scenario["id"] + "/short-window" if broken else None
            run["ledger"] = target.records
            runs.append(run)
    return {"dataset": verify_dataset(folder), "split": split, "runs": runs,
            "summary": summarize(runs), "execution": "scripted pilot targets"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--split", choices=("development", "evaluation"), default="development")
    parser.add_argument("--method", choices=METHODS, default="boundary")
    parser.add_argument("--model")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    if args.method != "boundary" and not args.model:
        parser.error("this method requires --model")
    client = LocalModel(args.model) if args.model else None
    result = suite(args.dataset, args.split, args.method, client)
    with args.output.open("x") as file:
        json.dump(result, file, indent=2)
        file.write("\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
