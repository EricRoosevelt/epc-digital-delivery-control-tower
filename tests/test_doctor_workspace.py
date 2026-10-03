"""The adapter's workspace entry: a finished run outside the checkout, and its comparison.

Four claims.

*Faithful* — the envelope says what the run's own document says, field for
field, and adds one thing read from somewhere else: an element's IFC ``Tag``,
from the model file, and only from the file that run read.

*The comparison is the adapter's, and it is all or nothing* — pairs both runs
evaluated carry both findings; a pair one run evaluated is listed apart; and
when the two runs did not ask the same question of the same models the whole
request is refused, with every reason named and no part of either run attached.

*Nothing else moved* — every ``fixture`` and ``real`` envelope is the bytes it
was before this entry existed, and reading a workspace writes nothing in it or
in the checkout.

*It concludes nothing* — the adapter hands over two statuses. No field says a
thing was fixed.

Every run here is a real ``epc-ct run`` over the public sample models, in a
workspace made under the system temporary directory. The "after" model is the
public HVAC sample with one type object's predefined type set, written by the
test; nothing private is involved.
"""

from __future__ import annotations

import ast
import atexit
import contextlib
import functools
import hashlib
import io
import json
import shutil
import tempfile
import types
import unittest
import uuid
from pathlib import Path

import ifcopenshell
import ifcopenshell.api

from epc_control_tower.cli import main as epc_ct
from epc_control_tower.determinism import sha256_file
from helpers import PROJECT_ROOT
from internal.doctor_adapter import (
    SCENARIOS,
    envelope_bytes,
    scenario_envelope,
    workspace_envelope,
)
from internal.doctor_adapter.__main__ import main as adapter_main
from internal.doctor_adapter.workspace import (
    REFUSAL_CODES,
    RUN_DOCUMENT,
    RUN_MANIFEST,
)
from test_doctor_preview import _get, _Server, serve

RULES = PROJECT_ROOT / "rules" / "product-validation"
RAW = PROJECT_ROOT / "data" / "raw"
ADAPTER = PROJECT_ROOT / "internal" / "doctor_adapter"

HVAC = "ws.hvac"
ARCHITECTURE = "ws.architecture"
#: The public HVAC sample's two air terminals.
CHIMNEY_COVER = "23uPJWDfXEcwHH3kdFgV9c"
FIREPLACE_CAP = "34Y6EIt3nDCAS1k$kPGOKm"

#: SHA-256 of ``envelope_bytes(scenario_envelope(name))`` for every scenario,
#: measured on ``main`` @ ``3f43191`` — before the workspace entry existed.
ENVELOPES_BEFORE_THIS_ENTRY = {
    "member-evidence": (
        "e1c667b381b95d618ee48704e24162fbb63018c8e9e4d291f46c565095344b94"
    ),
    "pair-verdicts": (
        "e1c667b381b95d618ee48704e24162fbb63018c8e9e4d291f46c565095344b94"
    ),
    "real-refusal": (
        "49e4fadb37be8b748d2236c1f1c8a5e7b47d1287718b33feee77eb533e0f6bfe"
    ),
    "recheck-both-reissued": (
        "33dd205bbe62cf323a8807b3d2ae42fa755be8d639ab5479aee89830800f556f"
    ),
    "recheck-comparison": (
        "d67dc8c29b6cf7cf51701dedd49fb0ac9bb24146205e3ae384995ed717169045"
    ),
    "recheck-consuming-reissued": (
        "2f4bcbefebc125763fca4f3ec4e2fb1357e424cdf51d2cc31fb5594cca865383"
    ),
    "recheck-key-change-only": (
        "4d362ecbdff4803fcd1b1d969b9e6c2f567c89c9479f65a5868a6d8418de0bd8"
    ),
    "recheck-member-gone": (
        "06da8487322125a66b1fbef1abbb132c4076323a5f5afd26dcb1be51d1530828"
    ),
    "recheck-prior-without-basis": (
        "ab9a2735eb6027f98d967f600d16640d59b3750578afb9f8b8d7e153dfa6b471"
    ),
    "recheck-producing-reissued": (
        "6179d4b629b0b793fa5e3f361007ca9af50ed840f66567ff57ebce4a7ece4c25"
    ),
    "recheck-producing-reissued-content-changed": (
        "871ce5775d740b6f8b9afca13228620defbf763de2cd7121908d492472c6e2fc"
    ),
    "recheck-requirement-relaxed": (
        "a559533d5242db603d2ad8211e1fce253c7918b45a9bd19d0b4f03aa1c3b149d"
    ),
    "recheck-semantics-changed": (
        "208fe9873d67ff624f2b301b2e4f5d183486a3dc068dcb1ede3ce5b4efc6f8dc"
    ),
}


