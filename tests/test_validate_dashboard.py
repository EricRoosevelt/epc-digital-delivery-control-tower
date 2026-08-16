import csv
import json
import shutil
import unittest
import uuid
from collections import defaultdict
from pathlib import Path

from src.validate_dashboard import (
    DEFAULT_CONTRACT_PATH,
    INVENTORY_GLOBAL_ID_COLUMN,
    SPECKLE_IFC_GUID_COLUMN,
    DashboardValidationError,
    validate_contract,
    validate_core,
    validate_dashboard,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIXTURE_PARENT = PROJECT_ROOT / "dashboard" / "local" / "test-fixtures"


def remove_test_fixture(path):
    resolved = path.resolve()
    expected_parent = FIXTURE_PARENT.resolve()
    if resolved.parent != expected_parent:
        raise RuntimeError(f"Refusing to remove unexpected test path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_full_fixture(root):
    processed_dir = root / "processed"
    processed_dir.mkdir(parents=True)
    for name in ("models.csv", "model_inventory.csv", "ids_findings.csv"):
        shutil.copyfile(SOURCE_PROCESSED_DIR / name, processed_dir / name)

    core = validate_core(processed_dir)
    issue_findings_by_element = defaultdict(list)
    for finding in core.issue_findings:
        issue_findings_by_element[finding["element_key"]].append(finding)

    topic_rows = []
    topic_finding_rows = []
    viewpoint_rows = []
    component_rows = []
    for element_key in sorted(issue_findings_by_element):
        element = core.elements_by_key[element_key]
        topic_guid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"topic:{element_key}"))
        viewpoint_guid = str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"viewpoint:{element_key}")
        )
        topic_rows.append(
            {
                "run_id": core.run_id,
                "topic_guid": topic_guid,
                "topic_status": "Open",
                "model_id": element["model_id"],
                "element_key": element_key,
                "global_id": element["global_id"],
                "finding_count": "2",
            }
        )
        for finding in issue_findings_by_element[element_key]:
            topic_finding_rows.append(
                {
                    "run_id": core.run_id,
                    "topic_guid": topic_guid,
                    "finding_key": finding["finding_key"],
                    "requirement_key": finding["requirement_key"],
                    "model_id": element["model_id"],
                    "element_key": element_key,
                    "global_id": element["global_id"],
                }
            )
        viewpoint_rows.append(
            {
                "run_id": core.run_id,
                "viewpoint_guid": viewpoint_guid,
                "topic_guid": topic_guid,
                "model_id": element["model_id"],
                "element_key": element_key,
                "global_id": element["global_id"],
            }
        )
        component_rows.append(
            {
                "run_id": core.run_id,
                "viewpoint_guid": viewpoint_guid,
                "topic_guid": topic_guid,
                "component_index": "1",
                "model_id": element["model_id"],
                "element_key": element_key,
                "global_id": element["global_id"],
            }
        )

    write_csv(processed_dir / "bcf_topics.csv", topic_rows)
    write_csv(processed_dir / "bcf_topic_findings.csv", topic_finding_rows)
    write_csv(processed_dir / "bcf_viewpoints.csv", viewpoint_rows)
    write_csv(processed_dir / "bcf_viewpoint_components.csv", component_rows)

    non_renderable_counts = {
        "architecture": 4,
        "structural": 2,
        "hvac": 1,
    }
    non_renderable = set()
    for model_id, expected_count in non_renderable_counts.items():
        eligible = [
            row
            for row in sorted(core.elements, key=lambda item: item["element_key"])
            if row["model_id"] == model_id
            and row["element_key"] not in core.issue_element_keys
        ]
        non_renderable.update(
            row["element_key"]
            for row in eligible[:expected_count]
        )
    mapping_rows = []
    for index, element in enumerate(
        sorted(core.elements, key=lambda item: item["element_key"]),
        start=1,
    ):
        model_id = element["model_id"]
        mapping_rows.append(
            {
                "model_id": model_id,
                SPECKLE_IFC_GUID_COLUMN: element["global_id"],
                INVENTORY_GLOBAL_ID_COLUMN: element["global_id"],
                "speckle_object_id": f"object-{index:02d}",
                "speckle_model_version_url": (
                    "https://app.speckle.systems/projects/project-001/models/"
                    f"{model_id}-model@version-{model_id}"
                ),
                "has_representation": str(
                    element["element_key"] not in non_renderable
                ).lower(),
                "highlight_verified": str(
                    element["element_key"] in core.issue_element_keys
                ).lower(),
            }
        )
    mapping_path = root / "local" / "speckle_mapping.csv"
    write_csv(mapping_path, mapping_rows)
    urls_by_model = {
        row["model_id"]: row["speckle_model_version_url"]
        for row in mapping_rows
    }
    connections_path = root / "local" / "speckle_connections.json"
    write_json(
        connections_path,
        {
            "federation_url": (
                "https://app.speckle.systems/projects/project-001/"
                "models/control-tower-federation"
            ),
            "models": [
                {
                    "model_id": model_id,
                    "model_version_url": urls_by_model[model_id],
                    "source_filename": core.models_by_id[model_id]["filename"],
                    "ifc_sha256": core.models_by_id[model_id]["content_sha256"],
                    "upload_route": "direct_ifc",
                }
                for model_id in ("architecture", "structural", "hvac")
            ],
        },
    )
    return processed_dir, mapping_path, connections_path, core


