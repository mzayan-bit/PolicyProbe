import pytest

from policyprobe.paired import run_pair
from policyprobe.paired_demo import ACCEPT, DECLINE, CLARIFY, OLD, NEW, execute
from policyprobe.transitions import TransitionOracle, score_transition


def oracle(before, after, group):
    return TransitionOracle(frozenset([before]), frozenset([after]), group)


@pytest.mark.parametrize("old,new,status", [
    (ACCEPT, ACCEPT, "correct_transition"),
    (ACCEPT, DECLINE, "introduced_failure"),
    (DECLINE, DECLINE, "persistent_failure"),
    (DECLINE, ACCEPT, "recovered"),
    (None, ACCEPT, "incomplete"),
])
def test_preservation_requires_correctness_under_both_versions(old, new, status):
    assert score_transition(old, new, oracle(ACCEPT, ACCEPT, "preserve")).status == status


def test_same_input_fresh_ledger_and_identical_policy_control():
    customer = {"age": 20, "premium": True}
    result = run_pair(customer, OLD, NEW, execute, oracle(ACCEPT, ACCEPT, "preserve"))
    assert result.verdict.status == "correct_transition"
    control = run_pair(customer, OLD, OLD, execute, oracle(ACCEPT, ACCEPT, "preserve"))
    assert control.before.policy_hash == control.after.policy_hash
    assert control.before.outcome == control.after.outcome


def test_unknown_premium_requires_specific_question():
    result = run_pair({"age": 20, "premium": None}, OLD, NEW, execute,
                      oracle(ACCEPT, CLARIFY, "clarify"))
    assert result.verdict.status == "correct_transition"
    assert score_transition(ACCEPT, DECLINE, oracle(ACCEPT, CLARIFY, "clarify")).after_correct is False


def test_mutating_callback_cannot_change_second_input():
    seen = []
    def target(customer, policy):
        seen.append(customer["value"])
        customer["value"] = 99
        return ACCEPT
    original = {"value": 1}
    run_pair(original, OLD, NEW, target, oracle(ACCEPT, ACCEPT, "preserve"))
    assert original == {"value": 1}
    assert seen == [1, 1]


def test_timeout_keeps_other_side_observable():
    def target(customer, policy):
        if policy == OLD:
            raise TimeoutError("offline")
        return ACCEPT
    result = run_pair({}, OLD, NEW, target, oracle(ACCEPT, ACCEPT, "preserve"))
    assert result.verdict.status == "incomplete"
    assert result.after.outcome == ACCEPT
