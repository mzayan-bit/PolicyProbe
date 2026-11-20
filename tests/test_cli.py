import json
import os
import subprocess
import sys

import pytest

from policyprobe.replay import replay


def test_check_and_replay_through_cli(tmp_path):
    path = tmp_path / "run.json"
    command = [sys.executable, "-m", "policyprobe.cli", "check", "--output", str(path)]
    output = subprocess.check_output(command, text=True)
    payload = json.loads(path.read_text())
    row = payload["attempts"][0]
    assert row["verdict"]["status"] == "missing_refund"
    assert row["case_id"] in output
    again = subprocess.check_output([
        sys.executable, "-m", "policyprobe.cli", "replay", str(path),
        "--case-id", row["case_id"],
    ], text=True)
    result = json.loads(again)["attempts"][0]
    assert result["case_id"] == row["case_id"]
    assert result["verdict"] == row["verdict"]
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert json.loads(path.read_text()) == payload
    row["order"]["purchased_on"] = "2026-10-30"
    with pytest.raises(ValueError, match="case id"):
        replay(payload, row["case_id"])
