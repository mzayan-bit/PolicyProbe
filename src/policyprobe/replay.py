"""Replay a saved bundled scenario in a fresh session."""

from datetime import date

from .bundled import BundledTarget
from .conversation import converse
from .demo_shop import correct_bot, flawed_bot
from .investigation import Attempt, Investigation
from .orders import ShopperOrder
from .reports import case_id, report
from .verdict import Expectation, evaluate


def replay(payload, identifier):
    if payload["schema_version"] != 1 or payload["scenario"] != "returns-2026-11-01":
        raise ValueError("unsupported report")
    targets = {"correct": correct_bot, "flawed": flawed_bot}
    bot = targets[payload["target"]]
    row = next((item for item in payload["attempts"] if item["case_id"] == identifier), None)
    if row is None:
        raise ValueError("case id was not found")
    data = row["order"]
    order = ShopperOrder(data["order_id"], date.fromisoformat(data["purchased_on"]),
                         date.fromisoformat(data["requested_on"]))
    expected = Expectation(**row["expectation"])
    if type(expected.refunded) is not bool or not isinstance(expected.clause, str):
        raise ValueError("invalid saved expectation")
    if case_id(order, expected) != identifier:
        raise ValueError("saved inputs do not match the case id")
    result = converse(BundledTarget(bot), order,
                      ["I'd like to return my order.", order.order_id])
    attempt = Attempt("repeat", "Replay saved inputs in a fresh session.", order,
                      expected, result, evaluate(result, expected))
    return report(Investigation((attempt,), "Replay complete."), payload["target"])
