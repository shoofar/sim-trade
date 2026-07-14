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


def _run_console(cwd: Path) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    completed = subprocess.run(
        [sys.executable, "-m", "sim_server"],
        cwd=cwd,
        env=env,
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
