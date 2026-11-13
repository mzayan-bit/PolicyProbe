"""Scripted support bots that act on the session's order ledger."""

import sqlite3
from datetime import date

from .reference import return_allowed
from .store import order_state, record_refund


def correct_bot(db: sqlite3.Connection, order_id: str, requested_on: date) -> str:
    purchased_on, _ = order_state(db, order_id)
    if return_allowed(purchased_on, requested_on):
        record_refund(db, order_id)
        return "I've refunded your order."
    return "Your return window has closed."
