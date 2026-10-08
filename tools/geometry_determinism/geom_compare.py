"""Explain a geometry digest mismatch between two geom_canon.py output directories.

For every model present in both, classify each element:
  identical            canonical bytes equal
  coords_only          same triangle count, vertices differ (prints the largest shift)
  topology             different triangle count after canonicalisation
  only_left/only_right element tessellated on one side only
Exit status 0 only when every element is identical.

usage: python geom_compare.py LEFT_DIR RIGHT_DIR
"""
import collections
import json
import os
import struct
import sys


def load(d, name):
    meta = json.load(open(os.path.join(d, f"{name}.canon.json")))
    blob = open(os.path.join(d, f"{name}.canon.bin"), "rb").read()
    out, off = {}, 0
    for g, nv, nt in meta["index"]:
        (n,) = struct.unpack_from("<I", blob, off)
        verts = struct.unpack_from(f"<{n * 3}i", blob, off + 4)
        off += 4 + 12 * n
        (m,) = struct.unpack_from("<I", blob, off)
        tri = struct.unpack_from(f"<{m}I", blob, off + 4)
        off += 4 + 4 * m
        out[g] = (verts, tri)
    return out, meta["grid_m"]


def main(left, right):
    suffix = ".canon.json"
    names = sorted(f[:-len(suffix)] for f in os.listdir(left) if f.endswith(suffix))
    worst_all, bad = 0.0, 0
    for name in names:
        if not os.path.exists(os.path.join(right, f"{name}.canon.json")):
            print(name, "missing on the right")
            bad += 1
            continue
        a, grid = load(left, name)
        b, _ = load(right, name)
        tally, worst = collections.Counter(), 0.0
        for g in sorted(set(a) | set(b)):
            if g not in b:
                tally["only_left"] += 1
            elif g not in a:
                tally["only_right"] += 1
            elif a[g] == b[g]:
                tally["identical"] += 1
            elif len(a[g][1]) != len(b[g][1]) or len(a[g][0]) != len(b[g][0]):
                tally["topology"] += 1
            else:
                tally["coords_only"] += 1
                worst = max(worst, max(abs(x - y) for x, y in zip(a[g][0], b[g][0])) * grid)
        bad += sum(v for k, v in tally.items() if k != "identical")
        worst_all = max(worst_all, worst)
        print(name, dict(tally), f"max_vertex_shift_m={worst:.6f}")
    print("elements_not_identical", bad, f"max_vertex_shift_m={worst_all:.6f}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
