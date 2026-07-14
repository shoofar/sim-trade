from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path


COMPACT_DATE = re.compile(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)")
DASHED_DATE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")


def discover_timeframes(instrument_dir: Path) -> list[str]:
    if not instrument_dir.is_dir():
        return []

    return timeframe_names((path.name, path.is_dir()) for path in instrument_dir.iterdir())


def discover_dates(instrument_dir: Path) -> list[str]:
    if not instrument_dir.is_dir():
        return []

    return dates_from_filenames(path.name for path in instrument_dir.rglob("*") if path.is_file())


def timeframe_names(entries: Iterable[tuple[str, bool]]) -> list[str]:
    return sorted(name for name, is_directory in entries if is_directory)


def dates_from_filenames(filenames: Iterable[str]) -> list[str]:
    dates = {
        date
        for filename in filenames
        for date in [normalize_date_from_filename(filename)]
        if date is not None
    }
    return sorted(dates)


def normalize_date_from_filename(filename: str) -> str | None:
    match = DASHED_DATE.search(filename)
    if match is None:
        match = COMPACT_DATE.search(filename)
    if match is None:
        return None

    year, month, day = match.groups()
    return f"{year}-{month}-{day}"
