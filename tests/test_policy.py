from datetime import date
from pathlib import Path

import pytest

from policyprobe.policy import compare_policies, read_policy


EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "returns"


def test_return_window_diff():
    changes = compare_policies(EXAMPLES / "before", EXAMPLES / "after")
    exception, window = changes
    assert (exception.kind, exception.before, exception.after.line) == ("added", None, 7)
    assert exception.after.date_boundaries == [("before", date(2026, 11, 1))]
    assert window.kind == "edited"
    assert window.before.headings == ("Standard returns", "Return window")
    assert window.after.date_boundaries == [("on or after", date(2026, 11, 1))]
    assert window.before.document == window.after.document == "returns.md"


def test_wording_and_substantive_change(tmp_path):
    first, second = [tmp_path / name for name in ("first", "second")]
    first.mkdir()
    second.mkdir()
    body = "An item may be returned within 14 calendar days of purchase."
    (first / "a.md").write_text(body)
    revised = body.replace("may", "can")
    (second / "a.md").write_text(revised)
    assert compare_policies(first, second)[0].kind == "wording"
    (second / "a.md").write_text(revised.replace("14", "30"))
    assert compare_policies(first, second)[0].kind == "edited"
    assert compare_policies(first, first) == []
    (second / "a.md").unlink()
    assert compare_policies(first, second)[0].kind == "removed"


def test_nested_document_repeated_heading_and_fenced_example(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "p.md").write_text("intro\n## Rule\none\n## Rule\n~~~\n# Example\n~~~\n")
    intro, one, two = read_policy(tmp_path).values()
    assert intro.document == "docs/p.md"
    assert (one.occurrence, two.occurrence, two.line) == (1, 2, 4)
    assert "# Example" in two.text
    with pytest.raises(NotADirectoryError):
        read_policy(tmp_path / "missing")
