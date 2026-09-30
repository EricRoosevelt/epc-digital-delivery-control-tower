"""What the rule set's identity sees, since contract 1.7 (ADR 0005 §5.1, §5.5-§5.8).

Until 1.7 the normalized digest covered each requirement's metadata and not one
facet parameter, so a rule could change what it checks with every
``validation_run_id`` and ``finding_key`` standing still. These tests pin the
fix from four sides:

* **identity** — each requirement carries a ``semantics_digest`` and the
  normalized digest covers it, while the frozen legacy rule set's digest does
  not move by a byte;
* **P-3** — which edits move which digest, measured on scratch copies of the
  rules and pinned: presentation text a checker does not evaluate moves
  nothing, a title still re-keys, and ``instructions`` the completeness checker
  publishes is semantics;
* **the guard with real digests** — G1-G5 and G10 of §5.5.7 against the real
  rules and edited copies of them (the stand-in versions are in
  ``test_ruleset_derivation_guard.py``);
* **legacy** — contract 1.7 moved no legacy byte.

Every rule edit happens in a scratch copy (``rule_edits``), never in ``rules/``.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
import subprocess
import unittest
from contextlib import contextmanager

from epc_control_tower.coverage import rule_definitions_digest
from epc_control_tower.determinism import json_bytes
from epc_control_tower.identity import (
    NORMALIZED_DIGEST_DERIVATION,
    build_ruleset_normalized_digest,
)
from epc_control_tower.rule_definitions import NON_EVALUATED_FIELDS
from epc_control_tower.rules import load_ruleset
from epc_control_tower.snapshots import (
    DERIVATION_LEDGER_NAME,
    SNAPSHOT_DIRECTORY,
    load_snapshot,
    ruleset_version_conflicts,
    snapshot_path,
)
from helpers import PROJECT_ROOT, frozen_ruleset, writable_test_directory
from rule_edits import RULES, edited_rules

CONTRACTS = PROJECT_ROOT / SNAPSHOT_DIRECTORY
LEDGER = CONTRACTS / DERIVATION_LEDGER_NAME

#: The frozen v0.1 rule set's normalized digest. The same under derivation 1
#: and 2, because none of its requirements carries a semantics digest.
FROZEN_DIGEST = "ecd1477878548dea29b4187761ecc42ef87df1a28fb1df1c4bb5ce1ec8df256b"

#: The eight files the legacy writers publish.
LEGACY_ARTIFACTS = (
    "data/processed/ids_findings.csv",
    "data/processed/bcf_topics.csv",
    "data/processed/bcf_topic_findings.csv",
    "data/processed/bcf_topic_events.csv",
    "data/processed/bcf_viewpoints.csv",
    "data/processed/bcf_viewpoint_components.csv",
    "reports/bcf/ids_failures.bcf",
    "reports/bcf/run_manifest.json",
)


def label(requirement) -> str:
    return f"{requirement.rule_id}/{requirement.requirement_id}"


def ruleset_block(ruleset) -> dict[str, object]:
    """A snapshot's ``ruleset`` block for a rule set, as a refresh would record it."""

    return {
        "id": ruleset.ruleset_id,
        "version": ruleset.version,
        "normalized_digest": ruleset.normalized_digest,
        "normalized_digest_derivation": NORMALIZED_DIGEST_DERIVATION,
        "requirements": len(ruleset.requirements),
    }


class SemanticsDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shipped = load_ruleset(RULES)

    def test_every_shipped_requirement_carries_one(self):
        self.assertEqual(len(self.shipped.requirements), 14)
        for requirement in self.shipped.requirements:
            with self.subTest(requirement=label(requirement)):
                self.assertRegex(requirement.semantics_digest, r"^[0-9a-f]{64}$")

    def test_no_two_requirements_share_one(self):
        digests = [r.semantics_digest for r in self.shipped.requirements]
        self.assertEqual(len(set(digests)), len(digests))

    def test_the_frozen_rule_set_carries_none_and_its_digest_did_not_move(self):
        frozen = frozen_ruleset()
        self.assertTrue(frozen.requirements)
        self.assertEqual({r.semantics_digest for r in frozen.requirements}, {""})
        self.assertEqual(frozen.normalized_digest, FROZEN_DIGEST)

    def test_the_normalized_digest_covers_it_and_only_when_it_is_there(self):
        requirements = self.shipped.requirements
        digest = self.shipped.normalized_digest
        moved = dataclasses.replace(requirements[0], semantics_digest="0" * 64)

        def rebuilt(items) -> str:
            return build_ruleset_normalized_digest(
                ruleset_id=self.shipped.ruleset_id,
                version=self.shipped.version,
                requirements=items,
            )

        self.assertEqual(rebuilt(requirements), digest)
        self.assertNotEqual(rebuilt((moved, *requirements[1:])), digest)
        # Emptying every fingerprint gives derivation 1 exactly: contract 1.6's
        # recorded digest, which is what keeps the frozen rule set still.
        emptied = [dataclasses.replace(r, semantics_digest="") for r in requirements]
        self.assertEqual(
            rebuilt(emptied),
            load_snapshot(snapshot_path(PROJECT_ROOT, "1.6"))["ruleset"][
                "normalized_digest"
            ],
        )

    def test_a_malformed_fingerprint_is_refused(self):
        with self.assertRaises(ValueError):
            dataclasses.replace(self.shipped.requirements[0], semantics_digest="abc")

    def test_what_each_checker_declares_it_does_not_evaluate(self):
        # A fact about each checker, read off its code (ADR 0005 §5.6): the IDS
        # checker hands `instructions` to IfcTester as prose; the completeness
        # checker publishes it as `expected`.
        self.assertEqual(
            NON_EVALUATED_FIELDS,
            {"ids": frozenset({"instructions"}), "completeness": frozenset()},
        )


class WhatAnEditMovesTests(unittest.TestCase):
    """P-3 and the facet edits, pinned to what was measured (ADR 0005 §5.6)."""

    #: ``edit -> (requirements whose semantics digest moves, normalized moves)``.
    EXPECTED = {
        "r002-datatype": ({"R-002/Pset_WallCommon.IsExternal"}, True),
        "r001-cardinality": ({"R-001/Name"}, True),
        "r006-entity": ({"R-006/Name / Category"}, True),
        "r010-pattern": ({"R-010/shared-across-models"}, True),
        "r005a-optional": (
            {"R-005A/EPC_Delivery.AssetTag", "R-005A/EPC_Delivery.SystemCode"},
            True,
        ),
        "r005a-datatype": (
            {"R-005A/EPC_Delivery.AssetTag", "R-005A/EPC_Delivery.SystemCode"},
            True,
        ),
        # The completeness checker's applicability is declared, and counted,
        # although that checker does not read it today (ADR 0005 U8).
        "r010-applicability": ({"R-010/shared-across-models"}, True),
        # Published as `expected` by the completeness checker: semantics.
        "r010-instructions": ({"R-010/shared-across-models"}, True),
        # Prose the IDS checker hands to IfcTester: nothing moves.
        "r005a-instructions": (set(), False),
        "r005a-description": (set(), False),
        "r005a-reformat": (set(), False),
        # Not semantics, and still re-keys: the title is in
        # `specification_label`, which the normalized digest has always covered
        # (P-3: no second migration to take text out).
        "r005a-title": (set(), True),
    }

    @classmethod
    def setUpClass(cls):
        cls.shipped = load_ruleset(RULES)
        cls.by_key = {r.requirement_key: r for r in cls.shipped.requirements}

    def test_each_edit_moves_exactly_what_was_measured(self):
        for edit, (moved, normalized_moves) in self.EXPECTED.items():
            with self.subTest(edit=edit), edited_rules(edit) as rules:
                after = load_ruleset(rules)
                self.assertEqual(
                    {r.requirement_key for r in after.requirements}, set(self.by_key)
                )
                self.assertEqual(
                    {
                        label(self.by_key[r.requirement_key])
                        for r in after.requirements
                        if r.semantics_digest
                        != self.by_key[r.requirement_key].semantics_digest
                    },
                    moved,
                )
                self.assertEqual(
                    after.normalized_digest != self.shipped.normalized_digest,
                    normalized_moves,
                )


