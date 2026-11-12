"""An isolated SQLite order ledger for a single simulated session."""

import sqlite3
from contextlib import closing, contextmanager
from datetime import date
from collections.abc import Iterator


@contextmanager
def order_store() -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("""
            CREATE TABLE orders (
                id TEXT PRIMARY KEY NOT NULL,
                purchased_on TEXT NOT NULL,
                refunded INTEGER NOT NULL DEFAULT 0 CHECK (refunded IN (0, 1))
            )
        """)
        yield db


def add_order(db: sqlite3.Connection, order_id: str, purchased_on: date) -> None:
    db.execute(
        "INSERT INTO orders (id, purchased_on) VALUES (?, ?)",
        (order_id, purchased_on.isoformat()),
    )


def order_state(db: sqlite3.Connection, order_id: str) -> tuple[date, bool]:
    row = db.execute(
        "SELECT purchased_on, refunded FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if row is None:
        raise KeyError(order_id)
    return date.fromisoformat(row[0]), bool(row[1])


def record_refund(db: sqlite3.Connection, order_id: str) -> None:
    result = db.execute("UPDATE orders SET refunded = 1 WHERE id = ?", (order_id,))
    if result.rowcount == 0:
        raise KeyError(order_id)
