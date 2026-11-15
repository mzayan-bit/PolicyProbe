from dataclasses import replace
from pathlib import Path

import pytest

from policyprobe.policy import compare_policies
from policyprobe.retrieval import Evidence, full_context, related_context, search, window_conflicts


ROOT = Path(__file__).resolve().parents[1] / "examples/gift-orders"


def test_search_finds_unchanged_gift_exception_in_another_document():
    full = full_context(ROOT / "after", "after")
    change, = compare_policies(ROOT / "before", ROOT / "after")
    assert change.kind == "edited"
    picked = related_context(full, change.after, 2)
    assert [c.citation for c in picked] == ["after/returns.md:3", "after/gifts.md:3"]
    assert len(full) == 3
    assert not window_conflicts(picked)
    assert search(full, "unknownterm") == []
    assert search(full, "gift", 0) == []
    with pytest.raises(ValueError):
        related_context(full, change.before)


def test_conflict_preserves_both_sources_in_same_version():
    full = full_context(ROOT / "before", "before")
    rule = next(item for item in full if item.clause.document == "returns.md")
    conflicting = replace(rule.clause, document="faq.md", text=rule.clause.text.replace("30", "14"))
    faq = Evidence("before", conflicting)
    assert window_conflicts([rule, faq]) == [(rule, faq)]
    assert window_conflicts([rule, Evidence("after", conflicting)]) == []
