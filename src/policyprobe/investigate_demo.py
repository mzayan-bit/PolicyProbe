"""Run the deterministic adaptive baseline against the flawed bundled shop."""

import argparse
from dataclasses import asdict
from datetime import date
import json

from .bundled import BundledTarget
from .demo_shop import flawed_bot
from .investigation import investigate
from .orders import boundary_orders
from .reference import return_allowed
from .selection import ReturnSelector
from .verdict import Expectation


def expectation_for(order):
    clause = "Earlier purchases" if order.purchased_on < date(2026, 11, 1) else "Return window"
    return Expectation(return_allowed(order.purchased_on, order.requested_on), clause)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, default=5)
    args = parser.parse_args()
    if args.budget < 0:
        parser.error("--budget must be nonnegative")
    candidates = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))
    result = investigate(BundledTarget(flawed_bot), ReturnSelector(candidates),
                         expectation_for, args.budget)
    print(json.dumps(asdict(result), default=date.isoformat, indent=2))


if __name__ == "__main__":
    main()
