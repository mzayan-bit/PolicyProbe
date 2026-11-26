"""Command line entry point for checking the bundled return-policy scenario."""

from .output import write_report

import argparse
import json
from pathlib import Path

from .bundled import BundledTarget
from .demo_shop import correct_bot, flawed_bot
from .investigate_demo import expectation_for
from .investigation import investigate
from .orders import boundary_orders
from .reports import report, markdown
from .selection import ReturnSelector
from .replay import replay
from .local_model import LocalModel
from .model_selector import ModelSelector, ModelShopper
from datetime import date


TARGETS = {"correct": correct_bot, "flawed": flawed_bot}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check the bundled November 2026 return scenario")
    check.add_argument("--target", choices=TARGETS, default="flawed")
    check.add_argument("--budget", type=int, default=5)
    check.add_argument("--output", type=Path, required=True)
    check.add_argument("--model", help="installed local Ollama model")
    check.add_argument("--model-endpoint", default="http://127.0.0.1:11434")
    saved = commands.add_parser("replay", help="repeat one case from a saved report")
    saved.add_argument("report", type=Path)
    saved.add_argument("--case-id", required=True)
    args = parser.parse_args()
    if args.command == "replay":
        try:
            payload = replay(json.loads(args.report.read_text(encoding="utf-8")), args.case_id)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            parser.error(str(exc))
        print(json.dumps(payload, indent=2))
        return
    if args.budget < 0:
        parser.error("--budget must be nonnegative")
    orders = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))
    if args.output.exists():
        parser.error("output already exists")
    client = None
    selector = ReturnSelector(orders)
    shopper = None
    try:
        if args.model:
            client = LocalModel(args.model, args.model_endpoint)
            selector = ModelSelector(client, orders)
            shopper = ModelShopper(client)
        result = investigate(BundledTarget(TARGETS[args.target]), selector,
                             expectation_for, args.budget, messages_for=shopper)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))
    payload = report(result, args.target)
    payload["selection"] = {
        "mode": "local_model" if client else "deterministic",
        "model": client.model if client else None,
        "calls": client.calls if client else 0,
    }
    write_report(args.output, payload)

    print(markdown(payload))


if __name__ == "__main__":
    main()
