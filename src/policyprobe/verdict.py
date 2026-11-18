"""Judge recorded order outcomes against an expectation set before a run."""

from dataclasses import dataclass
from .conversation import Conversation


@dataclass(frozen=True)
class Expectation:
    refunded: bool | None
    clause: str


@dataclass(frozen=True)
class Verdict:
    status: str
    reason: str

    @property
    def passed(self) -> bool | None:
        if self.status in ("incomplete", "ambiguous"):
            return None
        return self.status == "pass"


def evaluate(result: Conversation, expected: Expectation) -> Verdict:
    if result.error:
        return Verdict("incomplete", result.error)
    if type(result.refunded_before) is not bool or type(result.refunded_after) is not bool:
        return Verdict("incomplete", "Missing order observations.")
    if result.refunded_before:
        return Verdict("incomplete", "Order was already refunded before the test.")
    if expected.refunded is None or not expected.clause.strip():
        return Verdict("ambiguous", "A policy decision and supporting clause are required.")
    if result.refunded_after == expected.refunded:
        return Verdict("pass", "Recorded order outcome matches the policy expectation.")
    if result.refunded_after:
        return Verdict("wrong_approval", "Refund recorded for an ineligible order.")
    return Verdict("missing_refund", "Eligible order has no recorded refund.")
