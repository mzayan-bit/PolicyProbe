from pathlib import Path

from policyprobe.change_report import changes_report, markdown

ROOT = Path(__file__).resolve().parents[1] / "examples/returns"


def test_policy_diff_keeps_exception_and_source():
    report = changes_report(ROOT / "before", ROOT / "after")
    assert {item["kind"] for item in report["changes"]} == {"added", "edited"}
    edited = next(item for item in report["changes"] if item["kind"] == "edited")
    assert edited["evidence"][0]["citation"] == "after/returns.md:3"
    assert any("30-day" in item["text"] for item in edited["evidence"])
    assert "Earlier purchases" in markdown(report)


def test_no_change_and_removal(tmp_path):
    assert changes_report(ROOT / "after", ROOT / "after")["changes"] == []
    report = changes_report(ROOT / "after", tmp_path)
    assert all(item["kind"] == "removed" and item["evidence"] == [] for item in report["changes"])
    assert "removed" in markdown(report)
