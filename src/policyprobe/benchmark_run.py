"""Run selectors under a shared attempt budget and score only after selection."""

from copy import deepcopy
from pathlib import Path
from time import monotonic

from .baselines import make_selector
from .benchmark import load_scenarios, score_outcomes, verify_dataset


def run_scenario(folder: Path, scenario, method, execute, client=None, budget=20):
    if type(budget) is not int or not 0 <= budget <= 20:
        raise ValueError("budget must be an integer from zero to twenty")
    version = verify_dataset(folder)
    selector = make_selector(method, scenario, client, budget)
    cases = {case["id"]: case for case in scenario["cases"]}
    observations = []
    calls_before = client.calls if client else 0
    started = monotonic()
    stop_reason = "budget exhausted"
    for _ in range(budget):
        identifier = selector.choose(deepcopy(observations))
        if identifier is None:
            stop_reason = "selector stopped"
            break
        try:
            outcome = execute(deepcopy(cases[identifier]))
            if type(outcome) is not bool:
                raise ValueError("target outcome must be a verified boolean")
            observation = {"case_id": identifier, "allowed": outcome, "error": None}
        except (OSError, ValueError) as exc:
            observation = {"case_id": identifier, "allowed": None, "error": str(exc)}
        observations.append(observation)
    # Reject dataset edits that occurred while the target was running.
    verify_dataset(folder)
    # The answer key is loaded only once all test choices have been made.
    scored = []
    for observation in observations:
        passed = None
        if observation["error"] is None:
            passed = score_outcomes(folder, {observation["case_id"]: observation["allowed"]})[
                observation["case_id"]]
        scored.append({**observation, "passed": passed})
    return {
        "dataset": version, "scenario": scenario["id"], "method": method,
        "budget": budget, "attempts": scored, "stop_reason": stop_reason,
        "model": client.model if client else None,
        "model_calls": client.calls - calls_before if client else 0,
        "elapsed_seconds": monotonic() - started,
    }
