"""Shared test scaffolding.

Not a test module — it defines no tests and pytest does not collect it.
"""

from __future__ import annotations

import atexit
import functools
import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The project the frozen published contract describes. A second project now
#: exists, so tests that assert published numbers have to say which project
#: they mean instead of relying on there being only one.
LEGACY_PROJECT_ID = "pcert-sample"

__all__ = [
    "LEGACY_PROJECT_ID",
    "PROJECT_ROOT",
    "published_bundle",
    "shipped_pipeline_result",
    "shipped_reports_dir",
    "shipped_run_config",
    "widened_ruleset_bundle",
    "writable_test_directory",
]


@contextmanager
def writable_test_directory(prefix: str):
    """A scratch directory the tests can actually write to.

    ``tempfile.TemporaryDirectory`` is deliberately avoided: Python 3.14 gives
    it a restrictive ACL on Windows, which the pipeline's atomic writes trip
    over. This mirrors the helper the pre-existing BCF workflow tests already
    use, rather than introducing a second convention.
    """

    path = PROJECT_ROOT / "tests" / f".{prefix}-{uuid.uuid4().hex}"
    path.mkdir(mode=0o777)
    try:
        yield path
    finally:
        shutil.rmtree(path)


@functools.cache
def shipped_reports_dir() -> Path:
    """A scratch reports directory that outlives one test class.

    Deliberately not the repository's own ``reports/``: a test run must not
    rewrite tracked artifacts as a side effect of asserting something about
    them.
    """

    path = PROJECT_ROOT / "tests" / f".reports-{uuid.uuid4().hex}"
    path.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, path, True)
    return path


@functools.cache
def shipped_run_config():
    from epc_control_tower.config import load_run_config

    return load_run_config(PROJECT_ROOT)


@functools.cache
def shipped_pipeline_result():
    """Validate the shipped fixture once and share the result.

    A full run opens three IFC files and validates each against every
    specification, which is far too slow to repeat per test class. Nothing
    mutates the result, so sharing it is safe.
    """

    from epc_control_tower.pipeline import build_bundle

    return build_bundle(shipped_run_config(), reports_dir=shipped_reports_dir())


@functools.cache
def published_bundle():
    """The shipped run, narrowed to the project the published contract covers.

    Phase 1's characterization tests could say "47 findings" because there was
    only one project. There are two now, so the same assertions have to name
    the project they are about — which is what they always meant.
    """

    from epc_control_tower.exporters.legacy_projection import narrow_to_project

    return narrow_to_project(shipped_pipeline_result().bundle, LEGACY_PROJECT_ID)


@functools.cache
def widened_ruleset_bundle():
    """A run over a rule set with one rule more than the published one.

    Returns ``(bundle, frozen_ruleset)``. Built by adding a specification to the
    declared rules rather than by editing the shipped document, so the frozen
    document on disk stays exactly what it was — which is the whole point of
    the scope being tested.
    """

    import dataclasses
    import sys

    from ifctester import ids

    from epc_control_tower.pipeline import build_bundle
    from epc_control_tower.rules import load_ruleset

    if str(PROJECT_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from generate_ids import add_specification, build_document

    scratch = shipped_reports_dir().parent / f".widened-{uuid.uuid4().hex}"
    scratch.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, scratch, True)

    document = build_document()
    add_specification(
        document=document,
        identifier="R-006",
        name="Windows must declare IsExternal",
        entity_name="IFCWINDOW",
        requirements=[
            ids.Property(
                propertySet="Pset_WindowCommon",
                baseName="IsExternal",
                dataType="IFCBOOLEAN",
                cardinality="required",
                instructions="Declare whether the window is external.",
            )
        ],
        description="An eighth rule, used to test that adding one is safe.",
    )
    widened = scratch / "widened.ids"
    document.to_xml(str(widened))

    frozen_path = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
    config = dataclasses.replace(
        shipped_run_config(),
        ruleset_path=widened,
        legacy_ruleset_path=frozen_path,
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    result = build_bundle(config, reports_dir=scratch / "reports")
    return result.bundle, load_ruleset(frozen_path)
