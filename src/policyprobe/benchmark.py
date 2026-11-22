"""Load frozen benchmark inputs independently of the scorer's answers."""

from datetime import date
from hashlib import sha256
import json
from pathlib import Path


def verify_dataset(folder: Path) -> str:
    manifest = json.loads((folder / "manifest.json").read_text())
    for name in ("scenarios.json", "answers.json"):
        actual = sha256((folder / name).read_bytes()).hexdigest()
        if actual != manifest["sha256"][name]:
            raise ValueError(f"benchmark file changed: {name}")
    return manifest["version"]


def load_scenarios(folder: Path, split: str) -> list[dict]:
    if split not in ("development", "evaluation"):
        raise ValueError("unknown benchmark split")
    scenarios = json.loads((folder / "scenarios.json").read_text())
    identifiers = set()
    for scenario in scenarios:
        for case in scenario["cases"]:
            if case["id"] in identifiers:
                raise ValueError("duplicate benchmark case")
            identifiers.add(case["id"])
            if date.fromisoformat(case["requested_on"]) < date.fromisoformat(case["purchased_on"]):
                raise ValueError("request predates purchase")
            if case["action"] not in ("return", "exchange"):
                raise ValueError("unknown action")
    return [s for s in scenarios if s["split"] == split]


def score_outcomes(folder: Path, observed: dict[str, bool]) -> dict[str, bool]:
    answers = json.loads((folder / "answers.json").read_text())
    scores = {}
    for identifier, allowed in observed.items():
        if type(allowed) is not bool:
            raise ValueError("an outcome must be a verified boolean")
        scores[identifier] = allowed == answers[identifier]["allowed"]
    return scores
