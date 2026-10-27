# Enterprise rules and purpose review

The first editable input is one ZIP package: `manifest.json`,
`rules/ruleset.toml`, and `rules/<rule>.toml`. Rule TOML uses the existing
rule-definition compiler and IfcTester. No Excel, Word or PDF extraction is
implied. An uploaded package is a preview until a project user confirms its
source, requirements, unsupported parts, and responsible reviewer/team.

## Package v1

`manifest.json` has `schema_version: 1`, `package_id`, `title`, `version`,
`source: {organization, reference, issued_on}`, and `purposes`. Each purpose has
`purpose_id`, `title` (optional `title_zh`), `from_role`, `to_role`,
`subject_classes`, `required_rule_ids`, `requires_counterpart` (boolean), and
`evidence_requirements` (possibly empty). An evidence requirement has
`evidence_id`, `title`, `acceptance`, `execution: manual|unsupported`,
`method_id` and `method_description` for manual evidence, and `reason` for an
unsupported check. Optional rule `hypotheses` are suggestions, always unverified.
Package, purpose and evidence identifiers are at most 80 characters and may not
contain the reserved `::` reference separator. Titles/source text are separate.
The ZIP is at most 8 MiB, with at most 100 members and 4 MiB expanded text;
each member is at most 512 KiB. Paths are relative and no executable code runs.

For an editable starting point, download **Project rules → Public example**, or
run `python tools/enterprise_rules_example.py <outside-checkout>/example.zip`.
Edit the manifest and native TOML, then repack those files at the same ZIP root.
Rules use the existing IDS entity, attribute, property, classification, material
and part-of facets; the preview states the actual supported schema/predicate
basis. Native rule syntax is documented in `rules/product-validation/README.md`.
`discipline_scope` is not an executable filter on an upload without verified
discipline binding: such a declared constraint is shown as unsupported rather
than silently ignored. Use explicit IDS applicability and the selected purpose
scope. Metadata such as severity is not a purpose-readiness decision.

Unknown/unsupported rule fields are visible, never silently ignored. Invalid
package structure is rejected. A structurally valid package can retain unsupported
requirements; their absence of executable evidence contributes UNKNOWN. Each
compiled requirement gets its own Purpose evidence binding, preventing a partial
PASS from satisfying a group of simultaneous requirements. Empty partitions and
uncovered declared objects cannot produce readiness.

Confirmation freezes package bytes, source digest, compiler/checker versions,
preview and the declared project reviewer/team. Reusing a declared version with
different content creates a visibly distinct immutable revision. Existing
assessments never change when a package or manual judgment changes.

## Runtime boundaries

- Original single-file uploads remain temporarily in the existing bounded import
  spool (four results / 256 MiB including the source). Saving a revision with
  `retain_source:true` atomically retains the exact SHA-matching original in the
  local project database. The choice defaults off. A save without consent retains
  only the report and geometry. Viewing a revision never grants retention consent.
  Historical records lacking source offer explicit attachment; a different hash
  requires a new revision. Federated examples have no single source to retain.
- Enterprise checks run in a supervised child, parse/check only, and reuse the
  saved review geometry. Rule/scope changes create assessment runs, not fake
  model revisions. Existing import cancellation/deadlines remain intact.
- Purpose model keys use the stable project model slot. Unique valid IFC GlobalIds
  map to stable subjects; ambiguous identities remain non-comparable. Runtime
  results keep the current `review_element_key` separately for exact 3D links.
- Scope is declared independently of findings (all purpose objects, selected
  classes, or explicit objects). An actual counterpart revision is required for
  a purpose marked `requires_counterpart`; missing context is UNKNOWN/refused.
  Single-artifact purposes explicitly describe the same delivered artifact in
  producer/recipient roles, without inventing a second model or coordination test.
- Reuse `compose_purpose_inputs`, `assess_purpose`, and `recheck_purpose`.
  Preserve sealed records. Changed rules/configuration, scope, model content,
  engine, and human evidence have separate change explanations. Changed bases,
  deletion, reclassification or exclusion never count as a model repair.
- Human determinations require a recorder, evidence reference, basis, accepted
  method, outcome and exact model/scope context. They are user-recorded evidence,
  not authenticated signatures or risk authorisations. Progress notes stay separate.

## Module interfaces

