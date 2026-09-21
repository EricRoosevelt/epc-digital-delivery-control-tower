# BIM Doctor — D1 internal preview

A local, clickable preview of the D1 screen flow
([design](../docs/product/2026-09-16-doctor-d1-screen-flow.md), PR #11) for a
BIM manager who should not have to read JSON or use a CLI. It is an internal
prototype: not a release, not a public interface, not a compliance tool.

```bash
python doctor/serve.py        # then open http://127.0.0.1:8765/
```

## What it is

- **Presentation only.** The screens select, name and lay out what the internal
  adapter (A1) returns. They do not compute a verdict, member disposition,
  evidence carry-over, condition status or coverage reading. Where the
  Framework records no correspondence — a recheck disposition with no current
  subscope, because the pair no longer exists — the screens do not construct
  one, by key or otherwise.
- **One seam.** `serve.py` hands the browser A1's envelope unchanged:
  `mode`, `outcome`, `record` + `assessment_digest` or `refusal`, and
  `elements`. The envelope keys are fixed by the technical director. The runs a
  mode offers come from the adapter's `scenario_index()`, which runs nothing;
  the envelope's own `mode` is still checked against the chosen one before
  anything is rendered.
- **Provenance decided per citation.** Whether a label is true is a property of
  the one citation it sits beside, so the criterion is too: a fixture value is
  machine-visibly untrue and carries the fixture marker (`fixture/finding/…`,
  `fixture-determination/…`), and everything else does not. The envelope's mode
  is never consulted. One record can mix the two on a page — the model-reissue
  scenario cites six fixture-minted finding keys beside three real ones — and a
  per-envelope rule would call those six real validation output. Full sentences
  are in a legend on the same page, never hover-only. A policy `decision_basis`
  is not a citation and carries no marker, so the row says the source is not in
  the envelope rather than guessing whose decision it was.
- **An omitted key is words.** A key the envelope does not carry reads
  "记录未携带" — never `null`, `""`, `0`, `false` or a dash. A key carried as an
  empty string is a different fact: an empty `storey` is "无楼层归属", because
  the element has no storey assignment.
- **No bundled data.** Nothing under `doctor/` is a record, digest or refusal.
  Without the adapter the preview reports that input is unavailable.
- **No third-party code.** Python standard library (`http.server`) and plain
  HTML, CSS and ES modules; no build step, no `package.json`.
- **Loopback only, writes nothing, reads no clock.**

## Two experiences, kept apart

`fixture` shows simulated policy and determinations and says so on every
screen; it cannot be used for a project decision and offers no export. `real`
runs the shipped project's own policy and shows its actual refusal. Choosing or
switching a mode clears the result; a refused real run is never shown as a
fixture.

## Not in this preview

Model/version, Pack and activity selection catalogues (F2), exhaustive refusal
diagnostics (F4), Revit navigation and determination originals (F5), condition
discharge and risk authorisation (F6, E2), arbitrary model intake (F7),
separated refusal message text (F8), and the Singapore research view.
