import json
from pathlib import Path

import pytest

from policyprobe.benchmark import load_scenarios
from policyprobe.benchmark_run import run_scenario

ROOT = Path(__file__).resolve().parents[1] / "benchmarks/v1"


class FakeModel:
    model = "test-double"

    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0
        self.prompts = []

    def complete(self, prompt):
        self.calls += 1
        self.prompts.append(prompt)
        return next(self.responses)


def test_fixed_methods_plan_once_and_adaptive_sees_outcome():
    scenario = load_scenarios(ROOT, "development")[0]
    ids = [case["id"] for case in scenario["cases"][:2]]
    for method in ("full", "retrieval"):
        model = FakeModel([{"case_ids": ids}])
        result = run_scenario(ROOT, scenario, method, lambda case: False, model, 2)
        assert model.calls == 1 and len(result["attempts"]) == 2
        assert "observations" not in model.prompts[0]
    model = FakeModel([{"case_ids": [ids[0]]}, {"case_ids": [ids[0]]}])
    result = run_scenario(ROOT, scenario, "adaptive", lambda case: False, model, 2)
    assert len(result["attempts"]) == model.calls == 2
    assert '"allowed": false' in model.prompts[1]
    assert '"passed"' not in model.prompts[1]


def test_failed_attempts_consume_budget():
    scenario = load_scenarios(ROOT, "development")[0]
    def failed(case):
        raise TimeoutError("offline")
    result = run_scenario(ROOT, scenario, "boundary", failed, budget=2)
    assert len(result["attempts"]) == 2
    assert all(a["passed"] is None for a in result["attempts"])
    assert run_scenario(ROOT, scenario, "boundary", failed, budget=0)["attempts"] == []


def test_invalid_model_plan_is_rejected():
    scenario = load_scenarios(ROOT, "development")[0]
    model = FakeModel([{"case_ids": ["invented-case"]}])
    with pytest.raises(ValueError, match="supplied pool"):
        run_scenario(ROOT, scenario, "full", lambda case: True, model, 2)
