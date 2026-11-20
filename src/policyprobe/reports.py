"""Portable records for the bundled return-window experiment."""

from dataclasses import asdict
from datetime import date
from hashlib import sha256
import json


def case_id(order, expectation):
    payload = json.dumps({"order": asdict(order), "expectation": asdict(expectation)},
                         default=date.isoformat, sort_keys=True)
    return sha256(payload.encode()).hexdigest()[:16]


def report(result, target):
    attempts = []
    for attempt in result.attempts:
        record = asdict(attempt)
        record["case_id"] = case_id(attempt.order, attempt.expectation)
        attempts.append(record)
    return json.loads(json.dumps({
        "schema_version": 1, "scenario": "returns-2026-11-01",
        "target": target, "stop_reason": result.stop_reason, "attempts": attempts,
    }, default=date.isoformat))


def markdown(payload):
    lines = ["# PolicyProbe results", "", f"Scenario: {payload['scenario']}",
             f"Target: {payload['target']}", ""]
    for row in payload["attempts"]:
        lines.extend([
            f"## {row['case_id']}", "",
            f"Outcome: {row['verdict']['status']}",
            f"Reason: {row['verdict']['reason']}",
            f"Choice: {row['action']} — {row['reason']}",
            f"Policy clause: {row['expectation']['clause']}",
            f"Purchased: {row['order']['purchased_on']}",
            f"Requested: {row['order']['requested_on']}", "",
        ])
    lines.extend([payload["stop_reason"], ""])
    return "\n".join(lines)
