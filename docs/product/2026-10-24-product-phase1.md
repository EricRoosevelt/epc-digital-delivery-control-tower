# BIM Doctor: first product increment

## Product decision

Build a real model-review workspace for an engineer investigating IFC delivery
information and a manager deciding what needs attention. The first increment
connects real geometry, deterministic checks and evidence-backed advice in one
screen. It should feel like a product people can use, with a strong model view,
readable findings and clear next actions.

The user has commissioned PM-led programming, UI and BIM sub-sessions with
iterative handoffs. Routine decisions are delegated; old role approval chains
and design freezes do not apply. This document records implementation decisions,
not an additional approval step.

## Approach

Extend the existing local Python server and plain-module frontend. Add a
dedicated `/review.html` workspace so the established example and recheck flows
remain available. Reuse IfcOpenShell and the admitted Three.js 0.186.1 runtime.
A new framework or browser IFC parser would duplicate working infrastructure.

The user path is: open the public federated sample or select an IFC file;
review the check summary; select a finding and locate its element in 3D;
read the observed evidence and practical guidance; optionally ask OpenAI for
a concise explanation; modify at source and run a new check.

This phase uses four explicitly named review checks: PV-001 air-terminal type,
INFO-001 readable element name, INFO-002 storey association and ID-001 model-local
GlobalId validity/uniqueness. Information checks are project review conventions;
their failures do not establish regulatory noncompliance. Cross-model recurring
GlobalIds remain separate identities. Geometry is a locating aid, not a clash
analysis result.

## Implementation and ownership

- Engineering: `ReviewStore` and HTTP routes in `internal/doctor_adapter/review*`
  and `doctor/serve.py`; real indexed geometry linked by `element_key`.
- UI: `doctor/static/review*`; Three.js selection, focus, isolation, issue and
  model filters, dual-language copy and responsive layout; visible entry from
  the existing product.
- BIM: `internal/doctor_adapter/guidance.py`; specific English/Chinese local
  guidance, rule meaning and meaningful regression cases.
- PM/integration: `doctor/advice.py`; OpenAI Responses API,
  documentation, runtime asset hashes, integration verification and final
  assessment of the complete user path.

Reports expose `review_id`, source/model identities, elements, findings, rules
and measured summary counts. Geometry exposes meshes keyed to those elements.
API endpoints are `/api/review/demo`, `/models?filename=`, `/report?review=`,
`/geometry?review=`, `/ai` and `/advice`.

OpenAI is explicitly selected by the user. Configure `OPENAI_API_KEY` on the
server, with optional `OPENAI_MODEL`. AI is called only on the user's button
action. Send selected check evidence, not IFC bytes or mesh data. Facts and
citations remain server-owned; generated actions are suggestions. Without a
key, useful local rule guidance remains available and is labelled accordingly.
An upstream failure produces an actionable message, not a fabricated answer.

## Verification and handoffs

Each worker leaves a short handoff in `docs/handoffs/phase1-*.md`, covering the
actual implementation, checks and remaining gaps. PM integrates, exercises the
real public sample, uploads a model, selects and isolates geometry, tests filters
and Chinese/English/mobile layouts, and checks advice and error states. Regression
tests cover actual checks, identity/selection and the OpenAI transport boundary.
Published pipeline outputs and frozen fixture bytes must remain unchanged.

Handoffs: [engineering](../handoffs/phase1-engineering.md),
[UI](../handoffs/phase1-ui.md), [BIM](../handoffs/phase1-bim.md),
[PM integration](../handoffs/phase1-pm.md).

## First-increment limits

Review data lives in the running local server; a restart starts a new session.
This phase establishes a usable inspection and advice path, not multi-user issue
assignment, automatic source-model repair, geometric clash checking or contractual
acceptance. Later increments should be driven by observed engineer workflows and
the first phase's actual handoffs rather than a fixed approval sequence.
