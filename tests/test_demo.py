import json
import subprocess
import sys

from policyprobe.demo import run_demo


def test_demo_finds_one_wrong_denial_and_restarts_cleanly():
    rows = run_demo()
    assert len(rows) == 4
    assert all(not row["refunded_before"] for row in rows)
    assert [(row["bot"], row["order"]) for row in rows if not row["passed"]] == [
        ("flawed", "oct-31")
    ]
    assert [row["refunded_after"] for row in rows] == [True, False, False, False]
    assert run_demo() == rows


def test_json_output_contains_the_order_records():
    result = subprocess.check_output(
        [sys.executable, "-m", "policyprobe.demo", "--json"], text=True
    )
    assert json.loads(result) == run_demo()
