from __future__ import annotations

import csv
from pathlib import Path

from sim_server.csv_confirmation_records import (
    CsvLoadError,
    model_record_from_csv_row,
    require_fields,
)


def find_csv_for_selection(instrument_dir: Path, timeframe: str, date: str) -> Path | None:
    timeframe_dir = instrument_dir / timeframe
    if not timeframe_dir.is_dir():
        return None

    compact_date = date.replace("-", "")
    matches = sorted(
        path
        for path in timeframe_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".csv"
        and (date in path.name or compact_date in path.name)
    )
    return matches[0] if matches else None


def load_confirmation_records(csv_path: Path, timeframe: str) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_fields(reader.fieldnames or [])

        records = []
        for row in reader:
            records.append(model_record_from_csv_row(row, timeframe))
            if len(records) == 3:
                break

    return records
