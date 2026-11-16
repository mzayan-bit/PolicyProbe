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
