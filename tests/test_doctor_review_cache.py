"""Bounded serialized review cache, short locks and geometry-free project reads."""

from concurrent.futures import ThreadPoolExecutor
import json
import threading
import tracemalloc

import ifcopenshell
import pytest

from internal.doctor_adapter import review as review_module
from internal.doctor_adapter.project_library import ProjectLibrary
from internal.doctor_adapter.review import ReviewStore


def model_bytes(name="Public wall"):
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name=name)
    return model.to_string().encode()


def test_native_build_does_not_block_other_report_or_geometry_reads(monkeypatch):
    store = ReviewStore()
    first = store.create("first.ifc", model_bytes())
    entered, release = threading.Event(), threading.Event()
    original = review_module._mesh

    def waiting(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(review_module, "_mesh", waiting)
    with ThreadPoolExecutor(max_workers=3) as pool:
        build = pool.submit(store.create, "second.ifc", model_bytes("Second"))
        assert entered.wait(3)
        try:
            assert pool.submit(store.get, first["review_id"]).result(timeout=0.5) == first
            assert (
                pool.submit(store.geometry, first["review_id"]).result(timeout=0.5)["review_id"]
                == first["review_id"]
            )
        finally:
            release.set()
        build.result(timeout=5)


def test_lru_entry_limit_clear_and_database_recovery(tmp_path):
    store = ReviewStore(cache_max_entries=2, cache_max_bytes=1 << 20)
    library = ProjectLibrary(tmp_path, store)
    project = library.create_project("Public cache recovery")
    first = store.demo()
    saved = library.save_revision(project["project_id"], first["review_id"])
    geometry = store.geometry_payload(first["review_id"])
    assert json.loads(geometry)["meshes"]  # Actual public IFC triangles survive eviction.
    store.create("second.ifc", model_bytes("Second"))
    assert store.stats()["entries"] <= 2
    assert store.stats()["evictions"] > 0
    assert store.get(first["review_id"]) == first
    assert store.geometry_payload(first["review_id"]) == geometry
    stats = store.clear()
    assert stats["entries"] == stats["bytes"] == 0
    assert library.revision(saved["revision"]["revision_id"])["report"] == first
    assert store.stats()["geometries"] == 0
    assert store.geometry_payload(first["review_id"]) == geometry


def test_geometry_payload_stays_serialized_and_clear_releases_resident_bytes():
    source = ReviewStore()
    report = source.create("public.ifc", model_bytes())
    # Deliberately large JSON number arrays: callers must not allocate Python floats.
    payload = (
        b'{"review_id":'
        + json.dumps(report["review_id"]).encode()
        + b',"meshes":[{"positions":['
        + b"0.123456789," * 500000
        + b'0],"indices":[]}],"unavailable":[]}'
    )
    store = ReviewStore(cache_max_entries=4, cache_max_bytes=16 << 20)
    tracemalloc.start()
    store.admit_serialized(json.dumps(report).encode(), payload)
    current, peak = tracemalloc.get_traced_memory()
    assert store.geometry_payload(report["review_id"]) is payload
    assert peak < len(payload) // 2  # No float/list tree or full payload re-encoding.
    assert store.stats()["geometry_bytes"] == len(payload)
    store.clear()
    assert store.stats()["bytes"] == 0
    tracemalloc.stop()


def test_oversized_payload_bypasses_cache_but_loader_can_deliver_it(tmp_path):
    source = ReviewStore()
    report = source.create("public.ifc", model_bytes())
    geometry = source.geometry_payload(report["review_id"])
    store = ReviewStore(cache_max_entries=4, cache_max_bytes=1)
    store.set_loaders(
        report_loader=lambda _: json.dumps(report).encode(), geometry_loader=lambda _: geometry
    )
    assert store.get(report["review_id"]) == report
    assert store.geometry_payload(report["review_id"]) == geometry
    assert store.stats()["bytes"] == 0
    assert store.stats()["oversized"] > 0


def test_project_report_followup_compare_and_brief_never_select_geometry(tmp_path, monkeypatch):
    from doctor.project_brief import project_brief

    store = ReviewStore()
    library = ProjectLibrary(tmp_path, store)
    project = library.create_project("Report-only evidence")
    a = store.create("a.ifc", model_bytes())
    b = store.create("b.ifc", model_bytes())
    first = library.save_revision(project["project_id"], a["review_id"])["revision"]
    second = library.save_revision(
        project["project_id"], b["review_id"], model_id=first["model_id"]
    )["revision"]
    statements = []
    original = library._db
    from contextlib import contextmanager

    @contextmanager
    def traced():
        with original() as db:
            db.set_trace_callback(statements.append)
            yield db

    monkeypatch.setattr(library, "_db", traced)
    store.clear()
    library.revision(first["revision_id"])
    library.update_followup(
        first["revision_id"],
        a["findings"][0]["finding_id"],
        status="ready_for_recheck",
        owner="Public owner",
    )
    library.compare(first["revision_id"], second["revision_id"])
    project_brief(library, project["project_id"])
    assert not any("geometry_json" in sql.lower() for sql in statements)
    assert store.stats()["geometries"] == 0
    assert store.get(a["review_id"])["findings"][0] == a["findings"][0]


def test_repeat_save_does_not_reload_geometry(tmp_path, monkeypatch):
    store = ReviewStore()
    library = ProjectLibrary(tmp_path, store)
    project = library.create_project("Duplicate save")
    report = store.create("public.ifc", model_bytes())
    saved = library.save_revision(project["project_id"], report["review_id"])

    def forbidden(*args):
        raise AssertionError("Duplicate revision save loaded large geometry")

    monkeypatch.setattr(store, "geometry_payload", forbidden)
    assert library.save_revision(project["project_id"], report["review_id"]) == saved


def test_progress_and_worker_geometry_file_do_not_require_unbounded_cache(tmp_path):
    store = ReviewStore(cache_max_bytes=1)
    states = []
    path = tmp_path / "geometry.json"
    report = store.create(
        "public.ifc",
        model_bytes(),
        progress=lambda *args: states.append(args),
        geometry_output=path,
    )
    assert json.loads(path.read_bytes())["review_id"] == report["review_id"]
    assert {stage for stage, _, _ in states} >= {
        "parsing",
        "checking",
        "tessellating",
        "serializing",
        "complete",
    }
    assert all(0 <= completed <= total for _, completed, total in states)
    assert states[-1] == ("complete", 1, 1)
    assert store.stats()["bytes"] == 0


def test_clear_releases_actual_traced_geometry_allocation():
    import gc

    report = ReviewStore().create("trace.ifc", model_bytes())
    store = ReviewStore(cache_max_bytes=16 << 20)
    tracemalloc.start()
    try:
        payload = (
            b'{"review_id":'
            + json.dumps(report["review_id"]).encode()
            + b',"meshes":[],"unavailable":[],"public_padding":"'
            + b"x" * (8 << 20)
            + b'"}'
        )
        store.admit_serialized(json.dumps(report).encode(), payload)
        size = len(payload)
        del payload
        gc.collect()
        before, _ = tracemalloc.get_traced_memory()
        store.clear()
        gc.collect()
        after, _ = tracemalloc.get_traced_memory()
        assert before - after >= size
        assert store.stats()["bytes"] == 0
    finally:
        tracemalloc.stop()


def test_geometry_hashing_admission_does_not_block_cached_reads(monkeypatch):
    store = ReviewStore()
    first = store.create("first.ifc", model_bytes())
    report = ReviewStore().create("second.ifc", model_bytes("Second"))
    payload = (
        b'{"review_id":'
        + json.dumps(report["review_id"]).encode()
        + b',"meshes":[],"unavailable":[]}'
    )
    entered, release = threading.Event(), threading.Event()
    original = review_module._prepared

    def slow(value):
        if value is payload:
            entered.set()
            assert release.wait(5)
        return original(value)

    monkeypatch.setattr(review_module, "_prepared", slow)
    with ThreadPoolExecutor(max_workers=2) as pool:
        admission = pool.submit(store.admit_serialized, json.dumps(report).encode(), payload)
        assert entered.wait(3)
        try:
            assert pool.submit(store.get, first["review_id"]).result(timeout=0.5) == first
        finally:
            release.set()
        assert admission.result(timeout=5) == report


def test_lru_touches_report_entries_instead_of_fifo():
    reports = [ReviewStore().create(f"{i}.ifc", model_bytes(str(i))) for i in range(4)]
    store = ReviewStore(cache_max_entries=3)
    for report in reports[:2]:
        store.admit_report(report)
    assert store.get(reports[0]["review_id"]) == reports[0]
    for report in reports[2:]:
        store.admit_report(report)
    assert store.get(reports[0]["review_id"]) == reports[0]
    with pytest.raises(KeyError):
        store.get(reports[1]["review_id"])


def test_geometry_bytes_checksum_detects_corruption_without_decoding_floats(tmp_path):
    import sqlite3

    store = ReviewStore()
    library = ProjectLibrary(tmp_path, store)
    project = library.create_project("Public integrity")
    report = store.create("source.ifc", model_bytes())
    saved = library.save_revision(project["project_id"], report["review_id"])
    original = store.geometry_payload(report["review_id"])
    with sqlite3.connect(library.path) as db:
        kind = db.execute("SELECT typeof(geometry_json) FROM revisions").fetchone()[0]
        assert kind == "blob"
        db.execute("UPDATE revisions SET geometry_json=?", (original + b" ",))
    store.clear()
    assert library.revision(saved["revision"]["revision_id"])["report"] == report
    from internal.doctor_adapter.project_library import ProjectLibraryError

    with pytest.raises(ProjectLibraryError, match="geometry"):
        store.geometry_payload(report["review_id"])


def test_old_text_geometry_rows_stay_lazy_and_are_not_recaptured(tmp_path):
    import sqlite3

    store = ReviewStore()
    library = ProjectLibrary(tmp_path, store)
    project = library.create_project("Legacy public persistence")
    report = store.create("source.ifc", model_bytes())
    saved = library.save_revision(project["project_id"], report["review_id"])
    original = store.geometry_payload(report["review_id"])
    with sqlite3.connect(library.path) as db:
        db.execute(
            "UPDATE revisions SET geometry_json=?,geometry_sha256=NULL", (original.decode(),)
        )
    restarted = ReviewStore()
    older = ProjectLibrary(tmp_path, restarted)
    older.revision(saved["revision"]["revision_id"])
    assert restarted.stats()["geometries"] == 0
    assert restarted.geometry_payload(report["review_id"]) == original
    with sqlite3.connect(library.path) as db:
        assert db.execute("SELECT geometry_sha256 FROM revisions").fetchone()[0] is None


def test_old_database_schema_migrates_without_loading_geometry(tmp_path):
    import sqlite3
    from internal.doctor_adapter.project_library import _SCHEMA

    # Reproduce the previous schema, including a real old TEXT geometry row.
    old_schema = _SCHEMA.replace("    geometry_sha256 TEXT,\n", "")
    old_schema = old_schema.replace("report_json BLOB", "report_json TEXT").replace(
        "geometry_json BLOB", "geometry_json TEXT"
    )
    with sqlite3.connect(tmp_path / "library.sqlite3") as db:
        db.executescript(old_schema)
        assert "geometry_sha256" not in {
            r[1] for r in db.execute("PRAGMA table_info(revisions)")
        }
    store = ReviewStore()
    library = ProjectLibrary(tmp_path, store)
    with sqlite3.connect(library.path) as db:
        assert "geometry_sha256" in {r[1] for r in db.execute("PRAGMA table_info(revisions)")}
    assert store.stats()["bytes"] == 0


def test_payload_admission_rejects_conflicting_report_without_changing_geometry():
    from copy import deepcopy

    store = ReviewStore()
    report = store.create("original.ifc", model_bytes())
    original = store.geometry_payload(report["review_id"])
    changed = deepcopy(report)
    changed["elements"][0]["name"] = "Not the frozen observation"
    with pytest.raises(ValueError, match="different review payload"):
        store.admit_serialized(json.dumps(changed).encode(), original)
    assert store.get(report["review_id"]) == report
    assert store.geometry_payload(report["review_id"]) is original
