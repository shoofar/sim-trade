from __future__ import annotations

import json
import sys
from pathlib import Path


def generate(ir_path: Path, output_path: Path) -> None:
    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    scenarios = ir.get("scenarios", [])

    lines = [
        "from acceptance.runtime import run_scenario",
        "",
        "",
    ]
    for index, scenario in enumerate(scenarios, start=1):
        name = scenario["name"]
        test_name = f"test_scenario_{index:03d}"
        lines.extend(
            [
                f"def {test_name}():",
                f"    run_scenario({name!r})",
                "",
                "",
            ]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("usage: python -m acceptance.generate_acceptance <json-ir> <generated-test-output>")
        return 2

    generate(Path(args[0]), Path(args[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
