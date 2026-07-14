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
    instruments = discover_instruments(data_dir)

    if not data_dir.is_dir():
        print("No data directory available: DANE")
        return 0

    for instrument in instruments:
        print(instrument)

    try:
        selected = input().strip()
    except (EOFError, OSError):
        return 0

    if not selected:
        return 0

    instrument_dir = data_dir / selected
    timeframes = discover_timeframes(instrument_dir)
    if not timeframes:
        print(f"No timeframes available for {selected}")
        return 0

    for timeframe in timeframes:
        print(timeframe)

    for date in discover_dates(instrument_dir):
        print(date)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
