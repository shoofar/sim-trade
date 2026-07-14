from __future__ import annotations

from dataclasses import dataclass, field


SelectionRow = dict[str, str]


@dataclass(frozen=True)
class SelectionResult:
    accepted: bool
    message: str
    selection: SelectionRow | None = None


@dataclass
class SelectionTable:
    rows: list[SelectionRow] = field(default_factory=list)

    def store(self, instrument: str, date: str) -> SelectionRow:
        row = {"instrument": instrument, "date": date}
        self.rows.append(row)
        return row


def select_instrument(
    selected_instrument: str,
    available_instruments: list[str],
) -> SelectionResult:
    if selected_instrument not in available_instruments:
        return SelectionResult(False, f"Instrument {selected_instrument} is not available")

    return SelectionResult(True, f"Selected instrument {selected_instrument}")


def select_date(
    instrument: str,
    selected_date: str,
    available_dates: list[str],
) -> SelectionResult:
    if selected_date not in available_dates:
        return SelectionResult(False, f"Date {selected_date} is not available for {instrument}")

    row = {"instrument": instrument, "date": selected_date}
    return SelectionResult(True, f"Stored selection {instrument} {selected_date}", row)