class DashboardValidationTests(unittest.TestCase):
    def make_fixture_root(self):
        root = FIXTURE_PARENT / self._testMethodName
        remove_test_fixture(root)
        root.mkdir(parents=True)
        self.addCleanup(remove_test_fixture, root)
        return root

    def test_contract_locks_nine_tables_and_two_bidirectional_relationships(self):
        contract = validate_contract(DEFAULT_CONTRACT_PATH)
        tables = contract["semantic_model"]["tables"]
        relationships = contract["semantic_model"]["relationships"]

        self.assertEqual(len(tables), 9)
        self.assertEqual(len(relationships), 8)
        self.assertEqual(
            sum(item["cross_filter"] == "both" for item in relationships),
            2,
        )
        self.assertEqual(
            contract["speckle_connections"]["model_entry_fields"],
            [
                "model_id",
                "model_version_url",
                "source_filename",
                "ifc_sha256",
                "upload_route",
            ],
        )
        self.assertEqual(
            contract["speckle_connections"]["federation_url_role"],
            "audit_only",
        )

    def test_repository_core_data_matches_locked_kpis(self):
        core = validate_core(SOURCE_PROCESSED_DIR)

        self.assertEqual(core.summary["table_rows"]["DimElement"], 39)
        self.assertEqual(core.summary["table_rows"]["FactIDSCheck"], 31)
        self.assertEqual(core.summary["kpis"]["failed_checks"], 6)
        self.assertEqual(len({row["global_id"] for row in core.elements}), 32)

    def test_full_fixture_passes_all_offline_acceptance_checks(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)

        result = validate_dashboard(
            processed_dir=processed_dir,
            mapping_path=mapping_path,
            connections_path=connections_path,
            contract_path=DEFAULT_CONTRACT_PATH,
            mode="full",
        )

        self.assertEqual(result["table_rows"]["DimTopic"], 3)
        self.assertEqual(result["kpis"]["bcf_lineage_coverage"], 1.0)
        self.assertEqual(result["speckle_mapping"]["semantic_identity"]["mapped"], 39)
        self.assertEqual(
            result["speckle_mapping"]["semantic_identity"]["mapped_by_model"],
            {"architecture": 15, "structural": 18, "hvac": 6},
        )
        self.assertEqual(
            result["speckle_mapping"]["semantic_identity"][
                "unique_speckle_object_ids"
            ],
            39,
        )
        self.assertEqual(result["speckle_mapping"]["render_mapping"]["renderable"], 32)
        self.assertEqual(
            result["speckle_mapping"]["render_mapping"]["renderable_by_model"],
            {"architecture": 11, "structural": 16, "hvac": 5},
        )
        self.assertEqual(
            result["speckle_mapping"]["render_mapping"][
                "non_renderable_by_model"
            ],
            {"architecture": 4, "structural": 2, "hvac": 1},
        )
        self.assertEqual(result["speckle_connections"]["model_count"], 3)
        self.assertEqual(
            result["speckle_connections"]["federation_url_role"],
            "audit_only",
        )
        self.assertEqual(
            set(result["speckle_connections"]["upload_routes"].values()),
            {"direct_ifc"},
        )
        self.assertEqual(result["acceptance"], "OFFLINE_DATA_CONTRACT_PASSED")
        self.assertTrue(
            all(count == 2 for count in result["topic_linked_finding_counts"].values())
        )

    def test_duplicate_composite_business_key_fails_closed(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        rows = read_csv(mapping_path)
        rows[-1] = dict(rows[0])
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Duplicate/ambiguous Speckle business keys",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_legacy_nested_property_headers_fail_closed(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        rows = read_csv(mapping_path)
        legacy_rows = []
        for row in rows:
            legacy_row = dict(row)
            legacy_row['properties["IFC GUID"]'] = legacy_row.pop(
                SPECKLE_IFC_GUID_COLUMN
            )
            legacy_row['properties["IFC Attributes"]["GlobalId"]'] = (
                legacy_row.pop(INVENTORY_GLOBAL_ID_COLUMN)
            )
            legacy_rows.append(legacy_row)
        write_csv(mapping_path, legacy_rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Missing columns.*inventory_global_id.*speckle_ifc_guid",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_speckle_object_ids_must_be_globally_unique(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        rows = read_csv(mapping_path)
        rows[-1]["speckle_object_id"] = rows[0]["speckle_object_id"]
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Duplicate Speckle object ID",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_renderable_distribution_by_model_fails_closed(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        rows = read_csv(mapping_path)
        architecture_non_renderable = next(
            row
            for row in rows
            if row["model_id"] == "architecture"
            and row["has_representation"] == "false"
        )
        structural_renderable = next(
            row
            for row in rows
            if row["model_id"] == "structural"
            and row["has_representation"] == "true"
        )
        architecture_non_renderable["has_representation"] = "true"
        structural_renderable["has_representation"] = "false"
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Renderable mapping distribution",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_full_mode_requires_ignored_connections_manifest(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections_path.unlink()

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Speckle connections JSON is missing",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_connection_urls_must_exactly_match_mapping(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
        connections["models"][0]["model_version_url"] = (
            "https://app.speckle.systems/projects/project-001/models/"
            "architecture-model@different-version"
        )
        write_json(connections_path, connections)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "must exactly match the mapping CSV",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_connection_model_entry_fields_are_exact(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
        connections["models"][0].pop("source_filename")
        write_json(connections_path, connections)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Speckle model entry 0 has contract drift",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_connection_source_filename_must_match_models_csv(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
        connections["models"][0]["source_filename"] = "Different-Architecture.ifc"
        write_json(connections_path, connections)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "must exactly match models.csv filename",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_connection_ifc_sha256_must_match_models_csv(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
        connections["models"][0]["ifc_sha256"] = "0" * 64
        write_json(connections_path, connections)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "must exactly match models.csv content_sha256",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_connection_upload_route_must_be_direct_ifc(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
        connections["models"][0]["upload_route"] = "revit"
        write_json(connections_path, connections)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "upload_route for architecture must be direct_ifc",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_inventory_global_id_mismatch_fails_closed(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, _ = build_full_fixture(root)
        rows = read_csv(mapping_path)
        rows[0][INVENTORY_GLOBAL_ID_COLUMN] = "different-guid"
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "IFC GUID cross-check failed",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_issue_highlight_must_be_verified(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, core = build_full_fixture(root)
        rows = read_csv(mapping_path)
        for row in rows:
            business_key = (row["model_id"], row[SPECKLE_IFC_GUID_COLUMN])
            element = core.elements_by_business_key[business_key]
            if element["element_key"] in core.issue_element_keys:
                row["highlight_verified"] = "false"
                break
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Issue element highlight is not verified",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_non_issue_highlight_must_not_be_verified(self):
        root = self.make_fixture_root()
        processed_dir, mapping_path, connections_path, core = build_full_fixture(root)
        rows = read_csv(mapping_path)
        row = next(
            row
            for row in rows
            if row["has_representation"] == "true"
            and (
                row["model_id"],
                row[SPECKLE_IFC_GUID_COLUMN],
            )
            not in {
                (
                    core.elements_by_key[element_key]["model_id"],
                    core.elements_by_key[element_key]["global_id"],
                )
                for element_key in core.issue_element_keys
            }
        )
        row["highlight_verified"] = "true"
        write_csv(mapping_path, rows)

        with self.assertRaisesRegex(
            DashboardValidationError,
            "Exactly the three issue elements",
        ):
            validate_dashboard(
                processed_dir=processed_dir,
                mapping_path=mapping_path,
                connections_path=connections_path,
                contract_path=DEFAULT_CONTRACT_PATH,
                mode="full",
            )

    def test_core_mode_is_explicitly_not_full_acceptance(self):
        result = validate_dashboard(
            processed_dir=SOURCE_PROCESSED_DIR,
            mapping_path=Path("unused.csv"),
            contract_path=DEFAULT_CONTRACT_PATH,
            mode="core",
        )

        self.assertEqual(result["acceptance"], "CORE_ONLY_NOT_STAGE_3B_COMPLETE")


if __name__ == "__main__":
    unittest.main()
