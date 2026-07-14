from __future__ import annotations

import re
from pathlib import Path


COMPACT_DATE = re.compile(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)")
DASHED_DATE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")


def discover_timeframes(instrument_dir: Path) -> list[str]:
    if not instrument_dir.is_dir():
        return []

    return sorted(path.name for path in instrument_dir.iterdir() if path.is_dir())


def discover_dates(instrument_dir: Path) -> list[str]:
    if not instrument_dir.is_dir():
        return []

    dates = {
        date
        for path in instrument_dir.rglob("*")
        if path.is_file()
        for date in [normalize_date_from_filename(path.name)]
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
