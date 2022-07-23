import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from src.csv_data import read_opening_balances, read_movements, write_balances
from src.movements import update_balances_from_movements


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--opening-balances",
        help="CSV containing opening port balances",
        default=Path("/data/storage_asof_20200101.csv"),
        type=Path,
    )
    parser.add_argument(
        "--movements",
        help="CSV containing cargo movements",
        default=Path("/data/cargo_movements.csv"),
        type=Path,
    )
    parser.add_argument(
        "--cutoff",
        help="End cutoff; movements after this time will be ignored. "
        "Specified in ISO format.",
        default=datetime.fromisoformat("2020-01-14 23:59:59"),
        type=datetime.fromisoformat,
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    args = parse_args()

    port_balances = read_opening_balances(args.opening_balances)
    update_balances_from_movements(
        port_balances, read_movements(args.movements), args.cutoff
    )

    write_balances(sys.stdout, port_balances)
