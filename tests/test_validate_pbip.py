import hashlib
import json
import re
import shutil
import unittest
from pathlib import Path

from src.validate_pbip import (
    DATA_SNAPSHOT_PATHS,
    DEFAULT_DASHBOARD_DIR,
    DEFAULT_PROJECT_NAME,
    EXPECTED_FILTER_INTERACTION_KEYS,
    EXPECTED_FILTER_RESULTS,
    EXPECTED_LIFECYCLE_KEYS,
    EXPECTED_OVERVIEW_RESULTS,
    EXPECTED_PRIVACY_KEYS,
    EXPECTED_RUN_ID,
    EXPECTED_SCREENSHOT_IDS,
    EXPECTED_SCREENSHOT_FILENAMES,
    EXPECTED_TOPIC_MAPPINGS,
    PbipValidationError,
    definition_tree_sha256,
    validate_pbip,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PARENT = PROJECT_ROOT / "dashboard" / "local" / "pbip-validator-tests"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def remove_fixture(path):
    resolved = path.resolve()
    expected_parent = FIXTURE_PARENT.resolve()
    if resolved.parent != expected_parent:
        raise RuntimeError(f"Refusing to remove unexpected test path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def copy_pbip_fixture(root):
    dashboard_dir = root / "dashboard"
    dashboard_dir.mkdir(parents=True)
    project_name = DEFAULT_PROJECT_NAME
    report_name = f"{project_name}.Report"
    model_name = f"{project_name}.SemanticModel"

    shutil.copy2(
        DEFAULT_DASHBOARD_DIR / f"{project_name}.pbip",
        dashboard_dir / f"{project_name}.pbip",
    )
    report_source = DEFAULT_DASHBOARD_DIR / report_name
    report_target = dashboard_dir / report_name
    report_target.mkdir()
    shutil.copy2(report_source / "definition.pbir", report_target / "definition.pbir")
    shutil.copytree(report_source / "definition", report_target / "definition")

    model_source = DEFAULT_DASHBOARD_DIR / model_name
    model_target = dashboard_dir / model_name
    model_target.mkdir()
    shutil.copy2(model_source / "definition.pbism", model_target / "definition.pbism")
    shutil.copytree(model_source / "definition", model_target / "definition")
    editor_settings_target = model_target / ".pbi"
    editor_settings_target.mkdir()
    shutil.copy2(
        model_source / ".pbi" / "editorSettings.json",
        editor_settings_target / "editorSettings.json",
    )
    return dashboard_dir


def visual_paths(dashboard_dir):
    return sorted(
        dashboard_dir.glob(
            f"{DEFAULT_PROJECT_NAME}.Report/definition/pages/*/visuals/*/visual.json"
        )
    )


def find_visual(dashboard_dir, visual_type, *, title=None):
    for path in visual_paths(dashboard_dir):
        document = json.loads(path.read_text(encoding="utf-8"))
        visual = document.get("visual", {})
        if visual.get("visualType") != visual_type:
            continue
        title_value = (
            visual.get("visualContainerObjects", {})
            .get("title", [{}])[0]
            .get("properties", {})
            .get("text", {})
            .get("expr", {})
            .get("Literal", {})
            .get("Value")
        )
        if title is None or title_value == f"'{title}'":
            return path, document
    raise AssertionError(f"Visual fixture is missing: {visual_type}/{title}")


def model_definition(dashboard_dir):
    return dashboard_dir / f"{DEFAULT_PROJECT_NAME}.SemanticModel" / "definition"


def report_definition(dashboard_dir):
    return dashboard_dir / f"{DEFAULT_PROJECT_NAME}.Report" / "definition"


def editor_settings_path(dashboard_dir):
    return (
        dashboard_dir
        / f"{DEFAULT_PROJECT_NAME}.SemanticModel"
        / ".pbi"
        / "editorSettings.json"
    )


def write_json(path, document):
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_acceptance_fixture(root, dashboard_dir):
    evidence_dir = root / "docs" / "evidence" / "stage_3b"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    screenshots = []
    for screenshot_id in sorted(EXPECTED_SCREENSHOT_IDS):
        filename = EXPECTED_SCREENSHOT_FILENAMES[screenshot_id]
        path = evidence_dir / filename
        path.write_bytes(PNG_SIGNATURE + f"fixture:{screenshot_id}".encode("utf-8"))
        screenshots.append(
            {
                "id": screenshot_id,
                "path": filename,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )

    settings = json.loads(editor_settings_path(dashboard_dir).read_text(encoding="utf-8"))
    field_serialized = "autodetectRelationships" in settings
    relationships_path = model_definition(dashboard_dir) / "relationships.tmdl"
    manifest = {
        "manifest_version": "0.1",
        "project": DEFAULT_PROJECT_NAME,
        "run_id": EXPECTED_RUN_ID,
        "desktop_version": "2.156.951.0",
        "captured_at": "2026-08-14T12:00:00+08:00",
        "tracked_definition_tree_sha256": definition_tree_sha256(
            dashboard_dir,
            report_definition(dashboard_dir),
            model_definition(dashboard_dir),
        ),
        "post_reopen_relationships_sha256": hashlib.sha256(
            relationships_path.read_bytes()
        ).hexdigest(),
        "post_reopen_relationship_count": 8,
        "data_snapshot": {
            key: hashlib.sha256(path.read_bytes()).hexdigest()
            for key, path in DATA_SNAPSHOT_PATHS.items()
        },
        "autodetect_relationships": {
            "editor_settings_field_serialized": field_serialized,
            "verification": (
                "editor_settings_serialized_false"
                if field_serialized
                else "manual_unserialized"
            ),
            "disabled_in_desktop": True,
            "screenshot_id": "autodetect-settings",
        },
        "lifecycle": {key: True for key in EXPECTED_LIFECYCLE_KEYS},
        "filter_interactions": {
            key: True for key in EXPECTED_FILTER_INTERACTION_KEYS
        },
        "overview_results": dict(EXPECTED_OVERVIEW_RESULTS),
        "filter_results": json.loads(json.dumps(EXPECTED_FILTER_RESULTS)),
        "topics": [
            {
                "topic_guid": topic_guid,
                "element_key": element_key,
                "selected_element_count": 1,
                "linked_finding_count": 2,
                "highlighted_element_count": 1,
                "screenshot_id": f"topic-{topic_guid}",
            }
            for topic_guid, element_key in sorted(EXPECTED_TOPIC_MAPPINGS.items())
        ],
        "screenshots": screenshots,
        "privacy_review": {key: True for key in EXPECTED_PRIVACY_KEYS},
    }
    manifest_path = evidence_dir / "acceptance_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path, manifest


class PbipStaticValidationTests(unittest.TestCase):
    def make_fixture(self, suffix="base"):
        root = FIXTURE_PARENT / f"{self._testMethodName}-{suffix}"
        remove_fixture(root)
        root.mkdir(parents=True)
        self.addCleanup(remove_fixture, root)
        dashboard_dir = copy_pbip_fixture(root)
        manifest_path, manifest = write_acceptance_fixture(root, dashboard_dir)
        return root, dashboard_dir, manifest_path, manifest

    def test_current_project_with_tracked_acceptance_passes_contract(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()

        result = validate_pbip(
            dashboard_dir,
            acceptance_manifest_path=manifest_path,
        )

        self.assertEqual(
            result["acceptance"],
            "PBIP_STATIC_CONTRACT_AND_EVIDENCE_INTEGRITY_PASSED",
        )
        self.assertEqual(result["tables"], 9)
        self.assertEqual(result["relationships"], 8)
        self.assertEqual(result["bidirectional_relationships"], 2)
        self.assertTrue(result["automatic_relationship_detection"]["disabled"])
        self.assertEqual(
            result["automatic_relationship_detection"]["verification"],
            "manual_unserialized",
        )
        self.assertEqual(result["fixed_kpi_measures"], 7)
        self.assertEqual(result["visuals"], 16)
        self.assertEqual(result["visual_counts"]["slicer"], 4)
        self.assertEqual(
            result["filter_bindings"],
            {
                "Assignee": "DimTopic[assigned_to]",
                "Discipline": "DimModel[discipline_label]",
                "Priority": "DimTopic[priority]",
                "Rule": "DimRequirement[specification_id]",
                "Topic": "DimTopic[title]",
            },
        )
        self.assertEqual(
            result["filter_paths_to_dim_element"]["Rule"],
            ["DimRequirement", "FactIDSCheck", "DimElement"],
        )
        self.assertEqual(
            result["speckle_route"],
            {
                "upload_route": "direct_ifc",
                "version_pinned_model_queries": 3,
                "federation_function": "Speckle.Models.Federate",
            },
        )
        self.assertEqual(result["acceptance_manifest"]["screenshots"], 5)
        self.assertEqual(result["acceptance_manifest"]["topics"], 3)

    def test_acceptance_manifest_is_mandatory(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        manifest_path.unlink()

        with self.assertRaisesRegex(PbipValidationError, "Acceptance manifest is missing"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_duplicate_manifest_json_key_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        manifest_path.write_text(
            '{"manifest_version":"0.1","manifest_version":"0.1"}',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Duplicate JSON key"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_stale_definition_tree_hash_fails_closed(self):
        _, dashboard_dir, manifest_path, manifest = self.make_fixture()
        manifest["tracked_definition_tree_sha256"] = "0" * 64
        write_json(manifest_path, manifest)

        with self.assertRaisesRegex(PbipValidationError, "definition tree SHA-256 is stale"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_capture_metadata_fails_closed(self):
        for suffix, field, value, message in (
            ("desktop", "desktop_version", "2.156", "four-part numeric"),
            ("timestamp", "captured_at", "2026-08-14T12:00:00", "RFC 3339"),
        ):
            with self.subTest(field=field):
                _, dashboard_dir, manifest_path, manifest = self.make_fixture(suffix)
                manifest[field] = value
                write_json(manifest_path, manifest)
                with self.assertRaisesRegex(PbipValidationError, message):
                    validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_stale_data_snapshot_hash_fails_closed(self):
        _, dashboard_dir, manifest_path, manifest = self.make_fixture()
        manifest["data_snapshot"]["bcf_sha256"] = "0" * 64
        write_json(manifest_path, manifest)

        with self.assertRaisesRegex(PbipValidationError, "Data snapshot SHA-256 is stale"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_post_reopen_relationship_claims_fail_closed(self):
        for suffix, field, value, message in (
            ("hash", "post_reopen_relationships_sha256", "0" * 64, "relationships SHA-256"),
            ("count", "post_reopen_relationship_count", 7, "relationship count"),
        ):
            with self.subTest(field=field):
                _, dashboard_dir, manifest_path, manifest = self.make_fixture(suffix)
                manifest[field] = value
                write_json(manifest_path, manifest)
                with self.assertRaisesRegex(PbipValidationError, message):
                    validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_screenshot_artifacts_fail_closed(self):
        root, dashboard_dir, manifest_path, manifest = self.make_fixture("missing")
        missing_name = manifest["screenshots"][0]["path"]
        (root / "docs" / "evidence" / "stage_3b" / missing_name).unlink()
        with self.assertRaisesRegex(PbipValidationError, "screenshot is missing"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        _, dashboard_dir, manifest_path, manifest = self.make_fixture("hash")
        manifest["screenshots"][0]["sha256"] = "0" * 64
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "screenshot SHA-256 mismatch"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        _, dashboard_dir, manifest_path, manifest = self.make_fixture("retired")
        manifest["screenshots"][0]["sha256"] = (
            "434d80ca151ce8995c1d6edb57eda783d8ce0b4bd9cc200679c000527a42cafe"
        )
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "Retired Mapping QA"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_screenshot_paths_and_directory_set_fail_closed(self):
        root, dashboard_dir, manifest_path, manifest = self.make_fixture("filename")
        manifest["screenshots"][0]["path"] = "renamed.png"
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "fixed acceptance filename"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        _, dashboard_dir, manifest_path, manifest = self.make_fixture("traversal")
        manifest["screenshots"][0]["path"] = "../escape.png"
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "direct relative PNG path"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        root, dashboard_dir, manifest_path, _ = self.make_fixture("extra")
        (root / "docs" / "evidence" / "stage_3b" / "extra.png").write_bytes(
            PNG_SIGNATURE + b"unexpected"
        )
        with self.assertRaisesRegex(PbipValidationError, "exactly match"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_manual_acceptance_claims_fail_closed(self):
        for suffix, section, key, message in (
            ("lifecycle", "lifecycle", "reopened", "lifecycle.reopened"),
            (
                "filter",
                "filter_interactions",
                "rule_drives_speckle_visual",
                "filter_interactions.rule_drives_speckle_visual",
            ),
            (
                "privacy",
                "privacy_review",
                "no_token_or_credentials",
                "privacy_review.no_token_or_credentials",
            ),
        ):
            with self.subTest(section=section, key=key):
                _, dashboard_dir, manifest_path, manifest = self.make_fixture(suffix)
                manifest[section][key] = False
                write_json(manifest_path, manifest)
                with self.assertRaisesRegex(PbipValidationError, message):
                    validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_manual_acceptance_result_values_fail_closed(self):
        _, dashboard_dir, manifest_path, manifest = self.make_fixture("overview")
        manifest["overview_results"]["total_elements"] = 38
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "Overview acceptance results"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        _, dashboard_dir, manifest_path, manifest = self.make_fixture("filter-results")
        manifest["filter_results"]["rule_r_005a"]["failed_check_count"] = 3
        write_json(manifest_path, manifest)
        with self.assertRaisesRegex(PbipValidationError, "Rule/Priority/Assignee"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_topic_mapping_drift_fails_closed(self):
        _, dashboard_dir, manifest_path, manifest = self.make_fixture()
        manifest["topics"][0]["element_key"] = "hvac::wrong"
        write_json(manifest_path, manifest)

        with self.assertRaisesRegex(PbipValidationError, "Topic-to-element"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_serialized_false_editor_setting_is_accepted_only_with_matching_manifest(self):
        root, dashboard_dir, _, _ = self.make_fixture()
        settings_path = editor_settings_path(dashboard_dir)
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["autodetectRelationships"] = False
        write_json(settings_path, settings)
        manifest_path, _ = write_acceptance_fixture(root, dashboard_dir)

        result = validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

        self.assertEqual(
            result["automatic_relationship_detection"]["verification"],
            "editor_settings_serialized_false",
        )
        self.assertTrue(
            result["automatic_relationship_detection"]["field_serialized"]
        )

    def test_true_editor_setting_cannot_be_overridden_by_manifest(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        settings_path = editor_settings_path(dashboard_dir)
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["autodetectRelationships"] = True
        write_json(settings_path, settings)

        with self.assertRaisesRegex(PbipValidationError, "boolean false"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_missing_editor_field_requires_manual_unserialized_manifest(self):
        _, dashboard_dir, manifest_path, manifest = self.make_fixture()
        manifest["autodetect_relationships"]["verification"] = (
            "editor_settings_serialized_false"
        )
        write_json(manifest_path, manifest)

        with self.assertRaisesRegex(PbipValidationError, "manual_unserialized"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_rule_slicer_binding_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        visual_path, document = find_visual(dashboard_dir, "slicer", title="Rule")
        projection = document["visual"]["query"]["queryState"]["Values"]["projections"][0]
        projection["field"]["Column"]["Property"] = "requirement_id"
        projection["queryRef"] = "DimRequirement.requirement_id"
        write_json(visual_path, document)

        with self.assertRaisesRegex(PbipValidationError, "slicer contract drift"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_topic_table_without_topic_binding_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        visual_path, document = find_visual(
            dashboard_dir,
            "tableEx",
            title="Open BCF Topics — select one row",
        )
        projections = document["visual"]["query"]["queryState"]["Values"]["projections"]
        projections.pop(0)
        write_json(visual_path, document)

        with self.assertRaisesRegex(PbipValidationError, "one Topic selector table"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_speckle_tooltip_binding_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        visual_path, document = find_visual(dashboard_dir, "specklePowerBiVisual")
        tooltip = document["visual"]["query"]["queryState"]["tooltipData"][
            "projections"
        ][0]
        tooltip["field"]["Aggregation"]["Expression"]["Column"]["Property"] = (
            "global_id"
        )
        write_json(visual_path, document)

        with self.assertRaisesRegex(PbipValidationError, "tooltip must bind"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_rule_filter_path_to_dim_element_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        relationships_path = model_definition(dashboard_dir) / "relationships.tmdl"
        text = relationships_path.read_text(encoding="utf-8")
        marker = (
            "relationship DimElement_FactIDSCheck\n"
            "\tcrossFilteringBehavior: bothDirections"
        )
        self.assertEqual(text.count(marker), 1)
        relationships_path.write_text(
            text.replace(
                marker,
                "relationship DimElement_FactIDSCheck\n"
                "\tcrossFilteringBehavior: oneDirection",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Rule has no active filter path"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_direct_ifc_federate_route_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        self.assertEqual(text.count("Speckle.Models.Federate"), 1)
        expressions_path.write_text(
            text.replace("Speckle.Models.Federate", "Table.Combine"),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Speckle.Models.Federate"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_legacy_content_sha256_manifest_field_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        self.assertIn('Record.Field(_, "ifc_sha256")', text)
        expressions_path.write_text(
            text.replace(
                'Record.Field(_, "ifc_sha256")',
                'Record.Field(_, "content_sha256")',
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "ifc_sha256"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_legacy_speckle_global_id_path_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        self.assertIn('Record.Field([data], "properties")', text)
        self.assertIn('Record.Field([_raw_properties], "IFC GUID")', text)
        expressions_path.write_text(
            text.replace(
                'Record.Field([_raw_properties], "IFC GUID")',
                'Record.Field([_raw_properties], "GlobalId")',
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "IFC GUID"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_flattened_connector_properties_cannot_replace_raw_ifc_schema(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        self.assertIn('Record.Field([data], "properties")', text)
        expressions_path.write_text(
            text.replace(
                'Record.Field([data], "properties")',
                "[properties]",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "properties"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_speckle_hierarchy_container_filter_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        identity_filter = "each List.Count([_identity_evidence]) > 0"
        self.assertIn(identity_filter, re.sub(r"\s+", " ", text))
        expressions_path.write_text(
            text.replace(
                identity_filter,
                "each true",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "container-row filter"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_legacy_ifc_attributes_path_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        text = expressions_path.read_text(encoding="utf-8")
        legacy_path = 'Record.Field([_raw_properties], "Attributes")'
        self.assertIn(legacy_path, text)
        expressions_path.write_text(
            text.replace(legacy_path, 'Record.Field([_raw_properties], "Other")'),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Attributes"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_application_id_identity_fallback_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions_path = model_definition(dashboard_dir) / "expressions.tmdl"
        expressions_path.write_text(
            expressions_path.read_text(encoding="utf-8")
            + '\nexpression ForbiddenIdentity = Record.Field([data], "applicationId")\n',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "applicationId"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_topic_finding_detail_separator_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        measure_path = model_definition(dashboard_dir) / "tables" / "DimRun.tmdl"
        text = measure_path.read_text(encoding="utf-8")
        self.assertIn('& " - " &', text)
        measure_path.write_text(text.replace('& " - " &', '& " — " &'), encoding="utf-8")

        with self.assertRaisesRegex(PbipValidationError, "Selected Topic Finding Details"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_pass_rate_requires_zero_fallback_for_empty_pass_rows(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        measure_path = model_definition(dashboard_dir) / "tables" / "DimRun.tmdl"
        text = measure_path.read_text(encoding="utf-8")
        guarded = "COALESCE ( [Passed Checks], 0 )"
        self.assertIn(guarded, text)
        measure_path.write_text(
            text.replace(guarded, "[Passed Checks]"),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Applicable Check Pass Rate"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_pass_rate_rejects_nonzero_hard_coded_fallback(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        measure_path = model_definition(dashboard_dir) / "tables" / "DimRun.tmdl"
        text = measure_path.read_text(encoding="utf-8")
        guarded = "COALESCE ( [Passed Checks], 0 )"
        self.assertIn(guarded, text)
        measure_path.write_text(
            text.replace(guarded, "COALESCE ( [Passed Checks], 39 )"),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "hard-coded numeric values"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_topic_finding_count_requires_exactly_one_topic(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        measure_path = model_definition(dashboard_dir) / "tables" / "DimRun.tmdl"
        text = measure_path.read_text(encoding="utf-8")
        single_topic = "SELECTEDVALUE ( DimTopic[topic_guid] )"
        self.assertIn(single_topic, text)
        measure_path.write_text(
            text.replace(single_topic, "VALUES ( DimTopic[topic_guid] )", 1),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Selected Topic Linked Findings"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_real_speckle_url_in_definition_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        expressions = model_definition(dashboard_dir) / "expressions.tmdl"
        expressions.write_text(
            expressions.read_text(encoding="utf-8")
            + '\nexpression LeakedUrl = "https://app.speckle.systems/projects/abc123def4/models/1234567890@abcdef1234"\n',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "Real Speckle URL"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_speckle_stored_data_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        visual_path, document = find_visual(dashboard_dir, "specklePowerBiVisual")
        document["visual"].setdefault("objects", {})["storedData"] = [
            {"properties": {"receiveInfo": {"expr": {"Literal": {"Value": "leak"}}}}}
        ]
        write_json(visual_path, document)

        with self.assertRaisesRegex(
            PbipValidationError,
            "forbidden storedData/receiveInfo state",
        ):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_missing_table_file_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        (model_definition(dashboard_dir) / "tables" / "DimTopic.tmdl").unlink()

        with self.assertRaisesRegex(PbipValidationError, "exactly 9 TMDL table files"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_extra_relationship_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        relationships = model_definition(dashboard_dir) / "relationships.tmdl"
        relationships.write_text(
            relationships.read_text(encoding="utf-8")
            + "\nrelationship UnexpectedRelationship\n"
            + "\tfromColumn: DimTopic.model_id\n"
            + "\ttoColumn: DimModel.model_id\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PbipValidationError, "exactly 8 relationships"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)

    def test_hard_coded_kpi_value_fails_closed(self):
        _, dashboard_dir, manifest_path, _ = self.make_fixture()
        dim_run = model_definition(dashboard_dir) / "tables" / "DimRun.tmdl"
        text = dim_run.read_text(encoding="utf-8")
        original = "measure 'Total Elements' = DISTINCTCOUNT ( DimElement[element_key] )"
        replacement = original + " + 39"
        self.assertEqual(text.count(original), 1)
        dim_run.write_text(text.replace(original, replacement), encoding="utf-8")

        with self.assertRaisesRegex(PbipValidationError, "hard-coded numeric values"):
            validate_pbip(dashboard_dir, acceptance_manifest_path=manifest_path)


if __name__ == "__main__":
    unittest.main()
