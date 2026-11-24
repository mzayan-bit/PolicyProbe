"""Scripted pilot targets with an action ledger and a seeded window defect."""

from datetime import date
import sqlite3


class BenchmarkShop:
    def __init__(self, scenario, broken=False):
        self.family = scenario["family"]
        self.short, self.long, self.year = (14, 30, 2026)
        if scenario["id"].endswith("-b"):
            self.short, self.long, self.year = (10, 25, 2025)
        self.broken = broken
        self.records = []

    def __call__(self, case):
        purchase = date.fromisoformat(case["purchased_on"])
        age = (date.fromisoformat(case["requested_on"]) - purchase).days
        window = self.short
        if self.family == "grandfather" and purchase < date(self.year, 11, 1):
            window = self.long
        if self.family == "exception" and case["item_category"] == "gift":
            window = self.long
        if self.family == "exchange" and case["action"] == "exchange":
            window = self.long
        if self.broken:
            window = self.short - 1
        allowed = 0 <= age <= window
        with sqlite3.connect(":memory:") as db:
            try:
                db.execute("CREATE TABLE actions (case_id TEXT, action TEXT)")
                if allowed:
                    db.execute("INSERT INTO actions VALUES (?, ?)", (case["id"], case["action"]))
                rows = db.execute("SELECT case_id, action FROM actions").fetchall()
                self.records.append({"case_id": case["id"], "actions": rows})
                return bool(rows)
            finally:
                db.close()
