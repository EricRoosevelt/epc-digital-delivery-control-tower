"""The product validation rule set: separate, identified, and inert here.

One claim is made, in four parts.

*Isolation* — `rules/product-validation` exists and the shipped configuration
does not load it, so every artifact the shipped configuration writes is the same
bytes whether that directory is there or not. This is the counterfactual pinned:
the alternative, measured before this rule set was given a home of its own, was
adding its rule to `rules/epc-delivery`, which re-keys every canonical finding
and every issue. The run below is done twice, in two copies of the repository
that differ only by this rule set, and both are compared with what is committed.

*Identity* — a `(ruleset_id, version)` pair names one set of rules. The shipped
rule set gets that from the snapshot ceremony; this one is in no snapshot, so it
has a record of its own under `docs/contracts/`, and an edit that keeps the
version is refused here.

*Use from outside* — a workspace that is not in this repository names the
directory in its own `control-tower.toml` and runs. Nothing in the checkout
moves when it does.

*What the predicate reads* — measured, not assumed, on a model built for the
purpose. The checker is IfcTester and the answer is its, so this is a
characterization: it says what a pass under this rule can and cannot mean, and
it is here so that a change in that answer is noticed rather than inherited.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import io
import json
import shutil
import unittest
from pathlib import Path

from epc_control_tower.checkers.ids_checker import compile_rule_directory
from epc_control_tower.cli import main
from epc_control_tower.config import load_project_manifests, load_run_config
from epc_control_tower.coverage import rule_definitions_digest
from epc_control_tower.determinism import sha256_file
from epc_control_tower.domain import FindingStatus
from epc_control_tower.identity import NORMALIZED_DIGEST_DERIVATION
from epc_control_tower.pipeline import execute
from epc_control_tower.registry import default_registry
from epc_control_tower.rule_definitions import load_rule_definitions
from epc_control_tower.rules import load_ruleset
from epc_control_tower.stages.check import check
from epc_control_tower.stages.ingest import ingest
from epc_control_tower.stages.inventory import inventory
from helpers import (
    PROJECT_ROOT,
    outside_repository_directory,
    shipped_pipeline_result,
    shipped_run_config,
    writable_test_directory,
)

RULESET_ID = "product-validation"
RULES = PROJECT_ROOT / "rules" / RULESET_ID
SHIPPED_RULES = PROJECT_ROOT / "rules" / "epc-delivery"
RECORD = PROJECT_ROOT / "docs" / "contracts" / f"ruleset-{RULESET_ID}.json"

#: What a run of the shipped configuration reads, relative to the repository
#: root. Copied to build a repository that has, or has not, the rule set.
RUN_INPUTS = (
    "control-tower.toml",
    "data/raw",
    "docs/contracts/legacy",
    "ids/epc_delivery_requirements_v0.1.ids",
    "projects",
    "rules/epc-delivery",
    "third_party/buildingsmart/bcf-xml",
)

#: Everything a run writes. `ids` is here because the compiled rule document is
#: a build product under the same gate as the rest.
OUTPUT_ROOTS = ("data/processed", "ids", "reports")


def _record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _identity_conflicts(rules: Path, record: dict) -> list[str]:
    """Why ``rules`` cannot be the rule set ``record`` says its version names."""

    ruleset = load_ruleset(rules)
    versions = [entry["version"] for entry in record["versions"]]
    problems = [
        f"version {version} is recorded more than once"
        for version in sorted(set(versions))
        if versions.count(version) > 1
    ]
    if ruleset.ruleset_id != record["ruleset_id"]:
        return [*problems, f"ruleset_id is {ruleset.ruleset_id!r}"]
    recorded = [e for e in record["versions"] if e["version"] == ruleset.version]
    if not recorded:
        return [*problems, f"version {ruleset.version} has no recorded entry"]

    entry = recorded[0]
    observed = {
        "normalized_digest": ruleset.normalized_digest,
        "normalized_digest_derivation": NORMALIZED_DIGEST_DERIVATION,
        "requirement_keys": sorted(r.requirement_key for r in ruleset.requirements),
        "rule_definitions_digest": rule_definitions_digest(rules),
    }
    for field, value in observed.items():
        if entry[field] != value:
            problems.append(
                f"{field} of {ruleset.ruleset_id} v{ruleset.version}: recorded "
                f"{entry[field]!r}, now {value!r}. Raise the version in "
                "ruleset.toml and add an entry; a recorded version is never edited."
            )
    return problems


def _copy_of_rules(scratch: Path) -> Path:
    # Nested like the repository: a rule directory compiles to `<dir>/../../ids`.
    rules = scratch / "rules" / RULESET_ID
    shutil.copytree(RULES, rules)
    return rules


def _replace_once(path: Path, old: str, new: str) -> None:
    raw = path.read_bytes()
    assert raw.count(old.encode("utf-8")) == 1, (path.name, old)
    path.write_bytes(raw.replace(old.encode("utf-8"), new.encode("utf-8")))


def _tree(root: Path, relative: str) -> dict[str, str]:
    base = root / relative
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(base.rglob("*"))
        if path.is_file()
    }


class IdentityTests(unittest.TestCase):
    def test_the_version_names_the_rules_that_are_recorded_for_it(self):
        self.assertEqual(_identity_conflicts(RULES, _record()), [])

    def test_an_edit_that_keeps_the_version_is_refused(self):
        # One edit that changes what the rule accepts, and one that changes only
        # prose the checker hands on. Neither may hide behind version 1.0.
        edits = {
            "predicate": ('"LOUVRE", "REGISTER"]', '"LOUVRE"]', "normalized_digest"),
            "instructions": (
                "NOTDEFINED states nothing.",
                "NOTDEFINED says nothing.",
                "rule_definitions_digest",
            ),
        }
        for name, (old, new, moved) in edits.items():
            with self.subTest(edit=name), writable_test_directory("pv-edit") as scratch:
                rules = _copy_of_rules(scratch)
                self.assertEqual(_identity_conflicts(rules, _record()), [])
                _replace_once(rules / "PV-001.toml", old, new)
                problems = _identity_conflicts(rules, _record())
                self.assertTrue(any(p.startswith(moved) for p in problems), problems)

    def test_it_shares_no_identity_with_the_shipped_rule_set(self):
        ours, shipped = load_ruleset(RULES), load_ruleset(SHIPPED_RULES)
        self.assertEqual(ours.ruleset_id, RULESET_ID)
        self.assertNotEqual(ours.ruleset_id, shipped.ruleset_id)
        for field in ("rule_id", "requirement_key"):
            with self.subTest(field=field):
                self.assertFalse(
                    {getattr(r, field) for r in ours.requirements}
                    & {getattr(r, field) for r in shipped.requirements}
                )

    def test_no_two_rule_directories_claim_one_identifier(self):
        identifiers = [
            load_rule_definitions(path.parent).ruleset_id
            for path in sorted((PROJECT_ROOT / "rules").glob("*/ruleset.toml"))
        ]
        self.assertEqual(sorted(identifiers), sorted(set(identifiers)))
        self.assertIn(RULESET_ID, identifiers)

    def test_the_committed_document_is_what_the_rules_compile_to(self):
        # The shipped run never compiles this rule set, so the regeneration
        # gate does not reach its document. This does.
        entry = _record()["versions"][-1]
        committed = PROJECT_ROOT / entry["compiled_document"]
        with writable_test_directory("pv-compile") as scratch:
            compiled = compile_rule_directory(_copy_of_rules(scratch)).path
            self.assertEqual(compiled.name, committed.name)
            self.assertEqual(compiled.read_bytes(), committed.read_bytes())
        self.assertEqual(sha256_file(committed), entry["compiled_document_sha256"])


class ProvenanceTests(unittest.TestCase):
    def test_every_requirement_says_where_it_comes_from(self):
        for requirement in load_ruleset(RULES).requirements:
            with self.subTest(rule=requirement.rule_id):
                self.assertIn("Product validation rule", requirement.citation)
                self.assertIn(
                    "not a project, owner, statutory or buildingSMART requirement",
                    requirement.citation,
                )
                self.assertIn("ProductValidation", requirement.labels)

    def test_nothing_it_is_called_claims_compliance(self):
        definition = load_rule_definitions(RULES)
        names = [definition.title, definition.description, definition.purpose]
        for rule in definition.rules:
            names += [rule.title, rule.description]
        for text in names:
            with self.subTest(text=text):
                self.assertNotIn("compliance", text.lower())
                self.assertNotIn("合规", text)


class IsolationTests(unittest.TestCase):
    def test_the_shipped_configuration_does_not_load_it(self):
        self.assertEqual(shipped_run_config().ruleset_path, SHIPPED_RULES)
        shipped = shipped_pipeline_result().bundle
        self.assertEqual(shipped.ruleset.ruleset_id, "epc-delivery")
        ours = {r.requirement_key for r in load_ruleset(RULES).requirements}
        self.assertFalse(ours & {f.requirement_key for f in shipped.findings})

    def test_the_shipped_run_writes_the_same_bytes_with_and_without_it(self):
        document = _record()["versions"][-1]["compiled_document"]
        with outside_repository_directory("pv-isolation") as scratch:
            without = _run_a_copy(scratch / "without", "without")
            beside = _run_a_copy(scratch / "beside", "beside")

        # The rule set's own document is an input here, present in one copy by
        # construction; the run must not have touched it either.
        self.assertEqual(
            beside.pop(document),
            _record()["versions"][-1]["compiled_document_sha256"],
        )
        self.assertEqual(beside, without)

        # And both are what this repository publishes, not merely each other:
        # every file the run wrote is, byte for byte, the committed one.
        self.assertGreater(len(without), 30)
        for name in sorted(without):
            with self.subTest(artifact=name):
                self.assertEqual(without[name], sha256_file(PROJECT_ROOT / name))

    def test_inside_the_shipped_rule_set_the_same_rule_re_keys_every_finding(self):
        # Why it is beside and not inside. The same rule file, dropped into the
        # shipped rule set with the version left alone: the run succeeds, and no
        # published canonical finding key or issue key is left standing.
        canonical = "data/processed/canonical"
        with outside_repository_directory("pv-inside") as scratch:
            written = _run_a_copy(scratch, "inside")
            keys = {
                name: _column(scratch / canonical / f"{name}s.csv", f"{name}_key")
                for name in ("finding", "issue")
            }

        for name, inside in keys.items():
            with self.subTest(key=name):
                published = _column(
                    PROJECT_ROOT / canonical / f"{name}s.csv", f"{name}_key"
                )
                self.assertTrue(published)
                self.assertFalse(published & inside)
        self.assertNotEqual(
            written["reports/artifact_manifest.json"],
            sha256_file(PROJECT_ROOT / "reports" / "artifact_manifest.json"),
        )


def _run_a_copy(root: Path, where: str) -> dict[str, str]:
    """Run the shipped configuration in a copy of the repository.

    ``where`` puts the product validation rule ``without`` the copy, ``beside``
    the shipped rule set as its own directory, or ``inside`` the shipped one.
    """

    for relative in RUN_INPUTS:
        source, target = PROJECT_ROOT / relative, root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copyfile(source, target)
    if where == "beside":
        document = _record()["versions"][-1]["compiled_document"]
        shutil.copytree(RULES, root / "rules" / RULESET_ID)
        shutil.copyfile(PROJECT_ROOT / document, root / document)
    elif where == "inside":
        shutil.copyfile(RULES / "PV-001.toml", root / "rules/epc-delivery/PV-001.toml")

    execute(load_run_config(root))
    written = {}
    for relative in OUTPUT_ROOTS:
        written.update(_tree(root, relative))
    return written


def _column(path: Path, name: str) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row[name] for row in csv.DictReader(stream)}


class OutsideWorkspaceTests(unittest.TestCase):
    """A workspace elsewhere names the directory and runs against it."""

    def test_a_workspace_outside_the_repository_runs_against_it(self):
        before = {
            relative: _tree(PROJECT_ROOT, relative)
            for relative in (*OUTPUT_ROOTS, "rules")
        }
        with outside_repository_directory("pv-workspace") as workspace:
            (workspace / "control-tower.toml").write_bytes(
                (
                    "[run]\n"
                    f'ruleset_path = "{RULES.as_posix()}"\n'
                    'exporters = ["csv", "json"]\n'
                ).encode("utf-8")
            )
            project = workspace / "projects" / "outside"
            project.mkdir(parents=True)
            # The public HVAC sample, which has two air terminals. The rule's
            # stage has to be in the project's programme, as for any rule.
            (project / "project.toml").write_bytes(
                (
                    "[project]\n"
                    'project_id = "outside"\n'
                    'name = "Outside workspace"\n'
                    f'raw_data_dir = "{(PROJECT_ROOT / "data" / "raw").as_posix()}"\n'
                    "\n[[models]]\n"
                    'model_id = "hvac"\n'
                    'discipline = "HVAC"\n'
                    'filename = "Building-Hvac.ifc"\n'
                    "\n[[milestones]]\n"
                    'stage = "Coordination"\n'
                    'due = ""\n'
                ).encode("utf-8")
            )

            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main(["--repository-root", str(workspace), "run"])
            self.assertEqual(code, 0, err.getvalue())
            document = json.loads(
                (workspace / "data" / "processed" / "canonical" / "run.json").read_text(
                    encoding="utf-8"
                )
            )

        entry = _record()["versions"][-1]
        ruleset = document["run"]["ruleset"]
        self.assertEqual(
            (ruleset["id"], ruleset["version"], ruleset["normalized_digest"]),
            (RULESET_ID, entry["version"], entry["normalized_digest"]),
        )
        self.assertEqual(
            sorted(r["requirement_key"] for r in document["requirements"]),
            entry["requirement_keys"],
        )
        # Both air terminals in that sample are USERDEFINED with a free-text
        # object type, which this rule does not accept.
        self.assertEqual(
            [(f["status"], f["is_issue"]) for f in document["findings"]],
            [("FAIL", "true"), ("FAIL", "true")],
        )
        # Nothing in the checkout moved, the rule set's own document included.
        for relative, digests in before.items():
            with self.subTest(tree=relative):
                self.assertEqual(_tree(PROJECT_ROOT, relative), digests)


#: ``case -> (occurrence PredefinedType, occurrence ObjectType,
#: type PredefinedType or absent, type ElementType, measured status)``.
#:
#: Measured with IfcTester 0.8.5. The value is read from the type object first;
#: the occurrence is consulted only when the type gives nothing — no type, or a
#: type whose value is NOTDEFINED, or USERDEFINED with no element type. On
#: either object, USERDEFINED is replaced by the free text beside it before the
#: comparison, which is why two rows marked `free text` pass.
NO_TYPE = object()
READINGS = {
    "occurrence-only": ("LOUVRE", None, NO_TYPE, None, FindingStatus.PASS),
    "occurrence-notdefined": ("NOTDEFINED", None, NO_TYPE, None, FindingStatus.FAIL),
    "occurrence-unset": (None, None, NO_TYPE, None, FindingStatus.FAIL),
    "type-only": (None, None, "LOUVRE", None, FindingStatus.PASS),
    "type-over-notdefined": ("NOTDEFINED", None, "LOUVRE", None, FindingStatus.PASS),
    "occurrence-under-notdefined-type": (
        "LOUVRE", None, "NOTDEFINED", None, FindingStatus.PASS,
    ),
    "both-notdefined": ("NOTDEFINED", None, "NOTDEFINED", None, FindingStatus.FAIL),
    "type-free-text-wins": ("LOUVRE", None, "USERDEFINED", "SPECIAL", FindingStatus.FAIL),
    "occurrence-under-empty-userdefined-type": (
        "LOUVRE", None, "USERDEFINED", None, FindingStatus.PASS,
    ),
    "occurrence-userdefined": (
        "USERDEFINED", "Weather louvre", NO_TYPE, None, FindingStatus.FAIL,
    ),
    "occurrence-free-text": ("USERDEFINED", "LOUVRE", NO_TYPE, None, FindingStatus.PASS),
    "type-free-text": (None, None, "USERDEFINED", "GRILLE", FindingStatus.PASS),
}


def _global_id(prefix: str, index: int) -> str:
    return f"{prefix}{index:02d}".ljust(22, "0")


def _write_air_terminals(path: Path) -> dict[str, str]:
    """Write one IFC4 model with an air terminal per reading; ``case -> GlobalId``."""

    import ifcopenshell

    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcProject", GlobalId=_global_id("0P", 0), Name="readings")
    global_ids = {}
    for index, (case, reading) in enumerate(READINGS.items()):
        occurrence_type, object_type, type_type, element_type, _status = reading
        global_ids[case] = _global_id("0A", index)
        terminal = model.create_entity(
            "IfcAirTerminal",
            GlobalId=global_ids[case],
            Name=case,
            PredefinedType=occurrence_type,
            ObjectType=object_type,
        )
        if type_type is NO_TYPE:
            continue
        model.create_entity(
            "IfcRelDefinesByType",
            GlobalId=_global_id("0R", index),
            RelatedObjects=[terminal],
            RelatingType=model.create_entity(
                "IfcAirTerminalType",
                GlobalId=_global_id("0T", index),
                Name=case,
                PredefinedType=type_type,
                ElementType=element_type,
            ),
        )
    model.write(str(path))
    return global_ids


class PredefinedTypeReadingTests(unittest.TestCase):
    """Where the checker reads the predefined type this rule constrains."""

    def test_the_type_is_read_first_and_the_occurrence_only_when_it_says_nothing(self):
        with writable_test_directory("pv-readings") as scratch:
            project = scratch / "projects" / "readings"
            project.mkdir(parents=True)
            global_ids = _write_air_terminals(project / "terminals.ifc")
            (project / "project.toml").write_bytes(
                b'[project]\nproject_id = "readings"\nname = "Readings"\n'
                b'\n[[models]]\nmodel_id = "mep"\ndiscipline = "MEP"\n'
                b'filename = "terminals.ifc"\n'
            )
            config = dataclasses.replace(
                shipped_run_config(),
                ruleset_path=_copy_of_rules(scratch),
                reports_dir=scratch / "reports",
            )
            manifests = load_project_manifests(
                [project / "project.toml"], repository_root=scratch
            )
            # Up to the check stage and no further: these terminals have no
            # geometry, and a failing element is otherwise given a bounding box.
            ingested = ingest(manifests)
            paths = {"readings.mep": project / "terminals.ifc"}
            checked = check(
                registry=default_registry(config),
                ruleset=load_ruleset(config.ruleset_path),
                manifests=manifests,
                projects=ingested.projects,
                models=ingested.models,
                elements=inventory(ingested.models, paths),
                validation_run_id="product-validation-readings",
                as_of=config.as_of,
                reports_dir=config.reports_dir,
            )
            checked.raise_for_failures()

        measured = {f.element_key.split("::")[1]: f.status for f in checked.findings}
        self.assertEqual(len(checked.findings), len(READINGS))
        for case, reading in READINGS.items():
            with self.subTest(case=case):
                self.assertEqual(measured[global_ids[case]], reading[-1])


if __name__ == "__main__":
    unittest.main()
