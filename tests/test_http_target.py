import io
import json
from unittest.mock import patch

from policyprobe.conversation import converse
from policyprobe.demo_cases import CASES
from policyprobe.http_target import HttpTarget


def test_staging_protocol_keeps_labels_out_and_reads_the_order():
    calls = []
    responses = iter([{}, {"refunded": False}, {"reply": "order number?"},
                      {"reply": "refunded"}, {"refunded": True}, {}])

    def respond(request, timeout):
        calls.append((request.method, request.full_url, request.data))
        assert timeout == 0.5
        return io.BytesIO(json.dumps(next(responses)).encode())

    with patch("policyprobe.http_target.urlopen", respond):
        result = converse(HttpTarget("http://localhost:9000", timeout=0.5),
                          CASES[0], ["return", CASES[0].order_id])
    assert result.refunded_after and result.error is None
    assert [method for method, _, _ in calls] == ["PUT", "GET", "POST", "POST", "GET", "DELETE"]
    assert calls[-1][1] == calls[0][1]
    assert set(json.loads(calls[0][2])) == {"order_id", "purchased_on", "requested_on"}


def test_http_timeout_attempts_cleanup():
    responses = [io.BytesIO(b"{}"), io.BytesIO(b'{"refunded":false}'),
                 TimeoutError("late reply"), io.BytesIO()]
    with patch("policyprobe.http_target.urlopen", side_effect=responses) as transport:
        result = converse(HttpTarget("http://localhost:9000"), CASES[0], ["hello"])
    assert "late reply" in result.error
    assert result.refunded_after is None
    assert transport.call_args.args[0].method == "DELETE"
