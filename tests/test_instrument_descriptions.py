from sim_server.cli import main
from sim_server.instrument_descriptions import (
    DEFAULT_DESCRIPTION_FIELD,
    InstrumentDescription,
    description_for,
    load_initial_descriptions,
)


def write_instrument_file(data_dir, instrument, relative_path, content="rows are ignored"):
    path = data_dir / instrument / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_returns_configured_instrument_description_fields():
    descriptions = {
        "MESM6": InstrumentDescription(
            instrument="MESM6",
            kind="Futures",
            description="Micro E-mini S&P 500",
        )
    }

    assert description_for("MESM6", descriptions) == InstrumentDescription(
        instrument="MESM6",
        kind="Futures",
        description="Micro E-mini S&P 500",
    )


def test_uses_default_description_text_when_configured_text_is_missing():
    descriptions = {
        "MESM6": InstrumentDescription(
            instrument="MESM6",
            kind="Futures",
            description="",
        )
    }

    assert description_for("MESM6", descriptions) == InstrumentDescription(
        instrument="MESM6",
        kind="Futures",
        description=DEFAULT_DESCRIPTION_FIELD,
    )


def test_uses_default_kind_and_description_for_missing_configured_details():
    assert description_for("NQMM6", {}) == InstrumentDescription(
        instrument="NQMM6",
        kind=DEFAULT_DESCRIPTION_FIELD,
        description=DEFAULT_DESCRIPTION_FIELD,
    )


def test_loads_initial_descriptions_from_project_config(tmp_path):
    (tmp_path / "instrument_descriptions.json").write_text(
        '{"MESM6": {"kind": "Futures", "description": ""}}',
        encoding="utf-8",
    )

    assert load_initial_descriptions(tmp_path) == {
        "MESM6": InstrumentDescription(
            instrument="MESM6",
            kind="Futures",
            description="",
        )
    }


def test_main_prints_description_after_instrument_selection(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv", "csv row content")
    monkeypatch.chdir(tmp_path)
    selections = iter(["MESM6", ""])
    monkeypatch.setattr("builtins.input", lambda: next(selections))

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "MESM6" in output
    assert "Futures" in output
    assert "Micro E-mini S&P 500" in output
    assert "csv row content" not in output


def test_main_prints_default_description_for_missing_configured_details(
    tmp_path,
    monkeypatch,
    capsys,
):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "NQMM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    selections = iter(["NQMM6", ""])
    monkeypatch.setattr("builtins.input", lambda: next(selections))

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "NQMM6" in output
    assert DEFAULT_DESCRIPTION_FIELD in output
    assert "Traceback" not in output


def test_main_prints_default_description_when_configured_text_is_missing(
    tmp_path,
    monkeypatch,
    capsys,
):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    (tmp_path / "instrument_descriptions.json").write_text(
        '{"MESM6": {"kind": "Futures", "description": ""}}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    selections = iter(["MESM6", ""])
    monkeypatch.setattr("builtins.input", lambda: next(selections))

    assert main([]) == 0

    output = capsys.readouterr().out
    assert "MESM6" in output
    assert "Futures" in output
    assert DEFAULT_DESCRIPTION_FIELD in output


def test_main_does_not_offer_description_editing_workflow(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "DANE"
    write_instrument_file(data_dir, "MESM6", "tick/glbx-mdp3-20260501.trades.csv")
    monkeypatch.chdir(tmp_path)
    selections = iter(["MESM6", ""])
    monkeypatch.setattr("builtins.input", lambda: next(selections))

    assert main([]) == 0

    output = capsys.readouterr().out.lower()
    assert "edit" not in output
    assert "save description" not in output
