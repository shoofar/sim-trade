from sim_server.cli import main
from sim_server.timeframe_dates import (
    dates_from_filenames,
    discover_dates,
    discover_timeframes,
    normalize_date_from_filename,
    timeframe_names,
)


def create_timeframe_dir(instrument_dir, timeframe):
    (instrument_dir / timeframe).mkdir(parents=True, exist_ok=True)


def write_instrument_file(instrument_dir, relative_path, content="rows are ignored"):
    path = instrument_dir / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_discovers_direct_timeframe_directories(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    create_timeframe_dir(instrument_dir, "tick")
    create_timeframe_dir(instrument_dir, "1s")
    write_instrument_file(instrument_dir, "README.txt", "notes")

    assert discover_timeframes(instrument_dir) == ["1s", "tick"]


def test_timeframe_names_selects_sorted_directory_names():
    entries = [
        ("README.txt", False),
        ("tick", True),
        ("1s", True),
    ]

    assert timeframe_names(entries) == ["1s", "tick"]


def test_discovers_no_timeframes_for_empty_instrument_directory(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    instrument_dir.mkdir(parents=True)

    assert discover_timeframes(instrument_dir) == []


def test_discovers_no_timeframes_when_instrument_directory_is_missing(tmp_path):
    assert discover_timeframes(tmp_path / "DANE" / "MESM6") == []


def test_normalizes_dates_from_supported_filename_tokens():
    assert normalize_date_from_filename("glbx-mdp3-20260501.trades.csv") == "2026-05-01"
    assert normalize_date_from_filename("glbx-mdp3-2026-05-03.ohlc.csv") == "2026-05-03"


def test_ignores_filenames_without_date_tokens():
    assert normalize_date_from_filename("notes.csv") is None


def test_discovers_sorted_unique_dates_under_selected_instrument(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    create_timeframe_dir(instrument_dir, "tick")
    create_timeframe_dir(instrument_dir, "1s")
    write_instrument_file(instrument_dir, "tick/glbx-mdp3-20260501.trades.csv")
    write_instrument_file(instrument_dir, "1s/glbx-mdp3-2026-05-03.ohlc.csv")
    write_instrument_file(instrument_dir, "tick/duplicate-20260501.csv")
    write_instrument_file(instrument_dir, "tick/notes.csv", "not a date")

    assert discover_dates(instrument_dir) == ["2026-05-01", "2026-05-03"]


def test_dates_from_filenames_returns_sorted_unique_supported_dates():
    filenames = [
        "glbx-mdp3-20260501.trades.csv",
        "glbx-mdp3-2026-05-03.ohlc.csv",
        "duplicate-20260501.csv",
        "notes.csv",
    ]

    assert dates_from_filenames(filenames) == ["2026-05-01", "2026-05-03"]


def test_discovers_no_dates_when_instrument_directory_is_missing(tmp_path):
    assert discover_dates(tmp_path / "DANE" / "MESM6") == []


def test_main_prints_timeframes_and_dates_after_instrument_selection(tmp_path, monkeypatch, capsys):
    dane = tmp_path / "DANE"
    mesm = dane / "MESM6"
    create_timeframe_dir(mesm, "tick")
    create_timeframe_dir(mesm, "1s")
    create_timeframe_dir(dane / "NQMM6", "5s")
    write_instrument_file(mesm, "tick/glbx-mdp3-20260501.trades.csv", "csv row content")
    write_instrument_file(mesm, "1s/glbx-mdp3-2026-05-03.ohlc.csv", "csv row content")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda: "MESM6")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "MESM6" in output
    assert "tick" in output
    assert "1s" in output
    assert "5s" not in output
    assert "2026-05-01" in output
    assert "2026-05-03" in output
    assert "csv row content" not in output


def test_main_stops_after_blank_instrument_selection(tmp_path, monkeypatch, capsys):
    create_timeframe_dir(tmp_path / "DANE" / "MESM6", "tick")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda: " ")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "MESM6" in output
    assert "tick" not in output


def test_main_reports_no_timeframes_for_empty_selected_instrument(tmp_path, monkeypatch, capsys):
    (tmp_path / "DANE" / "MESM6").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda: "MESM6")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "No timeframes available for MESM6" in output
    assert "Traceback" not in output
