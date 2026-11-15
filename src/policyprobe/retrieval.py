"""Offline context selection over a single version of a policy folder."""

from dataclasses import dataclass
from pathlib import Path

from .policy import Clause, read_policy


@dataclass(frozen=True)
class Evidence:
    version: str
    clause: Clause

    @property
    def citation(self) -> str:
        return f"{self.version}/{self.clause.document}:{self.clause.line}"


def full_context(folder: Path, version: str) -> list[Evidence]:
    return [Evidence(version, clause) for clause in read_policy(folder).values()]
