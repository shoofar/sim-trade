from sim_server.cli import discover_instruments, main


def test_main_returns_zero():
    assert main([]) == 0


def test_discovers_direct_instrument_directories(tmp_path):
    data_dir = tmp_path / "DANE"
    (data_dir / "MESM6" / "tick").mkdir(parents=True)
    (data_dir / "NQMM6" / "tick").mkdir(parents=True)

    assert discover_instruments(data_dir) == ["MESM6", "NQMM6"]


def test_discovery_ignores_files_and_nested_timeframe_directories(tmp_path):
    data_dir = tmp_path / "DANE"
    (data_dir / "MESM6" / "tick").mkdir(parents=True)
    (data_dir / "README.txt").write_text("notes", encoding="utf-8")

    assert discover_instruments(data_dir) == ["MESM6"]


def test_main_prints_available_instruments_from_local_dane(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    (data_dir / "MESM6" / "tick").mkdir(parents=True)
    (data_dir / "NQMM6" / "tick").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "MESM6" in output
    assert "NQMM6" in output
    assert "tick" not in output


def test_main_reports_missing_local_dane(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "DANE" in output
    assert "No data directory" in output
