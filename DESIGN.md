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

No fetched fonts. Segoe/CJK fallbacks remain local. The v2 proposal's display family and compact spacing are adopted while the application's existing 16px body is retained on desktop and mobile. Density is achieved through geometry, not by reducing body text to the prototype's 15/14px. Main headings use 28px desktop / 26px mobile; home 34/30px; detail object names 26px and wrap fully. Existing smaller metadata remains metadata, not action instructions. Model keys/Tag/digests use the data stack.

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

Value path: CSS semantic root → existing shared component selectors → all main-path screens; DESIGN mirrors that path. No generated token exports, second stylesheet or per-page theme copy. Browser computed style and token drift validation are required.

## Iconography

BD is a text product mark. Directional arrows supplement named navigation controls, never substitute for an accessible name. No external icon asset or icon package.

## Motion

No animation is necessary for this reading workflow. In-page jumps move visible focus without changing the route hash. Reduced-motion preference retains immediate, operable navigation.

## Do's and Don'ts

- Keep source/FAIL/PASS/N/A/READY limitations next to the result or action they qualify.
- Use actual finding/model/record identity; do not label every user's file a public sample or use a software SHA as a model version.
- Preserve type-change impact and undecided value/actor outside folds. Checker-read folding is limited to the reviewed known local PV-001 FAIL notes.
- Return to a visible selected row or search; never focus a hidden filtered-out link.
- Describe actual verification and remaining review separately. Prototype approval does not mean the implemented candidate passed TD/UX/BIM.