@contextmanager
def repository_copy():
    """The recorded snapshots and ledger, copied to a scratch repository root."""

    with writable_test_directory("semantics-guard") as root:
        target = root / SNAPSHOT_DIRECTORY
        target.mkdir(parents=True)
        for path in sorted(CONTRACTS.glob("*.json")):
            shutil.copyfile(path, target / path.name)
        yield root


def codes(problems: list[str]) -> list[str]:
    return [problem[1 : problem.index("]")] for problem in problems]


class TheGuardWithRealDigestsTests(unittest.TestCase):
    """ADR 0005 §5.5.7 against the real rules, and edited copies of them."""

    @classmethod
    def setUpClass(cls):
        cls.shipped = load_ruleset(RULES)
        cls.ledger = json.loads(LEDGER.read_text("utf-8"))
        (cls.entry,) = cls.ledger["migrations"]

    def conflicts(self, root, ruleset, rules) -> list[str]:
        current = {"contract_version": "9.9", "ruleset": ruleset_block(ruleset)}
        return ruleset_version_conflicts(
            root, current, rule_definitions_digest=rule_definitions_digest(rules)
        )

    def test_the_entry_names_the_1_6_baseline_and_the_shipped_rules(self):
        sixteen = snapshot_path(PROJECT_ROOT, "1.6")
        self.assertEqual(self.entry["ruleset_id"], "epc-delivery")
        self.assertEqual(self.entry["version"], "2.2")
        self.assertEqual(
            self.entry["from"],
            {
                "derivation": 1,
                "normalized_digest": load_snapshot(sixteen)["ruleset"][
                    "normalized_digest"
                ],
            },
        )
        self.assertEqual(
            self.entry["to"],
            {"derivation": 2, "normalized_digest": self.shipped.normalized_digest},
        )
        self.assertEqual(self.entry["baseline"]["snapshot"], "contract-1.6.json")
        self.assertEqual(
            self.entry["baseline"]["sha256"],
            hashlib.sha256(sixteen.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            self.entry["baseline"]["commit"], "11e416364cfcd01ae85e2abfa5de3a94c793a725"
        )

    def test_the_two_pieces_of_evidence_never_disagree(self):
        # Evidence one is the rules directory's git tree, written into the entry
        # at the migration commit; evidence two is the declared-definitions
        # digest the guard recomputes. Whenever the rules still have the digest
        # the entry records, the committed tree must still be the entry's tree:
        # a byte change that the parsed definitions could not see would be the
        # only way for the two to part. When the rules have moved on, the entry
        # no longer applies and the guard already refuses through it.
        evidence = self.entry["evidence"]
        self.assertEqual(evidence["rules_git_tree"]["path"], "rules/epc-delivery")
        if rule_definitions_digest(RULES) != evidence["rule_definitions_digest"]:
            return
        tree = subprocess.run(
            ["git", "rev-parse", "HEAD:rules/epc-delivery"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(tree, evidence["rules_git_tree"]["tree"])

    def test_g1_without_the_entry_the_shipped_rules_conflict_with_1_6_once(self):
        with repository_copy() as root:
            (root / SNAPSHOT_DIRECTORY / "contract-1.7.json").unlink()
            ledger = dict(self.ledger, migrations=[])
            (root / SNAPSHOT_DIRECTORY / DERIVATION_LEDGER_NAME).write_bytes(
                json_bytes(ledger)
            )
            problems = self.conflicts(root, self.shipped, RULES)
        self.assertEqual(codes(problems), ["derivation-migration-missing"])
        self.assertIn("contract-1.6.json", problems[0])

    def test_g2_the_shipped_rules_pass_with_the_entry(self):
        self.assertEqual(self.conflicts(PROJECT_ROOT, self.shipped, RULES), [])

    def test_g3_and_g10_a_facet_edit_conflicts_with_1_6_and_with_1_7(self):
        with edited_rules("r002-datatype") as rules:
            edited = load_ruleset(rules)
            problems = self.conflicts(PROJECT_ROOT, edited, rules)
        self.assertEqual(
            codes(problems), ["derivation-migration-missing", "version-reused"]
        )
        self.assertIn("contract-1.6.json", problems[0])
        self.assertIn("contract-1.7.json", problems[1])

    def test_g5_an_edit_the_definitions_see_and_the_semantics_do_not_is_refused(self):
        # An IDS `instructions` edit keeps the derivation-2 digest, so 1.7 says
        # nothing against it — and it moves the declared definitions, so the
        # entry that bridges to 1.6 no longer describes these rules. Refused; the
        # way through is a new rule set version.
        with edited_rules("r005a-instructions") as rules:
            edited = load_ruleset(rules)
            self.assertEqual(edited.normalized_digest, self.shipped.normalized_digest)
            problems = self.conflicts(PROJECT_ROOT, edited, rules)
        self.assertEqual(codes(problems), ["migration-evidence-mismatch"])

    def test_a_reformat_changes_nothing_the_guard_can_see(self):
        with edited_rules("r005a-reformat") as rules:
            self.assertEqual(
                self.conflicts(PROJECT_ROOT, load_ruleset(rules), rules), []
            )


class LegacyDidNotMoveTests(unittest.TestCase):
    """Contract 1.7 moved the canonical contract and no legacy byte."""

    @classmethod
    def setUpClass(cls):
        cls.sixteen = load_snapshot(snapshot_path(PROJECT_ROOT, "1.6"))
        cls.seventeen = load_snapshot(snapshot_path(PROJECT_ROOT, "1.7"))

    def test_the_legacy_run_id_is_unchanged(self):
        self.assertEqual(self.seventeen["legacy_run_id"], "ids-v0.1-8706ef58303bfd11")
        self.assertEqual(self.sixteen["legacy_run_id"], self.seventeen["legacy_run_id"])

    def test_no_legacy_artifact_moved(self):
        for artifact in LEGACY_ARTIFACTS:
            with self.subTest(artifact=artifact):
                if artifact not in self.sixteen["artifacts"]:
                    # The legacy manifest is not a snapshot artifact; its
                    # published bytes are pinned instead, as of `dc351c9`, the
                    # last commit to write it, and unchanged at `9eda5e9`.
                    self.assertEqual(
                        hashlib.sha256((PROJECT_ROOT / artifact).read_bytes()).hexdigest(),
                        "b197b5943cd196703a00eda679a0519172080f663126868011172a1a6d7c8adf",
                    )
                    continue
                self.assertEqual(
                    self.sixteen["artifacts"][artifact],
                    self.seventeen["artifacts"][artifact],
                )

    def test_the_legacy_manifest_still_names_the_frozen_run(self):
        manifest = json.loads(
            (PROJECT_ROOT / "reports" / "bcf" / "run_manifest.json").read_text("utf-8")
        )
        self.assertEqual(manifest["run_id"], "ids-v0.1-8706ef58303bfd11")

    def test_the_canonical_identity_did_move(self):
        self.assertNotEqual(
            self.sixteen["validation_run_id"], self.seventeen["validation_run_id"]
        )
        self.assertEqual(
            self.seventeen["ruleset"]["normalized_digest_derivation"],
            NORMALIZED_DIGEST_DERIVATION,
        )
        self.assertEqual(self.seventeen["ruleset"]["version"], "2.2")


if __name__ == "__main__":
    unittest.main()
