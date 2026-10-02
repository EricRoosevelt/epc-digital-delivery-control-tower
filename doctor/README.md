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
  `mode`, `outcome`, `record` + `assessment_digest` or `refusal`, `elements`,
  and — beside a record only — `finding_details`. The envelope keys are fixed
  by the technical director. The runs a
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
- **A recheck is read, not re-derived.** The recheck screens answer what
  changed, what is still open and what to do next, in that order, with the
  evidence details behind a fold. The four carry-over states, their reasons, the
  changed aspects and the member dispositions are the record's; which side was
  re-issued is `changed_models` looked up against the same comparison's
  `producing` / `consuming`, and the role names are the request's handover. The
  wording lives in `static/recheck-model.js`, which has no DOM in it, and
  `tests/test_doctor_recheck_screens.py` runs it under Node (a missing Node
  skips locally and fails under `CI`). A value the page does not know is shown
  as it came and marked unrecognised. The fixture notice, each citation's
  provenance tag and the five sentences that must not be misread are never
  inside a collapsed block. Check results and determinations are counted
  apart and never added together. Words: [recheck vocabulary](../docs/product/2026-10-02-doctor-recheck-vocabulary.md).
- **What a cited finding required comes from the run that record cites.**
  `finding_details` maps a `finding_key` to `rule_id`, `requirement_id`,
  `labels`, `citation`, `expected`, `actual`, `reason` and `status`, copied
  unchanged from the validation run the citing record names — the requirement
  that assessment was made against, never today's rule file. A citation has an
  entry only if its record names that run and the predicate and content it
  sealed are the run's; otherwise it has none, and no `null`. So every
  `fixture/finding/…` citation is without one, and after a rule edit the
  findings under the edited requirement are without one too, while the sealed
  citations of the first assessment keep theirs. An entry carries no
  `owner_role`, `severity` or `priority`: those are a rule author's metadata,
  not the project's assignment. It also carries no required value, data type
  or Revit parameter mapping; the run does not hold them. The screens do not
  read this key yet.
- **An omitted key is words.** A key the envelope does not carry reads
  "记录未携带" — never `null`, `""`, `0`, `false` or a dash. A key carried as an
  empty string is a different fact: an empty `storey` is "无楼层归属", because
  the element has no storey assignment.
- **No bundled data.** Nothing under `doctor/` is a record, digest or refusal.
  Without the adapter the preview reports that input is unavailable.
- **No third-party code.** Python standard library (`http.server`) and plain
  HTML, CSS and ES modules; no build step, no `package.json`.
- **Loopback only, reads no clock, and writes nothing in this checkout.** The
  server itself writes no file. The adapter it calls does write, outside the
  checkout: each validation run copies the rule library into a scratch
  directory under the system temporary directory, puts the run's by-products
  there, and removes the directory when the run ends. The rule-edit recheck
  scenarios edit that scratch copy; `rules/` is never written.

## Two entries, kept apart

`fixture` is shown to the manager as **模拟示例**: simulated policy and
determinations, said so on every screen; it cannot be used for a project
decision and offers no export. `real` is shown as **随附项目的检查尝试** — not
"real input", because nothing can be imported: it runs the shipped project's own
policy and shows why that attempt did not start. Choosing or switching an entry
clears the result; a refused attempt is never shown as an example.

A refusal and a fault are different screens. A refusal is the system's answer
about the request's conditions and arrives as a result, worded from its code. An
exception or a missing adapter never reaches that screen: it is shown as a fault
of the program, with the technical message and no statement about a project.

## The path a manager walks

One path is carried end to end
([first-check path](../docs/product/2026-10-02-doctor-first-check-path.md)):
an ordinary first check, the items that need doing grouped by the team the
record assigns, one item with its elements, what to do, who handles it and what
a recheck must show — and then the same item in a recheck of that record. The
first-check screens are worded from `static/first-check-model.js`, which like
`recheck-model.js` has no DOM in it and is exercised under Node.

What qualifies a conclusion sits beside it and only where it applies: that its
evidence is simulated (decided per citation, as before), what a "can start"
covers, that "cannot be decided" is not a clean bill, that a team is an entry in
the record. General reading rules, identifiers and the Pack's English are one
fold away. The Chinese action sentences hold for one Pack version; a record
under any other is shown the Pack's own English. What a failing requirement asks
for is read only from the returned data's `finding_details`; the preview reads no
rule file. The record, activity and member screens were not revised and still
use internal terms.

## Not in this preview

Starting a recheck, marking an item resolved, assigning or notifying anyone and
exporting a recheck record (the recheck screens say so and carry no button for
them); model/version, Pack and activity selection catalogues (F2), exhaustive refusal
diagnostics (F4), Revit navigation and determination originals (F5), condition
discharge and risk authorisation (F6, E2), arbitrary model intake (F7),
separated refusal message text (F8), and the Singapore research view.
