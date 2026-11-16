from datetime import date

import pytest

from policyprobe.orders import ShopperOrder, boundary_orders
from policyprobe.store import order_state, record_refund, shopper_store


def test_leap_day_cutoff_uses_one_clock_and_stable_ids():
    cutoff = date(2028, 2, 29)
    clock = date(2028, 3, 1)
    orders = boundary_orders(cutoff, clock)
    assert [order.purchased_on for order in orders] == [
        date(2028, 2, 28), cutoff, clock,
    ]
    assert all(order.requested_on == clock for order in orders)
    assert len({order.order_id for order in orders}) == 3
    assert boundary_orders(cutoff, clock) == orders


@pytest.mark.parametrize("cutoff", [date.min, date.max])
def test_cutoff_needs_two_neighbors(cutoff):
    with pytest.raises(ValueError, match="both sides"):
        boundary_orders(cutoff, date.max)


def test_invalid_shoppers_are_rejected():
    with pytest.raises(ValueError, match="after purchase"):
        boundary_orders(date(2026, 11, 1), date(2026, 11, 1))
    with pytest.raises(ValueError, match="blank"):
        ShopperOrder(" ", date.min, date.min)


def test_replay_starts_with_an_unpaid_refund():
    order = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))[0]
    with shopper_store(order) as first:
        record_refund(first, order.order_id)
        with shopper_store(order) as second:
            assert order_state(second, order.order_id) == (order.purchased_on, False)
        assert order_state(first, order.order_id) == (order.purchased_on, True)
