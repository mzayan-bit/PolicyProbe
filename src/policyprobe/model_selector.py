"""Model-selected shoppers from a fixed candidate pool."""

from dataclasses import asdict
from datetime import date
import json

from .investigation import Choice


class ModelSelector:
    def __init__(self, client, candidates):
        self.client = client
        self.candidates = tuple(candidates)

    def choose(self, history):
        observations = [{"order": asdict(a.order), "turns": a.conversation.turns,
                         "refunded": a.conversation.refunded_after,
                         "error": a.conversation.error} for a in history]
        prompt = (
            'Choose a shopper to test next. Return JSON with "index" (integer candidate index, '
            'or null to stop) and "reason" (nonempty string). You can repeat a candidate. '
            'Use the observed conversations to investigate behavior. Candidate inputs and observations:\n'
            + json.dumps({"candidates": [asdict(c) for c in self.candidates],
                          "observations": observations}, default=date.isoformat)
        )
        answer = self.client.complete(prompt)
        index, reason = answer["index"], answer["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("model must explain its choice")
        if index is None:
            return Choice("stop", reason)
        if type(index) is not int or not 0 <= index < len(self.candidates):
            raise ValueError("model chose an invalid candidate")
        order = self.candidates[index]
        repeated = any(a.order == order for a in history)
        return Choice("repeat" if repeated else "explore", reason, order)


class ModelShopper:
    def __init__(self, client):
        self.client = client

    def __call__(self, order):
        answer = self.client.complete(
            'Write a short request to return an order. Return JSON with "message", a nonempty string. '
            'The order number will be supplied separately in the next turn.'
        )
        message = answer["message"]
        if not isinstance(message, str) or not message.strip():
            raise ValueError("model must supply a shopper message")
        return [message, order.order_id]
