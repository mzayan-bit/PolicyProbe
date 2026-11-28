"""Execute identical customer inputs against isolated policy snapshots."""

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from time import monotonic
from collections.abc import Callable

from .transitions import Outcome, TransitionOracle, TransitionVerdict, score_transition


@dataclass(frozen=True)
class Execution:
    policy_hash: str
    outcome: Outcome | None
    error: str | None
    elapsed_seconds: float


@dataclass(frozen=True)
class PairedResult:
    before: Execution
    after: Execution
    verdict: TransitionVerdict


def run_pair(customer: dict, before_policy: str, after_policy: str,
             execute: Callable[[dict, str], Outcome],
             oracle: TransitionOracle) -> PairedResult:
    """execute must create a fresh environment each time; the oracle is never passed."""
    executions = []
    for policy in (before_policy, after_policy):
        started = monotonic()
        outcome = None
        error = None
        try:
            outcome = execute(deepcopy(customer), policy)
            if not isinstance(outcome, Outcome):
                raise ValueError("target must return a verified Outcome")
        except (OSError, ValueError) as exc:
            outcome = None
            error = str(exc)
        executions.append(Execution(sha256(policy.encode()).hexdigest(), outcome,
                                    error, monotonic() - started))
    old, new = executions
    return PairedResult(old, new, score_transition(old.outcome, new.outcome, oracle))
