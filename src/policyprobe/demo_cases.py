"""Fixed inputs and independently labeled outcomes for the offline demo."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ReturnCase:
    order_id: str
    purchased_on: date
    requested_on: date
    expected_refund: bool
    clause: str


CASES = (
    ReturnCase("oct-31", date(2026, 10, 31), date(2026, 11, 20), True, "Earlier purchases"),
    ReturnCase("nov-01", date(2026, 11, 1), date(2026, 11, 20), False, "Return window"),
)
