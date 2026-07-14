from __future__ import annotations


REQUIRED_FIELDS = [
    "ts_event",
    "instrument_id",
    "side",
    "price",
    "size",
    "sequence",
    "symbol",
]
MODEL_FIELDS = [*REQUIRED_FIELDS, "timeframe", "source"]


class CsvLoadError(Exception):
    pass


def require_fields(fieldnames: list[str]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in fieldnames:
            raise CsvLoadError(f"Missing required column {field}")


def model_record_from_csv_row(row: dict[str, str], timeframe: str) -> dict[str, str]:
    record = {field: row[field] for field in REQUIRED_FIELDS}
    record["timeframe"] = timeframe
    record["source"] = source_for_timeframe(timeframe)
    return record


def source_for_timeframe(timeframe: str) -> str:
    if timeframe == "tick":
        return "RAW-TICK"
    return "OHLC"


def format_record(record: dict[str, str]) -> str:
    return " ".join(f"{field}={record[field]}" for field in MODEL_FIELDS)
