"""The rule set version guard, once digests carry a derivation (ADR 0005 §5.5).

Contract 1.7 changes what the normalized digest covers — each requirement's
``semantics_digest`` joins it — while the rule set keeps its version, 2.2 (the
PM's P-2(b)). That leaves the guard facing one ``(ruleset_id, version)`` pair
recorded under two different digests, and the whole question of this module is
how it tells "the same rules, derived two ways" from "different rules, one
name" without ever letting a difference of derivation stand in for an answer.

The shape of every test here is the same: build a repository root in a scratch
directory with a copy of the recorded snapshots and the ledger, change one thing,
and read what the guard returns. The G-numbers are ADR 0005 §5.5.7's.

The derivation-2 digests in this module are stand-ins made by hashing a label.
The tests that use the real derivation-2 digest of the real rules, and of edited
copies of them, are in ``test_rule_semantics_identity.py``.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import unittest
from contextlib import contextmanager
from pathlib import Path

from epc_control_tower.determinism import json_bytes
from epc_control_tower.identity import KNOWN_NORMALIZED_DIGEST_DERIVATIONS
from epc_control_tower.snapshots import (
    DERIVATION_LEDGER_NAME,
    SNAPSHOT_DIRECTORY,
    load_snapshot,
    ruleset_version_conflicts,
    snapshot_path,
)
from helpers import PROJECT_ROOT, writable_test_directory

CONTRACTS = PROJECT_ROOT / SNAPSHOT_DIRECTORY

#: What the shipped rules declare, measured on ``11e4163``, ``4e05c03``,
#: ``c9cf3b2`` and ``9eda5e9`` (ADR 0005 §5.5.5, evidence two).
RULE_DEFINITIONS_DIGEST = (
    "a0953845e0a2205a1513a506cb3211a157011b29f9f066dbbfc1aab02f6f32b6"
)

#: Contract 1.6's record of epc-delivery v2.2, under derivation 1.
DERIVATION_1_DIGEST = (
    "c3be0db4aab74fc87bba53c8e4cf4842ff67a7cfef30fbfaf7aa86ba9d97e729"
)

HISTORICAL = ("0.1", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6")


def stand_in(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


#: A derivation-2 digest for epc-delivery v2.2. A stand-in: see the module note.
DERIVATION_2_DIGEST = stand_in("derivation-2 digest of the unchanged rules")


def codes(problems: list[str]) -> list[str]:
    """The ``[code]`` each problem starts with, in order."""

    found = []
    for problem in problems:
        assert problem.startswith("["), problem
        found.append(problem[1 : problem.index("]")])
    return found


def current_snapshot(
    *,
    digest: str = DERIVATION_2_DIGEST,
    derivation: object = 2,
    version: str = "2.2",
    ruleset_id: str = "epc-delivery",
) -> dict[str, object]:
    ruleset: dict[str, object] = {
        "id": ruleset_id,
        "version": version,
        "normalized_digest": digest,
        "requirements": 14,
    }
    if derivation is not None:
        ruleset["normalized_digest_derivation"] = derivation
    return {"contract_version": "9.9", "ruleset": ruleset}


def migration(**overrides) -> dict[str, object]:
    """The entry contract 1.7 is meant to carry, with the stand-in target."""

    entry = {
        "ruleset_id": "epc-delivery",
        "version": "2.2",
        "from": {"derivation": 1, "normalized_digest": DERIVATION_1_DIGEST},
        "to": {"derivation": 2, "normalized_digest": DERIVATION_2_DIGEST},
        "baseline": {
            "snapshot": "contract-1.6.json",
            "sha256": hashlib.sha256(
                (CONTRACTS / "contract-1.6.json").read_bytes()
            ).hexdigest(),
            "commit": "11e416364cfcd01ae85e2abfa5de3a94c793a725",
        },
        "evidence": {
            "rule_definitions_digest": RULE_DEFINITIONS_DIGEST,
            "rules_git_tree": {
                "path": "rules/epc-delivery",
                "tree": "de7a6b0e7c29aca72b896a4e1bd2746afb94ee88",
                "measured_at": ["11e416364cfcd01ae85e2abfa5de3a94c793a725"],
            },
        },
    }
    for path, value in overrides.items():
        target = entry
        *parents, leaf = path.split(".")
        for parent in parents:
            target = target[parent]
        target[leaf] = value
    return entry


@contextmanager
def repository(*, migrations: list | None = None, derivation_1_only: bool = True):
    """A repository root holding the historical snapshots and a ledger.

    Only the eight snapshots recorded before derivations were written down are
    copied, and the ledger is the shipped one with ``migrations`` replaced. That
    keeps these tests about the guard rather than about whichever contract the
    repository happens to be at.
    """

    with writable_test_directory("derivation-guard") as root:
        contracts = root / SNAPSHOT_DIRECTORY
        contracts.mkdir(parents=True)
        for version in HISTORICAL:
            shutil.copyfile(
                CONTRACTS / f"contract-{version}.json",
                contracts / f"contract-{version}.json",
            )
        ledger = json.loads((CONTRACTS / DERIVATION_LEDGER_NAME).read_text("utf-8"))
        if derivation_1_only:
            ledger["derivation_1_snapshots"] = [
                entry
                for entry in ledger["derivation_1_snapshots"]
                if entry["name"] in {f"contract-{v}.json" for v in HISTORICAL}
            ]
        ledger["migrations"] = list(migrations or [])
        (contracts / DERIVATION_LEDGER_NAME).write_bytes(json_bytes(ledger))
        yield root


def guard(root: Path, current, digest: str | None = RULE_DEFINITIONS_DIGEST):
    return ruleset_version_conflicts(root, current, rule_definitions_digest=digest)


class TheLedgerTests(unittest.TestCase):
    """The closed list is data in ``docs/contracts/``, and it is exact."""

    def test_the_closed_list_names_the_eight_historical_snapshots_by_hash(self):
        ledger = json.loads((CONTRACTS / DERIVATION_LEDGER_NAME).read_text("utf-8"))
        listed = {e["name"]: e["sha256"] for e in ledger["derivation_1_snapshots"]}
        self.assertEqual(
            sorted(listed), [f"contract-{version}.json" for version in HISTORICAL]
        )
        for name, sha in listed.items():
            with self.subTest(snapshot=name):
                self.assertEqual(
                    hashlib.sha256((CONTRACTS / name).read_bytes()).hexdigest(), sha
                )
                self.assertNotIn(
                    "normalized_digest_derivation",
                    load_snapshot(CONTRACTS / name)["ruleset"],
                )

    def test_the_ledger_is_never_read_as_a_snapshot(self):
        self.assertFalse(
            DERIVATION_LEDGER_NAME.startswith("contract-"), DERIVATION_LEDGER_NAME
        )

    def test_the_package_knows_exactly_two_derivations(self):
        self.assertEqual(KNOWN_NORMALIZED_DIGEST_DERIVATIONS, frozenset({1, 2}))

    def test_a_missing_ledger_refuses_everything(self):
        with repository() as root:
            (root / SNAPSHOT_DIRECTORY / DERIVATION_LEDGER_NAME).unlink()
            self.assertEqual(
                codes(guard(root, current_snapshot())), ["derivation-ledger-missing"]
            )

    def test_a_malformed_ledger_refuses_rather_than_skipping_an_entry(self):
        broken = {
            "an unknown key": lambda ledger: ledger.update(extra=1),
            "a listed name that is not a snapshot": lambda ledger: ledger[
                "derivation_1_snapshots"
            ].append({"name": "notes.json", "sha256": "0" * 64}),
            "a listed name twice": lambda ledger: ledger[
                "derivation_1_snapshots"
            ].append(dict(ledger["derivation_1_snapshots"][0])),
            "a short hash": lambda ledger: ledger["derivation_1_snapshots"][0].update(
                sha256="abc"
            ),
            "a migration missing its evidence": lambda ledger: ledger[
                "migrations"
            ].append({k: v for k, v in migration().items() if k != "evidence"}),
            "a migration within one derivation": lambda ledger: ledger[
                "migrations"
            ].append(migration(**{"to.derivation": 1})),
            "a derivation given as a string": lambda ledger: ledger["migrations"].append(
                migration(**{"to.derivation": "2"})
            ),
            "two migrations for one version": lambda ledger: ledger["migrations"].extend(
                [migration(), migration(**{"to.normalized_digest": stand_in("other")})]
            ),
        }
        for label, mutate in broken.items():
            with self.subTest(label), repository(migrations=[migration()]) as root:
                path = root / SNAPSHOT_DIRECTORY / DERIVATION_LEDGER_NAME
                ledger = json.loads(path.read_text("utf-8"))
                mutate(ledger)
                path.write_bytes(json_bytes(ledger))
                self.assertEqual(
                    codes(guard(root, current_snapshot())),
                    ["derivation-ledger-invalid"],
                )


class CrossDerivationTests(unittest.TestCase):
    """G1–G5 and G10: across derivations, nothing passes unless proved."""

    def test_g1_without_a_migration_entry_v2_2_under_derivation_2_conflicts_once(self):
        with repository() as root:
            problems = guard(root, current_snapshot())
        self.assertEqual(codes(problems), ["derivation-migration-missing"])
        self.assertIn("contract-1.6.json", problems[0])

    def test_g2_the_right_migration_entry_is_the_only_thing_that_passes(self):
        with repository(migrations=[migration()]) as root:
            self.assertEqual(guard(root, current_snapshot()), [])

    def test_g3_a_different_derivation_2_digest_is_not_covered_by_the_entry(self):
        # The rules were edited after the entry was written: the derivation-2
        # digest now is not the entry's target.
        with repository(migrations=[migration()]) as root:
            problems = guard(
                root, current_snapshot(digest=stand_in("R-002 dataType edited"))
            )
        self.assertEqual(codes(problems), ["derivation-migration-missing"])

    def test_g4_an_entry_whose_source_is_not_what_1_6_recorded_proves_nothing(self):
        wrong = migration(**{"from.normalized_digest": stand_in("not c3be")})
        with repository(migrations=[wrong]) as root:
            problems = guard(root, current_snapshot())
        self.assertEqual(codes(problems), ["derivation-migration-missing"])

    def test_g5_the_rules_must_still_be_the_rules_the_entry_was_written_for(self):
        with repository(migrations=[migration()]) as root:
            for digest in (stand_in("an instructions edit"), None):
                with self.subTest(rule_definitions_digest=digest):
                    self.assertEqual(
                        codes(guard(root, current_snapshot(), digest)),
                        ["migration-evidence-mismatch"],
                    )

    def test_the_baseline_must_be_the_named_snapshot_byte_for_byte(self):
        with repository(
            migrations=[migration(**{"baseline.sha256": stand_in("another 1.6")})]
        ) as root:
            self.assertEqual(
                codes(guard(root, current_snapshot())), ["migration-evidence-mismatch"]
            )

    def test_every_single_field_of_the_entry_matters(self):
        # The "no path where a different derivation passes" property, stated as
        # exhaustively as the entry has fields. Each mutation must refuse; none
        # may leave the guard silent.
        mutations = {
            "ruleset_id": "another-ruleset",
            "version": "2.3",
            "from.normalized_digest": stand_in("x"),
            "to.normalized_digest": stand_in("y"),
            "baseline.sha256": stand_in("z"),
            "evidence.rule_definitions_digest": stand_in("w"),
        }
        for path, value in mutations.items():
            with self.subTest(field=path), repository(
                migrations=[migration(**{path: value})]
            ) as root:
                self.assertTrue(guard(root, current_snapshot()), path)

    def test_the_entry_is_symmetric_but_never_looser(self):
        # 1.6 offered as the current run against a recorded derivation-2
        # snapshot: the same pair, read the other way round.
        with repository(migrations=[migration()]) as root:
            seventeen = current_snapshot()
            seventeen["contract_version"] = "1.7"
            (root / SNAPSHOT_DIRECTORY / "contract-1.7.json").write_bytes(
                json_bytes(seventeen)
            )
            sixteen = load_snapshot(CONTRACTS / "contract-1.6.json")
            self.assertEqual(guard(root, sixteen), [])
            self.assertEqual(
                codes(guard(root, sixteen, stand_in("different rules"))),
                ["migration-evidence-mismatch"],
            )

    def test_g10_after_1_7_is_recorded_a_further_facet_edit_conflicts_with_it(self):
        with repository(migrations=[migration()]) as root:
            seventeen = current_snapshot()
            seventeen["contract_version"] = "1.7"
            (root / SNAPSHOT_DIRECTORY / "contract-1.7.json").write_bytes(
                json_bytes(seventeen)
            )
            self.assertEqual(guard(root, current_snapshot()), [])
            edited = current_snapshot(digest=stand_in("R-002 dataType edited"))
            problems = guard(root, edited, stand_in("R-002 dataType edited"))
        self.assertEqual(
            codes(problems), ["derivation-migration-missing", "version-reused"]
        )
        self.assertIn("contract-1.6.json", problems[0])
        self.assertIn("contract-1.7.json", problems[1])


class UnestablishedDerivationTests(unittest.TestCase):
    """G6–G8: a derivation is established before anything is compared."""

    def test_g6_a_derivation_this_package_does_not_know_is_refused(self):
        with repository(migrations=[migration()]) as root:
            with self.subTest("the current run"):
                self.assertEqual(
                    codes(guard(root, current_snapshot(derivation=3))),
                    ["unknown-derivation"],
                )
            # Zero, and three spellings of two that are not the integer two.
            for value in (0, True, "2", 2.0):
                with self.subTest("the current run", value=value):
                    self.assertEqual(
                        codes(guard(root, current_snapshot(derivation=value))),
                        ["unknown-derivation"],
                    )
            with self.subTest("a recorded snapshot"):
                (root / SNAPSHOT_DIRECTORY / "contract-9.8.json").write_bytes(
                    json_bytes(current_snapshot(derivation=3))
                )
                self.assertEqual(
                    codes(guard(root, current_snapshot())), ["unknown-derivation"]
                )

    def test_g6_a_migration_naming_an_unknown_derivation_is_refused(self):
        entry = migration(**{"to.derivation": 3})
        with repository(migrations=[entry]) as root:
            self.assertEqual(
                codes(guard(root, current_snapshot(derivation=3))),
                ["unknown-derivation"],
            )

    def test_g7_an_unlisted_snapshot_without_a_derivation_is_refused(self):
        with repository(migrations=[migration()]) as root:
            with self.subTest("a recorded snapshot"):
                (root / SNAPSHOT_DIRECTORY / "contract-9.8.json").write_bytes(
                    json_bytes(current_snapshot(derivation=None))
                )
                self.assertEqual(
                    codes(guard(root, current_snapshot())),
                    ["snapshot-derivation-missing"],
                )
        with repository(migrations=[migration()]) as root:
            with self.subTest("the current run"):
                self.assertEqual(
                    codes(guard(root, current_snapshot(derivation=None))),
                    ["snapshot-derivation-missing"],
                )

    def test_g8_a_listed_snapshot_whose_bytes_moved_is_refused(self):
        rewrites = {
            "one byte of whitespace": lambda raw: raw + b"\n",
            "1.6 relabelled as derivation 2 with the new digest": lambda raw: json_bytes(
                {
                    **json.loads(raw),
                    "ruleset": {
                        **json.loads(raw)["ruleset"],
                        "normalized_digest": DERIVATION_2_DIGEST,
                        "normalized_digest_derivation": 2,
                    },
                }
            ),
        }
        for label, rewrite in rewrites.items():
            with self.subTest(label), repository(migrations=[migration()]) as root:
                path = root / SNAPSHOT_DIRECTORY / "contract-1.6.json"
                path.write_bytes(rewrite(path.read_bytes()))
                problems = guard(root, current_snapshot())
                self.assertEqual(codes(problems), ["historical-snapshot-altered"])
                self.assertIn("contract-1.6.json", problems[0])

    def test_g8_a_listed_snapshot_that_was_deleted_is_refused(self):
        # Deleting 1.6 would otherwise remove the only record the new digest
        # has to be reconciled with.
        with repository() as root:
            (root / SNAPSHOT_DIRECTORY / "contract-1.6.json").unlink()
            self.assertEqual(
                codes(guard(root, current_snapshot())), ["historical-snapshot-missing"]
            )


class HistoricalSnapshotTests(unittest.TestCase):
    """G9: what the guard said about the record before, it still says."""

    @staticmethod
    def same_derivation_answer(root: Path, current) -> list[str]:
        """The pre-derivation rule, recomputed here: one version, one digest."""

        ruleset = current["ruleset"]
        return sorted(
            path.name
            for path in (root / SNAPSHOT_DIRECTORY).glob("contract-*.json")
            if (was := load_snapshot(path)["ruleset"])["id"] == ruleset["id"]
            and was["version"] == ruleset["version"]
            and was["normalized_digest"] != ruleset["normalized_digest"]
        )

    def test_g9_the_1_2_and_1_3_counterexample_is_still_refused(self):
        with repository(migrations=[migration()]) as root:
            for version in ("1.2", "1.3"):
                with self.subTest(contract=version):
                    problems = guard(
                        root, load_snapshot(snapshot_path(root, version))
                    )
                    self.assertTrue(problems)
                    self.assertEqual(set(codes(problems)), {"version-reused"})
                    for problem in problems:
                        self.assertIn("epc-delivery v1.0", problem)

    def test_g9_every_historical_snapshot_gets_exactly_the_answer_it_got_before(self):
        with repository(migrations=[migration()]) as root:
            for version in HISTORICAL:
                with self.subTest(contract=version):
                    current = load_snapshot(snapshot_path(root, version))
                    problems = guard(root, current)
                    self.assertEqual(set(codes(problems)) - {"version-reused"}, set())
                    self.assertEqual(
                        sorted(p.split()[1] for p in problems),
                        self.same_derivation_answer(root, current),
                    )

    def test_a_historical_snapshot_is_recognised_as_the_current_run_by_its_bytes(self):
        # The only way a snapshot without the field is read as derivation 1 when
        # it has no file name: it would be written as exactly a listed file.
        with repository() as root:
            sixteen = load_snapshot(CONTRACTS / "contract-1.6.json")
            self.assertEqual(guard(root, sixteen), [])
            sixteen["counts"] = {**sixteen["counts"], "issues": -1}
            self.assertEqual(
                codes(guard(root, sixteen)), ["snapshot-derivation-missing"]
            )


if __name__ == "__main__":
    unittest.main()
