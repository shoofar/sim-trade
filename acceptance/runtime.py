from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

LISTS_DIRECT_INSTRUMENTS = "Console instrument discovery 001 lists direct instrument directories"
IGNORES_NON_DIRECTORY_ENTRIES = "Console instrument discovery 002 ignores non-directory entries"
REPORTS_MISSING_DATA_DIRECTORY = "Console instrument discovery 003 reports missing data directory"
LISTS_SELECTED_INSTRUMENT_TIMEFRAMES = (
    "Console timeframe date discovery 001 lists timeframes for the selected instrument"
)
NORMALIZES_SELECTED_INSTRUMENT_DATES = (
    "Console timeframe date discovery 002 normalizes dates from filenames for the selected instrument"
)
IGNORES_FILENAMES_WITHOUT_DATES = (
    "Console timeframe date discovery 003 ignores filenames without date tokens"
)
REPORTS_EMPTY_SELECTED_INSTRUMENT_TIMEFRAMES = (
    "Console timeframe date discovery 004 reports no timeframes for an empty instrument directory"
)


def run_scenario(name: str) -> None:
    if name == LISTS_DIRECT_INSTRUMENTS:
        output = _run_console_with(
            directories=["MESM6", "NQMM6"],
            files=[],
        )
        _assert_console_output(
            output,
            contains=["MESM6", "NQMM6"],
            excludes=["tick", "glbx-mdp3"],
        )
        return

    if name == IGNORES_NON_DIRECTORY_ENTRIES:
        output = _run_console_with(
            directories=["MESM6"],
            files=["README.txt"],
        )
        _assert_console_output(
            output,
            contains=["MESM6"],
            excludes=["README.txt"],
        )
        return

    if name == REPORTS_MISSING_DATA_DIRECTORY:
        output = _run_console_without_dane()
        _assert_console_output(
            output,
            contains=["No data directory", "DANE"],
            excludes=["Traceback"],
        )
        return

    if name == LISTS_SELECTED_INSTRUMENT_TIMEFRAMES:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6/tick", "MESM6/1s", "NQMM6/5s"],
            files=[],
        )
        _assert_console_output(
            output,
            contains=["MESM6", "tick", "1s"],
            excludes=["5s", "glbx-mdp3"],
        )
        return

    if name == NORMALIZES_SELECTED_INSTRUMENT_DATES:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6/tick", "MESM6/1s"],
            files=[
                "MESM6/tick/glbx-mdp3-20260501.trades.csv",
                "MESM6/1s/glbx-mdp3-2026-05-03.ohlc.csv",
            ],
        )
        _assert_console_output(
            output,
            contains=["2026-05-01", "2026-05-03"],
            excludes=["csv row content"],
        )
        return

    if name == IGNORES_FILENAMES_WITHOUT_DATES:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6/tick"],
            files=[
                "MESM6/tick/glbx-mdp3-20260501.trades.csv",
                "MESM6/tick/notes.csv",
            ],
        )
        _assert_console_output(
            output,
            contains=["2026-05-01"],
            excludes=["notes.csv"],
        )
        return

    if name == REPORTS_EMPTY_SELECTED_INSTRUMENT_TIMEFRAMES:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6"],
            files=[],
        )
        _assert_console_output(
            output,
            contains=["No timeframes available for MESM6"],
            excludes=["Traceback"],
        )
        return

    raise AssertionError(f"Unhandled acceptance scenario: {name}")


def _run_console_with(directories: list[str], files: list[str]) -> str:
    with TemporaryDirectory() as temp:
        root = Path(temp)
        dane = root / "DANE"
        for directory in directories:
            (dane / directory / "tick").mkdir(parents=True)
        for file_name in files:
            (dane / file_name).write_text("notes", encoding="utf-8")
        return _run_console(root)


def _run_console_without_dane() -> str:
    with TemporaryDirectory() as temp:
        return _run_console(Path(temp))


def _run_console_with_selection(selected: str, directories: list[str], files: list[str]) -> str:
    with TemporaryDirectory() as temp:
        root = Path(temp)
        dane = root / "DANE"
        for directory in directories:
            (dane / directory).mkdir(parents=True, exist_ok=True)
        for file_name in files:
            path = dane / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("csv row content", encoding="utf-8")
        return _run_console(root, stdin=f"{selected}\n")


def _run_console(cwd: Path, stdin: str = "") -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    completed = subprocess.run(
        [sys.executable, "-m", "sim_server"],
        cwd=cwd,
        env=env,
        input=stdin,
        check=False,
        capture_output=True,
        text=True,
    )
    combined = completed.stdout + completed.stderr
    assert completed.returncode == 0, combined
    return combined


def _assert_console_output(output: str, contains: list[str], excludes: list[str]) -> None:
    for expected in contains:
        _assert_contains(output, expected)
    for unexpected in excludes:
        _assert_not_contains(output, unexpected)


def _assert_contains(output: str, expected: str) -> None:
    assert expected in output, output


def _assert_not_contains(output: str, unexpected: str) -> None:
    assert unexpected not in output, output
