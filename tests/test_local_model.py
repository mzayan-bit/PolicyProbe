from datetime import date
from unittest.mock import Mock
import pytest

from policyprobe.local_model import LocalModel
from policyprobe.model_selector import ModelSelector, ModelShopper
from policyprobe.orders import boundary_orders


@pytest.mark.parametrize("endpoint", ["https://example.com", "http://localhost:11434",
                                     "http://127.0.0.1/api", "http://user@127.0.0.1"])
def test_remote_or_invalid_endpoints_are_rejected(endpoint):
    with pytest.raises(ValueError):
        LocalModel("model", endpoint)


def test_candidate_selection_and_stop():
    client = Mock()
    candidates = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))
    selector = ModelSelector(client, candidates)
    client.complete.return_value = {"index": 1, "reason": "check the cutoff"}
    assert selector.choose(()).order == candidates[1]
    client.complete.return_value = {"index": None, "reason": "enough evidence"}
    assert selector.choose(()).action == "stop"
    client.complete.return_value = {"index": True, "reason": "invalid"}
    with pytest.raises(ValueError):
        selector.choose(())


def test_shopper_keeps_order_number_as_second_turn():
    client = Mock()
    client.complete.return_value = {"message": "Please help me return this"}
    order = boundary_orders(date(2026, 11, 1), date(2026, 11, 20))[0]
    assert ModelShopper(client)(order) == ["Please help me return this", order.order_id]
