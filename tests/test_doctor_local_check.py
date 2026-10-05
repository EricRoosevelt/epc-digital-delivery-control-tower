"""The local check: a user's own IFC files, checked in a workspace of their own.

What the measurement before this entry found, and what these tests keep true
(the table is in the pull request that added it; AGENTS.md rule 6):

*Nothing in the checkout moves.* Dropping a model into ``projects/`` and running
re-keyed every published canonical finding (0 of 121 survived); a workspace
that names the checkout's ``rules/`` rewrites ``ids/`` in the checkout; ``run``
keeps a coverage record in the user's state directory without saying so. A
local check copies the rule set into its own directory, writes only the JSON
document the Doctor reads, and keeps its coverage record beside it. The audited
run below counts every write the check attempts, and the counterfactual shows
the same audit catching the un-isolated route.

*The scope is said before the run, and it is the run's.* The plan names the
rule set (identifier, version, digest), the requirements, the models with their
declared discipline and content digest, and the logical date; the finished
run's own identity says the same.

*A refusal names every reason.* IFC2x3 is refused before anything runs, with
what to do instead, and the pipeline would refuse it for the same reason.

*Finding nothing to check is not a pass.* A model with no object a rule applies
to has model-level N/A findings and no PASS.

*A second model is a second request.* No code changes between them; each check
has its own directory, named from what it checked, and the same request gives
the same bytes.
"""

from __future__ import annotations

import ast
import functools
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from epc_control_tower.determinism import sha256_file
from epc_control_tower.rules import load_ruleset
from helpers import PROJECT_ROOT
from internal.doctor_adapter import local_check, workspace_envelope
from internal.doctor_adapter.local_check import (
    CHECKS_DIR_VARIABLE,
    REFUSAL_CODES,
    LocalChecks,
    resolve_checks_root,
)
from internal.doctor_adapter.workspace import RUN_DOCUMENT
from test_doctor_preview import serve

RAW = PROJECT_ROOT / "data" / "raw"
HVAC = RAW / "Building-Hvac.ifc"
ARCHITECTURE = RAW / "Building-Architecture.ifc"
RULES = PROJECT_ROOT / "rules"
PV_RECORD = PROJECT_ROOT / "docs" / "contracts" / "ruleset-product-validation.json"

