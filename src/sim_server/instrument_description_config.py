from __future__ import annotations

import json
from pathlib import Path

from sim_server.instrument_descriptions import (
    DEFAULT_INITIAL_DESCRIPTIONS,
    InstrumentDescription,
)


CONFIG_FILE = "instrument_descriptions.json"


def load_initial_descriptions(root: Path) -> dict[str, InstrumentDescription]:
    config_path = root / CONFIG_FILE
    if not config_path.is_file():
        return DEFAULT_INITIAL_DESCRIPTIONS

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    return {
        instrument: InstrumentDescription(
            instrument=instrument,
            kind=str(values.get("kind", "")),
            description=str(values.get("description", "")),
        )
        for instrument, values in payload.items()
        if isinstance(values, dict)
    }
