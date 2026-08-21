"""Layer three: the recorded contract snapshot, and the ceremony to move it.

The counts and digests a release published legitimately change — a column is
added, a rule is corrected, a model joins the project. What must not happen is
that they change by accident, or that somebody makes a red test green by
rewriting the expectation in the same commit that broke it.

So the snapshot lives in a file rather than in an assertion, `epc-ct snapshot`
compares against it, and refreshing it requires saying that the contract moved
*and* requires the CHANGELOG to already describe the change. The record of what
moved therefore exists before the expectation that says it did.
"""

from __future__ import annotations

import contextlib
import io
import unittest

from epc_control_tower import CONTRACT_VERSION
from epc_control_tower.cli import main
from epc_control_tower.snapshots import (
    changelog_mentions,
    compare_snapshots,
    load_snapshot,
    snapshot_path,
)
from helpers import PROJECT_ROOT, writable_test_directory

RECORDED = snapshot_path(PROJECT_ROOT, CONTRACT_VERSION)


def run_cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RecordedSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recorded = load_snapshot(RECORDED)

    def test_the_snapshot_exists_for_the_current_contract_version(self):
        self.assertEqual(self.recorded["contract_version"], CONTRACT_VERSION)

    def test_it_records_both_run_identities(self):
        # The canonical identity moves when a checker's version or
        # configuration moves, which is a real change to what a validation is.
        # The legacy one is what every published key is built on and must not
        # move while the adapter exists. Recording one would hide half of what
        # a refresh agrees to.
        self.assertEqual(self.recorded["legacy_run_id"], "ids-v0.1-8706ef58303bfd11")
        self.assertNotEqual(
            self.recorded["validation_run_id"], self.recorded["legacy_run_id"]
        )

    def test_it_records_the_published_counts(self):
        # Two projects: PCERT's three models and thirty-nine elements, plus the
        # reference-view project's three models and five.
        counts = self.recorded["counts"]
        self.assertEqual(counts["projects"], 2)
        self.assertEqual(counts["models"], 6)
        self.assertEqual(counts["elements"], 44)
        self.assertEqual(counts["findings"], 121)
        self.assertEqual(counts["applicable"], 64)
        self.assertEqual(counts["issues"], 21)
        self.assertEqual(counts["by_status"], {"PASS": 40, "FAIL": 24, "N/A": 57})
        self.assertEqual(self.recorded["ruleset"]["requirements"], 14)

    def test_the_rule_set_is_the_declarative_one(self):
        self.assertEqual(self.recorded["ruleset"]["id"], "epc-delivery")
        self.assertEqual(self.recorded["ruleset"]["version"], "2.2")
        self.assertEqual(self.recorded["ruleset"]["requirements"], 14)

    def test_the_earlier_contract_is_kept_as_history(self):
        # A snapshot is per contract version, so bumping adds a record rather
        # than overwriting one. What 0.1 published stays readable.
        earlier = load_snapshot(snapshot_path(PROJECT_ROOT, "0.1"))
        self.assertEqual(earlier["contract_version"], "0.1")
        self.assertEqual(earlier["counts"]["projects"], 1)
        self.assertEqual(earlier["counts"]["findings"], 47)

    def test_the_legacy_contract_did_not_move_when_the_canonical_one_did(self):
        # The whole point of the bump: the canonical identity changed because
        # the run covers six models now, while every byte the dashboard reads
        # stayed where it was.
        earlier = load_snapshot(snapshot_path(PROJECT_ROOT, "0.1"))
        self.assertNotEqual(
            earlier["validation_run_id"], self.recorded["validation_run_id"]
        )
        self.assertEqual(earlier["legacy_run_id"], self.recorded["legacy_run_id"])
        for published in (
            "data/processed/ids_findings.csv",
            "data/processed/models.csv",
            "data/processed/model_inventory.csv",
            "data/processed/bcf_topics.csv",
            "data/processed/bcf_topic_findings.csv",
            "data/processed/bcf_topic_events.csv",
            "data/processed/bcf_viewpoints.csv",
            "data/processed/bcf_viewpoint_components.csv",
            "reports/bcf/ids_failures.bcf",
        ):
            with self.subTest(artifact=published):
                self.assertEqual(
                    earlier["artifacts"][published],
                    self.recorded["artifacts"][published],
                )

    def test_it_records_the_published_digests(self):
        artifacts = self.recorded["artifacts"]
        self.assertEqual(
            artifacts["data/processed/ids_findings.csv"],
            "ea7d2fa2cd1690eb8b791dcab2792f116238566f0c60b10b64f1b02ce504eb4d",
        )
        self.assertEqual(
            artifacts["reports/bcf/ids_failures.bcf"],
            "b3c6f51abc9647ef4baeee9f9bccd884094b362362e516778c4bf083326abc99",
        )

    def test_every_recorded_artifact_is_present_with_the_recorded_digest(self):
        from epc_control_tower.determinism import sha256_file

        for relative, digest in self.recorded["artifacts"].items():
            path = PROJECT_ROOT / relative
            with self.subTest(artifact=relative):
                self.assertTrue(path.is_file(), f"{relative} is missing")
                self.assertEqual(sha256_file(path), digest)

    def test_the_changelog_describes_this_contract_version(self):
        self.assertTrue(changelog_mentions(PROJECT_ROOT, CONTRACT_VERSION))


