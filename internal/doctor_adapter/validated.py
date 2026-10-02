"""The validated facts both entries read, from a run that writes nothing here.

The facts are the shipped models validated against the shipped rule library by
the real pipeline — :func:`~epc_control_tower.pipeline.build_bundle` narrowed by
:func:`~epc_control_tower.purpose.facts_from_bundle`, the only projection an
assessment may read. What differs from an ordinary run is only where the run
puts its by-products. Compiling the rule library writes the IDS document into
the ``ids/`` directory beside it, and the IDS checker writes its reports; both
would land in tracked paths of this checkout. So the rule library is copied into
a scratch directory outside the checkout, both by-products go there, and the
directory is removed once the bundle exists. The validated facts do not depend on
that location — the adapter's tests compare them with the test suite's own run.

One run per process, cached, so every scenario in a process reads the same facts.

:func:`scratch_bundle` is that run with one seam: a caller may edit the scratch
copy of the rule library before it is loaded. Only the fixture entry does, for
the recheck scenarios that ask what a rule edit moves, and the copy it edits is
the one outside the checkout — ``rules/`` is never written (ADR 0005 §5.7, B-1).
The real entry has no route to that seam: it reads :func:`validated_facts`,
which is always the unedited run.
"""

from __future__ import annotations

import dataclasses
import functools
import shutil
import tempfile
import uuid
from collections.abc import Callable
from pathlib import Path

from epc_control_tower.config import load_run_config
from epc_control_tower.pipeline import build_bundle
from epc_control_tower.purpose import AssessmentFacts, facts_from_bundle

from .details import DetailSource, source_from_bundle
from .envelope import PROJECT_ROOT

__all__ = [
    "detail_source",
    "requirement_keys_by_ruleset",
    "scratch_bundle",
    "validated_facts",
]


def scratch_bundle(edit_rules: Callable[[Path], None] | None = None):
    """The shipped models validated against a scratch copy of the rule library.

    ``edit_rules`` receives the scratch copy's directory before it is loaded.
    """

    config = load_run_config(PROJECT_ROOT)
    # Created with an explicit mode rather than through tempfile's directory
    # helpers, which on Windows under Python 3.14 apply an ACL the pipeline's
    # atomic writes trip over; tests/helpers.py avoids them for the same reason.
    scratch = Path(tempfile.gettempdir()) / f"epc-ct-doctor-adapter-{uuid.uuid4().hex}"
    scratch.mkdir(mode=0o777)
    try:
        rules = scratch / "rules" / config.resolved_ruleset_path().name
        shutil.copytree(config.resolved_ruleset_path(), rules)
        if edit_rules is not None:
            edit_rules(rules)
        scratch_config = dataclasses.replace(
            config,
            ruleset_path=rules,
            processed_data_dir=scratch / "processed",
            reports_dir=scratch / "reports",
        )
        return build_bundle(scratch_config, reports_dir=scratch / "reports").bundle
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


@functools.cache
def _bundle():
    return scratch_bundle()


def validated_facts(project_id: str) -> AssessmentFacts:
    return facts_from_bundle(_bundle(), project_id)


@functools.cache
def detail_source() -> DetailSource:
    """That same run, as the one place a cited finding may be explained from.

    Always the unedited run. An edited scratch run is never offered here: its
    findings are real output of a rule set nobody published, and what they
    required is not what any published requirement requires.
    """

    return source_from_bundle(_bundle())


def requirement_keys_by_ruleset() -> dict[tuple[str, str], frozenset[str]]:
    """The requirement keys of the rule set that run actually loaded."""

    ruleset = _bundle().ruleset
    return {
        (ruleset.ruleset_id, ruleset.version): frozenset(
            requirement.requirement_key for requirement in ruleset.requirements
        )
    }
