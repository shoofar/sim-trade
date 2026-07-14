from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DESCRIPTION_FIELD = "pusty - do uzupelnienia"


@dataclass(frozen=True)
class InstrumentDescription:
    instrument: str
    kind: str
    description: str


DEFAULT_INITIAL_DESCRIPTIONS = {
    "MESM6": InstrumentDescription(
        instrument="MESM6",
        kind="Futures",
        description="Micro E-mini S&P 500",
    )
}

CONFIG_FILE = "instrument_descriptions.json"


def description_for(
    instrument: str,
    descriptions: dict[str, InstrumentDescription] | None = None,
) -> InstrumentDescription:
    configured = (descriptions or DEFAULT_INITIAL_DESCRIPTIONS).get(instrument)
    if configured is None:
        return InstrumentDescription(
            instrument=instrument,
            kind=DEFAULT_DESCRIPTION_FIELD,
            description=DEFAULT_DESCRIPTION_FIELD,
        )

    return InstrumentDescription(
        instrument=instrument,
        kind=configured.kind or DEFAULT_DESCRIPTION_FIELD,
        description=configured.description or DEFAULT_DESCRIPTION_FIELD,
    )


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
