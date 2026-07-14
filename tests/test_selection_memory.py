from sim_server.cli import main
from sim_server.selection_memory import SelectionTable, select_date, select_instrument


def write_instrument_file(data_dir, instrument, relative_path, content="rows are ignored"):
    path = data_dir / instrument / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def provide_console_inputs(monkeypatch, *values):
    selections = iter(values)
    monkeypatch.setattr("builtins.input", lambda: next(selections))


def test_stores_valid_selection_row_in_memory():
    table = SelectionTable()

    row = table.store("MESM6", "2026-05-01")

    assert row == {"instrument": "MESM6", "date": "2026-05-01"}
    assert table.rows == [{"instrument": "MESM6", "date": "2026-05-01"}]


def test_rejects_undiscovered_instrument_without_storing_selection():
    table = SelectionTable()

    result = select_instrument("NQMM6", ["MESM6"])

    assert not result.accepted
    assert result.message == "Instrument NQMM6 is not available"
    assert table.rows == []


def test_rejects_undiscovered_date_without_storing_selection():
    result = select_date("MESM6", "2026-05-02", ["2026-05-01"])

    assert not result.accepted
    assert result.message == "Date 2026-05-02 is not available for MESM6"
    assert result.selection is None


def test_accepts_discovered_date_and_returns_selection_row():
    result = select_date("MESM6", "2026-05-01", ["2026-05-01"])

    assert result.accepted
    assert result.message == "Stored selection MESM6 2026-05-01"
    assert result.selection == {"instrument": "MESM6", "date": "2026-05-01"}


def test_selection_table_is_in_memory_only(tmp_path):
    table = SelectionTable()

    table.store("MESM6", "2026-05-01")

    assert not (tmp_path / "selection.json").exists()
    assert not (tmp_path / "selections.csv").exists()


def test_main_confirms_valid_selection_without_printing_csv_content(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv", "csv row content")
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-01")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "Stored selection MESM6 2026-05-01" in output
    assert "csv row content" not in output


def test_main_rejects_invalid_date_without_traceback(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", "2026-05-02")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "Date 2026-05-02 is not available for MESM6" in output
    assert "Stored selection MESM6 2026-05-02" not in output
    assert "Traceback" not in output


def test_main_stops_when_date_input_is_unavailable(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "2026-05-01" in output
    assert "Stored selection" not in output
    assert "Traceback" not in output


def test_main_stops_after_blank_date_selection(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    provide_console_inputs(monkeypatch, "MESM6", " ")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "2026-05-01" in output
    assert "Stored selection" not in output


def test_main_rejects_invalid_instrument_without_traceback(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda: "NQMM6")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "Instrument NQMM6 is not available" in output
    assert "Stored selection NQMM6" not in output
    assert "Traceback" not in output
