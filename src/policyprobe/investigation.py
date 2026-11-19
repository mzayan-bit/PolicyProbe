"""Budgeted conversations with an inspectable choice before every run."""

from dataclasses import dataclass
from collections.abc import Callable
from typing import Protocol

from .conversation import Conversation, Target, converse
from .orders import ShopperOrder
from .verdict import Expectation, Verdict, evaluate


@dataclass(frozen=True)
class Attempt:
    action: str
    reason: str
    order: ShopperOrder
    expectation: Expectation
    conversation: Conversation
    verdict: Verdict


@dataclass(frozen=True)
class Choice:
    action: str
    reason: str
    order: ShopperOrder | None = None


class Selector(Protocol):
    def choose(self, history: tuple[Attempt, ...]) -> Choice: ...


@dataclass(frozen=True)
class Investigation:
    attempts: tuple[Attempt, ...]
    stop_reason: str


def investigate(target: Target, selector: Selector,
                expectation_for: Callable[[ShopperOrder], Expectation],
                budget: int = 20) -> Investigation:
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    attempts = []
    for _ in range(budget):
        choice = selector.choose(tuple(attempts))
        if choice.action == "stop":
            return Investigation(tuple(attempts), choice.reason)
        if choice.action not in ("explore", "repeat", "change") or choice.order is None:
            raise ValueError("a runnable choice needs an action and order")
        if not choice.reason.strip():
            raise ValueError("a choice needs a reason")
        expected = expectation_for(choice.order)
        result = converse(target, choice.order,
                          ["I'd like to return my order.", choice.order.order_id])
        attempts.append(Attempt(choice.action, choice.reason, choice.order, expected,
                                result, evaluate(result, expected)))
    return Investigation(tuple(attempts), "Conversation budget exhausted.")
