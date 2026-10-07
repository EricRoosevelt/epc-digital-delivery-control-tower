"""Geometry is computed for the exporters that read it, and a run may say it has none.

Bounding boxes exist so that a BCF exporter can place a camera without reopening
a model. Nothing else reads them: the canonical CSV and JSON documents carry no
geometry. Until a run could say so, every run tessellated every element with a
failing finding, whichever exporters it ran, and an element with no shape —
an IFC object without a representation, which IFC allows — ended the whole run
with ``RuntimeError: Representation is NULL``. Measured on the Doctor's local
check (AGENTS.md rule 6): a check whose only exporter is JSON lost every result
over a box nothing was going to read.

These tests pin both halves: skipping geometry changes no canonical byte of the
shipped run, and a run that skips it refuses any exporter that would read it,
instead of failing halfway through an export.
"""

from __future__ import annotations

import dataclasses
import unittest

from epc_control_tower.determinism import sha256_file
from epc_control_tower.pipeline import build_bundle, execute
from epc_control_tower.registry import default_registry
from helpers import shipped_reports_dir, shipped_run_config, writable_test_directory


class GeometryOnlyWhereReadTests(unittest.TestCase):
    def test_a_run_without_geometry_has_none_and_the_default_still_does(self):
        config = shipped_run_config()
        reports = shipped_reports_dir()
        default = build_bundle(config, reports_dir=reports).bundle
        skipped = build_bundle(config, reports_dir=reports, with_geometry=False).bundle
        self.assertGreater(len(default.geometry), 0)
        self.assertEqual(skipped.geometry, ())
        self.assertEqual(
            dataclasses.replace(skipped, geometry=default.geometry), default
        )

    def test_skipping_geometry_moves_no_canonical_byte(self):
        with writable_test_directory("geometry-skip") as scratch:
            config = dataclasses.replace(
                shipped_run_config(),
                processed_data_dir=scratch / "processed",
                reports_dir=scratch / "reports",
            )
            digests = []
            for with_geometry in (True, False):
                execute(config, exporter_ids=("csv", "json"), with_geometry=with_geometry)
                digests.append(
                    {
                        path.relative_to(scratch).as_posix(): sha256_file(path)
                        for path in sorted(scratch.rglob("*"))
                        if path.is_file()
                    }
                )
        self.assertGreater(len(digests[0]), 10)
        self.assertEqual(digests[0], digests[1])

    def test_only_the_canonical_exporters_say_they_read_no_geometry(self):
        registry = default_registry(shipped_run_config())
        free = sorted(
            exporter_id
            for exporter_id, exporter in registry.exporters.items()
            if getattr(exporter, "reads_geometry", True) is False
        )
        self.assertEqual(free, ["csv", "json"])

    def test_a_run_without_geometry_refuses_an_exporter_that_reads_it(self):
        with writable_test_directory("geometry-refused") as scratch:
            config = dataclasses.replace(
                shipped_run_config(),
                processed_data_dir=scratch / "processed",
                reports_dir=scratch / "reports",
            )
            with self.assertRaisesRegex(ValueError, r"without geometry.*bcf"):
                execute(config, exporter_ids=("json", "bcf"), with_geometry=False)
            # Refused before anything ran: nothing was written.
            self.assertEqual(sorted(scratch.rglob("*")), [])


if __name__ == "__main__":
    unittest.main()
