from sim_server.cli import main
from sim_server.timeframe_dates import (
    discover_dates,
    discover_timeframes,
    normalize_date_from_filename,
)


def test_discovers_direct_timeframe_directories(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    (instrument_dir / "tick").mkdir(parents=True)
    (instrument_dir / "1s").mkdir()
    (instrument_dir / "README.txt").write_text("notes", encoding="utf-8")

    assert discover_timeframes(instrument_dir) == ["1s", "tick"]


def test_discovers_no_timeframes_for_empty_instrument_directory(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    instrument_dir.mkdir(parents=True)

    assert discover_timeframes(instrument_dir) == []


def test_normalizes_dates_from_supported_filename_tokens():
    assert normalize_date_from_filename("glbx-mdp3-20260501.trades.csv") == "2026-05-01"
    assert normalize_date_from_filename("glbx-mdp3-2026-05-03.ohlc.csv") == "2026-05-03"


def test_ignores_filenames_without_date_tokens():
    assert normalize_date_from_filename("notes.csv") is None


def test_discovers_sorted_unique_dates_under_selected_instrument(tmp_path):
    instrument_dir = tmp_path / "DANE" / "MESM6"
    tick = instrument_dir / "tick"
    one_second = instrument_dir / "1s"
    tick.mkdir(parents=True)
    one_second.mkdir()
    (tick / "glbx-mdp3-20260501.trades.csv").write_text("rows are ignored", encoding="utf-8")
    (one_second / "glbx-mdp3-2026-05-03.ohlc.csv").write_text("rows are ignored", encoding="utf-8")
    (tick / "duplicate-20260501.csv").write_text("rows are ignored", encoding="utf-8")
    (tick / "notes.csv").write_text("not a date", encoding="utf-8")

    assert discover_dates(instrument_dir) == ["2026-05-01", "2026-05-03"]


def test_main_prints_timeframes_and_dates_after_instrument_selection(tmp_path, monkeypatch, capsys):
    dane = tmp_path / "DANE"
    (dane / "MESM6" / "tick").mkdir(parents=True)
    (dane / "MESM6" / "1s").mkdir()
    (dane / "NQMM6" / "5s").mkdir(parents=True)
    (dane / "MESM6" / "tick" / "glbx-mdp3-20260501.trades.csv").write_text(
        "csv row content",
        encoding="utf-8",
    )
    (dane / "MESM6" / "1s" / "glbx-mdp3-2026-05-03.ohlc.csv").write_text(
        "csv row content",
        encoding="utf-8",
    )
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


def test_main_reports_no_timeframes_for_empty_selected_instrument(tmp_path, monkeypatch, capsys):
    (tmp_path / "DANE" / "MESM6").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda: "MESM6")

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "No timeframes available for MESM6" in output
    assert "Traceback" not in output
