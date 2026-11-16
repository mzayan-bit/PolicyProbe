"""Inspect reproducible shopper inputs for an explicit simulated request date."""

import argparse
from dataclasses import asdict
from datetime import date
import json

from .orders import boundary_orders


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cutoff", type=date.fromisoformat, required=True)
    parser.add_argument("--requested-on", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    try:
        orders = boundary_orders(args.cutoff, args.requested_on)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps([asdict(order) for order in orders], default=date.isoformat, indent=2))


if __name__ == "__main__":
    main()
