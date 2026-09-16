"""The internal Doctor adapter hands over what the Framework produced, and no more.

One claim is under test: for exactly four scenarios, the adapter returns what the
Framework already produced, unchanged, inside one fixed envelope, and adds no
judgement of its own. Every test below compares the adapter against a result this
module builds **independently**, by calling the Framework the way the existing
assessment tests do, so an adapter that re-derived, reordered, trimmed or
re-labelled anything would disagree with it.

The adapter's output is read the way a consumer reads it — as the bytes the
command line prints, in a separate process — because an envelope that is right in
memory and wrong on the wire is wrong. A second process runs every scenario under
an audit hook that **refuses every remote connection**, and records what it opened
for writing and whether it opened the frozen inventory — so "writes nothing in this
checkout" and "never reads the frozen inventory" are measurements rather than
readings of the source.

**What is claimed about the network is deliberately narrow.** The adapter adds no
egress of its own. The validation it has to call does attempt some: IfcTester's
``ids.xsd`` imports W3C schemas by URL, and ``epc-ct check`` makes the same
attempts. So the claim pinned here is the counterfactual (``AGENTS.md`` rule 6):
with every remote connection refused, every envelope is byte for byte what it is
with the network available. Asserting that no socket is ever touched would assert
something false of the production validation path, which is a separate
checkpoint's to change.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import os
import subprocess
import sys
import unittest

import assessment_fixtures as fx
from epc_control_tower.determinism import read_csv_rows
from epc_control_tower.purpose import (
    PurposeAssessmentError,
    PurposeCompositionError,
    PurposeError,
    assess_purpose,
    compose_purpose_inputs,
    load_project_overlay,
    load_purpose_pack,
    recheck_purpose,
)
from epc_control_tower.purpose.assessment.record import build_assessment_digest
from helpers import PROJECT_ROOT
from internal.doctor_adapter import (
    SCENARIOS,
    build_envelope,
    display_elements,
    envelope_bytes,
    real_envelope,
    scenario_envelope,
    scenario_index,
)

ADAPTER = PROJECT_ROOT / "internal" / "doctor_adapter"
PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"
CANONICAL_ELEMENTS = PROJECT_ROOT / "data" / "processed" / "canonical" / "elements.csv"

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)
OPENINGS = f"{fx.PACK_ID}::builders-work-openings"

RECORD_SCENARIOS = ("member-evidence", "pair-verdicts", "recheck-comparison")
REFUSAL_SCENARIOS = ("real-refusal",)


def _compact(document) -> bytes:
    """Order-preserving bytes, so a reordered key is a difference."""

    return json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class _Direct:
    """The four results, produced without the adapter."""

    @classmethod
    def build(cls):
        facts = fx.assessment_facts()
        composed = fx.fixture_composed()
        request = fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=facts)
        first = assess_purpose(
            request=request,
            composed=composed,
            facts=facts,
            determinations=fx.fixture_determinations(facts=facts),
        )
        roof = [
            subscope.ordinal
            for activity in first.activities
            if activity.activity_ref == OPENINGS
            for subscope in activity.subscopes
            if any(
                tuple(member.keys) == (fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF)
                for member in subscope.members
            )
        ]
        assert len(roof) == 1, roof
        recheck = recheck_purpose(
            prior=first,
            request=request,
            composed=composed,
            facts=facts,
            determinations=fx.fixture_superseding_determinations(facts=facts),
            succeeds=((OPENINGS, roof[0]),),
        )
        real_composed = compose_purpose_inputs(
            project_id="pcert-sample",
            overlay=load_project_overlay(PCERT_MANIFEST),
            packs=(load_purpose_pack(fx.PACK_PATH),),
            requirement_keys_by_ruleset=fx.requirement_keys_by_ruleset(),
        )
        try:
            assess_purpose(request=request, composed=real_composed, facts=facts)
        except PurposeAssessmentError as error:
            refusal = error
        else:  # pragma: no cover - the shipped policy must refuse
            raise AssertionError("pcert-sample produced a record through the real entry")
        return {
            "request": request,
            "records": {
                "member-evidence": first,
                "pair-verdicts": first,
                "recheck-comparison": recheck,
            },
            "refusal": refusal,
        }


#: Runs every scenario in one process under an audit hook that refuses every remote
#: connection, and reports what that process opened for writing inside the
#: checkout, whether it ever opened the frozen inventory, and how many remote
#: connections it refused. Envelopes are separated by NUL, which JSON text cannot
#: contain, and the report comes last.
_AUDITED_DRIVER = r"""
import io, json, os, sys
root = os.path.normcase(os.path.abspath(sys.argv[1]))
report = {"writes_in_checkout": [], "inventory_opens": [], "refused_remote": []}
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
LOOPBACK = {"localhost", "::1"}

