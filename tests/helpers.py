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
    "frozen_ruleset",
    "legacy_compat",
    "shipped_run_config",
    "declared_rules_plus_one",
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

    from epc_control_tower.exporters.legacy_projection import (
        narrow_to_project,
        narrow_to_ruleset,
    )

    return narrow_to_ruleset(
        narrow_to_project(shipped_pipeline_result().bundle, LEGACY_PROJECT_ID),
        frozen_ruleset(),
    )


@functools.cache
def frozen_ruleset():
    """The rule set version the published contract was built from.

    The run's rule set has moved on — it is a directory of declarative rules
    now — so anything asserting published numbers has to name the frozen one,
    exactly as it has to name the project.
    """

    from epc_control_tower.rules import load_ruleset

    return load_ruleset(
        PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
    )


@functools.cache
def legacy_compat():
    """The frozen legacy compatibility metadata the shipped config pins."""

    from epc_control_tower.exporters.legacy_compat import load_legacy_compatibility

    config = shipped_run_config()
    return load_legacy_compatibility(
        config.legacy_compat_path, expected_sha256=config.legacy_compat_sha256
    )


@functools.cache
def widened_ruleset_bundle():
    """A run over a rule library with one rule more than the shipped one.

    Returns ``(bundle, frozen_ruleset)``. The extra rule is added the way a
    rule is actually added — a TOML file in the library — rather than by
    swapping the whole library for a hand-built IDS document. That distinction
    started mattering the moment rules could carry priority, stage and labels:
    a bare `.ids` rule set has nowhere to state them, so a fixture built that
    way would drop the metadata and the published archive would change for a
    reason that has nothing to do with the scope being tested.
    """

    import dataclasses

    from epc_control_tower.pipeline import build_bundle
    from epc_control_tower.rules import load_ruleset

    scratch = PROJECT_ROOT / "tests" / f".widened-{uuid.uuid4().hex}"
    scratch.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, scratch, True)

    rules = scratch / "rules" / "epc-delivery"
    shutil.copytree(PROJECT_ROOT / "rules" / "epc-delivery", rules)
    (rules / "R-011.toml").write_text(_INERT_RULE, encoding="utf-8")

    frozen_path = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
    config = dataclasses.replace(
        shipped_run_config(),
        ruleset_path=rules,
        legacy_ruleset_path=frozen_path,
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    result = build_bundle(config, reports_dir=scratch / "reports")
    return result.bundle, load_ruleset(frozen_path)


#: A rule that finds nothing in this fixture: every window already declares
#: ``IsExternal``. Used to measure what adding a rule costs when it changes no
#: answer at all, so that anything which moves moved because the rule set moved.
_INERT_RULE = """rule_id = "R-011"
title = "Windows must declare IsExternal"
description = "An extra rule, used to measure what adding one costs."
checker = "ids"
severity = "WARNING"
owner_role = "architecture-lead"
stage = "Design"
discipline_scope = ["Architecture"]
citation = "IFC4 Pset_WindowCommon."

[[applicability]]
facet = "entity"
name = "IFCWINDOW"

[[requirements]]
facet = "property"
propertySet = "Pset_WindowCommon"
baseName = "IsExternal"
dataType = "IFCBOOLEAN"
cardinality = "required"
instructions = "Declare whether the window is external."
"""


@functools.cache
def declared_rules_plus_one():
    """The shipped run again, with one more declarative rule in the library.

    The extra rule is deliberately inert — it fails nothing and fixes nothing —
    so that whatever differs between this bundle and the shipped one differs
    because the rule set moved, not because the answers did.
    """

    import dataclasses

    from epc_control_tower.pipeline import build_bundle

    scratch = PROJECT_ROOT / "tests" / f".plus-one-{uuid.uuid4().hex}"
    scratch.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, scratch, True)

    # Nested to mirror the repository layout, and not for tidiness: a rule
    # directory compiles its IDS document to `<dir>/../../ids`, so a copy placed
    # one level shallower writes the build product into `tests/` and leaves the
    # working tree dirty — which CI fails on, correctly.
    rules = scratch / "rules" / "epc-delivery"
    shutil.copytree(PROJECT_ROOT / "rules" / "epc-delivery", rules)
    (rules / "R-011.toml").write_text(_INERT_RULE, encoding="utf-8")

    config = dataclasses.replace(
        shipped_run_config(),
        ruleset_path=rules,
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    return build_bundle(config, reports_dir=scratch / "reports").bundle
