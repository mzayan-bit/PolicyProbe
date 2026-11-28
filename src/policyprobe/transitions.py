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