class ComparisonTests(unittest.TestCase):
    def test_an_identical_snapshot_reports_no_differences(self):
        recorded = load_snapshot(RECORDED)
        self.assertEqual(compare_snapshots(recorded, dict(recorded)), [])

    def test_a_changed_digest_is_named(self):
        recorded = load_snapshot(RECORDED)
        changed = dict(recorded)
        changed["artifacts"] = dict(recorded["artifacts"])
        changed["artifacts"]["data/processed/ids_findings.csv"] = "0" * 64
        differences = compare_snapshots(recorded, changed)
        self.assertEqual(len(differences), 1)
        self.assertIn("artifact changed: data/processed/ids_findings.csv", differences[0])

    def test_a_new_or_missing_artifact_is_named(self):
        recorded = load_snapshot(RECORDED)
        fewer = dict(recorded)
        fewer["artifacts"] = {
            key: value
            for key, value in recorded["artifacts"].items()
            if key != "reports/bcf/ids_failures.bcf"
        }
        self.assertEqual(
            compare_snapshots(recorded, fewer),
            ["artifact no longer produced: reports/bcf/ids_failures.bcf"],
        )
        self.assertEqual(
            compare_snapshots(fewer, recorded),
            ["artifact added: reports/bcf/ids_failures.bcf"],
        )

    def test_a_moved_count_is_named_alongside_a_moved_digest(self):
        recorded = load_snapshot(RECORDED)
        changed = dict(recorded)
        changed["counts"] = dict(recorded["counts"], findings=48)
        changed["legacy_run_id"] = "ids-v0.1-somethingelse"
        differences = compare_snapshots(recorded, changed)
        self.assertEqual(len(differences), 2)


class RefreshCeremonyTests(unittest.TestCase):
    def test_a_refresh_without_acknowledgement_is_refused(self):
        code, _, err = run_cli("snapshot", "--refresh")
        self.assertEqual(code, 2)
        self.assertIn("Pass --contract-changed", err)

    def test_a_refresh_is_refused_until_the_changelog_describes_the_version(self):
        with writable_test_directory("snapshot-no-changelog") as scratch:
            # A repository root with no CHANGELOG at all.
            code, _, err = run_cli(
                "--repository-root",
                str(scratch),
                "snapshot",
                "--refresh",
                "--contract-changed",
            )
        self.assertNotEqual(code, 0)

    def test_verifying_the_shipped_snapshot_passes(self):
        # Deliberately against the repository's own configured locations: the
        # snapshot records repository-relative paths, so redirecting the output
        # would compare a different set of files and prove nothing. This
        # rewrites the tracked artifacts with the bytes they already contain,
        # which the determinism layer establishes is a no-op.
        code, out, err = run_cli("snapshot")
        self.assertEqual(code, 0, err)
        self.assertIn("matches", out)


