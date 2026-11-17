from contextlib import contextmanager

from policyprobe.bundled import BundledTarget
from policyprobe.conversation import TargetError, converse
from policyprobe.demo_cases import CASES
from policyprobe.demo_shop import correct_bot


def test_two_open_sessions_keep_separate_orders():
    target = BundledTarget(correct_bot)
    with target.open(CASES[0]) as first, target.open(CASES[0]) as second:
        assert first.send("return") == "What is your order number?"
        assert not first.refunded()
        first.send(CASES[0].order_id)
        assert first.refunded() and not second.refunded()


def test_unanswered_turn_is_saved():
    class Broken:
        @contextmanager
        def open(self, order):
            yield self

        def refunded(self):
            return False

        def send(self, message):
            raise TargetError("timed out")

    result = converse(Broken(), CASES[0], ["hello"])
    assert result.turns == [("shopper", "hello")]
    assert result.error == "timed out"
    assert result.refunded_after is None
