"""Inspect a baseline's initial plan using frozen development inputs."""

import argparse
from pathlib import Path
import json

from .baselines import METHODS, make_selector
from .benchmark import load_scenarios, verify_dataset
from .local_model import LocalModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--method", choices=METHODS, default="boundary")
    parser.add_argument("--model")
    parser.add_argument("--budget", type=int, default=20)
    args = parser.parse_args()
    if not 0 <= args.budget <= 20:
        parser.error("budget must be between zero and twenty")
    if args.method != "boundary" and not args.model:
        parser.error("select a local model for this method")
    verify_dataset(args.dataset)
    client = LocalModel(args.model) if args.model else None
    for scenario in load_scenarios(args.dataset, "development"):
        selector = make_selector(args.method, scenario, client, args.budget)
        first = selector.choose([]) if args.budget else None
        print(json.dumps({"scenario": scenario["id"], "method": args.method, "first_case": first}))


if __name__ == "__main__":
    main()
