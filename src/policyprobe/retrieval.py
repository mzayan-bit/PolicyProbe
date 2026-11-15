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


def search(clauses: list[Evidence], query: str, limit: int = 3) -> list[Evidence]:
    """Rank lexical overlaps with rare words weighted more heavily."""
    from collections import Counter
    from math import log
    import re

    if limit < 0:
        raise ValueError("limit must be nonnegative")
    terms = set(re.findall(r"\w+", query.casefold()))
    frequency = Counter()
    documents = []
    for item in clauses:
        content = " ".join((*item.clause.headings, item.clause.text))
        words = set(re.findall(r"\w+", content.casefold()))
        documents.append(words)
        frequency.update(words)
    ranked = []
    for item, words in zip(clauses, documents):
        overlap = sorted(terms & words)
        if overlap:
            score = sum(1 + log((1 + len(clauses)) / (1 + frequency[w])) for w in overlap)
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].citation))
    return [item for _, item in ranked[:limit]]
