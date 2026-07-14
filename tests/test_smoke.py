from sim_server.cli import discover_instruments, main


def create_instrument_dir(data_dir, instrument):
    (data_dir / instrument / "tick").mkdir(parents=True)


def test_main_returns_zero():
    assert main([]) == 0


def test_discovers_direct_instrument_directories(tmp_path):
    data_dir = tmp_path / "DANE"
    create_instrument_dir(data_dir, "MESM6")
    create_instrument_dir(data_dir, "NQMM6")

    assert discover_instruments(data_dir) == ["MESM6", "NQMM6"]


def test_discovery_ignores_files_and_nested_timeframe_directories(tmp_path):
    data_dir = tmp_path / "DANE"
    create_instrument_dir(data_dir, "MESM6")
    (data_dir / "README.txt").write_text("notes", encoding="utf-8")

    assert discover_instruments(data_dir) == ["MESM6"]


def test_main_prints_available_instruments_from_local_dane(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    create_instrument_dir(data_dir, "MESM6")
    create_instrument_dir(data_dir, "NQMM6")
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