def _element_key(model_key: str, global_id: str) -> str:
    return f"{model_key}::{global_id}"


def _hvac_variant(target: Path, variant: str) -> None:
    """Write the public HVAC sample, as issued or with one deliberate change."""

    if variant == "as-issued":
        shutil.copyfile(RAW / "Building-Hvac.ifc", target)
        return
    model = ifcopenshell.open(str(RAW / "Building-Hvac.ifc"))
    terminal = model.by_guid(CHIMNEY_COVER)
    if variant == "type-declared":
        # The type object, which is where the checker reads first.
        [relation] = terminal.IsTypedBy
        relation.RelatingType.PredefinedType = "LOUVRE"
        relation.RelatingType.ElementType = None
    elif variant == "terminal-removed":
        ifcopenshell.api.run("root.remove_product", model, product=terminal)
    else:
        raise ValueError(variant)
    model.write(str(target))


def _make_workspace(
    root: Path,
    name: str,
    *,
    hvac: str = "as-issued",
    rules: Path = RULES,
    models: tuple[str, ...] = ("hvac", "architecture"),
    as_of: str | None = None,
) -> Path:
    """A workspace with one project, run once by the real command."""

    workspace = root / name
    project = workspace / "projects" / "ws"
    project.mkdir(parents=True)
    config = f'[run]\nruleset_path = "{rules.as_posix()}"\nexporters = ["csv", "json"]\n'
    if as_of is not None:
        config += f'as_of = "{as_of}"\n'
    (workspace / "control-tower.toml").write_bytes(config.encode("utf-8"))

    manifest = '[project]\nproject_id = "ws"\nname = "Workspace"\n'
    if "hvac" in models:
        _hvac_variant(project / "Building-Hvac.ifc", hvac)
        manifest += (
            '\n[[models]]\nmodel_id = "hvac"\ndiscipline = "HVAC"\n'
            'filename = "Building-Hvac.ifc"\n'
        )
    if "architecture" in models:
        shutil.copyfile(
            RAW / "Building-Architecture.ifc", project / "Building-Architecture.ifc"
        )
        manifest += (
            '\n[[models]]\nmodel_id = "architecture"\ndiscipline = "Architecture"\n'
            'filename = "Building-Architecture.ifc"\n'
        )
    for stage in ("Coordination", "Design", "Handover"):
        manifest += f'\n[[milestones]]\nstage = "{stage}"\ndue = ""\n'
    (project / "project.toml").write_bytes(manifest.encode("utf-8"))

    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = epc_ct(["--repository-root", str(workspace), "run"])
    assert code == 0, err.getvalue()
    return workspace


