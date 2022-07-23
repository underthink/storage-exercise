import dataclasses
import datetime
import enum
from typing import Generator, Tuple


class CargoProduct(str, enum.Enum):
    """All products that we're aware of"""

    CrudeOil = "crude oil"
    Diesel = "diesel"


@dataclasses.dataclass
class ProductQuantity:
    """The quantity of a product held at a port"""

    current: float
    maximum: float

    @property
    def relative(self) -> float:
        return self.current / self.maximum


class Port:
    """Represents a port and the products stored there"""

    def __init__(self, port_name: str):
        self._port_name = port_name
        self._current_product_quantities: dict[CargoProduct, ProductQuantity] = {}

    def set_product_quantity(
        self, product: CargoProduct, current_absolute: float, current_percentage: float
    ):
        """Sets the quantity of a product at this port to a fixed value"""
        maximum_capacity = current_absolute / current_percentage
        self._current_product_quantities[product] = ProductQuantity(
            current=current_absolute, maximum=maximum_capacity
        )

    def change_product_quantity(self, product: CargoProduct, delta: float) -> None:
        """Increments or decrements the quantity of the given product at this port.

        The delta is the change of quantity of product - positive for a discharge, negative
        for a load.
        """
        self._current_product_quantities[product].current += delta

    @property
    def port_name(self) -> str:
        return self._port_name

    def iter_products(
        self,
    ) -> Generator[Tuple[CargoProduct, ProductQuantity], None, None]:
        """Returns all products at this port as an iterator of tuples"""
        yield from self._current_product_quantities.items()


@dataclasses.dataclass
class CargoMovement:
    """A single cargo movement, including the load and discharge of a product"""

    loading_port: str
    load_time: datetime.datetime
    discharge_port: str
    discharge_time: datetime.datetime
    product: CargoProduct
    quantity: int
