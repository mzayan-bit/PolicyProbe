"""Scripted premium-return example demonstrating paired transition scoring."""

from dataclasses import asdict
import json
import sqlite3
from contextlib import closing

from .paired import run_pair
from .transitions import Outcome, TransitionOracle

OLD = "Returns within 30 days."
NEW = "Returns within 14 days. Premium customers retain 30 days."
ACCEPT = Outcome("refund", (("refunded", "true"),))
DECLINE = Outcome("decline", (("refunded", "false"),))
CLARIFY = Outcome("clarify", (("question", "premium_status"), ("refunded", "false")))


def execute(customer, policy):
    if policy not in (OLD, NEW):
        raise ValueError("unsupported demo policy")
    premium = customer["premium"]
    if policy == NEW and premium is None and 14 < customer["age"] <= 30:
        return CLARIFY
    window = 30 if policy == OLD or premium is True else 14
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE refunds (recorded INTEGER)")
        if 0 <= customer["age"] <= window:
            db.execute("INSERT INTO refunds VALUES (1)")
        refunded = db.execute("SELECT COUNT(*) FROM refunds").fetchone()[0] > 0
    return ACCEPT if refunded else DECLINE


def main():
    cases = [
        ({"age": 20, "premium": False}, DECLINE, "change"),
        ({"age": 20, "premium": True}, ACCEPT, "preserve"),
        ({"age": 10, "premium": False}, ACCEPT, "preserve"),
        ({"age": 20, "premium": None}, CLARIFY, "clarify"),
    ]
    for customer, expected, group in cases:
        oracle = TransitionOracle(frozenset([ACCEPT]), frozenset([expected]), group)
        print(json.dumps({"customer": customer,
                          "result": asdict(run_pair(customer, OLD, NEW, execute, oracle))}))


if __name__ == "__main__":
    main()
