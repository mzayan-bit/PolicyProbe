"""Conversation adapter for the bundled scripted shops."""

from contextlib import contextmanager

from .store import order_state, shopper_store


class BundledTarget:
    def __init__(self, bot):
        self.bot = bot

    @contextmanager
    def open(self, order):
        with shopper_store(order) as db:
            yield _ShopSession(db, order, self.bot)


class _ShopSession:
    def __init__(self, db, order, bot):
        self.db = db
        self.order = order
        self.bot = bot

    def refunded(self):
        return order_state(self.db, self.order.order_id)[1]

    def send(self, message):
        if message.strip() != self.order.order_id:
            return "What is your order number?"
        return self.bot(self.db, self.order.order_id, self.order.requested_on)
