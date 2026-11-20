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
