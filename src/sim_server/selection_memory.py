from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SelectionResult:
    accepted: bool
    message: str


@dataclass
class SelectionTable:
    rows: list[dict[str, str]] = field(default_factory=list)

    def store(self, instrument: str, date: str) -> dict[str, str]:
        row = {"instrument": instrument, "date": date}
        self.rows.append(row)
        return row


def select_instrument(
    selected_instrument: str,
    available_instruments: list[str],
    selection_table: SelectionTable,
) -> SelectionResult:
    del selection_table
    if selected_instrument not in available_instruments:
        return SelectionResult(False, f"Instrument {selected_instrument} is not available")

    return SelectionResult(True, f"Selected instrument {selected_instrument}")


def select_date(
    instrument: str,
    selected_date: str,
    available_dates: list[str],
    selection_table: SelectionTable,
) -> SelectionResult:
    if selected_date not in available_dates:
        return SelectionResult(False, f"Date {selected_date} is not available for {instrument}")

    selection_table.store(instrument, selected_date)
    return SelectionResult(True, f"Stored selection {instrument} {selected_date}")