`enterprise_rules.py` owns `parse_package(body, filename) -> EnterprisePackage`,
with `.preview() -> dict`, `.manifest`, `.definition`, `.checks` and
`.source_sha256`. `evaluate_rules(package, body, report, model_id) -> dict`
returns `ruleset`, `checks`, `elements`, `findings`, `coverage`, `models`.
Elements retain `element_key` (stable purpose identity), `review_element_key`,
`model_key` (slot id), `global_id`, `identity_comparable`, `ifc_class`,
`class_ancestors`, `step_id`, `name`. Each check includes `requirement_key`,
`rule_id`, `semantics_digest`, `expected`, `support`, `unsupported_reasons`.
Each finding cites these keys, its PASS/FAIL/N/A status, expected/actual/reason
and checker basis. Geometry is never read or regenerated here.

`purpose_review.py` owns `assess_evaluation(package, evaluation, *, project_id,
revision_id, purpose_id, scope, responsible_team, determinations=(), prior=None,
consumer=None) -> dict`. It returns a sealed `record`, `conclusion`, `blockers`,
`evidence_requests`, and `change_summary`. Blocks retain rule/check/evidence,
stable subject and current review-element links. `prior` is the complete saved
run, `consumer` an optional actual revision/report context. Changed questions
produce a fresh assessment and an explicit non-comparable explanation.

`enterprise_library.py`, the purpose worker and HTTP routes own project storage,
confirmed revisions, exact source attachment, supervised evaluation and immutable
assessment history. They do not modify canonical outputs or the base review.

## HTTP/UI contract

- `GET /api/review/source-status?review=ID`: source metadata only,
  `review_id`, `source_available`, `retainable`, `reason`.
- `POST /api/projects/revisions`: existing save fields plus optional strict boolean
  `retain_source`; response revision includes `source_available`. Source and
  revision commit together; a failed source save does not leave a new revision.
- `GET /api/projects/rules?project=ID`: `rule_revisions`, `previews`.
- `POST /api/projects/rules/preview?project=ID&filename=FILE.zip`: binary ZIP;
  returns `preview_id`, package/source metadata, `rules`, `purposes`, diagnostics.
- `POST /api/projects/rules/confirm`: `{project_id,preview_id,confirmed_by,
  responsible_team}`; returns `rule_revision_id` and frozen preview fields.
- `GET /api/projects/rules/detail?rule_revision=ID`: frozen package preview.
- `POST /api/projects/source?revision=ID&filename=FILE.ifc`: binary exact source;
  returns `revision_id`, `source_available`, SHA.
- `GET /api/projects/purpose?project=ID`: `rule_revisions`, `sources`, `assessments`.
- `POST /api/projects/purpose/runs`: `{project_id,revision_id,rule_revision_id,
  purpose_id,scope,consuming_revision_id?,prior_run_id?}` returns a 202 job.
- `GET /api/projects/purpose/jobs?job=ID` / `POST .../jobs/cancel {job_id}`:
  existing job states and `result.run_id` on success.
- `GET /api/projects/purpose/run?run=ID`: full immutable run with metadata,
  checks/elements/findings, engine record, conclusion/blockers, manual evidence,
  change summary. Scope is `{kind:all|classes|elements,classes:[],element_keys:[]}`.
- `POST /api/projects/purpose/determinations`: `{run_id,evidence_id,subject_keys,
  outcome,method_id,determiner,basis,reference}` persists a new user judgment;
  a subsequent explicit review uses it. It never edits the old verdict.
- `GET /api/projects/rules/example`: original public example ZIP, downloadable.

The main path is Project → Project rules → Model revisions → Purpose review.
Saved revisions link directly to their purpose form; projects without adopted rules
first link to rule preparation while retaining the revision context. Problem cards
prioritize element, requirement, observed result and next step. Technical identities
and route data are folded. Counts separate objects from evidence observations;
UNKNOWN and manual gaps are not labelled machine violations. Recheck summaries
separate rule passes from evidence updates, deletion, class and scope changes.
Findings
link to `review.html?revision=ID&assessment=RUN&purpose_finding=BLOCK&lang=...`.
Purpose evidence remains distinct from the four base review rules. Missing mesh
does not hide evidence. English/Chinese and a 390px viewport use the same state
and boundary semantics.

## Verification path

The automated public workflow uses two geometric IFC revisions made from the
repository's editable synthetic source. It adopts the downloaded native package,
tests consented source retention and historical exact-source attachment, shows machine and missing-evidence outcomes,
opens the precise mesh, records a human judgment without editing the old record,
and explicitly reassesses. It also tests unsupported adoption, missing counterpart,
bounded lists beyond 100 observations, saved explicit scope, failed-save drafts,
Chinese/390px layouts and immutable history. Python integration tests restart the
service/library and call the native child plus the core Purpose recheck again.
The candidate CI runs this alongside the existing import/project/browser gates.
