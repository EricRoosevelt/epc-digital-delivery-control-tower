"""Markdown table: does each runner's geometry match the reference, per model and encoding?

The reference is the windows-latest single-thread runner. A second reference, recorded on a
local Windows machine with the same pins, makes the comparison cross-machine as well.

usage: python summarise.py ARTIFACTS_DIR LOCAL_REFERENCE.json
"""
import json
import os
import sys


def main(root, local_ref):
    runs = {}
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "report.json")
        if os.path.exists(p):
            runs[d] = json.load(open(p, encoding="utf-8"))
    refs = {"windows-latest t1": runs.get("geom-windows-latest-t1"),
            "local Windows t1": json.load(open(local_ref, encoding="utf-8"))}
    print("## Geometry determinism (candidate C)\n")
    print("| runner | platform | python | ifcopenshell | numpy | threads | elements |")
    print("|---|---|---|---|---|---:|---:|")
    for d, r in runs.items():
        n = sum(m["elements"] for m in r["models"].values())
        print(f"| {d} | {r['platform']} | {r['python']} | {r['ifcopenshell']} | {r['numpy']} "
              f"| {r['threads']} | {n} |")
    oses = ("ubuntu-latest", "windows-latest", "macos-latest")
    missing = sorted({f"geom-{o}-t{t}" for o in oses for t in (1, 4)} - set(runs))
    if missing:
        print(f"\nNo artifact (job failed before writing geometry): {', '.join(missing)}")
    for name, ref in refs.items():
        print(f"\n### Against {name}\n")
        if ref is None:
            print("Reference missing.")
            continue
        print("| runner | " + " | ".join(ref["models"]) + " |")
        print("|---|" + "---|" * len(ref["models"]))
        for d, r in runs.items():
            cells = []
            for m, a in ref["models"].items():
                b = r["models"].get(m)
                if b is None:
                    cells.append("missing")
                    continue
                raw = "raw same" if a["raw_sha256"] == b["raw_sha256"] else "raw DIFF"
                canon = "canon same" if a["canon_sha256"] == b["canon_sha256"] else "canon DIFF"
                cells.append(f"{raw} {canon}")
            print(f"| {d} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
