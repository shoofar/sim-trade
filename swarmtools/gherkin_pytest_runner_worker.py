from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TEST_SUCCESS = "test_success"
TEST_FAILURE = "test_failure"
INFRASTRUCTURE_ERROR = "infrastructure_error"


@dataclass(slots=True)
class WorkerRequest:
    id: str
    feature_json: str
    generated_dir: str
    work_dir: str
    timeout: str | None = None


def _parse_timeout(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(ms|s|m|h)?", value.strip())
    if not match:
        raise ValueError(f"unsupported timeout value: {value!r}")
    amount = float(match.group(1))
    unit = match.group(2) or "s"
    if unit == "ms":
        return amount / 1000.0
    if unit == "s":
        return amount
    if unit == "m":
        return amount * 60.0
    if unit == "h":
        return amount * 3600.0
    raise ValueError(f"unsupported timeout unit: {unit!r}")


def _read_request() -> WorkerRequest | None:
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        if line.strip():
            break
    payload = json.loads(line)
    return WorkerRequest(
        id=str(payload["id"]),
        feature_json=str(payload.get("feature_json", "")),
        generated_dir=str(payload.get("generated_dir", "")),
        work_dir=str(payload.get("work_dir", "")),
        timeout=payload.get("timeout"),
    )


def _resolve_path(base: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _emit_response(response: dict[str, Any]) -> None:
    json.dump(response, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")
    sys.stdout.flush()


def _make_response(request_id: str, outcome: str, output: str = "", error: str = "", duration: int = 0) -> dict[str, Any]:
    return {
        "id": request_id,
        "outcome": outcome,
        "output": output,
        "error": error,
        "duration": duration,
    }


def _handle_request(request: WorkerRequest) -> dict[str, Any]:
    started = time.monotonic()
    try:
        work_dir = Path(request.work_dir).resolve() if request.work_dir else Path.cwd()
        generated_dir = _resolve_path(work_dir, request.generated_dir) if request.generated_dir else work_dir
        if not generated_dir.exists():
            return _make_response(
                request.id,
                INFRASTRUCTURE_ERROR,
                error=f"generated_dir does not exist: {generated_dir}",
            )
        timeout = _parse_timeout(request.timeout)
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(generated_dir)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        outcome = TEST_SUCCESS if completed.returncode == 0 else TEST_FAILURE
        duration = int((time.monotonic() - started) * 1000)
        return _make_response(request.id, outcome, output=output, duration=duration)
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        duration = int((time.monotonic() - started) * 1000)
        return _make_response(
            request.id,
            INFRASTRUCTURE_ERROR,
            output=output,
            error="pytest timed out",
            duration=duration,
        )
    except Exception as exc:  # noqa: BLE001 - worker boundary needs a hard failure report
        duration = int((time.monotonic() - started) * 1000)
        return _make_response(request.id, INFRASTRUCTURE_ERROR, error=str(exc), duration=duration)


def main() -> int:
    while True:
        request = _read_request()
        if request is None:
            return 0
        response = _handle_request(request)
        _emit_response(response)


if __name__ == "__main__":
    raise SystemExit(main())
