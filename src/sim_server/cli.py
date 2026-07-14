from __future__ import annotations

from pathlib import Path
from typing import Sequence

from sim_server.instruments import instrument_names


def discover_instruments(data_dir: Path) -> list[str]:
    if not data_dir.is_dir():
        return []

    return instrument_names((path.name, path.is_dir()) for path in data_dir.iterdir())


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    data_dir = Path.cwd() / "DANE"
    instruments = discover_instruments(data_dir)

    if not data_dir.is_dir():
        print("No data directory available: DANE")
        return 0

    for instrument in instruments:
        print(instrument)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
