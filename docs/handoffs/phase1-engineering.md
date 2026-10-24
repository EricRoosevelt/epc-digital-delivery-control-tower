# Phase 1 engineering handoff

Implemented session-local IFC review in `internal/doctor_adapter/review.py` and wired HTTP/static routes into `doctor/serve.py`. The PM subsequently owns the advice routes in the same server.

## Interface

`ReviewStore.demo()`, `create(filename, bytes)`, `get(review_id)`, and `geometry(review_id)` return isolated JSON-shaped copies. A single store is injected using the third optional `make_handler(..., review_factory=...)` argument. Existing source/local factories remain compatible.

- `GET /api/review/demo`: actual unmodified buildingSMART PCERT Architecture/HVAC/Structural federation; input SHA-256 checked against the project manifest, original attribution retained.
- `POST /api/review/models?filename=model.ifc`: raw `application/octet-stream`; 64 MiB default, configurable with the existing `--max-model-bytes`. Only the basename is displayed; the filename is never opened as a path.
- `GET /api/review/report?review=id` and `/api/review/geometry?review=id`: same review identity; absent session reviews return 404.
- `/vendor/three/` maps to pinned `third_party/three/0.186.1/` ES modules. The UI owns source intake.

Element selection uses the full `model_key::GlobalId`; malformed, absent, or duplicated IDs receive a STEP-entity suffix. Duplicate counts include all IfcRoot objects in each file. Meshes are tessellated from the actual entity, never reselected by GlobalId. Geometry uses world-space flat xyz in metres, flat triangle indices, RGB 0..1, and IFC Z up. `geometry_status` is `renderable` or `unavailable`; unavailable rows carry a reason in the geometry envelope.

Four checks: unchanged PV-001 effective air-terminal type set; INFO-001 optional instance Name readability; INFO-002 storey resolution through containment/parent relations; ID-001 compressed identifier validity and file-local uniqueness. Status values are PASS/FAIL/NOT_APPLICABLE. Severity ERROR identifies PV/ID failures; INFO identifies the optional Name/storey prompts. Summary `failed` counts every FAIL, while `errors` and `information` distinguish those groups. PV uses the existing IfcOpenShell effective-type semantics, including assigned types and USERDEFINED text; IFC2x3 IfcFlowTerminal+IfcAirTerminalType mapping has one small tested branch.

The actual public demo has 39 elements, 32 meshes, seven elements with no representation, and 156 findings: 2 ERROR failures (PV-001), 19 INFO prompts (storey), 98 passes, 37 not applicable. Many site/building-level objects legitimately have no storey; no automatic model correction is implied. The source also contains far-away geo-reference markers (approximately x=-29m,y=-14m); these are real source placements, not a federation offset bug.

## Verification

- `pytest -p no:cacheprovider tests/test_doctor_review.py tests/test_doctor_preview.py tests/test_doctor_local_check.py -q --tb=short`: 74 passed, 127 subtests passed before the final IFC2x3 mapping addition.
- Final `pytest -p no:cacheprovider tests/test_doctor_review.py -q --tb=short`: 12 passed, including IFC2x3 mapping, type priority/free text, aggregate/opening storey resolution, real distinct duplicate-ID meshes, metre conversion, report immutability, invalid input, HTTP upload/report/geometry identity, and the actual demo.
- `ruff check --no-cache internal/doctor_adapter/review.py tests/test_doctor_review.py`: passed.
- `git diff --exit-code -- data/processed reports`: passed, no published drift. No pipeline regeneration or snapshot refresh was performed.
- Loopback HTTP and scratch-writing old tests require an escalated shell in this Windows sandbox; sandbox failures (10013 sockets and atomic temp-file access denied) were resolved by running the same tests with that permission.

## Limits and review

This is synchronous local IFC STEP inspection, with review data retained only for the server session. It inspects IfcElement occurrences, not all spatial roots, property schemas or every IFC concept. IFC4 is covered by the real public demo and geometry tests; the IFC2x3 air-terminal mapping has a synthetic fixture. No exhaustive IFC4X3 certification, clash detection, clearance assessment, statutory compliance or source-model editing is claimed. Mesh conversion failure is reported rather than replaced with geometry.

Reviewed the PM advice/server path: trusted review/finding selection and provider payload boundaries are correct; status remains review evidence. Reported one minor potential mismatch: provider output validation requires non-empty actions even for PASS while the prompt permits no corrective action. PM owns its resolution. No blocking issue was found in that path.
