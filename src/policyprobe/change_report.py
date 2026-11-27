"""Describe policy changes with retrieved evidence and an optional smoke check."""

from dataclasses import asdict
from pathlib import Path

from .policy import compare_policies
from .retrieval import full_context, related_context


def changes_report(before: Path, after: Path):
    context = full_context(after, "after")
    changes = []
    for change in compare_policies(before, after):
        evidence = related_context(context, change.after) if change.after else []
        changes.append({
            "kind": change.kind,
            "before": asdict(change.before) if change.before else None,
            "after": asdict(change.after) if change.after else None,
            "evidence": [{"citation": item.citation, "text": item.clause.text}
                         for item in evidence],
        })
    return {"changes": changes, "evaluation": "policy comparison only"}
