from pathlib import Path

from sim_server.csv_confirmation_records import MODEL_FIELDS, REQUIRED_FIELDS, CsvLoadError
from sim_server.memory_table import (
    MAX_RECORDS,
    InMemoryDataTable,
    ensure_record_limit_allows,
    load_data_table,
)


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(header), *(",".join(row) for row in rows)]
    path.write_text("\n".join(lines), encoding="utf-8")


def valid_rows(count: int) -> list[list[str]]:
    return [
        [
            f"2026-05-01T00:00:00.{index:09d}Z",
            "42005163",
            "B",
            "7253.000000000",
            "25",
            str(374608942 + index),
            "MESM6",
        ]
        for index in range(count)
    ]


def csv_path_for(root: Path) -> Path:
    return root / "DANE" / "MESM6" / "tick" / "glbx-mdp3-20260501.trades.csv"


def test_loads_all_required_model_records_into_memory(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(4))

    table = load_data_table(csv_path, "tick")

    assert table.count == 4
    assert set(table.rows[0]) == set(MODEL_FIELDS)
    assert table.rows[0]["timeframe"] == "tick"
    assert table.rows[0]["source"] == "RAW-TICK"


def test_confirmation_sample_displays_at_most_three_records(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(4))

    table = load_data_table(csv_path, "tick")

    assert len(table.sample_records()) == 3


def test_accepts_exactly_maximum_record_count(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(MAX_RECORDS))

    assert load_data_table(csv_path, "tick").count == MAX_RECORDS


def test_rejects_above_maximum_without_partial_table(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(MAX_RECORDS + 1))

    try:
        load_data_table(csv_path, "tick")
    except CsvLoadError as error:
        assert str(error) == "Selected CSV exceeds the 20000 record limit"
    else:
        raise AssertionError("expected record limit rejection")


def test_empty_csv_stores_zero_records(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, [])

    table = load_data_table(csv_path, "tick")

    assert table.count == 0
    assert table.sample_records() == []


def test_data_table_is_in_memory_only(tmp_path):
    table = InMemoryDataTable()
    table.store({"ts_event": "2026-05-01T00:00:00Z"})

    assert table.count == 1
    assert not (tmp_path / "data_table.json").exists()
    assert not (tmp_path / "data_table.csv").exists()


def test_record_limit_allows_count_below_maximum():
    assert ensure_record_limit_allows(MAX_RECORDS - 1) is None
