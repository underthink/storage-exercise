import datetime
import logging
from typing import Iterable

from src.models import Port, CargoMovement, CargoProduct


def _update_port_from_movement(
    ports: dict[str, Port],
    port_name: str,
    quantity: float,
    product: CargoProduct,
    movement_time: datetime.datetime,
    cutoff: datetime.datetime,
) -> None:
    if not (port := ports.get(port_name.lower())):
        logging.warning(f"Ignoring movement at unknown port {port_name}")
        return

    if cutoff < movement_time:
        logging.debug(f"Ignoring movement at {movement_time} after cutoff {cutoff}")
        return

    try:
        port.change_product_quantity(product, quantity)
    except KeyError:
        logging.warning(f"Ignoring movement for untracked product {product} at {port}")


def update_balances_from_movements(
    port_balances: dict[str, Port],
    movements: Iterable[CargoMovement],
    end_cutoff: datetime.datetime,
):
    """Updates some port cargo balances from a set of movements, ignoring those after a cutoff.

    The balances for ports are updated in-place, in the passed port_balances object.
    """
    for movement in movements:
        _update_port_from_movement(
            port_balances,
            movement.loading_port,
            -movement.quantity,
            movement.product,
            movement.load_time,
            end_cutoff,
        )
        _update_port_from_movement(
            port_balances,
            movement.discharge_port,
            movement.quantity,
            movement.product,
            movement.discharge_time,
            end_cutoff,
        )
