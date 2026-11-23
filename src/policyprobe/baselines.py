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


def checked_ids(answer, candidates):
    values = answer["case_ids"]
    if not isinstance(values, list) or any(
        not isinstance(value, str) or value not in candidates for value in values
    ):
        raise ValueError("model must select case ids from the supplied pool")
    return values


class ModelPlan:
    def __init__(self, scenario, client, method, budget):
        self.scenario = deepcopy(scenario)
        self.client = client
        self.method = method
        self.budget = budget
        self.ids = None

    def choose(self, observations):
        if self.ids is None:
            answer = self.client.complete(
                'Plan the test cases before execution. Return JSON {"case_ids": [ids]}. '
                f"Select at most {self.budget} cases; repeats count toward the limit.\n"
                + json.dumps({"policy": context_for(self.scenario, self.method),
                              "candidates": self.scenario["cases"]})
            )
            self.ids = checked_ids(answer, {case["id"] for case in self.scenario["cases"]})
            if len(self.ids) > self.budget:
                raise ValueError("model plan exceeds the conversation budget")
        if len(observations) >= len(self.ids):
            return None
        return self.ids[len(observations)]


def make_selector(method, scenario, client, budget):
    if method not in METHODS:
        raise ValueError("unknown benchmark method")
    if method == "boundary":
        return BoundaryPlan(scenario)
    if client is None:
        raise ValueError("this method requires a model client")
    if method == "adaptive":
        return AdaptivePlan(scenario, client, budget)
    return ModelPlan(scenario, client, method, budget)


class AdaptivePlan(ModelPlan):
    def choose(self, observations):
        answer = self.client.complete(
            'Choose the next test from the candidate pool using observed outcomes. '
            'Return JSON {"case_ids": [one_id]} or {"case_ids": []} to stop.\n'
            + json.dumps({"policy": context_for(self.scenario, "retrieval"),
                          "candidates": self.scenario["cases"],
                          "observations": observations,
                          "remaining": self.budget - len(observations)})
        )
        ids = checked_ids(answer, {case["id"] for case in self.scenario["cases"]})
        if len(ids) > 1:
            raise ValueError("adaptive selection must choose one case at a time")
        return ids[0] if ids else None
