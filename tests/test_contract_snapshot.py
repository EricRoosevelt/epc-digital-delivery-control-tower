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
        counts = self.recorded["counts"]
        self.assertEqual(counts["models"], 3)
        self.assertEqual(counts["elements"], 39)
        self.assertEqual(counts["findings"], 47)
        self.assertEqual(counts["applicable"], 31)
        self.assertEqual(counts["issues"], 3)
        self.assertEqual(counts["by_status"], {"PASS": 25, "FAIL": 6, "N/A": 16})
        self.assertEqual(self.recorded["ruleset"]["requirements"], 9)

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


if __name__ == "__main__":
    unittest.main()
