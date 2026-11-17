"""Run a shopper's messages and collect independent order observations."""

from collections.abc import Iterable
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Protocol

from .orders import ShopperOrder


class Session(Protocol):
    def send(self, message: str) -> str: ...
    def refunded(self) -> bool: ...


class Target(Protocol):
    def open(self, order: ShopperOrder) -> AbstractContextManager[Session]: ...


@dataclass
class Conversation:
    turns: list[tuple[str, str]] = field(default_factory=list)
    refunded_before: bool | None = None
    refunded_after: bool | None = None
    error: str | None = None


class TargetError(Exception):
    """A staging operation could not be completed or verified."""


def converse(target: Target, order: ShopperOrder, messages: Iterable[str]) -> Conversation:
    result = Conversation()
    try:
        with target.open(order) as session:
            result.refunded_before = session.refunded()
            for message in messages:
                result.turns.append(("shopper", message))
                reply = session.send(message)
                result.turns.append(("bot", reply))
            result.refunded_after = session.refunded()
    except TargetError as exc:
        result.error = str(exc)
    return result
