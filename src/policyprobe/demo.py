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


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the full order records")
    args = parser.parse_args()
    records = run_demo()
    if args.json:
        print(json.dumps(records, indent=2))
        return
    for row in records:
        verdict = "pass" if row["passed"] else "fail"
        print(f"{verdict:4}  {row['bot']:7}  {row['order']}  "
              f"refund expected={row['expected_refund']} recorded={row['refunded_after']}  "
              f"({row['clause']})")


if __name__ == "__main__":
    main()
