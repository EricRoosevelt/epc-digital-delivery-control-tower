"""Single-use native IFC worker. Only the supervisor publishes its completed files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    stage = "starting"

    def emit(name, completed=0, total=0):
        nonlocal stage
        stage = name
        print("BIMDOCTOR_IMPORT " + json.dumps(
            {"stage": name, "completed": completed, "total": total}
        ), flush=True)

    try:
        from internal.doctor_adapter.review import ReviewStore

        store = ReviewStore(args.root)
        report = store.create(
            args.filename, args.input.read_bytes(), progress=emit,
            geometry_output=args.output / "geometry.json",
        )
        emit("serializing")
        (args.output / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":")),
            encoding="utf-8",
        )
        emit("complete")
        return 0
    except Exception as error:
        print("BIMDOCTOR_IMPORT " + json.dumps({"error": {
            "code": "import_failed", "stage": stage, "type": type(error).__name__,
            "message": str(error),
        }}), flush=True)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
