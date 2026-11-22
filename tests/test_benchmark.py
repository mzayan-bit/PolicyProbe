import json
from pathlib import Path

import pytest

from policyprobe.benchmark import load_scenarios, score_outcomes, verify_dataset

ROOT = Path(__file__).resolve().parents[1] / "benchmarks/v1"


def test_frozen_cases_cover_the_five_families():
    assert verify_dataset(ROOT) == "v1"
    development = load_scenarios(ROOT, "development")
    evaluation = load_scenarios(ROOT, "evaluation")
    assert len(development) == len(evaluation) == 5
    assert {s["id"] for s in development}.isdisjoint(s["id"] for s in evaluation)
    assert {s["family"] for s in development} == {
        "cutoff", "grandfather", "exception", "exchange", "wording",
    }
    assert all("allowed" not in case for s in development + evaluation for case in s["cases"])


def test_scorer_handles_clean_and_broken_targets():
    answers = json.loads((ROOT / "answers.json").read_text())
    clean = {key: value["allowed"] for key, value in answers.items()}
    assert all(score_outcomes(ROOT, clean).values())
    assert not any(score_outcomes(ROOT, {key: not value for key, value in clean.items()}).values())
    with pytest.raises(ValueError):
        score_outcomes(ROOT, {"cutoff-a-0": "true"})


def test_expected_boundaries_are_explicit():
    assert score_outcomes(ROOT, {
        "cutoff-a-1": True, "cutoff-a-2": False,
        "grandfather-a-0": True, "grandfather-a-1": False,
        "exception-b-2": True, "exception-b-3": False,
        "exchange-a-0": False, "exchange-a-1": True,
        "wording-b-1": True, "wording-b-2": False,
    }) == dict.fromkeys([
        "cutoff-a-1", "cutoff-a-2", "grandfather-a-0", "grandfather-a-1",
        "exception-b-2", "exception-b-3", "exchange-a-0", "exchange-a-1",
        "wording-b-1", "wording-b-2",
    ], True)
