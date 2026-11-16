"""Inputs shared by shopper scenarios and the simulated store."""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ShopperOrder:
    order_id: str
    purchased_on: date
    requested_on: date

    def __post_init__(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order id must not be blank")
        if self.requested_on < self.purchased_on:
            raise ValueError("return request must be on or after purchase")


def boundary_orders(cutoff: date, requested_on: date) -> tuple[ShopperOrder, ...]:
    """Make one purchase on either side of the cutoff and one on the cutoff."""
    if cutoff in (date.min, date.max):
        raise ValueError("cutoff needs a representable day on both sides")
    orders = []
    for offset in (-1, 0, 1):
        purchased_on = cutoff + timedelta(days=offset)
        order_id = f"order-{purchased_on.isoformat()}-return-{requested_on.isoformat()}"
        orders.append(ShopperOrder(order_id, purchased_on, requested_on))
    return tuple(orders)
