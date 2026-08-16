# BCF Issue Workflow Data Contract

Version: 0.1
Status: Implemented

This contract defines the deterministic conversion of normalized IDS failures
into BCF 3.0 issues and analytical sidecars. The normative inputs are
`ids_findings.csv`, `models.csv`, `model_inventory.csv`, the project IDS, and
the source HVAC IFC recorded by those tables.

## Identity and issue semantics

- Only rows with `status=FAIL` enter the BCF workflow.
- Findings are grouped by the federation-safe `element_key`; a bare IFC GUID
  is never used as a cross-model key.
- A topic represents one affected element and has exactly two linked findings,
  one perspective viewpoint, and one selected component in the current run.
- Topic GUIDs are UUIDv5 values over `bcf-topic:v1:[element_key]` using the
  namespace documented in `data_contract.md`.
- Viewpoint GUIDs are UUIDv5 values over `bcf-viewpoint:v1:[topic_guid]`.
- The three issues describe project-assumed information requirements that are
  unmet. They do not assert defects in the public source model.

The fixed workflow metadata is:

| Field | Value |
|---|---|
| Creation time | `2026-08-13T00:00:00Z` |
| Topic type/status | `Issue` / `Open` |
| Priority/stage | `Medium` / `Coordination` |
| Creation author | `control-tower@example.invalid` |
| Assigned to | `model-coordination@example.invalid` |

## BCF package

`reports/bcf/ids_failures.bcf` is a BCF 3.0 ZIP with:

- `bcf.version`, `extensions.xml`, and a stable-UUID `project.bcfp`;
- three explicit lowercase topic directory entries;
- one `markup.bcf` and one `.bcfv` in each topic directory;
- no snapshots, documents, embedded models, or unrecognized entries.

Every topic Header identifies `Building-Hvac.ifc`, IfcProject
`2Ndyd$OSX7s9A04nc4lyye`, and `IsExternal=true`. `Reference` is omitted because
the model register currently provides a GitHub `/blob/` page rather than a
stable, versioned raw IFC URL.

The archive uses forward-slash paths, lexical entry order, explicit directory
entries, DOS timestamp `1980-01-01 00:00:00`, and `ZIP_STORED`. Generation and
validation reject duplicate or case-ambiguous names, absolute paths,
backslashes, traversal components, encryption, unexpected compression, and
oversized content.

Every XML payload is validated against the byte-preserved buildingSMART BCF
3.0 schemas pinned in `third_party/buildingsmart/bcf-xml/3.0/`. The generator
and normative validator do not import `bcf-client`.

## Analytical sidecars

All sidecars use UTF-8 with BOM, LF line endings, fixed column order, and
deterministic row sorting.

| File | Grain | Current rows | Primary key |
|---|---|---:|---|
| `bcf_topics.csv` | One BCF topic/issue element | 3 | `topic_guid` |
| `bcf_topic_findings.csv` | One topic-to-finding lineage edge | 6 | `(topic_guid, finding_key)` |
| `bcf_viewpoints.csv` | One deterministic perspective viewpoint | 3 | `viewpoint_guid` |
| `bcf_viewpoint_components.csv` | One selected IFC component | 3 | `(viewpoint_guid, component_index)` |
| `bcf_topic_events.csv` | One analytical topic-created event | 3 | `event_id` |

All tables retain `run_id`. Topic and viewpoint tables retain `model_id`,
`element_key`, and `global_id`; the bare `global_id` is used only where BCF
requires an IFC component identifier. The topic-finding bridge preserves the
normalized `finding_key`, `requirement_key`, `specification_id`, and
`requirement_id` without recomputing them downstream.

The viewpoint sidecar records the world-coordinate AABB, target, camera
position/direction/up vectors, 60-degree vertical field of view, and 16:9
aspect ratio. Generation fails for empty, non-finite, or degenerate geometry
and verifies all eight AABB corners against the serialized view frustum.

## Build manifest and validation

`reports/bcf/run_manifest.json` records repository-relative inputs and outputs,
SHA-256 hashes, row counts, dependency versions, the BCF version, and the
pinned schema commit/hashes. It deliberately excludes its own hash.

The validator fails closed unless the current fixture reconciles to exactly:

- 3 models, 39 inventory elements, and 47 IDS findings;
- 25 PASS, 6 FAIL, 16 N/A, and 31 applicable checks;
- 3 topics, 3 viewpoints, 3 selected components, and 6/6 lineage links.

It also verifies all GUID/file references, Header/model identity, IFC content
hashes, sidecar foreign keys, world geometry/cameras, manifest hashes, archive
safety, and strict XSD validity.
