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

__all__ = [
    "PROJECT_ROOT",
    "shipped_pipeline_result",
    "shipped_reports_dir",
    "shipped_run_config",
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
