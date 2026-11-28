"""Independent outcome oracles for paired policy executions."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Outcome:
    action: str
    state: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        if not self.action.strip():
            raise ValueError("action must be nonempty")
        if len(dict(self.state)) != len(self.state):
            raise ValueError("state keys must be unique")
        object.__setattr__(self, "state", tuple(sorted(self.state)))


@dataclass(frozen=True)
class TransitionOracle:
    before: frozenset[Outcome]
    after: frozenset[Outcome]
    group: Literal["change", "preserve", "clarify"]

    def __post_init__(self):
        if not self.before or not self.after:
            raise ValueError("both policy versions need permitted outcomes")
        if self.group not in ("change", "preserve", "clarify"):
            raise ValueError("unknown transition group")
        if self.group == "preserve" and self.before != self.after:
            raise ValueError("preserve requires equal permitted outcome sets")
        if self.group == "change" and self.before & self.after:
            raise ValueError("required change needs disjoint outcome sets")
        if self.group == "clarify" and any(o.action != "clarify" for o in self.after):
            raise ValueError("clarification cases require a clarification outcome")


@dataclass(frozen=True)
class TransitionVerdict:
    status: str
    before_correct: bool | None
    after_correct: bool | None
    expected_group: str


def score_transition(before: Outcome | None, after: Outcome | None,
                     oracle: TransitionOracle) -> TransitionVerdict:
    old_ok = None if before is None else before in oracle.before
    new_ok = None if after is None else after in oracle.after
    if old_ok is None or new_ok is None:
        status = "incomplete"
    elif old_ok and new_ok:
        status = "correct_transition"
    elif old_ok:
        status = "introduced_failure"
    elif new_ok:
        status = "recovered"
    else:
        status = "persistent_failure"
    return TransitionVerdict(status, old_ok, new_ok, oracle.group)
