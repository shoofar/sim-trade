from __future__ import annotations

from pathlib import Path
from typing import Sequence

from sim_server.csv_load_confirmation import (
    CsvLoadError,
    find_csv_for_selection,
    format_record,
    load_confirmation_records,
)
from sim_server.instrument_description_config import load_initial_descriptions
from sim_server.instrument_descriptions import description_for
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
    print_instrument_description(description)

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

    if not date_result.accepted:
        return 0

    try:
        selected_timeframe = input().strip()
    except (EOFError, OSError, StopIteration):
        return 0

    if not selected_timeframe:
        return 0

    try:
        load_command = input().strip()
    except (EOFError, OSError, StopIteration):
        return 0

    if load_command != "load":
        return 0

    csv_path = find_csv_for_selection(instrument_dir, selected_timeframe, selected_date)
    if csv_path is None:
        print(f"No CSV file available for {instrument} {selected_date} {selected_timeframe}")
        return 0

    try:
        records = load_confirmation_records(csv_path, selected_timeframe)
    except CsvLoadError as error:
        print(str(error))
        return 0

    print("CSV loaded")
    for record in records:
        print(format_record(record))

    return 0


def print_instrument_description(description) -> None:
    print(description.instrument)
    print(description.kind)
    print(description.description)


if __name__ == "__main__":
    raise SystemExit(main())
