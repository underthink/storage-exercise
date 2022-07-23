import unittest
from csv import DictWriter
from datetime import datetime
from io import StringIO
from typing import Iterable, List
from pathlib import Path
from unittest import mock

from src.csv_data import read_opening_balances, read_movements, write_balances
from src.models import CargoProduct, ProductQuantity, CargoMovement, Port


def _build_mock_csv_path(headers: List[str], rows: Iterable[dict[str, str]]) -> Path:
    csv_io = StringIO()
    csv_writer = DictWriter(csv_io, fieldnames=headers)
    csv_writer.writeheader()
    for row in rows:
        csv_writer.writerow(row)

    mock_path = mock.MagicMock(Path)
    csv_io.seek(0)
    mock_path.open.return_value = csv_io

    return mock_path


def _build_mock_balance_csv_path(rows: Iterable[dict[str, str]]) -> Path:
    return _build_mock_csv_path(["port", "product", "absolute", "relative"], rows)


def _build_mock_movement_csv_path(rows: Iterable[dict[str, str]]) -> Path:
    return _build_mock_csv_path(
        [
            "loading_port",
            "start_timestamp",
            "discharge_port",
            "end_timestamp",
            "product",
            "quantity",
        ],
        rows,
    )


class CsvBalanceReadTests(unittest.TestCase):
    def test_parse_opening_balances_reads_multiple_ports(self):
        mock_path = _build_mock_balance_csv_path(
            [
                dict(
                    port="A", product=CargoProduct.Diesel.value, absolute=1, relative=1
                ),
                dict(
                    port="B", product=CargoProduct.Diesel.value, absolute=1, relative=1
                ),
            ]
        )

        balances = read_opening_balances(mock_path)

        self.assertListEqual(["a", "b"], list(balances.keys()))

        self.assertEqual("A", balances["a"].port_name)
        self.assertEqual("B", balances["b"].port_name)

    def test_parse_opening_balances_reads_multiple_products(self):
        mock_path = _build_mock_balance_csv_path(
            [
                dict(
                    port="A", product=CargoProduct.Diesel.value, absolute=1, relative=1
                ),
                dict(
                    port="A",
                    product=CargoProduct.CrudeOil.value,
                    absolute=2,
                    relative=1,
                ),
            ]
        )

        balances = read_opening_balances(mock_path)

        self.assertListEqual(
            [
                (CargoProduct.CrudeOil, ProductQuantity(current=2.0, maximum=2.0)),
                (CargoProduct.Diesel, ProductQuantity(current=1.0, maximum=1.0)),
            ],
            sorted(list(balances["a"].iter_products())),
        )

    def test_parse_opening_balances_handles_no_rows(self):
        mock_path = _build_mock_balance_csv_path([])

        balances = read_opening_balances(mock_path)

        self.assertDictEqual({}, balances)

    def test_parse_opening_balances_unknown_product_ignored(self):
        mock_path = _build_mock_balance_csv_path(
            [dict(port="A", product="cheese", absolute=1, relative=1)]
        )

        balances = read_opening_balances(mock_path)

        self.assertListEqual(list(balances["a"].iter_products()), [])

    def test_invalid_balance_file_raises_error(self):
        mock_path = _build_mock_csv_path(
            ["totally", "invalid"], [dict(totally="1", invalid="2")]
        )

        self.assertRaises(KeyError, read_opening_balances, mock_path)


class MovementReadTests(unittest.TestCase):
    def test_read_valid_movement_returns_correct_movements(self):
        movement_mock_path = _build_mock_movement_csv_path(
            [
                dict(
                    loading_port="a",
                    start_timestamp="2021-01-01 00:00:00",
                    discharge_port="b",
                    end_timestamp="2021-01-02 01:02:03",
                    product=CargoProduct.Diesel.value,
                    quantity=1,
                )
            ]
        )

        movements = read_movements(movement_mock_path)

        self.assertListEqual(
            [
                CargoMovement(
                    loading_port="a",
                    load_time=datetime(2021, 1, 1, 0, 0, 0),
                    discharge_port="b",
                    discharge_time=datetime(2021, 1, 2, 1, 2, 3),
                    product=CargoProduct.Diesel,
                    quantity=1,
                )
            ],
            list(movements),
        )

    def test_read_movement_with_unknown_product_ignored(self):
        movement_mock_path = _build_mock_movement_csv_path(
            [
                dict(
                    loading_port="a",
                    start_timestamp="2021-01-01 00:00:00",
                    discharge_port="b",
                    end_timestamp="2021-01-02 01:02:03",
                    product="cheese",
                    quantity=1,
                )
            ]
        )

        movements = read_movements(movement_mock_path)

        self.assertListEqual([], list(movements))


class WriteBalanceTests(unittest.TestCase):
    def test_balance_multiple_products_written_correctly(self):
        port = Port("A")
        port.set_product_quantity(CargoProduct.Diesel, 2, 0.5)
        port.set_product_quantity(CargoProduct.CrudeOil, 3, 0.5)
        balances = {"a": port}

        output_io = StringIO()

        write_balances(output_io, balances)

        self.assertListEqual(
            ["port,product,absolute,relative", "A,diesel,2,0.5", "A,crude oil,3,0.5"],
            output_io.getvalue().splitlines(),
        )

    def test_write_balance_with_no_products_writes_empty_csv(self):
        port = Port("A")
        balances = {"a": port}

        output_io = StringIO()

        write_balances(output_io, balances)

        self.assertListEqual(
            ["port,product,absolute,relative"], output_io.getvalue().splitlines()
        )

    def test_write_balance_with_no_ports_writes_empty_csv(self):
        balances = {}

        output_io = StringIO()

        write_balances(output_io, balances)

        self.assertListEqual(
            ["port,product,absolute,relative"], output_io.getvalue().splitlines()
        )
