from pathlib import Path

from policyprobe.benchmark_suite import suite
from policyprobe.benchmark_metrics import summarize

ROOT = Path(__file__).resolve().parents[1] / "benchmarks/v1"


def test_all_clean_policies_and_exchange_execution():
    result = suite(ROOT, "development")
    clean = [run for run in result["runs"] if run["target"] == "clean"]
    assert len(clean) == 5
    assert all(row["passed"] for run in clean for row in run["attempts"])
    exchange = next(run for run in clean if run["scenario"] == "exchange-a")
    assert exchange["ledger"][1]["actions"] == [("exchange-a-1", "exchange")]
    seeded = [row for row in result["summary"] if row["target"] == "seeded"]
    assert all(row["distinct_seeded_defects"] == 1 for row in seeded)


def test_repeats_do_not_inflate_defect_count():
    result = suite(ROOT, "development")
    run = next(run for run in result["runs"] if run["target"] == "seeded")
    failure = next(row for row in run["attempts"] if row["passed"] is False)
    run["attempts"] = [failure, failure]
    summary = summarize([run])[0]
    assert summary["failing_cases"] == summary["distinct_seeded_defects"] == 1
    assert summary["attempts"] == 2
