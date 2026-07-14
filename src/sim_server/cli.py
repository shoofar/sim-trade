from __future__ import annotations

from pathlib import Path
from typing import Sequence

from sim_server.instrument_descriptions import description_for, load_initial_descriptions
from sim_server.instruments import instrument_names
from sim_server.selection_memory import SelectionTable, select_date, select_instrument
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

    instruments = discover_instruments(data_dir)
    for instrument in instruments:
        print(instrument)

    try:
        selected_instrument = input().strip()
    except (EOFError, OSError):
        return 0

    if not selected_instrument:
        return 0

    selection_table = SelectionTable()
    instrument_result = select_instrument(selected_instrument, instruments)
    if not instrument_result.accepted:
        print(instrument_result.message)
        return 0

    return show_selected_instrument_details(data_dir, selected_instrument, selection_table)


def show_selected_instrument_details(
    data_dir: Path,
    instrument: str,
    selection_table: SelectionTable,
) -> int:
    instrument_dir = data_dir / instrument
    description = description_for(instrument, load_initial_descriptions(data_dir.parent))
    print(description.instrument)
    print(description.kind)
    print(description.description)

    timeframes = discover_timeframes(instrument_dir)
    if not timeframes:
        print(f"No timeframes available for {instrument}")
        return 0

    for timeframe in timeframes:
        print(timeframe)

    dates = discover_dates(instrument_dir)
    for date in dates:
        print(date)

    try:
        selected_date = input().strip()
    except (EOFError, OSError, StopIteration):
        return 0

    if not selected_date:
        return 0

    date_result = select_date(instrument, selected_date, dates)
    if date_result.selection is not None:
        selection_table.store(date_result.selection["instrument"], date_result.selection["date"])
    print(date_result.message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
