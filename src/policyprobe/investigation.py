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
