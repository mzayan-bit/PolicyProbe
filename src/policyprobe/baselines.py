"""Comparable candidate selectors for frozen benchmark scenarios."""

from copy import deepcopy
from datetime import date
import json

from .policy import Clause
from .retrieval import Evidence, search


METHODS = ("boundary", "full", "retrieval", "adaptive")


def context_for(scenario, method):
    if method == "full":
        return {"before": scenario["before"], "after": scenario["after"]}
    clauses = [
        Evidence("after", Clause("policy", (), index, index + 1, text.strip()))
        for index, text in enumerate(scenario["after"].split("."))
        if text.strip()
    ]
    selected = search(clauses, scenario["before"] + " " + scenario["after"], limit=2)
    return {"before": scenario["before"], "after": [
        {"citation": item.citation, "text": item.clause.text} for item in selected
    ]}


class BoundaryPlan:
    def __init__(self, scenario):
        # Visit purchase dates and request ages in a fixed, reproducible order.
        def key(case):
            age = (date.fromisoformat(case["requested_on"]) -
                   date.fromisoformat(case["purchased_on"])).days
            return (case["purchased_on"], age, case["id"])
        self.ids = [case["id"] for case in sorted(scenario["cases"], key=key)]

    def choose(self, observations):
        if len(observations) >= len(self.ids):
            return None
        return self.ids[len(observations)]
