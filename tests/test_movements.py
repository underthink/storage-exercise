from datetime import datetime, timedelta
import unittest

from src.models import Port, CargoProduct, CargoMovement, ProductQuantity
from src.movements import update_balances_from_movements


def _make_default_test_balances():
    port_a = Port("A")
    port_a.set_product_quantity(CargoProduct.Diesel, 2, 0.5)
    port_a.set_product_quantity(CargoProduct.CrudeOil, 4, 0.5)

    port_b = Port("B")
    port_b.set_product_quantity(CargoProduct.Diesel, 2, 0.5)
    port_b.set_product_quantity(CargoProduct.CrudeOil, 4, 0.5)

    return {"a": port_a, "b": port_b}


def _make_movement(**movement_update_kwargs):
    return CargoMovement(
        **(
            dict(
                loading_port="a",
                load_time=datetime(2021, 1, 1, 0, 0, 0),
                discharge_port="b",
                discharge_time=datetime(2021, 1, 2, 1, 2, 3),
                product=CargoProduct.Diesel,
                quantity=1,
            )
            | movement_update_kwargs
        )
    )


class MovementModellingTests(unittest.TestCase):
    def test_movements_updates_port_balances(self):
        balances = _make_default_test_balances()
        movements = [_make_movement()]
        cutoff = datetime(2022, 1, 1, 0, 0, 0)

        update_balances_from_movements(balances, movements, cutoff)

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(1, 4.0)),
            ],
            sorted(balances["a"].iter_products()),
        )

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(3, 4.0)),
            ],
            sorted(balances["b"].iter_products()),
        )

    def test_movement_to_unknown_port_ignores_discharge(self):
        balances = _make_default_test_balances()
        movements = [_make_movement(discharge_port="unknown")]
        cutoff = datetime(2022, 1, 1, 0, 0, 0)

        update_balances_from_movements(balances, movements, cutoff)

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(1, 4.0)),
            ],
            sorted(balances["a"].iter_products()),
        )

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(2, 4.0)),
            ],
            sorted(balances["b"].iter_products()),
        )

    def test_movement_at_cutoff_included(self):
        balances = _make_default_test_balances()
        cutoff = datetime(2022, 1, 1, 0, 0, 0)
        movements = [_make_movement(discharge_time=cutoff)]

        update_balances_from_movements(balances, movements, cutoff)

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(3, 4.0)),
            ],
            sorted(balances["b"].iter_products()),
        )

    def test_movement_after_cutoff_included(self):
        balances = _make_default_test_balances()
        cutoff = datetime(2022, 1, 1, 0, 0, 0)
        movements = [_make_movement(discharge_time=cutoff + timedelta(seconds=1))]

        update_balances_from_movements(balances, movements, cutoff)

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(4, 8.0)),
                (CargoProduct.Diesel, ProductQuantity(2, 4.0)),
            ],
            sorted(balances["b"].iter_products()),
        )
