from datetime import date

from policyprobe.bundled import BundledTarget
from policyprobe.demo_shop import correct_bot, flawed_bot
from policyprobe.investigate_demo import expectation_for
from policyprobe.investigation import investigate
from policyprobe.orders import boundary_orders
from policyprobe.selection import ReturnSelector


def run(bot, budget):
    orders = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))
    return investigate(BundledTarget(bot), ReturnSelector(orders), expectation_for, budget)


def test_failure_changes_the_next_choice_and_preserves_purchase():
    result = run(flawed_bot, 6)
    assert [a.action for a in result.attempts] == ["explore", "repeat", "change", "explore", "explore"]
    first, repeat, changed = result.attempts[:3]
    assert first.order == repeat.order
    assert changed.order.purchased_on == first.order.purchased_on
    assert changed.order.order_id == first.order.order_id
    assert changed.order.requested_on != first.order.requested_on
    assert first.verdict.status == repeat.verdict.status == "missing_refund"
    assert changed.verdict.passed
    assert all(a.conversation.refunded_before is False for a in result.attempts)


def test_passing_cases_do_not_need_repeats():
    result = run(correct_bot, 6)
    assert [a.action for a in result.attempts] == ["explore"] * 3


def test_budget_includes_repeats_and_allows_zero():
    assert run(flawed_bot, 0).attempts == ()
    result = run(flawed_bot, 2)
    assert [a.action for a in result.attempts] == ["explore", "repeat"]
    assert result.stop_reason == "Conversation budget exhausted."
