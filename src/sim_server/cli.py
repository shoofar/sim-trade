from __future__ import annotations

from pathlib import Path
from typing import Sequence

from sim_server.instruments import instrument_names
from sim_server.timeframe_dates import discover_dates, discover_timeframes


def discover_instruments(data_dir: Path) -> list[str]:
    if not data_dir.is_dir():
        return []

    return instrument_names((path.name, path.is_dir()) for path in data_dir.iterdir())


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    data_dir = Path.cwd() / "DANE"

    if not data_dir.is_dir():
        print("No data directory available: DANE")
        return 0

    for instrument in discover_instruments(data_dir):
        print(instrument)

    try:
        selected_instrument = input().strip()
    except (EOFError, OSError):
        return 0

    if not selected_instrument:
        return 0

    return show_selected_instrument_details(data_dir, selected_instrument)


def show_selected_instrument_details(data_dir: Path, instrument: str) -> int:
    instrument_dir = data_dir / instrument
    timeframes = discover_timeframes(instrument_dir)
    if not timeframes:
        print(f"No timeframes available for {instrument}")
        return 0

    for timeframe in timeframes:
        print(timeframe)

    for date in discover_dates(instrument_dir):
        print(date)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
