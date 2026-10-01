"""The scenarios, the mode each declares, and which entry each one calls.

======================  =======  ==============================================
``member-evidence``     fixture  one sealed record: members to path, readings,
                                 citations and route
``pair-verdicts``       fixture  the same record: the chimney's slab pair READY
                                 and roof pair BLOCKED
``real-refusal``        real     the shipped manifest's actual refusal
``recheck-comparison``  fixture  the roof pair rechecked after a review re-held
                                 under the same model versions
``recheck-…``           fixture  nine more rechecks of that first record, one
                                 per entry of ``fixture.RECHECK_SCENARIOS``
======================  =======  ==============================================

The first two are one record on purpose: the prototype reads two things out of a
single sealed assessment, not two assessments that happen to agree.

The nine further rechecks exist so the prototype can show every state a carry-over
row can be in, and each side a re-issue can come from. What each is *given* is in
the table below; what it then *records* is the Framework's answer, pinned by
``tests/test_doctor_recheck_scenarios.py`` and decided nowhere in this package.

==============================================  ================================
``recheck-key-change-only``                     an unrelated rule edited; model
                                                versions unchanged
``recheck-semantics-changed``                   a cited rule's data type edited;
                                                model versions unchanged
``recheck-requirement-relaxed``                 a cited rule relaxed; model
                                                versions unchanged
``recheck-prior-without-basis``                 the prior record sealed without a
                                                comparison basis; nothing else
                                                moved
``recheck-producing-reissued``                  the producing model reissued,
                                                reading what it read
``recheck-producing-reissued-content-changed``  the producing model reissued, its
                                                R-005 failures now passing
``recheck-consuming-reissued``                  the consuming model reissued
``recheck-both-reissued``                       both reissued at once
``recheck-member-gone``                         the producing model reissued with
                                                the duct deleted
==============================================  ================================

The mode in :func:`scenario_index` is a **declaration**, made here so the
prototype can label a scenario before running it. It does not set the envelope's
``mode`` — the entry each scenario calls does that — and the adapter's tests hold
the two equal, so a declaration that drifted from its entry would be caught
rather than shown. Every recheck scenario calls the fixture entry: the real entry
has no recheck at all, because ``pcert-sample``'s own policy refuses the first
assessment and there is no sealed real record to succeed.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from types import MappingProxyType

from .envelope import FIXTURE, REAL
from .fixture import (
    PROJECT_ID,
    RECHECK_SCENARIOS,
    declared_request,
    first_record_envelope,
    recheck_scenario_envelope,
    superseding_recheck_envelope,
)
from .real import real_envelope
from .validated import validated_facts

__all__ = ["SCENARIOS", "scenario_envelope", "scenario_index"]


def _real_refusal() -> dict[str, object]:
    return real_envelope(declared_request(validated_facts(PROJECT_ID)))


#: ``name`` → ``(declared mode, entry)``.
SCENARIOS: MappingProxyType[str, tuple[str, Callable[[], dict[str, object]]]] = (
    MappingProxyType(
        {
            "member-evidence": (FIXTURE, first_record_envelope),
            "pair-verdicts": (FIXTURE, first_record_envelope),
            "real-refusal": (REAL, _real_refusal),
            "recheck-comparison": (FIXTURE, superseding_recheck_envelope),
            **{
                name: (FIXTURE, functools.partial(recheck_scenario_envelope, name))
                for name in RECHECK_SCENARIOS
            },
        }
    )
)


def scenario_index() -> list[dict[str, str]]:
    """``[{"name", "mode"}]`` for every scenario, in name order. Runs nothing."""

    return [{"name": name, "mode": SCENARIOS[name][0]} for name in sorted(SCENARIOS)]


def scenario_envelope(name: str) -> dict[str, object]:
    """The envelope for one named scenario; an unknown name is a ``KeyError``."""

    _mode, entry = SCENARIOS[name]
    return entry()
