import unittest

from src.models import Port, CargoProduct, ProductQuantity


class ModelUpdateTests(unittest.TestCase):
    def test_setting_port_quantities_updates_quantities_correctly(self):
        port = Port("A")
        port.set_product_quantity(
            product=CargoProduct.Diesel, current_absolute=10, current_percentage=0.5
        )

        port_products = list(port.iter_products())

        self.assertListEqual(
            [(CargoProduct.Diesel, ProductQuantity(10, 20))], port_products
        )

    def test_incrementing_port_quantities_updates_quantities_correctly(self):
        port = Port("A")
        port.set_product_quantity(
            product=CargoProduct.Diesel, current_absolute=10, current_percentage=0.5
        )

        port.change_product_quantity(CargoProduct.Diesel, 10)

        self.assertListEqual(
            [(CargoProduct.Diesel, ProductQuantity(20, 20))], list(port.iter_products())
        )

    def test_decrementing_port_quantities_updates_quantities_correctly(self):
        port = Port("A")
        port.set_product_quantity(
            product=CargoProduct.Diesel, current_absolute=10, current_percentage=0.5
        )

        port.change_product_quantity(CargoProduct.Diesel, -10)

        self.assertListEqual(
            [(CargoProduct.Diesel, ProductQuantity(0, 20))], list(port.iter_products())
        )

    def test_fetching_percentage_gives_expected_result(self):
        port = Port("A")
        port.set_product_quantity(
            product=CargoProduct.Diesel, current_absolute=10, current_percentage=0.5
        )

        port.change_product_quantity(CargoProduct.Diesel, 5)

        _, quantity = next(port.iter_products())
        self.assertEqual(0.75, quantity.relative)