def _remote(host):
    host = host.decode() if isinstance(host, bytes) else str(host)
    return host not in LOOPBACK and not host.startswith("127.")

#: For each event that modifies the filesystem, which arguments name what it
#: modifies, and which argument (if any) is the directory descriptor a relative
#: name is resolved against. A copy's *source* is read, never modified, and is
#: not listed. The descriptor matters on POSIX, where ``shutil.rmtree`` removes
#: entries by bare name relative to an open directory: resolving those names
#: against the working directory would place them in the checkout.
MODIFIED = {
    "os.remove": ((0, 1),),
    "os.rmdir": ((0, 1),),
    "os.mkdir": ((0, 2),),
    "os.chmod": ((0, 2),),
    "os.rename": ((0, 2), (1, 3)),
    "os.truncate": ((0, None),),
    "shutil.copyfile": ((1, None),),
    "shutil.rmtree": ((0, 1),),
}

def _path(value, dir_fd=None):
    if isinstance(value, int):
        return ""
    path = os.fsdecode(os.fspath(value))
    if isinstance(dir_fd, int) and not os.path.isabs(path):
        try:
            path = os.path.join(os.readlink(f"/proc/self/fd/{dir_fd}"), path)
        except OSError:
            # Unresolvable: count it as inside, so the test fails closed.
            return root + os.sep + f"<unresolved dir_fd {dir_fd}>" + os.sep + path
    return os.path.normcase(os.path.abspath(path))

def _inside(path):
    return path == root or path.startswith(root + os.sep)

def hook(event, args):
    if event == "open":
        path = _path(args[0])
        mode, flags = args[1], args[2]
        writing = (isinstance(flags, int) and flags & WRITE_FLAGS) or (
            isinstance(mode, str) and any(c in mode for c in "wax+")
        )
        if os.path.basename(path) == "model_inventory.csv":
            report["inventory_opens"].append(path)
        if writing and _inside(path):
            report["writes_in_checkout"].append(path)
    elif event in MODIFIED:
        for index, fd_index in MODIFIED[event]:
            value = args[index]
            dir_fd = args[fd_index] if fd_index is not None else None
            if isinstance(value, (str, bytes, os.PathLike)):
                path = _path(value, dir_fd)
                if _inside(path):
                    report["writes_in_checkout"].append(f"{event}: {path}")
    elif event in {"socket.connect", "socket.sendto"}:
        address = args[1]
        host = address[0] if isinstance(address, tuple) else address
        if _remote(host):
            report["refused_remote"].append(f"{event}: {address!r}")
            raise OSError(f"remote connection refused by the audit hook: {address!r}")
    elif event == "socket.getaddrinfo" and args[0] is not None and _remote(args[0]):
        report["refused_remote"].append(f"{event}: {args[0]!r}")
        raise OSError(f"remote name lookup refused by the audit hook: {args[0]!r}")

sys.addaudithook(hook)
sys.path.insert(0, sys.argv[1])
from internal.doctor_adapter.__main__ import main
out = io.BytesIO()
for name in sys.argv[2:]:
    code = main([name], out)
    assert code == 0, code
    out.write(b"\0")
