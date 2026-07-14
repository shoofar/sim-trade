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
STORES_VALID_SELECTION = "Console selection memory 001 stores a valid instrument and date selection"
REJECTS_UNDISCOVERED_DATE = (
    "Console selection memory 002 rejects a date that was not discovered for the selected instrument"
)
REJECTS_UNDISCOVERED_INSTRUMENT = (
    "Console selection memory 003 rejects an instrument that was not discovered"
)
KEEPS_SELECTION_IN_SESSION = (
    "Console selection memory 004 keeps selections only for the current run"
)
SHOWS_CONFIGURED_INSTRUMENT_DETAILS = (
    "Console instrument description 001 shows configured instrument details"
)
SHOWS_DEFAULT_DESCRIPTION_TEXT = (
    "Console instrument description 002 shows the default description when text is missing"
)
SHOWS_DEFAULT_FIELDS_FOR_MISSING_DETAILS = (
    "Console instrument description 003 uses default fields for a discovered instrument without configured details"
)
DOES_NOT_ALLOW_DESCRIPTION_EDITING = (
    "Console instrument description 004 does not allow editing descriptions in this slice"
)
SHOWS_THREE_RAW_TICK_RECORDS = (
    "Console CSV load confirmation 001 shows up to three RAW-TICK records with required fields"
)
SHOWS_SHORT_CSV_RECORD_COUNT = (
    "Console CSV load confirmation 002 shows all records when fewer than three are loaded"
)
REJECTS_MISSING_REQUIRED_COLUMN = (
    "Console CSV load confirmation 003 rejects a CSV missing a required column"
)
HIDES_NON_REQUIRED_COLUMNS = (
    "Console CSV load confirmation 004 does not expose non-required CSV columns as model fields"
)
SHOWS_OHLC_SOURCE = (
    "Console CSV load confirmation 005 shows OHLC source for a selected OHLC data category"
)
STORES_LOADED_CSV_IN_MEMORY = (
    "Console in-memory data table 001 stores required fields for a loaded CSV"
)
SUPPORTS_MAXIMUM_RECORD_COUNT = (
    "Console in-memory data table 002 supports the agreed maximum record count"
)
REJECTS_ABOVE_MAXIMUM_RECORD_COUNT = (
    "Console in-memory data table 003 rejects files above the agreed maximum record count"
)
REPORTS_EMPTY_CSV_TABLE = (
    "Console in-memory data table 004 reports an empty CSV without sample records"
)
KEEPS_DATA_TABLE_IN_SESSION = (
    "Console in-memory data table 005 is available only during the current run"
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

    if name == STORES_VALID_SELECTION:
        output = _run_console_with_selection(
            selected="MESM6\n2026-05-01",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["Stored selection MESM6 2026-05-01"],
            excludes=["csv row content"],
        )
        return

    if name == REJECTS_UNDISCOVERED_DATE:
        output = _run_console_with_selection(
            selected="MESM6\n2026-05-02",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["Date 2026-05-02 is not available for MESM6"],
            excludes=["Stored selection MESM6 2026-05-02", "Traceback"],
        )
        return

    if name == REJECTS_UNDISCOVERED_INSTRUMENT:
        output = _run_console_with_selection(
            selected="NQMM6",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["Instrument NQMM6 is not available"],
            excludes=["Stored selection NQMM6", "Traceback"],
        )
        return

    if name == KEEPS_SELECTION_IN_SESSION:
        output = _run_console_with_selection(
            selected="MESM6\n2026-05-01",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["Stored selection MESM6 2026-05-01"],
            excludes=["selection.json", "selections.csv"],
        )
        return

    if name == SHOWS_CONFIGURED_INSTRUMENT_DETAILS:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["MESM6", "Futures", "Micro E-mini S&P 500"],
            excludes=["csv row content"],
        )
        return

    if name == SHOWS_DEFAULT_DESCRIPTION_TEXT:
        output = _run_console_with_description_config(
            selected="MESM6",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
            config='{"MESM6": {"kind": "Futures", "description": ""}}',
        )
        _assert_console_output(
            output,
            contains=["MESM6", "Futures", "pusty - do uzupelnienia"],
            excludes=[],
        )
        return

    if name == SHOWS_DEFAULT_FIELDS_FOR_MISSING_DETAILS:
        output = _run_console_with_selection(
            selected="NQMM6",
            directories=["NQMM6/tick"],
            files=["NQMM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["NQMM6", "pusty - do uzupelnienia"],
            excludes=["Traceback"],
        )
        return

    if name == DOES_NOT_ALLOW_DESCRIPTION_EDITING:
        output = _run_console_with_selection(
            selected="MESM6",
            directories=["MESM6/tick"],
            files=["MESM6/tick/glbx-mdp3-20260501.trades.csv"],
        )
        _assert_console_output(
            output,
            contains=["MESM6", "Futures", "Micro E-mini S&P 500"],
            excludes=["edit", "save description"],
        )
        return

    if name == SHOWS_THREE_RAW_TICK_RECORDS:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(4),
        )
        _assert_console_output(
            output,
            contains=["CSV loaded", "timeframe=tick", "source=RAW-TICK", "sequence=374608942"],
            excludes=[],
        )
        assert output.count("ts_event=") == 3, output
        return

    if name == SHOWS_SHORT_CSV_RECORD_COUNT:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(2),
        )
        _assert_console_output(output, contains=["CSV loaded"], excludes=[])
        assert output.count("ts_event=") == 2, output
        return

    if name == REJECTS_MISSING_REQUIRED_COLUMN:
        header = [field for field in REQUIRED_CSV_FIELDS if field != "sequence"]
        rows = [[value for index, value in enumerate(row) if REQUIRED_CSV_FIELDS[index] != "sequence"] for row in _csv_rows(1)]
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=header,
            rows=rows,
        )
        _assert_console_output(
            output,
            contains=["Missing required column sequence"],
            excludes=["ts_event=", "Traceback"],
        )
        return

    if name == HIDES_NON_REQUIRED_COLUMNS:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=[*REQUIRED_CSV_FIELDS, "publisher_id", "flags", "ts_recv"],
            rows=[[*_csv_rows(1)[0], "1", "130", "2026-05-01T00:00:00Z"]],
        )
        _assert_console_output(
            output,
            contains=["CSV loaded", "ts_event=", "source=RAW-TICK"],
            excludes=["publisher_id", "flags", "ts_recv"],
        )
        return

    if name == SHOWS_OHLC_SOURCE:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\n1s\nload",
            timeframe="1s",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(1),
        )
        _assert_console_output(
            output,
            contains=["timeframe=1s", "source=OHLC"],
            excludes=[],
        )
        return

    if name == STORES_LOADED_CSV_IN_MEMORY:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(4),
        )
        _assert_console_output(
            output,
            contains=["4 records stored in memory", "ts_event=", "timeframe=tick", "source=RAW-TICK"],
            excludes=[],
        )
        assert output.count("ts_event=") == 3, output
        return

    if name == SUPPORTS_MAXIMUM_RECORD_COUNT:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(20000),
        )
        _assert_console_output(
            output,
            contains=["20000 records stored in memory"],
            excludes=["Traceback"],
        )
        assert output.count("ts_event=") == 3, output
        return

    if name == REJECTS_ABOVE_MAXIMUM_RECORD_COUNT:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(20001),
        )
        _assert_console_output(
            output,
            contains=["Selected CSV exceeds the 20000 record limit"],
            excludes=["records stored in memory", "ts_event=", "Traceback"],
        )
        return

    if name == REPORTS_EMPTY_CSV_TABLE:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=[],
        )
        _assert_console_output(
            output,
            contains=["0 records stored in memory"],
            excludes=["ts_event=", "Traceback"],
        )
        return

    if name == KEEPS_DATA_TABLE_IN_SESSION:
        output = _run_console_with_csv(
            selected="MESM6\n2026-05-01\ntick\nload",
            timeframe="tick",
            header=REQUIRED_CSV_FIELDS,
            rows=_csv_rows(4),
        )
        _assert_console_output(
            output,
            contains=["4 records stored in memory"],
            excludes=["data_table.json", "data_table.csv"],
        )
        return

    raise AssertionError(f"Unhandled acceptance scenario: {name}")


REQUIRED_CSV_FIELDS = [
    "ts_event",
    "instrument_id",
    "side",
    "price",
    "size",
    "sequence",
    "symbol",
]


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


def _run_console_with_description_config(
    selected: str,
    directories: list[str],
    files: list[str],
    config: str,
) -> str:
    with TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "instrument_descriptions.json").write_text(config, encoding="utf-8")
        dane = root / "DANE"
        for directory in directories:
            (dane / directory).mkdir(parents=True, exist_ok=True)
        for file_name in files:
            path = dane / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("csv row content", encoding="utf-8")
        return _run_console(root, stdin=f"{selected}\n")


def _run_console_with_csv(
    selected: str,
    timeframe: str,
    header: list[str],
    rows: list[list[str]],
) -> str:
    with TemporaryDirectory() as temp:
        root = Path(temp)
        csv_path = root / "DANE" / "MESM6" / timeframe / "glbx-mdp3-20260501.trades.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [",".join(header), *(",".join(row) for row in rows)]
        csv_path.write_text("\n".join(lines), encoding="utf-8")
        return _run_console(root, stdin=f"{selected}\n")


def _csv_rows(count: int) -> list[list[str]]:
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
