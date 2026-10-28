"""Original public geometric fixtures and an explicitly unsupported rule variant."""

import argparse
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.enterprise_rules_example import example_package  # noqa: E402
from tools.phase2_demo.export_public import export  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        sys.executable, str(ROOT / "tools/phase2_demo/export_public.py"),
        "--output-dir", str(args.output_dir),
    ], check=True)
    body = example_package()
    (args.output_dir / "public-rules.zip").write_bytes(body)
    with ZipFile(BytesIO(body)) as source:
        files = {name: source.read(name) for name in source.namelist()}
    files["rules/terminal.toml"] = (
        b'unsupported_enterprise_operator="explicit public negative fixture"\n'
        + files["rules/terminal.toml"]
    )
    target = BytesIO()
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            archive.writestr(name, content)
    (args.output_dir / "public-unsupported-rules.zip").write_bytes(target.getvalue())
    source = {
        "title": "PUBLIC SYNTHETIC bulk purpose selection", "units": "metres",
        "elements": [
            {"id": f"bulk-{index}", "name": f"PUBLIC BULK terminal {index:03d}",
             "class": "IfcAirTerminal", "type": "NOTDEFINED",
             "position": [float(index % 15) * 1.5, float(index // 15) * 1.5, 0.2],
             "size": [0.8, 0.6, 0.2]}
            for index in range(150)
        ],
    }
    (args.output_dir / "bulk-source.json").write_text(json.dumps(source), encoding="utf-8")
    (args.output_dir / "PUBLIC-BULK.ifc").write_bytes(export(source, "before")[0])


if __name__ == "__main__":
    main()
