import pytest

from policyprobe.bundled import BundledTarget
from policyprobe.conversation import Conversation
from policyprobe.demo import run_demo
from policyprobe.demo_shop import false_promise_bot, overgenerous_bot
from policyprobe.verdict import Expectation, evaluate


def test_promised_refund_is_checked_against_store():
    rows = run_demo([("promise", BundledTarget(false_promise_bot))])
    assert rows[0]["reply"] == "I've refunded your order."
    assert rows[0]["status"] == "missing_refund"
    assert rows[0]["passed"] is False


def test_ineligible_refund_is_wrong_approval():
    rows = run_demo([("generous", BundledTarget(overgenerous_bot))])
    assert rows[0]["status"] == "pass"
    assert rows[1]["status"] == "wrong_approval"


@pytest.mark.parametrize("result", [
    Conversation(),
    Conversation(refunded_before=True, refunded_after=True),
    Conversation(refunded_before=False, refunded_after=True, error="cleanup failed"),
    Conversation(refunded_before=False, refunded_after=1),
])
def test_unverified_result_cannot_pass(result):
    verdict = evaluate(result, Expectation(True, "returns.md"))
    assert verdict.status == "incomplete"
    assert verdict.passed is None


@pytest.mark.parametrize("expectation", [Expectation(None, "conflicting rules"), Expectation(True, "")])
def test_unresolved_policy_requires_review(expectation):
    verdict = evaluate(Conversation(refunded_before=False, refunded_after=False), expectation)
    assert verdict.status == "ambiguous"
    assert verdict.passed is None
