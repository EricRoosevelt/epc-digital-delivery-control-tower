"""A read-only internal adapter between the Framework and the BIM Doctor prototype.

It hands over, for exactly four scenarios, what the Framework has already
produced — unchanged, inside one fixed envelope — and adds no judgement of its
own. No verdict, disposition, condition status or coverage reading is made here;
every one of them is whatever :func:`~epc_control_tower.purpose.assess_purpose`
or :func:`~epc_control_tower.purpose.recheck_purpose` returned.

The envelope is the seam with the Doctor UI, and its keys and meanings are fixed
by the technical director rather than chosen here:

``mode``
    ``"fixture"`` or ``"real"`` — which entry was called. Never inferred from a
    project name or a refusal code.
``outcome``
    ``"record"`` or ``"refusal"``.
``record``, ``assessment_digest``
    ``AssessmentRecord.as_document()`` as returned, and the record's own digest
    (which that document deliberately does not contain). Only for a record.
``refusal``
    ``{"code": error.code, "text": str(error)}``, the text whole and with its
    ``[code]`` prefix. Only for a refusal.
``elements``
    ``element_key`` → name, class, storey, GlobalId and model, read from the
    canonical element inventory for display only.

**This is not a Framework interface.** It lives outside ``epc_control_tower``, is
not a ``Checker``, ``GroupingPolicy`` or ``Exporter``, is absent from
``default_registry``, and no ``epc-ct`` subcommand reaches it. It is not a public
machine contract either; the Doctor prototype is its only consumer.

**Transport** is a function call, or ``python -m internal.doctor_adapter`` printing
UTF-8 JSON on standard output: ``--index`` for ``[{"name", "mode"}]``, or a
scenario name for its envelope. Nothing is written inside this checkout: the
validation run the facts come from is directed at a scratch directory outside it,
and removed afterwards.

**Network.** The adapter adds no network egress of its own: it opens no socket,
runs no server, and imports no network module. Neither does the validation it
calls, since ``epc_control_tower.ids_schema`` made IfcTester resolve the three
W3C schemas ``ids.xsd`` imports by URL from the copies ``xmlschema`` installs.
It used to: loading the schema attempted those three fetches, exactly as
``epc-ct check`` and ``epc-ct run`` did, and ``xmlschema`` reached the right
copies only afterwards, by falling back when the fetch failed. The adapter's
tests still pin that blocking every remote connection changes no byte of any
envelope; ``tests/test_validation_path_egress.py`` now pins the stronger claim
that nothing is attempted.
"""

from __future__ import annotations

from .envelope import MODES, build_envelope, display_elements, envelope_bytes
from .real import real_envelope
from .scenarios import SCENARIOS, scenario_envelope, scenario_index

__all__ = [
    "MODES",
    "SCENARIOS",
    "build_envelope",
    "display_elements",
    "envelope_bytes",
    "real_envelope",
    "scenario_envelope",
    "scenario_index",
]