class RuleSetVersionTests(unittest.TestCase):
    """A `(ruleset_id, version)` pair names exactly one set of rules.

    The rule set had a version and it did not move: `epc-delivery v1.0` stood
    for three contracts while the rules went from seven to twelve, so the tag
    named three different rule sets and `ids/epc-delivery_v1.0.ids` held three
    different byte sequences.

    Nothing broke, which is why nobody noticed. The normalized digest carries
    identity and moved every time; the tag carries the *name*, and a name that
    points at three things is worse than none. So the tag is not discretionary
    and it did not get a ceremony of its own — it rides on the refresh, which
    is already the moment somebody says what moved.
    """

    def test_the_shipped_rule_set_does_not_reuse_a_version(self):
        from epc_control_tower.snapshots import ruleset_version_conflicts

        recorded = load_snapshot(RECORDED)
        self.assertEqual(ruleset_version_conflicts(PROJECT_ROOT, recorded), [])

    def test_the_two_refreshes_that_should_not_have_happened_are_refused(self):
        # The counterfactual, pinned. Contracts 1.2 and 1.3 were both refreshed
        # with the rule set tagged v1.0 and different rules underneath it. Offer
        # either of those recorded snapshots to the guard and it refuses.
        from epc_control_tower.snapshots import (
            load_snapshot,
            ruleset_version_conflicts,
            snapshot_path,
        )

        for version in ("1.2", "1.3"):
            with self.subTest(contract=version):
                recorded = load_snapshot(snapshot_path(PROJECT_ROOT, version))
                self.assertEqual(recorded["ruleset"]["version"], "1.0")
                conflicts = ruleset_version_conflicts(PROJECT_ROOT, recorded)
                self.assertTrue(conflicts)
                for conflict in conflicts:
                    self.assertIn("epc-delivery v1.0", conflict)

    def test_the_record_of_what_happened_is_left_alone(self):
        # Those snapshots are the account of what this repository actually did.
        # Rewriting them so a new rule looks retroactively obeyed would be the
        # same dishonesty the ceremony exists to prevent, so the breach stands
        # in the record and this test says so on purpose.
        from epc_control_tower.snapshots import load_snapshot, snapshot_path

        tagged = {
            version: load_snapshot(snapshot_path(PROJECT_ROOT, version))["ruleset"]
            for version in ("1.1", "1.2", "1.3")
        }
        self.assertEqual({r["version"] for r in tagged.values()}, {"1.0"})
        # One tag, three different rule sets, still on the record.
        self.assertEqual(len({r["normalized_digest"] for r in tagged.values()}), 3)

    def test_a_version_bump_alone_re_keys_everything(self):
        # Why the tag is not free to raise on a whim, measured rather than
        # assumed: changing only the tag, touching no rule, moves the digest,
        # the run id and every finding key.
        import shutil

        from epc_control_tower.rules import load_ruleset
        from helpers import writable_test_directory

        source = PROJECT_ROOT / "rules" / "epc-delivery"
        before = load_ruleset(source)
        with writable_test_directory("ruleset-version") as scratch:
            target = scratch / "epc-delivery"
            shutil.copytree(source, target)
            meta = target / "ruleset.toml"
            meta.write_text(
                meta.read_text(encoding="utf-8").replace(
                    'version = "2.2"', 'version = "2.3"'
                ),
                encoding="utf-8",
            )
            after = load_ruleset(target)

        self.assertEqual(before.version, "2.2")
        self.assertEqual(after.version, "2.3")
        self.assertNotEqual(before.normalized_digest, after.normalized_digest)
        # The requirements themselves are untouched, so their keys do not move.
        # Only what is built *on top of* the rule set does.
        self.assertEqual(
            {r.requirement_key for r in before.requirements},
            {r.requirement_key for r in after.requirements},
        )

    def test_the_compiled_document_is_named_for_the_version_it_holds(self):
        # The filename is what a delivery archives, so it carries the version.
        # It said v1.0 while holding three different documents; it must not
        # again.
        from epc_control_tower.rules import load_ruleset

        ruleset = load_ruleset(PROJECT_ROOT / "rules" / "epc-delivery")
        compiled = PROJECT_ROOT / "ids" / f"{ruleset.ruleset_id}_v{ruleset.version}.ids"
        self.assertTrue(compiled.is_file(), compiled)
        self.assertEqual(
            sorted(p.name for p in (PROJECT_ROOT / "ids").glob("epc-delivery*.ids")),
            [compiled.name],
        )


if __name__ == "__main__":
    unittest.main()