out.write(json.dumps(report).encode("utf-8"))
sys.stdout.buffer.write(out.getvalue())
"""


def _run(arguments) -> bytes:
    completed = subprocess.run(
        [sys.executable, "-B", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


class _AdapterCase(unittest.TestCase):
    """Two independent processes, plus the in-process envelopes, built once."""

    @classmethod
    def setUpClass(cls):
        cls.direct = _Direct.build()
        cls.cli = {
            name: _run(["-m", "internal.doctor_adapter", name]) for name in sorted(SCENARIOS)
        }
        names = sorted(SCENARIOS)
        *audited, report = _run(
            ["-c", _AUDITED_DRIVER, str(PROJECT_ROOT), *names]
        ).split(b"\0")
        cls.audited = dict(zip(names, audited, strict=True))
        cls.audit = json.loads(report)
        cls.in_process = {name: envelope_bytes(scenario_envelope(name)) for name in names}
        cls.envelopes = {name: json.loads(data) for name, data in cls.cli.items()}
        cls.index = _run(["-m", "internal.doctor_adapter", "--index"])


class ExactlyFourScenariosTests(_AdapterCase):
    def test_the_scenarios_are_exactly_these_four(self):
        self.assertEqual(
            sorted(SCENARIOS),
            ["member-evidence", "pair-verdicts", "real-refusal", "recheck-comparison"],
        )

    def test_an_unknown_scenario_is_not_answered_with_another_one(self):
        with self.assertRaises(KeyError):
            scenario_envelope("fixture-instead")


class RecordIsTheFrameworksDocumentTests(_AdapterCase):
    """Acceptance 1: ``record`` is ``as_document()``, byte for byte."""

    def test_the_record_is_byte_identical_to_as_document(self):
        for name in RECORD_SCENARIOS:
            direct = self.direct["records"][name]
            with self.subTest(scenario=name):
                self.assertEqual(
                    _compact(self.envelopes[name]["record"]),
                    _compact(direct.as_document()),
                )

    def test_the_digest_is_the_records_own(self):
        for name in RECORD_SCENARIOS:
            direct = self.direct["records"][name]
            envelope = self.envelopes[name]
            with self.subTest(scenario=name):
                self.assertEqual(envelope["assessment_digest"], direct.assessment_digest)
                # And the record carried is the one that digest seals.
                self.assertEqual(
                    build_assessment_digest(envelope["record"]),
                    envelope["assessment_digest"],
                )

    def test_the_envelope_carries_exactly_the_keys_its_outcome_allows(self):
        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                envelope = self.envelopes[name]
                self.assertEqual(
                    list(envelope),
                    ["mode", "outcome", "record", "assessment_digest", "elements"],
                )
                self.assertEqual(envelope["mode"], "fixture")
                self.assertEqual(envelope["outcome"], "record")
        for name in REFUSAL_SCENARIOS:
            with self.subTest(scenario=name):
                self.assertEqual(
                    list(self.envelopes[name]), ["mode", "outcome", "refusal", "elements"]
                )

    def test_both_fixture_views_are_one_record(self):
        """Scenarios 1 and 2 read the same sealed record, not two lookalikes."""

        self.assertEqual(self.cli["member-evidence"], self.cli["pair-verdicts"])


class RealRefusalTests(_AdapterCase):
    """Acceptance 2: the real entry refuses, and says so in the Framework's words."""

    def test_the_real_entry_returns_the_actual_refusal(self):
        error = self.direct["refusal"]
        envelope = self.envelopes["real-refusal"]
        self.assertEqual(envelope["mode"], "real")
        self.assertEqual(envelope["outcome"], "refusal")
        self.assertEqual(list(envelope["refusal"]), ["code", "text"])
        self.assertEqual(
            envelope["refusal"]["code"], "team-mapping-decision-basis-illustrative"
        )
        self.assertEqual(envelope["refusal"]["code"], error.code)
        self.assertEqual(envelope["refusal"]["text"], str(error))

    def test_the_text_keeps_its_code_prefix(self):
        text = self.envelopes["real-refusal"]["refusal"]["text"]
        self.assertTrue(text.startswith("[team-mapping-decision-basis-illustrative] "))

    def test_the_real_entry_is_real_whatever_it_refuses_with(self):
        """Mode is the entry called, never inferred from the project or the code."""

        request = dataclasses.replace(self.direct["request"], pack_version="0.0.0-other")
        envelope = real_envelope(request)
        self.assertEqual(envelope["mode"], "real")
        self.assertEqual(envelope["outcome"], "refusal")
        self.assertEqual(envelope["refusal"]["code"], "request-pack-version-mismatch")

    def test_the_real_entry_has_no_way_to_receive_fixture_policy(self):
        """No composed inputs, overlay, or determinations can be handed to it."""

        self.assertEqual(list(inspect.signature(real_envelope).parameters), ["request"])
        tree = ast.parse((ADAPTER / "real.py").read_text(encoding="utf-8"))
        imported = [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ] + [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        for name in imported:
            with self.subTest(module=name):
                self.assertNotIn("fixture", name)


class OnlyAnAssessmentRefusalIsARefusalTests(unittest.TestCase):
    """Acceptance 3: a crash propagates unchanged; it is never "refused"."""

    def _record(self):
        raise AssertionError("unreachable")

    def test_other_exceptions_propagate_as_themselves(self):
        for error in (
            ValueError("a bug"),
            KeyError("a bug"),
            RuntimeError("a bug"),
            PurposeCompositionError("composition-defect", "a sibling refusal class"),
            PurposeError("purpose-defect", "the shared base class"),
        ):
            def produce(error=error):
                raise error

            with self.subTest(error=type(error).__name__):
                with self.assertRaises(type(error)) as caught:
                    build_envelope("fixture", produce)
                self.assertIs(caught.exception, error)

    def test_an_assessment_refusal_becomes_the_refusal(self):
        error = PurposeAssessmentError("scope-declared-empty", "declared nothing")

        def produce():
            raise error

        envelope = build_envelope("real", produce)
        self.assertEqual(
            envelope["refusal"], {"code": "scope-declared-empty", "text": str(error)}
        )
        self.assertNotIn("record", envelope)

    def test_the_mode_is_one_of_two_and_nothing_else(self):
        with self.assertRaises(ValueError):
            build_envelope("demo", self._record)


class DisplayElementsTests(_AdapterCase):
    """Acceptance 4: canonical elements for display, and the frozen inventory never."""

    def test_exactly_the_canonical_elements(self):
        rows = read_csv_rows(CANONICAL_ELEMENTS)
        self.assertEqual(len(rows), 44)
        expected = {
            row["element_key"]: {
                "name": row["name"],
                "ifc_class": row["ifc_class"],
                "storey": row["storey"],
                "global_id": row["global_id"],
                "model_key": row["model_key"],
            }
            for row in rows
        }
        for name in sorted(SCENARIOS):
            with self.subTest(scenario=name):
                elements = self.envelopes[name]["elements"]
                self.assertEqual(len(elements), 44)
                self.assertEqual(elements, expected)
                for value in elements.values():
                    self.assertEqual(
                        list(value), ["name", "ifc_class", "storey", "global_id", "model_key"]
                    )

    def test_an_empty_storey_stays_an_empty_string(self):
        elements = display_elements()
        empty = [key for key, value in elements.items() if value["storey"] == ""]
        self.assertEqual(len(empty), 21)
        self.assertNotIn(None, [value["storey"] for value in elements.values()])
        self.assertEqual(elements[fx.HVAC_ORIGIN]["storey"], "")

    def test_no_run_opens_the_frozen_inventory(self):
        self.assertEqual(self.audit["inventory_opens"], [])
        for path in sorted(ADAPTER.rglob("*.py")):
            with self.subTest(module=path.name):
                self.assertNotIn("model_inventory", path.read_text(encoding="utf-8"))


class TheVerdictsTheUiNeedsAreTheFrameworksTests(_AdapterCase):
    """Acceptance 5: the chimney's two pairs, and what the recheck recorded."""

    def _openings(self, record):
        (activity,) = [
            item for item in record["activities"] if item["activity_ref"] == OPENINGS
        ]
        return activity

    def test_the_chimney_is_in_a_ready_pair_and_a_blocked_pair(self):
        activity = self._openings(self.envelopes["pair-verdicts"]["record"])
        verdicts = {
            tuple(member["keys"]): (subscope["verdict"], member.get("refined_from"))
            for subscope in activity["subscopes"]
            for member in subscope["members"]
            if fx.HVAC_CHIMNEY in member["keys"]
        }
        self.assertEqual(
            verdicts,
            {
                (fx.HVAC_CHIMNEY, fx.ARCHITECTURE_SLAB): ("READY", fx.HVAC_CHIMNEY),
                (fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF): ("BLOCKED", fx.HVAC_CHIMNEY),
            },
        )

    def test_the_recheck_records_a_pairing_that_stopped_being_derived(self):
        record = self.envelopes["recheck-comparison"]["record"]
        successor = record["successor"]
        self.assertEqual(successor["kind"], "recheck")
        self.assertEqual(
            successor["prior_assessment_digest"],
            self.envelopes["member-evidence"]["assessment_digest"],
        )
        (outcome,) = successor["subscopes"]
        self.assertEqual(outcome["activity_ref"], OPENINGS)
        self.assertEqual(outcome["prior_verdict"], "BLOCKED")
        self.assertEqual(
            [member["keys"] for member in outcome["prior_members"]],
            [[fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF]],
        )
        self.assertEqual(
            [item["disposition"] for item in outcome["dispositions"]],
            ["pairing-no-longer-derived"],
        )
        self.assertEqual(outcome["condition_status"], "not-comparable")


class DeterminismAndIsolationTests(_AdapterCase):
    """Acceptance 6: the same bytes every time, and nothing in the checkout moves."""

    def test_two_processes_print_the_same_bytes(self):
        for name in sorted(SCENARIOS):
            with self.subTest(scenario=name):
                self.assertEqual(self.cli[name], self.in_process[name])

    def test_the_output_is_utf8_json_with_lf_line_endings(self):
        for name, data in sorted(self.cli.items()):
            with self.subTest(scenario=name):
                self.assertNotIn(b"\r", data)
                self.assertTrue(data.endswith(b"}\n"))
                data.decode("utf-8")

    def test_nothing_is_written_inside_the_checkout(self):
        written = self.audit["writes_in_checkout"]
        self.assertEqual(written, [], "\n".join(written))

    def test_the_adapter_is_unreachable_from_the_package_and_its_cli(self):
        package = PROJECT_ROOT / "epc_control_tower"
        offenders = []
        for path in sorted(package.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                elif isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                else:
                    continue
                offenders.extend(
                    f"{path.name}: {name}"
                    for name in names
                    if name.split(".")[0] == "internal" or "doctor" in name
                )
        self.assertEqual(offenders, [])
        self.assertFalse(ADAPTER.is_relative_to(package))


class TheAdapterAddsNoNetworkEgressTests(_AdapterCase):
    """What the adapter itself does about the network, and nothing broader."""

    NETWORK_MODULES = frozenset({"socket", "urllib", "http", "requests", "httpx"})

    def test_the_adapter_imports_no_network_module(self):
        offenders = []
        for path in sorted(ADAPTER.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""] if node.level == 0 else []
                elif isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                else:
                    continue
                offenders.extend(
                    f"{path.name}: {name}"
                    for name in names
                    if name.split(".")[0] in self.NETWORK_MODULES
                )
        self.assertEqual(offenders, [])

    def test_refusing_every_remote_connection_changes_no_byte(self):
        """Rule 6's counterfactual: the envelopes do not depend on the network."""

        for name in sorted(SCENARIOS):
            with self.subTest(scenario=name):
                self.assertEqual(self.audited[name], self.cli[name])


class ScenarioIndexTests(_AdapterCase):
    """The prototype can list the scenarios and their modes without running one."""

    def test_the_index_lists_every_scenario_with_its_declared_mode(self):
        index = json.loads(self.index)
        self.assertEqual(index, scenario_index())
        self.assertEqual([entry["name"] for entry in index], sorted(SCENARIOS))
        for entry in index:
            with self.subTest(scenario=entry["name"]):
                self.assertEqual(list(entry), ["name", "mode"])

    def test_every_envelope_is_in_the_mode_its_index_entry_declares(self):
        for entry in json.loads(self.index):
            with self.subTest(scenario=entry["name"]):
                self.assertEqual(self.envelopes[entry["name"]]["mode"], entry["mode"])


if __name__ == "__main__":
    unittest.main()
