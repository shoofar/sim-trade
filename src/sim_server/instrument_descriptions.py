from __future__ import annotations

from dataclasses import dataclass


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
        kind=description_field_or_default(configured.kind),
        description=description_field_or_default(configured.description),
    )


def description_field_or_default(value: str) -> str:
    return value or DEFAULT_DESCRIPTION_FIELD
