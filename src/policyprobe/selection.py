"""A deterministic adaptive baseline for the return-window experiment."""

from dataclasses import replace
from datetime import timedelta

from .investigation import Choice


class ReturnSelector:
    def __init__(self, candidates):
        self.candidates = tuple(candidates)

    def choose(self, history):
        explored = {attempt.order for attempt in history if attempt.action == "explore"}
        for order in self.candidates:
            if order not in explored:
                return Choice("explore", "Try the next untested purchase scenario.", order)
        return Choice("stop", "All candidate scenarios have been visited.")
