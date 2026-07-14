from __future__ import annotations

from collections.abc import Iterable


def instrument_names(entries: Iterable[tuple[str, bool]]) -> list[str]:
    return sorted(name for name, is_directory in entries if is_directory)
