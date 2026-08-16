"""Regression tests for the deterministic BCF 3.0 issue workflow."""

from __future__ import annotations

import math
import csv
import io
import shutil
import sys
import unittest
import uuid
import zipfile
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bcf_common import (  # noqa: E402
    FIXED_ZIP_TIMESTAMP,
    PROJECT_ROOT as COMMON_PROJECT_ROOT,
    SCHEMA_DIR,
    Aabb,
    Camera,
    read_safe_zip,
    verify_camera_frames_aabb,
    verify_schema_bundle,
)
from generate_bcf import (  # noqa: E402
    FINDINGS_PATH,
    IDS_PATH,
    INVENTORY_PATH,
    MODELS_PATH,
    RAW_DATA_DIR,
    build_workflow_artifacts,
    write_workflow_outputs,
)
from validate_bcf import load_bcf_package, validate_bcf_workflow  # noqa: E402


@contextmanager
def writable_test_directory(prefix: str):
    """Avoid Python 3.14 TemporaryDirectory's restrictive Windows ACL mode."""

    path = PROJECT_ROOT / "tests" / f".{prefix}-{uuid.uuid4().hex}"
    path.mkdir(mode=0o777)
    try:
        yield path
    finally:
        shutil.rmtree(path)


class BcfWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if PROJECT_ROOT != COMMON_PROJECT_ROOT:
            raise AssertionError("Test and workflow project roots differ")
        cls.artifacts = build_workflow_artifacts()

    def test_two_builds_are_byte_for_byte_deterministic(self):
        second = build_workflow_artifacts()
        self.assertEqual(self.artifacts.bcf_bytes, second.bcf_bytes)
        self.assertEqual(self.artifacts.sidecar_bytes, second.sidecar_bytes)
        self.assertEqual(self.artifacts.sidecar_rows, second.sidecar_rows)

    def test_archive_has_canonical_explicit_topic_directories(self):
        with writable_test_directory("bcf-archive-test") as temporary_dir:
            path = temporary_dir / "issues.bcf"
            path.write_bytes(self.artifacts.bcf_bytes)
            entries = read_safe_zip(path)
            directories = [name for name in entries if name.endswith("/")]
            self.assertEqual(3, len(directories))
            self.assertTrue(all(entries[name] == b"" for name in directories))
            loaded = load_bcf_package(path)
            self.assertEqual("3.0", loaded["version"])
            self.assertEqual(3, len(loaded["topics"]))

    def test_world_aabb_camera_frames_every_corner_and_aims_at_center(self):
        rows = self.artifacts.sidecar_rows["bcf_viewpoints.csv"]
        self.assertEqual(3, len(rows))
        for row in rows:
            minimum = tuple(float(row[f"aabb_min_{axis}"]) for axis in "xyz")
            maximum = tuple(float(row[f"aabb_max_{axis}"]) for axis in "xyz")
            # The sample's local element geometry starts near zero. These positive
            # X/Y values prove that USE_WORLD_COORDS was applied before the AABB.
            self.assertGreater(minimum[0], 7.0)
            self.assertGreater(minimum[1], 7.0)
            aabb = Aabb(minimum=minimum, maximum=maximum)
            camera = Camera(
                position=tuple(
                    float(row[f"camera_view_point_{axis}"]) for axis in "xyz"
                ),
                direction=tuple(
                    float(row[f"camera_direction_{axis}"]) for axis in "xyz"
                ),
                up=tuple(float(row[f"camera_up_{axis}"]) for axis in "xyz"),
                target=tuple(float(row[f"target_{axis}"]) for axis in "xyz"),
                field_of_view=float(row["field_of_view"]),
                aspect_ratio=float(row["aspect_ratio"]),
            )
            verify_camera_frames_aabb(aabb, camera)
            aim = tuple(
                target - origin
                for target, origin in zip(
                    camera.target,
                    camera.position,
                    strict=True,
                )
            )
            length = math.sqrt(sum(value * value for value in aim))
            normalized = tuple(value / length for value in aim)
            self.assertTrue(
                all(
                    abs(left - right) < 2e-6
                    for left, right in zip(
                        normalized,
                        camera.direction,
                        strict=True,
                    )
                )
            )

    def test_written_outputs_reload_with_exact_counts_and_lineage(self):
        with writable_test_directory("bcf-workflow-test") as root:
            bcf_path = root / "reports" / "bcf" / "ids_failures.bcf"
            manifest_path = root / "reports" / "bcf" / "run_manifest.json"
            sidecar_dir = root / "data" / "processed"
            write_workflow_outputs(
                self.artifacts,
                bcf_output=bcf_path,
                sidecar_dir=sidecar_dir,
                manifest_output=manifest_path,
                findings_path=FINDINGS_PATH,
                models_path=MODELS_PATH,
                inventory_path=INVENTORY_PATH,
                raw_data_dir=RAW_DATA_DIR,
                ids_path=IDS_PATH,
                schema_dir=SCHEMA_DIR,
            )
            result = validate_bcf_workflow(
                bcf_path=bcf_path,
                findings_path=FINDINGS_PATH,
                models_path=MODELS_PATH,
                inventory_path=INVENTORY_PATH,
                raw_data_dir=RAW_DATA_DIR,
                sidecar_dir=sidecar_dir,
                manifest_path=manifest_path,
                ids_path=IDS_PATH,
                schema_dir=SCHEMA_DIR,
            )
            self.assertEqual(3, result["topics"])
            self.assertEqual(3, result["viewpoints"])
            self.assertEqual(3, result["components"])
            self.assertEqual(6, result["finding_links"])
            manifest_paths = {
                record["path"] for record in result["manifest"]["outputs"]
            }
            self.assertNotIn(
                manifest_path.relative_to(PROJECT_ROOT).as_posix(),
                manifest_paths,
            )

    def test_unsafe_zip_member_is_rejected(self):
        with writable_test_directory("bcf-unsafe-test") as temporary_dir:
            path = temporary_dir / "unsafe.bcf"
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
                info = zipfile.ZipInfo("../outside.txt", FIXED_ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 0
                info.external_attr = 0o600 << 16
                archive.writestr(info, b"unsafe")
            with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
                read_safe_zip(path)

    def test_schema_hash_gate_fails_closed(self):
        with writable_test_directory("bcf-schema-test") as temporary_dir:
            copied = temporary_dir / "Schemas"
            shutil.copytree(SCHEMA_DIR, copied)
            markup = copied / "markup.xsd"
            markup.write_bytes(markup.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_schema_bundle(copied)

    @contextmanager
    def _mutated_csv(self, source: Path, mutate):
        rows = []
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames
            rows = list(reader)
        if columns is None:
            raise AssertionError("Test fixture CSV has no header")
        mutate(rows)
        with writable_test_directory("bcf-input-test") as directory:
            path = directory / source.name
            output = io.StringIO(newline="")
            writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            path.write_bytes(b"\xef\xbb\xbf" + output.getvalue().encode("utf-8"))
            yield path

    def _assert_findings_mutation_rejected(self, mutate, message: str):
        with self._mutated_csv(FINDINGS_PATH, mutate) as path:
            with self.assertRaisesRegex(ValueError, message):
                build_workflow_artifacts(findings_path=path)

    def test_fail_closed_source_contract_mutations(self):
        def change_run(rows):
            row = next(row for row in rows if row["status"] == "FAIL")
            row["run_id"] = "different-run"
            row["finding_key"] = ""

        def duplicate_finding(rows):
            indexes = [
                index for index, row in enumerate(rows) if row["status"] == "FAIL"
            ]
            rows[indexes[1]] = dict(rows[indexes[0]])

        def use_unknown_element(rows):
            row = next(row for row in rows if row["status"] == "FAIL")
            row["element_key"] = "hvac::unknown"
            row["finding_key"] = ""

        mutations = (
            (
                change_run,
                "exactly one IDS run",
            ),
            (
                duplicate_finding,
                "finding_key values are not unique",
            ),
            (
                use_unknown_element,
                "unknown element_key",
            ),
            (
                lambda rows: next(
                    row for row in rows if row["status"] == "FAIL"
                ).update(global_id="0000000000000000000000"),
                "Finding/inventory mismatch",
            ),
            (
                lambda rows: next(
                    row for row in rows if row["status"] == "FAIL"
                ).update(requirement_key="11111111-1111-5111-8111-111111111111"),
                "requirement_key does not match",
            ),
            (
                lambda rows: next(
                    row for row in rows if row["status"] == "FAIL"
                ).update(finding_key="11111111-1111-5111-8111-111111111111"),
                "finding_key does not match",
            ),
            (
                lambda rows: next(
                    row for row in rows if row["status"] == "FAIL"
                ).update(specification_id="R-OTHER"),
                "specification_id does not match",
            ),
        )
        for mutate, message in mutations:
            with self.subTest(message=message):
                self._assert_findings_mutation_rejected(mutate, message)

    def test_models_csv_ifc_hash_mismatch_is_rejected(self):
        with self._mutated_csv(
            MODELS_PATH,
            lambda rows: next(
                row for row in rows if row["model_id"] == "hvac"
            ).update(content_sha256="0" * 64),
        ) as path:
            with self.assertRaisesRegex(ValueError, "IFC content hash mismatch"):
                build_workflow_artifacts(models_path=path)


if __name__ == "__main__":
    unittest.main()
