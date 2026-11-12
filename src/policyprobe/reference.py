"""Handwritten reference for the policy in examples/returns/after."""

from datetime import date


def return_allowed(purchased_on: date, requested_on: date) -> bool:
    window = 30 if purchased_on < date(2026, 11, 1) else 14
    return 0 <= (requested_on - purchased_on).days <= window
