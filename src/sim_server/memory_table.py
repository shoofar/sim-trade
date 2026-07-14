from __future__ import annotations

from dataclasses import dataclass, field

from sim_server.csv_confirmation_records import CsvLoadError


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


def data_table_from_records(records: list[dict[str, str]]) -> InMemoryDataTable:
    for index, _record in enumerate(records):
        ensure_record_limit_allows(index)
    return InMemoryDataTable(records)


def ensure_record_limit_allows(current_count: int) -> None:
    if current_count == MAX_RECORDS:
        raise CsvLoadError("Selected CSV exceeds the 20000 record limit")