def _rewritten(root: Path, name: str, source: Path, change) -> Path:
    """A copy of a finished run whose document was changed and vouched for again.

    For the preconditions a real run cannot be made to break on its own: the
    document is edited and the manifest's hash for it is brought into line, so
    what is exercised is the comparison's guard and not the integrity check.
    """

    target = root / name
    shutil.copytree(source, target)
    document = json.loads((target / RUN_DOCUMENT).read_text(encoding="utf-8"))
    change(document)
    (target / RUN_DOCUMENT).write_bytes(
        json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8")
    )
    manifest = json.loads((target / RUN_MANIFEST).read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        if artifact["path"] == RUN_DOCUMENT:
            artifact["sha256"] = sha256_file(target / RUN_DOCUMENT)
    (target / RUN_MANIFEST).write_bytes(json.dumps(manifest).encode("utf-8"))
    return target


def _drop_register(rules: Path) -> None:
    path = rules / "PV-001.toml"
    raw = path.read_bytes()
    old, new = b'"LOUVRE", "REGISTER"]', b'"LOUVRE"]'
    assert raw.count(old) == 1
    path.write_bytes(raw.replace(old, new))


def _empty_semantics(document) -> None:
    for requirement in document["requirements"]:
        requirement["semantics_digest"] = ""


def _other_checker(document) -> None:
    document["run"]["checkers"][0]["version"] = "9.9.9"


@functools.cache
def _runs() -> types.SimpleNamespace:
    """Every workspace the tests read, each run once per session."""

    # Made with ``mkdir`` rather than tempfile's helpers; see ``tests/helpers.py``.
    root = Path(tempfile.gettempdir()) / f"epc-ct-doctor-workspace-{uuid.uuid4().hex}"
    root.mkdir(mode=0o777)
    atexit.register(shutil.rmtree, root, True)

    edited = root / "edited-rules" / "rules" / "product-validation"
    shutil.copytree(RULES, edited)
    _drop_register(edited)

    before = _make_workspace(root, "before")
    return types.SimpleNamespace(
        root=root,
        before=before,
        after=_make_workspace(root, "after", hvac="type-declared"),
        removed=_make_workspace(root, "removed", hvac="terminal-removed"),
        shipped_rules=_make_workspace(
            root, "shipped-rules", rules=PROJECT_ROOT / "rules" / "epc-delivery"
        ),
        edited_rules=_make_workspace(root, "edited", rules=edited),
        one_model=_make_workspace(root, "one-model", models=("hvac",)),
        other_date=_make_workspace(root, "other-date", as_of="2026-09-01T00:00:00Z"),
        no_semantics=_rewritten(root, "no-semantics", before, _empty_semantics),
        other_checker=_rewritten(root, "other-checker", before, _other_checker),
    )


def _document(workspace: Path) -> dict:
    return json.loads((workspace / RUN_DOCUMENT).read_text(encoding="utf-8"))


def _tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class ExistingEnvelopesTests(unittest.TestCase):
    def test_every_fixture_and_real_envelope_is_the_bytes_it_was(self):
        self.assertEqual(sorted(SCENARIOS), sorted(ENVELOPES_BEFORE_THIS_ENTRY))
        for name, recorded in ENVELOPES_BEFORE_THIS_ENTRY.items():
            with self.subTest(scenario=name):
                data = envelope_bytes(scenario_envelope(name))
                self.assertEqual(hashlib.sha256(data).hexdigest(), recorded)

    def test_no_scenario_is_a_workspace_and_no_record_entry_can_be(self):
        from internal.doctor_adapter import MODES, build_envelope

        self.assertEqual(MODES, ("fixture", "real"))
        self.assertEqual({mode for mode, _entry in SCENARIOS.values()}, set(MODES))
        with self.assertRaises(ValueError):
            build_envelope("workspace", lambda: None, lambda document: {})


class FaithfulTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = _runs().after
        cls.envelope = workspace_envelope(cls.workspace)
        cls.document = _document(cls.workspace)

    def test_it_is_a_validation_and_carries_no_assessment(self):
        self.assertEqual(
            list(self.envelope),
            ["mode", "outcome", "run", "findings", "requirements", "elements"],
        )
        self.assertEqual(self.envelope["mode"], "workspace")
        self.assertEqual(self.envelope["outcome"], "validation")

    def test_the_run_is_identified_as_it_identified_itself(self):
        run, published = self.envelope["run"], self.document["run"]
        self.assertEqual(run["validation_run_id"], published["validation_run_id"])
        self.assertEqual(run["as_of"], published["as_of"])
        self.assertEqual(
            run["ruleset"],
            {key: published["ruleset"][key] for key in ("id", "version", "normalized_digest")},
        )
        self.assertEqual(run["checkers"], published["checkers"])
        self.assertEqual(
            {m["model_key"]: m["content_sha256"] for m in run["models"]},
            {m["model_key"]: m["content_sha256"] for m in published["model_inputs"]},
        )
        for model in run["models"]:
            with self.subTest(model=model["model_key"]):
                file = self.workspace / "projects" / "ws" / model["filename"]
                self.assertEqual(model["content_sha256"], sha256_file(file))

    def test_every_finding_is_the_runs_own_and_none_is_missing(self):
        published = {f["finding_key"]: f for f in self.document["findings"]}
        self.assertEqual(
            sorted(f["finding_key"] for f in self.envelope["findings"]), sorted(published)
        )
        for finding in self.envelope["findings"]:
            with self.subTest(finding=finding["finding_key"]):
                source = published[finding["finding_key"]]
                self.assertEqual(finding, {key: source[key] for key in finding})
        self.assertEqual(
            sorted(f["status"] for f in self.envelope["findings"]),
            ["FAIL", "N/A", "PASS"],
        )

    def test_a_requirement_is_described_without_its_authors_metadata(self):
        published = {r["requirement_key"]: r for r in self.document["requirements"]}
        self.assertEqual(sorted(self.envelope["requirements"]), sorted(published))
        for key, requirement in self.envelope["requirements"].items():
            source = published[key]
            self.assertEqual(
                sorted(requirement),
                [
                    "checker",
                    "citation",
                    "discipline_scope",
                    "labels",
                    "requirement_id",
                    "requirement_label",
                    "rule_id",
                    "semantics_digest",
                    "specification_label",
                ],
            )
            for field in ("rule_id", "citation", "semantics_digest", "requirement_label"):
                self.assertEqual(requirement[field], source[field])
            self.assertEqual(";".join(requirement["labels"]), source["labels"])
            self.assertEqual(
                ";".join(requirement["discipline_scope"]), source["discipline_scope"]
            )

    def test_the_elements_are_the_runs_inventory(self):
        published = {e["element_key"]: e for e in self.document["elements"]}
        self.assertEqual(sorted(self.envelope["elements"]), sorted(published))
        for key, element in self.envelope["elements"].items():
            for field in ("name", "ifc_class", "storey", "global_id", "model_key"):
                self.assertEqual(element[field], published[key][field])
            self.assertLessEqual(
                set(element),
                {"name", "ifc_class", "storey", "global_id", "model_key", "tag"},
            )

    def test_the_same_request_gives_the_same_bytes_and_writes_nothing(self):
        runs = _runs()
        before = _tree(runs.root)
        checkout = {
            relative: _tree(PROJECT_ROOT / relative)
            for relative in ("data/processed", "reports", "ids", "rules")
        }
        first = envelope_bytes(workspace_envelope(runs.after, runs.before))
        second = envelope_bytes(workspace_envelope(runs.after, runs.before))
        self.assertEqual(first, second)
        self.assertNotIn(b"\r", first)
        self.assertEqual(_tree(runs.root), before)
        for relative, digests in checkout.items():
            self.assertEqual(_tree(PROJECT_ROOT / relative), digests)

    def test_the_entry_reads_no_clock_and_lists_no_directory(self):
        tree = ast.parse((ADAPTER / "workspace.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
            elif isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
        self.assertFalse(imported & {"time", "datetime", "os", "glob", "socket", "urllib"})
        called = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(called & {"glob", "rglob", "iterdir", "walk", "scandir", "now"})


class TagTests(unittest.TestCase):
    def test_a_tag_is_the_model_files_own(self):
        workspace = _runs().before
        envelope = workspace_envelope(workspace)
        model = ifcopenshell.open(str(workspace / "projects" / "ws" / "Building-Hvac.ifc"))
        for entity in model.by_type("IfcElement"):
            with self.subTest(element=entity.GlobalId):
                element = envelope["elements"][_element_key(HVAC, entity.GlobalId)]
                self.assertTrue(entity.Tag)
                self.assertEqual(element["tag"], entity.Tag)
        self.assertEqual(
            {m["model_key"]: m["tag_source"] for m in envelope["run"]["models"]},
            {HVAC: "model-file", ARCHITECTURE: "model-file"},
        )

    def test_an_element_that_states_no_tag_has_no_tag_key(self):
        workspace = _runs().before
        envelope = workspace_envelope(workspace)
        path = workspace / "projects" / "ws" / "Building-Architecture.ifc"
        untagged = [
            entity.GlobalId
            for entity in ifcopenshell.open(str(path)).by_type("IfcElement")
            if entity.Tag is None
        ]
        for global_id in untagged:
            element = envelope["elements"][_element_key(ARCHITECTURE, global_id)]
            self.assertNotIn("tag", element)

    def test_a_file_that_is_not_the_one_the_run_read_gives_no_tag(self):
        runs = _runs()
        workspace = runs.root / "swapped"
        shutil.copytree(runs.before, workspace)
        # The run recorded the as-issued file; a different one is now in place.
        shutil.copyfile(
            runs.after / "projects" / "ws" / "Building-Hvac.ifc",
            workspace / "projects" / "ws" / "Building-Hvac.ifc",
        )
        (workspace / "projects" / "ws" / "Building-Architecture.ifc").unlink()

        envelope = workspace_envelope(workspace)
        self.assertEqual(
            {m["model_key"]: m["tag_source"] for m in envelope["run"]["models"]},
            {HVAC: "model-file-differs", ARCHITECTURE: "model-file-not-located"},
        )
        self.assertFalse([e for e in envelope["elements"].values() if "tag" in e])
        self.assertEqual(len(envelope["elements"]), len(_document(workspace)["elements"]))

    def test_the_tag_is_in_no_key(self):
        envelope = workspace_envelope(_runs().after, _runs().before)
        tags = {e["tag"] for e in envelope["elements"].values() if "tag" in e}
        self.assertTrue(tags)
        for row in envelope["comparison"]["pairs"]:
            keys = {row["model_key"], row["element_key"], row["requirement_key"]}
            keys |= {row["prior"]["finding_key"], row["current"]["finding_key"]}
            self.assertFalse(tags & keys)


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runs = _runs()
        cls.envelope = workspace_envelope(runs.after, runs.before)
        cls.comparison = cls.envelope["comparison"]

    def test_it_is_carried_only_when_an_earlier_run_is_named(self):
        self.assertNotIn("comparison", workspace_envelope(_runs().after))
        self.assertEqual(list(self.envelope)[-1], "comparison")
        self.assertEqual(
            list(self.comparison),
            [
                "prior_run",
                "changed_models",
                "pairs",
                "not_re_evaluated",
                "newly_appearing",
                "prior_elements",
            ],
        )

    def test_each_pair_carries_both_findings_as_each_run_published_them(self):
        runs = _runs()
        was = {
            (f["model_key"], f["element_key"], f["requirement_key"]): f
            for f in _document(runs.before)["findings"]
        }
        now = {
            (f["model_key"], f["element_key"], f["requirement_key"]): f
            for f in _document(runs.after)["findings"]
        }
        self.assertEqual(len(self.comparison["pairs"]), len(was))
        for row in self.comparison["pairs"]:
            pair = (row["model_key"], row["element_key"], row["requirement_key"])
            for side, source in (("prior", was[pair]), ("current", now[pair])):
                with self.subTest(pair=pair, side=side):
                    self.assertEqual(
                        row[side],
                        {
                            key: source[key]
                            for key in ("finding_key", "status", "expected", "actual", "reason")
                        },
                    )

    def test_the_statuses_are_before_and_after_and_nothing_more(self):
        statuses = {
            row["element_key"]: (row["prior"]["status"], row["current"]["status"])
            for row in self.comparison["pairs"]
        }
        self.assertEqual(
            statuses,
            {
                _element_key(HVAC, CHIMNEY_COVER): ("FAIL", "PASS"),
                _element_key(HVAC, FIREPLACE_CAP): ("FAIL", "FAIL"),
                "": ("N/A", "N/A"),
            },
        )
        self.assertEqual(self.comparison["not_re_evaluated"], [])
        self.assertEqual(self.comparison["newly_appearing"], [])
        self.assertEqual(self.comparison["prior_elements"], {})

    def test_the_models_whose_content_changed_are_listed(self):
        runs = _runs()
        hvac = "projects/ws/Building-Hvac.ifc"
        self.assertEqual(
            self.comparison["changed_models"],
            [
                {
                    "model_key": HVAC,
                    "prior_content_sha256": sha256_file(runs.before / hvac),
                    "current_content_sha256": sha256_file(runs.after / hvac),
                }
            ],
        )
        self.assertNotEqual(
            self.comparison["prior_run"]["validation_run_id"],
            self.envelope["run"]["validation_run_id"],
        )

    def test_the_adapter_concludes_nothing(self):
        text = envelope_bytes(self.envelope).decode("utf-8").lower()
        for word in ("fixed", "resolved", "repaired", "improved", "已修复", "修正"):
            with self.subTest(word=word):
                self.assertNotIn(word, text)

    def test_a_pair_only_the_earlier_run_evaluated_is_not_re_evaluated(self):
        runs = _runs()
        comparison = workspace_envelope(runs.removed, runs.before)["comparison"]
        key = _element_key(HVAC, CHIMNEY_COVER)
        [row] = comparison["not_re_evaluated"]
        self.assertEqual(row["element_key"], key)
        self.assertEqual(row["prior"]["status"], "FAIL")
        self.assertNotIn("current", row)
        self.assertIs(row["element_in_current_run"], False)
        self.assertEqual(comparison["newly_appearing"], [])
        self.assertNotIn(key, [r["element_key"] for r in comparison["pairs"]])
        # Still nameable: its display row comes from the earlier run's inventory.
        self.assertEqual(list(comparison["prior_elements"]), [key])
        self.assertEqual(comparison["prior_elements"][key]["ifc_class"], "IfcAirTerminal")
        # The file in the workspace is not the one the earlier run read.
        self.assertNotIn("tag", comparison["prior_elements"][key])

    def test_a_pair_only_the_current_run_evaluated_is_newly_appearing(self):
        runs = _runs()
        envelope = workspace_envelope(runs.before, runs.removed)
        comparison = envelope["comparison"]
        key = _element_key(HVAC, CHIMNEY_COVER)
        [row] = comparison["newly_appearing"]
        self.assertEqual(row["element_key"], key)
        self.assertEqual(row["current"]["status"], "FAIL")
        self.assertNotIn("prior", row)
        self.assertIs(row["element_in_prior_run"], False)
        self.assertEqual(comparison["not_re_evaluated"], [])
        self.assertNotIn(key, [r["element_key"] for r in comparison["pairs"]])


class RefusalTests(unittest.TestCase):
    """Each precondition, broken by a run that really differs where one can."""

    def _refused(self, prior: Path) -> list[str]:
        envelope = workspace_envelope(_runs().before, prior)
        # No partial result: neither run's findings, nor any comparison.
        self.assertEqual(list(envelope), ["mode", "outcome", "refusal"])
        self.assertEqual((envelope["mode"], envelope["outcome"]), ("workspace", "refusal"))
        refusal = envelope["refusal"]
        self.assertEqual(list(refusal), ["code", "text", "reasons"])
        codes = [reason["code"] for reason in refusal["reasons"]]
        self.assertEqual(refusal["code"], codes[0])
        self.assertEqual(
            refusal["text"], "\n".join(reason["text"] for reason in refusal["reasons"])
        )
        for reason in refusal["reasons"]:
            self.assertTrue(reason["text"].startswith(f"[{reason['code']}] "))
            self.assertIn(reason["code"], REFUSAL_CODES)
        return codes

    def test_another_rule_set(self):
        self.assertEqual(
            self._refused(_runs().shipped_rules),
            [
                "ruleset-id-differs",
                "ruleset-version-differs",
                "ruleset-digest-differs",
                "requirement-set-differs",
                # The shipped rule set also routes a rule to a second checker.
                "checker-differs",
            ],
        )

    def test_the_same_identifier_and_version_over_an_edited_rule(self):
        self.assertEqual(
            self._refused(_runs().edited_rules),
            ["ruleset-digest-differs", "requirement-semantics-differs"],
        )

    def test_a_predicate_that_was_not_recorded(self):
        self.assertEqual(
            self._refused(_runs().no_semantics), ["requirement-semantics-not-recorded"]
        )

    def test_another_checker(self):
        self.assertEqual(self._refused(_runs().other_checker), ["checker-differs"])

    def test_another_logical_date(self):
        self.assertEqual(self._refused(_runs().other_date), ["as-of-differs"])

    def test_another_set_of_models(self):
        self.assertEqual(self._refused(_runs().one_model), ["model-set-differs"])

    def test_every_code_is_reached(self):
        runs = _runs()
        reached = set()
        for prior in (
            runs.shipped_rules,
            runs.edited_rules,
            runs.no_semantics,
            runs.other_checker,
            runs.other_date,
            runs.one_model,
        ):
            reached.update(self._refused(prior))
        self.assertEqual(reached, set(REFUSAL_CODES))


class FaultTests(unittest.TestCase):
    """A directory that does not hold a finished run is a fault, never a result."""

    def test_a_directory_without_a_run(self):
        with self.assertRaises(FileNotFoundError):
            workspace_envelope(_runs().root)
        with self.assertRaises(FileNotFoundError):
            workspace_envelope(_runs().before, _runs().root)

    def test_a_document_changed_after_the_run(self):
        runs = _runs()
        edited = runs.root / "edited-document"
        shutil.copytree(runs.before, edited)
        path = edited / RUN_DOCUMENT
        path.write_bytes(path.read_bytes().replace(b'"FAIL"', b'"PASS"'))
        with self.assertRaises(ValueError):
            workspace_envelope(edited)
        with self.assertRaises(ValueError):
            workspace_envelope(runs.before, edited)


class TransportTests(unittest.TestCase):
    def test_the_command_line_prints_the_entrys_bytes(self):
        runs = _runs()
        for arguments, expected in (
            (["--workspace", str(runs.after)], workspace_envelope(runs.after)),
            (
                ["--workspace", str(runs.after), "--prior", str(runs.before)],
                workspace_envelope(runs.after, runs.before),
            ),
        ):
            with self.subTest(arguments=len(arguments)):
                out = io.BytesIO()
                self.assertEqual(adapter_main(arguments, out), 0)
                self.assertEqual(out.getvalue(), envelope_bytes(expected))

    def test_a_malformed_request_is_still_a_usage_error(self):
        for arguments in (["--workspace"], ["--prior", "x"], ["--workspace", "a", "b"]):
            with self.subTest(arguments=arguments):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    self.assertEqual(adapter_main(arguments, io.BytesIO()), 2)
                self.assertIn("usage:", err.getvalue())

    def test_the_server_offers_a_workspace_only_when_started_with_one(self):
        with _Server(serve.adapter_source) as base:
            _status, _type, body = _get(f"{base}/api/runs?mode=workspace")
            self.assertEqual(json.loads(body), {"mode": "workspace", "runs": []})
            status, _type, _body = _get(f"{base}/api/envelope?mode=workspace&run=workspace")
            self.assertEqual(status, 500)

    def test_the_server_hands_the_browser_the_entrys_envelope(self):
        runs = _runs()
        factory = functools.partial(serve.adapter_source, runs.after, runs.before)
        with _Server(factory) as base:
            _status, _type, body = _get(f"{base}/api/runs?mode=workspace")
            self.assertEqual(
                json.loads(body), {"mode": "workspace", "runs": [{"run_id": "workspace"}]}
            )
            status, _type, body = _get(f"{base}/api/envelope?mode=workspace&run=workspace")
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body), workspace_envelope(runs.after, runs.before))
            # The other two experiences list what they listed.
            for mode in ("fixture", "real"):
                _status, _type, body = _get(f"{base}/api/runs?mode={mode}")
                self.assertEqual(
                    [run["run_id"] for run in json.loads(body)["runs"]],
                    sorted(name for name, entry in SCENARIOS.items() if entry[0] == mode),
                )


if __name__ == "__main__":
    unittest.main()
