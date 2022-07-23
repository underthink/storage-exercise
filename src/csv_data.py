import logging
from csv import DictWriter, DictReader
from datetime import datetime
from pathlib import Path
from typing import TextIO, Generator

from src.models import Port, CargoProduct, CargoMovement

PORT_HEADER = "port"
ABSOLUTE_HEADER = "absolute"
RELATIVE_HEADER = "relative"
PRODUCT_HEADER = "product"


def read_movements(src_file: Path) -> Generator[CargoMovement, None, None]:
    """Opens the given path as a CSV file, and yields product movements from that file.

    Unknown product types are ignored.
    """
    with src_file.open("r") as port_csv_fh:
        csv_reader = DictReader(port_csv_fh)
        for row in csv_reader:
            try:
                product = CargoProduct(row[PRODUCT_HEADER])
            except ValueError:
                logging.warning(
                    f"Ignoring movement of unknown product {row[PRODUCT_HEADER]}"
                )
                continue

            yield CargoMovement(
                loading_port=row["loading_port"].lower(),
                load_time=datetime.fromisoformat(row["start_timestamp"]),
                discharge_port=row["discharge_port"],
                discharge_time=datetime.fromisoformat(row["end_timestamp"]),
                product=product,
                quantity=int(row["quantity"]),
            )


def write_balances(target_fh: TextIO, port_balances: dict[str, Port]) -> None:
    """
    Writes the balances for the ports provided as a CSV to the provided, open, writable
    file handle.
    """
    csv_writer = DictWriter(
        target_fh,
        fieldnames=[PORT_HEADER, PRODUCT_HEADER, ABSOLUTE_HEADER, RELATIVE_HEADER],
    )
    csv_writer.writeheader()
    for port in port_balances.values():
        for port_product, port_product_quantity in port.iter_products():
            csv_writer.writerow(
                dict(
                    port=port.port_name,
                    product=port_product.value,
                    absolute=port_product_quantity.current,
                    relative=port_product_quantity.relative,
                )
            )


def read_opening_balances(src_file: Path) -> dict[str, Port]:
    """Reads the opening balances for a set of ports from a CSV file, returning the result.

    The key of the returned dictionary is the name of the associated port, converted to lower-case.
    """
    ports: dict[str, Port] = {}
    with src_file.open("r") as port_csv_fh:
        csv_reader = DictReader(port_csv_fh)
        for row in csv_reader:
            port_name = row[PORT_HEADER]
            if not (port := ports.get(port_name.lower())):
                port = Port(port_name)
                ports[port_name.lower()] = port

            try:
                port.set_product_quantity(
                    CargoProduct(row[PRODUCT_HEADER]),
                    float(row[ABSOLUTE_HEADER]),
                    float(row[RELATIVE_HEADER]),
                )
            except ValueError:
                logging.debug(f"Ignoring unknown product {row[PRODUCT_HEADER]}")

    return ports
