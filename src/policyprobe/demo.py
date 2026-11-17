"""Compare scripted refund decisions with labeled cases using isolated stores."""

from .demo_cases import CASES
from .demo_shop import correct_bot, flawed_bot
from .conversation import converse
from .bundled import BundledTarget
from .http_target import HttpTarget


def run_demo(targets=None) -> list[dict]:
    if targets is None:
        targets = (("correct", BundledTarget(correct_bot)), ("flawed", BundledTarget(flawed_bot)))
    records = []
    for name, target in targets:
        for case in CASES:
            result = converse(target, case, ["I'd like to return my order.", case.order_id])
            records.append({
                "bot": name,
                "order": case.order_id,
                "purchased_on": case.purchased_on.isoformat(),
                "requested_on": case.requested_on.isoformat(),
                "clause": case.clause,
                "expected_refund": case.expected_refund,
                "refunded_before": result.refunded_before,
                "refunded_after": result.refunded_after,
                "reply": next((text for role, text in reversed(result.turns) if role == "bot"), None),
                "turns": [list(turn) for turn in result.turns],
                "error": result.error,
                "passed": None if result.error else result.refunded_after == case.expected_refund,
            })
    return records


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the full order records")
    parser.add_argument("--target-url", help="use a staging bot implementing the session API")
    args = parser.parse_args()
    records = run_demo([("staging", HttpTarget(args.target_url))]) if args.target_url else run_demo()
    if args.json:
        print(json.dumps(records, indent=2))
    for row in ([] if args.json else records):
        verdict = "pass" if row["passed"] else "fail"
        if row["error"]:
            verdict = "incomplete"
        print(f"{verdict:4}  {row['bot']:7}  {row['order']}  "
              f"refund expected={row['expected_refund']} recorded={row['refunded_after']}  "
              f"({row['clause']})")

    if any(row["error"] for row in records):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
