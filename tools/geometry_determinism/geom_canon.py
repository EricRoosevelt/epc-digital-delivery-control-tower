"""Cross-platform geometry determinism probe for candidate C (IfcOpenShell pre-tessellation).

Writes two encodings of the same tessellation and prints their SHA-256 digests as JSON:

  raw    -- the round-2 format: elements in GlobalId order, vertices and triangles exactly
            as IfcOpenShell emitted them (float32 world coordinates, metres).
  canon  -- the same triangles with emission order removed: vertices quantised to a
            0.1 mm integer grid, each triangle rotated to start at its smallest vertex
            (winding kept), triangles sorted, vertices renumbered in first-use order,
            degenerate triangles dropped.

If raw matches across platforms, the round-2 format is already portable. If only canon
matches, emission order or float noise below 0.1 mm differs and the canonical form is
needed. If neither matches, geom_compare.py says which elements differ and how.

Public inputs only: never run this on private models in CI.

usage: python geom_canon.py OUT_DIR [--threads N] model.ifc [model.ifc ...]
"""
import argparse
import hashlib
import json
import multiprocessing
import os
import platform
import struct
import sys

import ifcopenshell
import ifcopenshell.geom
import numpy as np

GRID = 1e-4  # metres; 0.1 mm


def tessellate(path, threads):
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    f = ifcopenshell.open(path)
    it = ifcopenshell.geom.iterator(s, f, threads)
    items = {}
    if it.initialize():
        while True:
            sh = it.get()
            g = sh.geometry
            faces = np.asarray(g.faces, dtype=np.uint32)
            if len(faces):
                items[sh.guid] = (np.asarray(g.verts, dtype=np.float32).reshape(-1, 3), faces)
            if not it.next():
                break
    return items


def raw_blob(items):
    pos, idx, index, vb, ib = [], [], [], 0, 0
    for g in sorted(items):
        v, fa = items[g]
        pos.append(v)
        idx.append(fa + vb)
        index.append([g, ib, len(fa)])
        vb += len(v)
        ib += len(fa)
    verts, tris = np.concatenate(pos), np.concatenate(idx)
    blob = (struct.pack("<II", len(verts), len(tris))
            + verts.astype("<f4").tobytes() + tris.astype("<u4").tobytes())
    meta = json.dumps({"index": index}, sort_keys=True, separators=(",", ":")).encode()
    return blob, meta


def canon_element(v, fa):
    q = np.rint(v.astype(np.float64) / GRID).astype(np.int64)
    tris = []
    for t in fa.reshape(-1, 3):
        a, b, c = (tuple(q[i]) for i in t)
        if a == b or b == c or a == c:
            continue  # degenerate after quantisation
        k = min(range(3), key=lambda i: (a, b, c)[i])
        tri = ((a, b, c), (b, c, a), (c, a, b))[k]  # rotation keeps winding
        tris.append(tri)
    tris.sort()
    verts, ids, out = [], {}, []
    for tri in tris:
        for p in tri:
            if p not in ids:
                ids[p] = len(verts)
                verts.append(p)
            out.append(ids[p])
    return verts, out


def canon_blob(items):
    parts, index, per = [], [], {}
    for g in sorted(items):
        verts, tri = canon_element(*items[g])
        flat = [c for p in verts for c in p]
        body = struct.pack(f"<I{len(flat)}iI{len(tri)}I", len(verts), *flat, len(tri), *tri)
        parts.append(body)
        index.append([g, len(verts), len(tri)])
        per[g] = hashlib.sha256(body).hexdigest()
    blob = b"".join(parts)
    meta = json.dumps({"grid_m": GRID, "index": index}, sort_keys=True,
                      separators=(",", ":")).encode()
    return blob, meta, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--threads", type=int, default=multiprocessing.cpu_count())
    ap.add_argument("models", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    report = {"platform": platform.platform(), "machine": platform.machine(),
              "python": sys.version.split()[0], "ifcopenshell": ifcopenshell.version,
              "numpy": np.__version__, "threads": a.threads, "models": {}}
    for path in a.models:
        name = os.path.splitext(os.path.basename(path))[0]
        items = tessellate(path, a.threads)
        rb, rm = raw_blob(items)
        cb, cm, per = canon_blob(items)
        outputs = (("raw.bin", rb), ("raw.json", rm), ("canon.bin", cb), ("canon.json", cm))
        for suffix, data in outputs:
            with open(os.path.join(a.out, f"{name}.{suffix}"), "wb") as fh:
                fh.write(data)
        with open(os.path.join(a.out, f"{name}.elements.json"), "w", newline="\n") as fh:
            json.dump(per, fh, sort_keys=True, indent=0)
        report["models"][name] = {"elements": len(items),
                                  "raw_sha256": hashlib.sha256(rb + rm).hexdigest(),
                                  "canon_sha256": hashlib.sha256(cb + cm).hexdigest()}
    print(json.dumps(report, sort_keys=True, indent=1))


if __name__ == "__main__":
    main()
