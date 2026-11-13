"""Compare scripted refund decisions with labeled cases using isolated stores."""

from .demo_cases import CASES
from .demo_shop import correct_bot, flawed_bot
from .store import add_order, order_state, order_store


def run_demo() -> list[dict]:
    records = []
    for name, bot in (("correct", correct_bot), ("flawed", flawed_bot)):
        for case in CASES:
            with order_store() as db:
                add_order(db, case.order_id, case.purchased_on)
                _, before = order_state(db, case.order_id)
                reply = bot(db, case.order_id, case.requested_on)
                _, after = order_state(db, case.order_id)
            records.append({
                "bot": name,
                "order": case.order_id,
                "purchased_on": case.purchased_on.isoformat(),
                "requested_on": case.requested_on.isoformat(),
                "clause": case.clause,
                "expected_refund": case.expected_refund,
                "refunded_before": before,
                "refunded_after": after,
                "reply": reply,
                "passed": after == case.expected_refund,
            })
    return records
