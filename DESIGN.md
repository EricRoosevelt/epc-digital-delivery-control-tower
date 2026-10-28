---
version: alpha
name: BIM Doctor
description: A light workspace for reading IFC checks and scoped handover items.
colors:
  canvas: "#f3f6f8"
  surface: "#ffffff"
  ink: "#172b3a"
  muted: "#536777"
  line: "#dbe3e9"
  primary: "#245c70"
  focus: "#176c9c"
  blocked: "#943d31"
  unknown: "#465b71"
typography:
  display:
    fontFamily: '"Segoe UI Variable Display", "Segoe UI", "Microsoft YaHei", sans-serif'
  body:
    fontFamily: '"Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif'
    fontSize: "16px"
    lineHeight: "1.65"
  data:
    fontFamily: 'Consolas, "SFMono-Regular", monospace'
rounded:
  DEFAULT: "7px"
  control: "5px"
spacing:
  base: "24px"
components:
  status:
    borderRadius: "4px"
  button:
    borderRadius: "5px"
---

## Overview

The light workspace direction was approved by the user on 2026-10-12 through the PM implementation decision. This records the implementation's shared identity, not a claim of independent implementation acceptance. The audience is a BIM reader finding the next action and a recruiter understanding the two actual product paths. Conclusions, sources and next steps carry the hierarchy; no decorative dashboard, false score, fake personnel or speculative navigation.

## Colors

Ownership model B: `doctor/static/doctor.css :root` is canonical. DESIGN.md mirrors its accepted semantic values. The CSS roles `--bg`, `--surface`, `--ink`, `--muted`, `--line`, `--accent`, `--focus`, `--problem-ink`, `--unknown` map respectively to canvas, surface, ink, muted, line, primary, focus, blocked and unknown here. Hover, fill and scrollbar tokens are named in that same root. Every shared control consumes those roles. Light is the approved theme; an operating-system dark preference does not silently change the approved theme.

## Typography

No fetched fonts. Segoe/CJK fallbacks remain local. Existing reading screens retain their 16px body. Main headings use 28px desktop / 26px mobile; home 34/30px; existing detail object names 26px and wrap fully. The operational 3D workspace uses 14px finding names, 13px action text at 1.7 line height, 22px selected object names, and 10–12px metadata. Model keys/Tag/digests use the data stack.

## Layout

1280px maximum, 32px desktop / 18px phone gutter. The desktop shell is 56px high and mobile uses two rows for product/language and the real path links. Homepage recommended action is before its long description, fully visible at 375×812 from scroll zero.

Example results use team registers with individual item links and separate original routes. The complete item unit/count explanation and quiet records have disclosures; the items-are-not-defects sentence stays open near counts. No example search or full inline-detail system.

Local desktop detail uses a 320–360px name-priority list and a naturally growing detail panel; at 700px and below a finding route shows a single detail and visible Back. Vertical scrolling belongs to the document. No bounded detail `max-height` or internal vertical scroller. Generic workspace/compare retains all its existing columns and status branches.

## Elevation & Depth

Flat white surfaces and low-emphasis borders. Selected rows use the pale selected surface. The main safe action is teal; no gradients, ambient animation, large sidebar or drop shadows. Verdict words, evidence kinds and reading limits remain explicit.

## Shapes

Panels 7px, controls 5px, textual state markers 4px. State labels never wrap vertically. BLOCKED/FAIL caution, UNKNOWN dashed, PASS/READY are separate textual concepts; neither becomes a green overall-release signal.

## Components

`shell.js` owns app identity/main links; `language.js` owns the language control; `dom.js` owns text-safe construction and shared primitives; `screens.js` owns example/item/recheck arrangement; `workspace-screens.js` owns result selection/detail; `local-check.js` owns real input steps and result framing. `view-state.js` owns transient same-check UI continuity. `ui-words.js` registers navigation/layout wording separately from domain vocabulary. See UX-CONTRACT.md for ownership and behavior.

Value path: CSS semantic root → shared component selectors → main-path screens; DESIGN mirrors that path. No generated token exports or per-page theme copy. The named review workspace variant adds review.css for geometry and operational components while importing doctor.css for all shared color/font/control tokens. Browser computed style and token drift validation are required.

## Iconography

BD is a text product mark. Directional arrows supplement named navigation controls, never substitute for an accessible name. No external icon asset or icon package.

## Motion

No animation is necessary for this reading workflow. In-page jumps move visible focus without changing the route hash. Reduced-motion preference retains immediate, operable navigation.

## Entry resource recovery

The three HTML entries carry the same small, static bilingual recovery region.
Its native reload action and minimal inline styles deliberately do not depend on
the application's module graph or external stylesheets. Successful entry loading
hides the region; a stylesheet or entry-module graph failure leaves a readable
retry action. Reload retains the exact current URL and never loops automatically.

## Do's and Don'ts

- Keep source/FAIL/PASS/N/A/READY limitations next to the result or action they qualify.
- Use actual finding/model/record identity; do not label every user's file a public sample or use a software SHA as a model version.
- Preserve type-change impact and undecided value/actor outside folds. Checker-read folding is limited to the reviewed known local PV-001 FAIL notes.
- Return to a visible selected row or search; never focus a hidden filtered-out link.
- Describe actual verification and remaining review separately. Prototype approval does not mean the implemented candidate passed TD/UX/BIM.

## 3D review workspace variant

The 2026-10-24 product implementation extends BIM Doctor with `/review.html?lang=zh|en`. Its audience is an engineer checking a real IFC; its single job is to connect a requirement, its actual element, and an evidence-grounded next action. Existing record routes remain available.

