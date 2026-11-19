"""A deterministic adaptive baseline for the return-window experiment."""

from dataclasses import replace
from datetime import timedelta

from .investigation import Choice


class ReturnSelector:
    def __init__(self, candidates):
        self.candidates = tuple(candidates)

    def choose(self, history):
        if history:
            last = history[-1]
            if last.action == "explore" and last.verdict.passed is False:
                return Choice("repeat", f"Repeat the observed {last.verdict.status} in a fresh session.",
                              last.order)
        explored = {attempt.order for attempt in history if attempt.action == "explore"}
        for order in self.candidates:
            if order not in explored:
                return Choice("explore", "Try the next untested purchase scenario.", order)
        return Choice("stop", "All candidate scenarios have been visited.")
