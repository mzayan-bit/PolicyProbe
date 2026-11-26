import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from policyprobe.benchmark import load_scenarios
from policyprobe.benchmark_run import run_scenario
from policyprobe.conversation import converse, TargetError
from policyprobe.demo_cases import CASES
from policyprobe.http_target import HttpTarget
from policyprobe.output import write_report


def test_concurrent_writers_publish_one_complete_report(tmp_path):
    path = tmp_path / "report.json"
    def publish(number):
        try:
            write_report(path, {"writer": number})
            return number
        except FileExistsError:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        winners = [n for n in pool.map(publish, [1, 2]) if n is not None]
    assert winners == [json.loads(path.read_text())["writer"]]
    assert list(tmp_path.iterdir()) == [path]


def test_interrupted_publish_leaves_no_partial_report(tmp_path):
    path = tmp_path / "report.json"
    with patch("policyprobe.output.os.link", side_effect=OSError("interrupted")):
        with pytest.raises(OSError):
            write_report(path, {"complete": True})
    assert list(tmp_path.iterdir()) == []
    write_report(path, {"complete": True})
    assert json.loads(path.read_text()) == {"complete": True}


def test_cleanup_keeps_the_original_failure():
    target = HttpTarget("http://localhost:9000")
    with patch.object(target, "request", side_effect=[
        TargetError("create timed out"), TargetError("delete timed out")
    ]):
        result = converse(target, CASES[0], ["hello"])
    assert "create timed out" in result.error
    assert "delete timed out" in result.error


def test_dataset_modified_during_execution_is_rejected(tmp_path):
    source = Path(__file__).resolve().parents[1] / "benchmarks/v1"
    folder = tmp_path / "dataset"
    shutil.copytree(source, folder)
    scenario = load_scenarios(folder, "development")[0]
    def target(case):
        with (folder / "answers.json").open("a") as file:
            file.write(" ")
        return True
    with pytest.raises(ValueError, match="benchmark file changed"):
        run_scenario(folder, scenario, "boundary", target, budget=1)