The signature is a large, pale engineering model stage between two quiet evidence rails. Source geometry, rather than a decorative hero or score, carries the page. Existing teal #245c70, ink #172b3a, surface #ffffff and muted #536777 remain canonical. Review-only roles live in `.review-app`: viewport #e7edf1, selection #0a6c85, selection fill #edf8fb, viewport ink #244759. Three.js uses cyan for the selected element and muted orange for elements needing review; words identify both states.

At 1440px the layout uses 270px / flexible viewport / 330px columns and 24px outside gutters. Below 1180px the evidence panel moves below; below 700px the model stage, issue list, and evidence stack in that order. The document owns overall vertical scroll, while only the finite issue register has a bounded internal scroller. The right evidence/actions rail grows naturally. No overlay hides evidence on a phone.

IFC remains Z-up in world metres. Initial framing uses an IQR-based main spatial cluster so source origin/georeference helper objects do not make the building tiny; Show all frames every visible source mesh. No source position is modified. Model filter visibility, element selection, focus/isolation, and the detail rail all use `element_key`, never GlobalId alone. Advice puts actions and verification before folded known facts. INFO is a neutral information state; PV-001 is a repository rule requiring review, not a statutory or construction failure.

Canonical owners are review.js (state, loading, finite result list, source/upload and advice), review-viewer.js (Three renderer and camera/picking), review-words.js (registered bilingual UI), and existing dom.js/language.js (safe text and language switching). Native selects retain OS-owned popup behavior. Loading is indeterminate and cancellable; failures preserve the prior report and expose Retry. A failed WebGL/geometry request leaves checks and advice usable. No configured AI key means explicitly labelled local rule guidance. A configured key alone is labelled configured; generated advice is only labelled AI after the endpoint returns mode=ai.

The real-model case exposed washed-out thin MEP geometry at overview scale. Backend normalized palette arrays are interpreted as sRGB before Three.js lighting, with hemisphere intensity 1.2 and directional intensity 1.6. Grid lines use quieter #c4d1d9/#dce4e9 so they do not dominate the geometry. Camera bounds, source vertices, source palette values and visible-element counts are unchanged. This improves contrast; a long, thin floor still requires focus/isolation to inspect small terminals.

## Persistent projects and rechecks

The 2026-10-25 extension adds a durable daily workflow without changing the model-stage identity: project → logical model → saved revision → follow-up → comparison. `projects.css` extends the same `doctor.css` and `review.css` tokens. A 280px project register sits beside naturally growing model/revision sections. These are actual records, with clear revision labels, dates and direct 3D entry links, not decorative dashboard cards. On phones the project register, selected project and comparison stack; both revision directions and actions remain available.

The comparison signature is six selectable evidence categories: rule recheck passed, still needs review, new failed check, missing, no longer applicable and not comparable. Counts come from the response rows, and errors versus information prompts have independent selectors. Missing and not-comparable use neutral tones; neither looks like a completed repair. Raw before/after observations, the reason, and an exact revision/finding link make each category inspectable. The server's scope note is visible before the categories, particularly for multi-file comparisons that cannot safely match identities.

Saved revision context sits directly above the existing 3D workspace. A compact save panel explicitly chooses a project and either a new model or an existing model's next revision. Check results and the 3D snapshot are saved; a separate unchecked control explicitly retains the uploaded original IFC permanently in local project data. The server's source status distinguishes retained, temporary, expired and federated-demo inputs. Retained-source save opens purpose review for the exact revision, or rule adoption first when the project has no adopted rules. Snapshot-only saves keep the current 3D view. Follow-up uses an in-place disclosure with a visible manual status and owner; editing expands the three actual fields. Notes auto-grow to 360px, then scroll. Advice remains ahead of detailed check evidence. Project and follow-up drafts do not go into localStorage; server responses are the source of saved identity.

Canonical owners are `projects.js` (project/model revision navigation), `projects-compare.js` (comparison selection and evidence rendering), `projects-review.js` (save/follow-up state and unsaved-draft guard), `projects-words.js` (registered Chinese/English copy), and `projects-api.js` (shared bounded JSON requests). Existing safe DOM and language owners remain unchanged. New errors are inline and retryable; no toast or modal framework is introduced. An app-owned native HTML dialog is used only to protect unsaved follow-up input on navigation, with Keep editing initially focused, Escape, native modality and focus restoration.

## Project rules and purpose evidence

The project detail adds local Model revisions / Project rules / Purpose review tabs.
The main entry follows Project → Enterprise rules → Model → Purpose review. New
project detail opens rules first; explicit model and comparison routes retain their
destination. Historical examples and standalone checks remain subordinate links.
Rule onboarding explains the editable template's actual ZIP tree and the distinction
between executable requirements, human evidence and unsupported requirements.
Rules preview shows the declared source, version, actual requirements, unsupported
parts and manual evidence methods before adoption. The confirmer and team are local
project declarations. Distinct immutable contents retain distinct revision identities.
The existing teal/ink/surface tokens and natural document scrolling remain canonical.

`projects-rules.js` owns preview/adoption, `projects-purpose.js` owns source attachment,
scope, supervised review jobs and user evidence, and `review-purpose.js` supplies a
distinct evidence list/detail in the existing 3D viewport. `enterprise-ui.js` shares
safe evidence rows, finite lists, comparison presentation and the draft guard;
`enterprise-words.js` owns bilingual labels. Purpose counts distinguish objects in
scope from evidence observations. Human evidence changes, basis changes and machine
rule recheck passes have separate labels. Opaque identities stay in technical details
and exact links; frozen purpose/rule snapshots supply human-readable context.
