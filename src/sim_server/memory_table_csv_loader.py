from __future__ import annotations

import csv
from pathlib import Path

from sim_server.csv_confirmation_records import model_record_from_csv_row, require_fields
from sim_server.memory_table import InMemoryDataTable, data_table_from_records, ensure_record_limit_allows


def load_data_table(csv_path: Path, timeframe: str) -> InMemoryDataTable:
    records: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_fields(reader.fieldnames or [])

        for row in reader:
            ensure_record_limit_allows(len(records))
            records.append(model_record_from_csv_row(row, timeframe))

    return data_table_from_records(records)
