from pathlib import Path

from sim_server.cli import main
from sim_server.csv_load_confirmation import (
    REQUIRED_FIELDS,
    CsvLoadError,
    find_csv_for_selection,
    load_confirmation_records,
    model_record_from_csv_row,
    require_fields,
    source_for_timeframe,
)


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(header), *(",".join(row) for row in rows)]
    path.write_text("\n".join(lines), encoding="utf-8")


def valid_rows(count: int) -> list[list[str]]:
    return [
        [
            f"2026-05-01T00:00:00.00000000{index}Z",
            "42005163",
            "B",
            f"7253.{index:09d}",
            str(index + 1),
            str(374608942 + index),
            "MESM6",
        ]
        for index in range(count)
    ]


def provide_console_inputs(monkeypatch, *values):
    selections = iter(values)
    monkeypatch.setattr("builtins.input", lambda: next(selections))


def csv_path_for(root: Path, timeframe: str = "tick") -> Path:
    return root / "DANE" / "MESM6" / timeframe / "glbx-mdp3-20260501.trades.csv"


def test_loads_at_most_three_required_field_records(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(4))

    records = load_confirmation_records(csv_path, timeframe="tick")

    assert len(records) == 3
    assert set(records[0]) == {*REQUIRED_FIELDS, "timeframe", "source"}
    assert records[0]["timeframe"] == "tick"
    assert records[0]["source"] == "RAW-TICK"


def test_loads_all_records_when_csv_has_fewer_than_three(tmp_path):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(2))

    assert len(load_confirmation_records(csv_path, timeframe="tick")) == 2


def test_rejects_csv_missing_required_column(tmp_path):
    csv_path = csv_path_for(tmp_path)
    header = [field for field in REQUIRED_FIELDS if field != "sequence"]
    write_csv(csv_path, header, [row[:-2] + row[-1:] for row in valid_rows(1)])

    try:
        load_confirmation_records(csv_path, timeframe="tick")
    except CsvLoadError as error:
        assert str(error) == "Missing required column sequence"
    else:
        raise AssertionError("expected missing required column rejection")


def test_hides_non_required_csv_columns_from_model_fields(tmp_path):
    csv_path = csv_path_for(tmp_path)
    header = [*REQUIRED_FIELDS, "publisher_id", "flags", "ts_recv"]
    row = [*valid_rows(1)[0], "1", "130", "2026-05-01T00:00:00Z"]
    write_csv(csv_path, header, [row])

    records = load_confirmation_records(csv_path, timeframe="tick")

    assert "publisher_id" not in records[0]
    assert "flags" not in records[0]
    assert "ts_recv" not in records[0]


def test_assigns_source_by_selected_timeframe():
    assert source_for_timeframe("tick") == "RAW-TICK"
    assert source_for_timeframe("1s") == "OHLC"


def test_required_fields_accepts_complete_header():
    assert require_fields(REQUIRED_FIELDS) is None


def test_model_record_from_csv_row_adds_timeframe_and_source():
    row = dict(zip(REQUIRED_FIELDS, valid_rows(1)[0]))

    record = model_record_from_csv_row(row, timeframe="1s")

    assert record["timeframe"] == "1s"
    assert record["source"] == "OHLC"


def test_finds_matching_csv_by_selected_date_token(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    match = instrument_dir / "tick" / "glbx-mdp3-20260501.trades.csv"
    other = instrument_dir / "tick" / "glbx-mdp3-20260502.trades.csv"
    write_csv(match, REQUIRED_FIELDS, valid_rows(1))
    write_csv(other, REQUIRED_FIELDS, valid_rows(1))

    assert find_csv_for_selection(instrument_dir, "tick", "2026-05-01") == match


def test_main_loads_selected_csv_confirmation(tmp_path, monkeypatch, capsys):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(4))
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-01", "tick", "load")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "CSV loaded" in output
    assert output.count("ts_event=") == 3
    assert "timeframe=tick" in output
    assert "source=RAW-TICK" in output


def test_main_reports_missing_required_column_without_partial_records(tmp_path, monkeypatch, capsys):
    csv_path = csv_path_for(tmp_path)
    header = [field for field in REQUIRED_FIELDS if field != "sequence"]
    write_csv(csv_path, header, [row[:-2] + row[-1:] for row in valid_rows(1)])
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-01", "tick", "load")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "Missing required column sequence" in output
    assert "ts_event=" not in output
    assert "Traceback" not in output


def test_main_reports_missing_csv_for_selected_timeframe(tmp_path, monkeypatch, capsys):
    csv_path = csv_path_for(tmp_path, timeframe="1s")
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(1))
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-01", "tick", "load")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "No CSV file available for MESM6 2026-05-01 tick" in output
    assert "CSV loaded" not in output


def test_main_stops_when_load_command_is_not_requested(tmp_path, monkeypatch, capsys):
    csv_path = csv_path_for(tmp_path)
    write_csv(csv_path, REQUIRED_FIELDS, valid_rows(1))
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-01", "tick", "")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "CSV loaded" not in output
