from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from sim_server.csv_confirmation_records import (
    CsvLoadError,
    model_record_from_csv_row,
    require_fields,
)


MAX_RECORDS = 20000


@dataclass
class InMemoryDataTable:
    rows: list[dict[str, str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.rows)

    def store(self, record: dict[str, str]) -> None:
        self.rows.append(record)

    def sample_records(self) -> list[dict[str, str]]:
        return self.rows[:3]


def load_data_table(csv_path: Path, timeframe: str) -> InMemoryDataTable:
    records: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_fields(reader.fieldnames or [])

        for row in reader:
            ensure_record_limit_allows(len(records))
            records.append(model_record_from_csv_row(row, timeframe))

    return InMemoryDataTable(records)


def ensure_record_limit_allows(current_count: int) -> None:
    if current_count == MAX_RECORDS:
        raise CsvLoadError("Selected CSV exceeds the 20000 record limit")
