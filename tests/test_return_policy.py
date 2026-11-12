from datetime import date

from policyprobe.reference import return_allowed
from policyprobe.store import add_order, order_state, order_store, record_refund


def test_two_shoppers_on_opposite_sides_of_policy_change():
    requested_on = date(2026, 11, 20)
    shoppers = [(date(2026, 10, 31), True), (date(2026, 11, 1), False)]
    for purchased_on, expected_refund in shoppers:
        with order_store() as db:
            add_order(db, "order-1", purchased_on)
            stored_date, refunded = order_state(db, "order-1")
            assert not refunded
            if return_allowed(stored_date, requested_on):
                record_refund(db, "order-1")
            assert order_state(db, "order-1") == (purchased_on, expected_refund)