#: The smallest IFC2x3 file the pipeline will open: written here, not shipped.
IFC2X3 = b"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView_V2.0]'),'2;1');
FILE_NAME('x3.ifc','2026-01-01T00:00:00',(''),(''),'','','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'m',$,$,$,$,$);
#2=IFCORGANIZATION($,'m',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'1','m','m');
#5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,$,$,0);
#6=IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);
#7=IFCUNITASSIGNMENT((#6));
#8=IFCPROJECT('0YvctVUKr0kugbFTf53O9L',#5,'x3',$,$,$,$,$,#7);
#9=IFCWALL('1YvctVUKr0kugbFTf53O9L',#5,'w',$,$,$,$,$);
#10=IFCRELAGGREGATES('2YvctVUKr0kugbFTf53O9L',#5,$,$,#8,(#11));
#11=IFCBUILDING('3YvctVUKr0kugbFTf53O9L',#5,'b',$,$,$,$,$,.ELEMENT.,$,$,$);
#12=IFCRELCONTAINEDINSPATIALSTRUCTURE('4YvctVUKr0kugbFTf53O9L',#5,$,$,(#9),#11);
ENDSEC;
END-ISO-10303-21;
"""


def _scratch(prefix: str) -> Path:
    """A directory outside the checkout, removed when the process ends.

    Made with ``mkdir`` rather than tempfile's helpers; see ``tests/helpers.py``.
    """

    import atexit

    path = Path(tempfile.gettempdir()) / f"epc-ct-{prefix}-{uuid.uuid4().hex}"
    path.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, path, True)
    return path


def _stage(checks: LocalChecks, data: bytes | Path, filename: str | None = None) -> dict:
    if isinstance(data, Path):
        filename = filename or data.name
        data = data.read_bytes()
    return checks.stage_model(filename, io.BytesIO(data), len(data))


def _request(ruleset: str, *models: tuple[dict, str]) -> dict:
    return {
        "ruleset": ruleset,
        "models": [
            {
                "upload": staged["model"]["upload"],
                "filename": staged["model"]["filename"],
                "discipline": discipline,
            }
            for staged, discipline in models
        ],
    }


def _codes(answer: dict) -> list[str]:
    assert answer["outcome"] == "refusal", answer
    return [reason["code"] for reason in answer["refusal"]["reasons"]]


@functools.cache
def _session():
    """The checks the tests read, each run once per session."""

    checks = LocalChecks(_scratch("local-checks"))
    hvac = _stage(checks, HVAC)
    architecture = _stage(checks, ARCHITECTURE)
    hvac_request = _request("product-validation", (hvac, "HVAC"))
    plan = checks.plan(hvac_request)
    first = checks.run(hvac_request)
    first_bytes = {
        name: (checks.root / "checks" / first["check"]["check_id"] / name).read_bytes()
        for name in (RUN_DOCUMENT, local_check.CHECK_RECORD)
    }
    again = checks.run(hvac_request)
    nothing = checks.run(_request("product-validation", (architecture, "Architecture")))
    return checks, plan, first, first_bytes, again, nothing


class ScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks, cls.plan, cls.finished, _bytes, _again, _nothing = _session()
        cls.check_id = cls.finished["check"]["check_id"]
        cls.envelope = cls.checks.envelope(cls.check_id)

    def test_only_product_validation_1_0_is_offered(self):
        offered = self.checks.describe()["rulesets"]
        ruleset = load_ruleset(RULES / "product-validation")
        self.assertEqual(
            [
                (item["name"], item["id"], item["version"], item["normalized_digest"])
                for item in offered
            ],
            [("product-validation", "product-validation", "1.0", ruleset.normalized_digest)],
        )
        self.assertEqual(ruleset.version, "1.0")
        self.assertEqual(offered[0]["requirements"], self.plan["plan"]["requirements"])

    def test_the_plan_is_what_the_run_then_says_it_checked(self):
        self.assertEqual(self.plan["outcome"], "plan")
        plan, run = self.plan["plan"], self.envelope["run"]
        self.assertEqual(plan["check_id"], self.check_id)
        self.assertEqual(
            {key: plan["ruleset"][key] for key in ("id", "version", "normalized_digest")},
            run["ruleset"],
        )
        self.assertEqual(plan["as_of"], run["as_of"])
        self.assertEqual(
            [
                {
                    key: model[key]
                    for key in ("model_key", "filename", "discipline", "content_sha256")
                }
                for model in plan["models"]
            ],
            [
                {
                    key: model[key]
                    for key in ("model_key", "filename", "discipline", "content_sha256")
                }
                for model in run["models"]
            ],
        )
        self.assertEqual(
            plan["requirements"],
            {
                key: {k: v for k, v in requirement.items() if k != "semantics_digest"}
                for key, requirement in self.envelope["requirements"].items()
            },
        )
        self.assertEqual(Path(plan["location"]), self.checks.root / "checks" / self.check_id)

    def test_the_scope_carries_no_rule_author_metadata(self):
        for requirement in self.plan["plan"]["requirements"].values():
            self.assertFalse({"owner_role", "severity", "priority", "stage"} & set(requirement))

    def test_the_copied_rule_set_is_the_recorded_one(self):
        record = json.loads(PV_RECORD.read_text(encoding="utf-8"))
        [version] = [v for v in record["versions"] if v["version"] == "1.0"]
        self.assertEqual(
            self.envelope["run"]["ruleset"]["normalized_digest"], version["normalized_digest"]
        )
        self.assertEqual(sorted(self.envelope["requirements"]), version["requirement_keys"])
        self.assertEqual(
            self.plan["plan"]["ruleset"]["definitions_digest"],
            version["rule_definitions_digest"],
        )

    def test_the_result_is_the_workspace_entrys_envelope(self):
        self.assertEqual(
            self.envelope, workspace_envelope(self.checks.root / "checks" / self.check_id)
        )
        self.assertEqual(self.envelope["mode"], "workspace")
        self.assertEqual(self.envelope["outcome"], "validation")

    def test_the_finished_check_is_listed_with_its_scope_and_location(self):
        listed = {item["check_id"]: item for item in self.checks.checks()}
        self.assertIn(self.check_id, listed)
        entry = listed[self.check_id]
        self.assertEqual(Path(entry["location"]), self.checks.root / "checks" / self.check_id)
        self.assertEqual(entry["scope"]["ruleset"], self.plan["plan"]["ruleset"])
        self.assertEqual(entry["scope"]["models"], self.plan["plan"]["models"])


class NothingApplicableTests(unittest.TestCase):
    def test_no_applicable_object_is_not_a_pass(self):
        checks, _plan, _first, _bytes, _again, nothing = _session()
        envelope = checks.envelope(nothing["check"]["check_id"])
        statuses = {finding["status"] for finding in envelope["findings"]}
        self.assertEqual(statuses, {"N/A"})
        self.assertTrue(all(finding["element_key"] == "" for finding in envelope["findings"]))
        self.assertEqual(
            len(envelope["findings"]),
            len(envelope["requirements"]) * len(envelope["run"]["models"]),
        )


class OfferTests(unittest.TestCase):
    """The local check offers ``product-validation`` 1.0 and nothing else.

    The product decision of 2026-10-03 (docs/product/2026-10-03-pm-local-ifc-
    scope-decision.md, §1): the shipped ``epc-delivery`` rule set, run on a real
    MEP model, gave 444 FAIL, 222 PASS and 8 N/A, most of them from the sample
    project's own conventions. It stays in the checkout and in the bundled
    example path; this entry does not offer it.
    """

    @classmethod
    def setUpClass(cls):
        cls.checks = LocalChecks(_scratch("local-offer"))
        cls.hvac = _stage(cls.checks, HVAC)

    def test_the_shipped_rule_set_is_refused_and_stays_where_it_is(self):
        answer = self.checks.plan(_request("epc-delivery", (self.hvac, "HVAC")))
        self.assertEqual(_codes(answer), ["unknown-ruleset"])
        self.assertIn("product-validation 1.0", answer["refusal"]["text"])
        self.assertTrue((RULES / "epc-delivery" / "ruleset.toml").is_file())

    def test_another_version_of_the_offered_rule_set_is_not_offered(self):
        checkout = _scratch("local-offer-checkout")
        shutil.copyfile(PROJECT_ROOT / "control-tower.toml", checkout / "control-tower.toml")
        rules = checkout / "rules" / "product-validation"
        shutil.copytree(RULES / "product-validation", rules)
        marker = rules / "ruleset.toml"
        marker.write_bytes(
            marker.read_bytes().replace(b'version = "1.0"', b'version = "1.1"')
        )
        self.assertEqual(load_ruleset(rules).version, "1.1")
        checks = LocalChecks(_scratch("local-offer-other"), repository_root=checkout)
        self.assertEqual(checks.describe()["rulesets"], [])
        staged = _stage(checks, HVAC)
        answer = checks.plan(_request("product-validation", (staged, "HVAC")))
        self.assertEqual(_codes(answer), ["unknown-ruleset"])


#: An air terminal whose predefined type fails PV-001, and which has no shape.
NO_SHAPE_GLOBAL_ID = "23uPJWDfXEcwHH3kdFgV9c"


class NoGeometryTests(unittest.TestCase):
    """A failing element with no geometry keeps its result.

    IFC lets an element have no representation. Before, the pipeline computed a
    bounding box for every failing element whichever exporters ran, and such an
    element ended the check with ``RuntimeError: Representation is NULL`` and no
    result at all. The check writes only the JSON document, which carries no
    geometry, so it now asks for none.
    """

    @classmethod
    def setUpClass(cls):
        import ifcopenshell

        source = ifcopenshell.open(str(HVAC))
        source.by_guid(NO_SHAPE_GLOBAL_ID).Representation = None
        cls.model = _scratch("local-no-shape") / "no-shape.ifc"
        source.write(str(cls.model))
        cls.checks = LocalChecks(_scratch("local-no-shape-checks"))
        staged = _stage(cls.checks, cls.model)
        cls.answer = cls.checks.run(_request("product-validation", (staged, "HVAC")))

    def test_the_check_finishes_and_names_the_element(self):
        self.assertEqual(self.answer["outcome"], "finished")
        envelope = self.checks.envelope(self.answer["check"]["check_id"])
        key = f"local.no-shape::{NO_SHAPE_GLOBAL_ID}"
        [finding] = [f for f in envelope["findings"] if f["element_key"] == key]
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(envelope["elements"][key]["global_id"], NO_SHAPE_GLOBAL_ID)
        self.assertEqual(
            sorted(f["status"] for f in envelope["findings"]), ["FAIL", "FAIL"]
        )

    def test_the_scope_says_no_geometry_is_computed(self):
        self.assertIs(self.answer["check"]["scope"]["geometry"], False)

    def test_without_it_the_same_workspace_fails_on_geometry_nothing_reads(self):
        from epc_control_tower.config import load_run_config
        from epc_control_tower.pipeline import build_bundle

        workspace = _scratch("local-no-shape-counterfactual") / "check"
        shutil.copytree(
            self.checks.root / "checks" / self.answer["check"]["check_id"], workspace
        )
        with self.assertRaisesRegex(RuntimeError, "Representation is NULL"):
            build_bundle(load_run_config(workspace))


class PlaceTests(unittest.TestCase):
    """Where the checks are kept, as a file manager will find them."""

    def test_nothing_is_on_disk_until_a_file_is_chosen(self):
        checks = LocalChecks(_scratch("local-place") / "not-yet")
        described = checks.describe()
        self.assertIsNone(described["checks_dir_on_disk"])
        self.assertEqual(described["kept"], {"uploads": 0, "checks": 0})
        self.assertFalse(checks.root.exists())

    def test_once_kept_it_is_where_the_system_put_it(self):
        checks = LocalChecks(_scratch("local-place-kept"))
        _stage(checks, HVAC)
        described = checks.describe()
        self.assertEqual(described["checks_dir_on_disk"], os.path.realpath(checks.root))
        self.assertEqual(described["kept"], {"uploads": 1, "checks": 0})

    def test_a_redirected_directory_is_reported_where_it_really_is(self):
        # A server started inside a packaged (MSIX) app writes under
        # %LOCALAPPDATA% into the package's own folder instead; Python sees
        # the given path, and only realpath tells where the files really are.
        checks = LocalChecks(_scratch("local-place-redirected"))
        _stage(checks, HVAC)
        elsewhere = str(Path(tempfile.gettempdir()) / "Packages" / "app" / "LocalCache")
        with mock.patch.object(local_check.os.path, "realpath", return_value=elsewhere):
            described = checks.describe()
        self.assertEqual(described["checks_dir"], str(checks.root))
        self.assertEqual(described["checks_dir_on_disk"], elsewhere)


class SecondModelTests(unittest.TestCase):
    def test_each_model_is_its_own_check(self):
        checks, _plan, first, _bytes, _again, nothing = _session()
        self.assertNotEqual(first["check"]["check_id"], nothing["check"]["check_id"])
        listed = {item["check_id"] for item in checks.checks()}
        self.assertLessEqual({first["check"]["check_id"], nothing["check"]["check_id"]}, listed)
        for answer, source in ((first, HVAC), (nothing, ARCHITECTURE)):
            [model] = checks.envelope(answer["check"]["check_id"])["run"]["models"]
            self.assertEqual(model["content_sha256"], sha256_file(source))
            self.assertEqual(model["filename"], source.name)

    def test_the_same_request_gives_the_same_check_and_the_same_bytes(self):
        checks, _plan, first, first_bytes, again, _nothing = _session()
        self.assertEqual(again["check"]["check_id"], first["check"]["check_id"])
        directory = checks.root / "checks" / again["check"]["check_id"]
        for name, data in first_bytes.items():
            with self.subTest(file=name):
                self.assertEqual((directory / name).read_bytes(), data)

    def test_two_checks_of_one_model_name_can_be_compared(self):
        checks, _plan, first, _bytes, _again, _nothing = _session()
        envelope = checks.envelope(first["check"]["check_id"], first["check"]["check_id"])
        self.assertEqual(envelope["outcome"], "validation")
        self.assertIn("comparison", envelope)


class RefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks = LocalChecks(_scratch("local-refusals"), max_model_bytes=1 << 22)
        cls.hvac = _stage(cls.checks, HVAC)

    def _nothing_was_kept(self):
        checks = self.checks.root / "checks"
        self.assertEqual(sorted(checks.iterdir()) if checks.exists() else [], [])
        uploads = self.checks.root / "uploads"
        self.assertEqual(
            sorted(p.name for p in uploads.iterdir() if p.name.startswith(".")), []
        )

    def test_ifc2x3_is_refused_before_anything_runs_with_what_to_do(self):
        staged = _stage(self.checks, IFC2X3, "old-export.ifc")
        self.assertEqual(staged["model"]["ifc_schema"], "IFC2X3")
        request = _request("product-validation", (staged, "Architecture"))
        for answer in (self.checks.plan(request), self.checks.run(request)):
            self.assertEqual(_codes(answer), ["unsupported-schema"])
            self.assertIn("IFC4", answer["refusal"]["text"])
        self._nothing_was_kept()

    def test_the_pipeline_refuses_ifc2x3_for_the_same_reason(self):
        from epc_control_tower.config import load_run_config
        from epc_control_tower.pipeline import build_bundle

        workspace = _scratch("local-x3-pipeline")
        shutil.copytree(
            RULES / "product-validation", workspace / "rules" / "product-validation"
        )
        project = workspace / "projects" / "local"
        project.mkdir(parents=True)
        (project / "x3.ifc").write_bytes(IFC2X3)
        (project / "project.toml").write_bytes(
            b'[project]\nproject_id = "local"\nname = "x"\n\n[[models]]\nmodel_id = "x3"\n'
            b'discipline = "Architecture"\nfilename = "x3.ifc"\n\n'
            b'[[milestones]]\nstage = "Coordination"\ndue = ""\n'
        )
        (workspace / "control-tower.toml").write_bytes(
            b'[run]\nruleset_path = "rules/product-validation"\nexporters = ["json"]\n'
        )
        with self.assertRaisesRegex(
            ValueError, r"does not support IFC schema\(s\) \['IFC2X3'\]"
        ):
            build_bundle(load_run_config(workspace))

    def test_a_file_that_is_not_an_ifc_is_refused_and_not_kept(self):
        answer = _stage(self.checks, b"PK\x03\x04 a zip, not a model", "model.ifc")
        self.assertEqual(_codes(answer), ["not-an-ifc"])
        self.assertEqual(
            list((self.checks.root / "uploads").glob("*.ifc")),
            [self.checks.root / "uploads" / f"{self.hvac['model']['upload']}.ifc"],
        )
        self._nothing_was_kept()

    def test_a_name_that_could_leave_the_check_directory_is_refused(self):
        for name in (
            "../model.ifc",
            "a/model.ifc",
            "a\\model.ifc",
            "model.txt",
            ".ifc",
            "C:model.ifc",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    _codes(_stage(self.checks, HVAC, name)), ["model-name-invalid"]
                )

    def test_a_file_too_large_is_refused_unread(self):
        stream = io.BytesIO(b"x" * 16)
        answer = self.checks.stage_model("big.ifc", stream, (1 << 22) + 1)
        self.assertEqual(_codes(answer), ["model-too-large"])
        self.assertEqual(stream.tell(), 0)

    def test_a_file_that_arrives_short_is_refused_and_not_kept(self):
        data = HVAC.read_bytes()
        answer = self.checks.stage_model("short.ifc", io.BytesIO(data[:1000]), len(data))
        self.assertEqual(_codes(answer), ["model-incomplete"])
        self._nothing_was_kept()

    def test_every_reason_is_named_and_the_first_is_the_code(self):
        request = {
            "ruleset": "no-such-rules",
            "models": [
                {"upload": "0" * 64, "filename": "gone.ifc", "discipline": "HVAC"},
                {
                    "upload": self.hvac["model"]["upload"],
                    "filename": "Building-Hvac.ifc",
                    "discipline": "",
                },
                {
                    "upload": self.hvac["model"]["upload"],
                    "filename": "other.ifc",
                    "discipline": "Plumbing-ish",
                },
            ],
        }
        answer = self.checks.plan(request)
        codes = _codes(answer)
        self.assertEqual(
            codes,
            sorted(
                [
                    "unknown-ruleset",
                    "unknown-model",
                    "discipline-not-declared",
                    "unknown-discipline",
                    "duplicate-model",
                ],
                key=REFUSAL_CODES.index,
            ),
        )
        self.assertEqual(answer["refusal"]["code"], codes[0])
        # A reason about one file names it; one about the request names none.
        self.assertEqual(
            [reason.get("filename") for reason in answer["refusal"]["reasons"]],
            ["gone.ifc", "other.ifc", None, "Building-Hvac.ifc", "other.ifc"],
        )
        self._nothing_was_kept()

    def test_no_model_is_a_refusal(self):
        self.assertEqual(
            _codes(self.checks.plan({"ruleset": "product-validation", "models": []})),
            ["no-model"],
        )

    def test_a_second_check_while_one_runs_is_refused(self):
        request = _request("product-validation", (self.hvac, "HVAC"))
        with self.checks._running:
            self.assertEqual(_codes(self.checks.run(request)), ["busy"])

    def test_a_malformed_request_is_not_a_refusal(self):
        for request in (
            None,
            [],
            {"ruleset": 1, "models": []},
            {"ruleset": "x", "models": [3]},
        ):
            with self.subTest(request=request), self.assertRaises(local_check.MalformedRequest):
                self.checks.plan(request)

    def test_a_check_that_fails_leaves_nothing_behind(self):
        def broken(config, **_):
            (config.repository_root / "half-written").write_bytes(b"x")
            raise RuntimeError("Representation is NULL")

        request = _request("product-validation", (self.hvac, "HVAC"))
        with mock.patch.object(local_check, "execute", broken):
            with self.assertRaisesRegex(RuntimeError, "Representation is NULL"):
                self.checks.run(request)
        self._nothing_was_kept()
        self.assertEqual(self.checks.checks(), [])


class RootTests(unittest.TestCase):
    def test_the_checks_directory_is_never_inside_a_checkout(self):
        for inside in (PROJECT_ROOT, PROJECT_ROOT / "reports" / "checks"):
            with self.subTest(path=inside), self.assertRaisesRegex(ValueError, "outside"):
                resolve_checks_root(PROJECT_ROOT, environ={CHECKS_DIR_VARIABLE: str(inside)})
        with self.assertRaisesRegex(ValueError, "outside"):
            LocalChecks(PROJECT_ROOT / "tests" / "checks")

    def test_it_is_the_named_directory_or_the_users_state_directory(self):
        named = _scratch("local-named")
        self.assertEqual(
            resolve_checks_root(PROJECT_ROOT, environ={CHECKS_DIR_VARIABLE: str(named)}), named
        )
        state = _scratch("local-state")
        variable = "LOCALAPPDATA" if os.name == "nt" else "XDG_STATE_HOME"
        self.assertEqual(
            resolve_checks_root(PROJECT_ROOT, environ={variable: str(state)}),
            state / "epc-control-tower" / "doctor-checks",
        )

    def test_the_module_reads_no_clock(self):
        tree = ast.parse(Path(local_check.__file__).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
            elif isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
        self.assertFalse(imported & {"time", "datetime", "socket", "urllib", "http"})


#: Runs one local check — offering the rule sets, staging a public model,
#: planning, running and reading the result — under an audit hook that records
#: every write the process attempts, and refuses those inside the checkout. Then,
#: the counterfactual: the same model run the way it could be done without this
#: entry — a workspace naming the checkout's rule set, and ``epc-ct run`` with
#: its default coverage location — under the same hook.
_AUDITED = r"""
import io, json, os, sys
checkout = os.path.normcase(os.path.abspath(sys.argv[1]))
base = os.path.normcase(os.path.abspath(sys.argv[2]))
checks_root = os.path.join(base, "checks-root")
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
MODIFIED = {
    "os.remove": (0,), "os.rmdir": (0,), "os.mkdir": (0,), "os.rename": (0, 1),
    "os.replace": (0, 1), "os.truncate": (0,), "shutil.copyfile": (1,),
    "_winapi.CopyFile2": (1,), "shutil.rmtree": (0,), "shutil.copytree": (1,),
}
attempts = []

def _path(value):
    return os.path.normcase(os.path.abspath(os.fsdecode(os.fspath(value))))

def _under(path, root):
    return path == root or path.startswith(root + os.sep)

def note(path):
    attempts.append(path)
    if _under(path, checkout):
        raise PermissionError(f"write inside the checkout refused by the audit: {path}")

def hook(event, args):
    if event == "open":
        target, mode, flags = args[0], args[1], args[2]
        writing = (isinstance(flags, int) and flags & WRITE_FLAGS) or (
            isinstance(mode, str) and any(c in mode for c in "wax+"))
        if writing and isinstance(target, (str, bytes, os.PathLike)):
            note(_path(target))
    elif event in MODIFIED:
        for index in MODIFIED[event]:
            value = args[index] if index < len(args) else None
            if isinstance(value, (str, bytes, os.PathLike)):
                note(_path(value))

sys.path.insert(0, sys.argv[1])
os.environ.pop("EPC_CT_COVERAGE_DIR", None)
home = os.path.join(base, "home")
os.environ["LOCALAPPDATA"] = home
os.environ["XDG_STATE_HOME"] = home
from pathlib import Path
from internal.doctor_adapter.local_check import LocalChecks
from epc_control_tower.cli import main as epc_ct
model = Path(sys.argv[1]) / "data" / "raw" / "Building-Hvac.ifc"
data = model.read_bytes()
os.makedirs(checks_root)
sys.addaudithook(hook)

checks = LocalChecks(Path(checks_root))
checks.describe()
staged = checks.stage_model(model.name, io.BytesIO(data), len(data))["model"]
request = {"ruleset": "product-validation",
           "models": [{"upload": staged["upload"], "filename": model.name,
                       "discipline": "HVAC"}]}
checks.plan(request)
finished = checks.run(request)
checks.checks()
checks.envelope(finished["check"]["check_id"])
isolated, attempts[:] = list(attempts), []

naive = os.path.join(base, "naive")
project = os.path.join(naive, "projects", "local")
os.makedirs(project)
with open(os.path.join(project, model.name), "wb") as out:
    out.write(data)
with open(os.path.join(project, "project.toml"), "w", encoding="utf-8") as out:
    out.write('[project]\nproject_id = "local"\nname = "x"\n\n[[models]]\nmodel_id = "hvac"\n'
              f'discipline = "HVAC"\nfilename = "{model.name}"\n\n'
              '[[milestones]]\nstage = "Coordination"\ndue = ""\n')
rules = (Path(sys.argv[1]) / "rules" / "product-validation").as_posix()
with open(os.path.join(naive, "control-tower.toml"), "w", encoding="utf-8") as out:
    out.write(f'[run]\nruleset_path = "{rules}"\nexporters = ["json"]\n')
attempts[:] = []
try:
    code = epc_ct(["--repository-root", naive, "run"])
except PermissionError:
    code = "refused by the audit"
in_checkout = [p for p in attempts if _under(p, checkout)]
attempts[:] = []
copy = os.path.join(naive, "rules", "product-validation")
import shutil
shutil.copytree(rules, copy)
with open(os.path.join(naive, "control-tower.toml"), "w", encoding="utf-8") as out:
    out.write('[run]\nruleset_path = "rules/product-validation"\nexporters = ["json"]\n')
attempts[:] = []
code_copied = epc_ct(["--repository-root", naive, "run"])
coverage_elsewhere = [p for p in attempts if _under(p, os.path.normcase(home))]
json.dump({
    "checks_root": os.path.normcase(checks_root),
    "isolated": isolated,
    "naive_exit": code,
    "naive_in_checkout": in_checkout,
    "copied_exit": code_copied,
    "copied_coverage_in_state_dir": coverage_elsewhere,
}, sys.stdout)
"""


@functools.cache
def _audit() -> dict:
    base = _scratch("local-audit")
    completed = subprocess.run(
        [sys.executable, "-B", "-c", _AUDITED, str(PROJECT_ROOT), str(base)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return json.loads(completed.stdout.decode("utf-8").splitlines()[-1])


class IsolationTests(unittest.TestCase):
    """Rule 6, pinned: what this entry writes, beside what doing nothing writes."""

    def test_a_check_writes_only_under_its_checks_directory(self):
        audit = _audit()
        self.assertTrue(audit["isolated"])
        outside = [
            path
            for path in audit["isolated"]
            if not (
                path == audit["checks_root"] or path.startswith(audit["checks_root"] + os.sep)
            )
        ]
        self.assertEqual(outside, [])

    def test_without_the_copy_the_checkouts_rule_set_would_be_rewritten(self):
        audit = _audit()
        self.assertNotEqual(audit["naive_exit"], 0)
        # Compiling the rule set writes beside it: the checkout's own ``ids/``.
        compiled = os.path.normcase(str(PROJECT_ROOT / "ids"))
        self.assertTrue(
            any(path.startswith(compiled + os.sep) for path in audit["naive_in_checkout"]),
            audit["naive_in_checkout"],
        )

    def test_without_a_named_place_the_coverage_record_goes_to_the_state_directory(self):
        audit = _audit()
        self.assertEqual(audit["copied_exit"], 0)
        self.assertTrue(
            any("coverage" in path for path in audit["copied_coverage_in_state_dir"]),
            audit["copied_coverage_in_state_dir"],
        )


class _Server:
    def __init__(self, checks: LocalChecks):
        def no_source():
            raise serve.SourceUnavailable("not used here")

        self.httpd = ThreadingHTTPServer(
            ("127.0.0.1", 0), serve.make_handler(no_source, lambda: checks)
        )
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def __exit__(self, *exception):
        self.httpd.shutdown()
        self.httpd.server_close()


def _call(url, data=None, headers=None, method=None):
    request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read() or b"null")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"null")


class ServerTests(unittest.TestCase):
    def test_a_check_is_made_and_opened_over_http(self):
        checks = LocalChecks(_scratch("local-http"))
        with _Server(checks) as base:
            status, described = _call(f"{base}/api/local")
            self.assertEqual(status, 200)
            self.assertEqual(Path(described["checks_dir"]), checks.root)
            status, staged = _call(
                f"{base}/api/local/models?filename=Building-Hvac.ifc",
                HVAC.read_bytes(),
                {"Content-Type": "application/octet-stream"},
            )
            self.assertEqual((status, staged["outcome"]), (200, "staged"))
            body = json.dumps(_request("product-validation", (staged, "HVAC"))).encode()
            json_type = {"Content-Type": "application/json"}
            status, plan = _call(f"{base}/api/local/plan", body, json_type)
            self.assertEqual((status, plan["outcome"]), (200, "plan"))
            status, finished = _call(f"{base}/api/local/checks", body, json_type)
            self.assertEqual((status, finished["outcome"]), (200, "finished"))
            check_id = finished["check"]["check_id"]
            status, listed = _call(f"{base}/api/local/checks")
            self.assertEqual([item["check_id"] for item in listed["checks"]], [check_id])
            status, envelope = _call(f"{base}/api/local/envelope?run={check_id}")
            self.assertEqual(status, 200)
            self.assertEqual(envelope, workspace_envelope(checks.root / "checks" / check_id))
            status, refused = _call(
                f"{base}/api/local/models?filename=x3.ifc",
                IFC2X3,
                {"Content-Type": "application/octet-stream"},
            )
            body = json.dumps(_request("product-validation", (refused, "HVAC"))).encode()
            status, answer = _call(f"{base}/api/local/checks", body, json_type)
            self.assertEqual((status, _codes(answer)), (200, ["unsupported-schema"]))
            status, missing = _call(f"{base}/api/local/envelope?run={'0' * 16}")
            self.assertEqual(status, 404)

    def test_only_this_machines_own_pages_may_ask(self):
        checks = LocalChecks(_scratch("local-guard"))
        with _Server(checks) as base:
            for headers in ({"Host": "attacker.example"}, {"Host": "127.0.0.1.nip.io:80"}):
                with self.subTest(headers=headers):
                    self.assertEqual(_call(f"{base}/api/local", headers=headers)[0], 403)
            json_body = json.dumps({"ruleset": "product-validation", "models": []}).encode()
            status, _ = _call(
                f"{base}/api/local/plan",
                json_body,
                {"Content-Type": "application/json", "Origin": "http://attacker.example"},
            )
            self.assertEqual(status, 403)
            # A form post needs no preflight, so it is not accepted at all.
            status, _ = _call(
                f"{base}/api/local/plan", json_body, {"Content-Type": "text/plain"}
            )
            self.assertEqual(status, 415)
            status, _ = _call(
                f"{base}/api/local/plan",
                json_body,
                {"Content-Type": "application/json", "Origin": base},
            )
            self.assertEqual(status, 200)
        self.assertFalse((checks.root / "checks").exists())

    def test_the_server_listens_on_loopback_only(self):
        tree = ast.parse((PROJECT_ROOT / "doctor" / "serve.py").read_text(encoding="utf-8"))
        hosts = {
            node.args[0].elts[0].value
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and getattr(node.func, "id", "") == "ThreadingHTTPServer"
            and isinstance(node.args[0], ast.Tuple)
        }
        self.assertEqual(hosts, {"127.0.0.1"})


if __name__ == "__main__":
    unittest.main()
