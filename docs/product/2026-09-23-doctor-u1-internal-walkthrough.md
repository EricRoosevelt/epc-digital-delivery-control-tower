# Doctor U1 internal walkthrough

Date: 2026-09-23. Owner: Product/UI Engineer.
Scope: an internal usability walkthrough of the clickable Doctor preview merged
in PR #13 (`feat/doctor-d1-ui`), commit `a438f5d5195af2186266b7d8bcf1904f0f153d10`.
Original requirement: [dual-track commission](2026-09-16-dual-track-delivery-plan.md),
D1 section. Adopted constraints: [D1 product adjudication](2026-09-16-d1-product-adjudication.md).
Screen flow design: [doctor-d1-screen-flow.md](2026-09-16-doctor-d1-screen-flow.md).

## What this is and is not

This is a task script and a blank observation template for a colleague to click
through the already-merged preview and report what they see. It does not change
`doctor/`, the internal adapter, or any Framework, Pack, rule or policy behaviour.
Defects a walkthrough turns up are recorded, not fixed, here.

It is internal role-play, not target-user validation — the D1 design brief says
this explicitly and this script does not change that. No aggregate readiness
score is computed by this walkthrough or by the preview itself. It does not
adjudicate the Singapore candidate checklist, and it does not authorise any
implementation work.

**Do not commit a filled-in copy of the record template in this repository.**
The template asks for a self-assigned session code, not a name; keep the
completed copy wherever you keep working notes outside this checkout. Nothing
under `data/processed/` or `reports/` is touched by this walkthrough.

## Set up the preview from a clean checkout

Verified on this machine against `a438f5d` in a dedicated worktree, separate
from any other checkout:

```bash
git worktree add ../doctor-u1-walk a438f5d5195af2186266b7d8bcf1904f0f153d10
cd ../doctor-u1-walk
python -m venv .venv
```

Activate it (`.venv/Scripts/activate` on Windows, `source .venv/bin/activate`
elsewhere), then install only what the preview itself needs — `doctor/serve.py`
is standard-library only, but the internal adapter it calls imports the
Framework, which needs the pinned runtime dependencies:

```bash
python -m pip install -r requirements.txt
python doctor/serve.py
```

Open `http://127.0.0.1:8765/`. The server binds to loopback only, reads no
clock, and writes nothing; stop it with Ctrl-C when the session is over.

Optional, to also confirm the shipped preview's own tests pass on this
checkout before treating anything you see as representative:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -p no:cacheprovider tests/test_doctor_preview.py tests/test_doctor_adapter.py -q
```

Both steps above were run against this exact checkout while writing this
script (see "What was verified while preparing this" below).

## Who the walkthrough is for

A Revit-using BIM subcontractor's BIM manager: not a programmer, does not read
JSON, does not use a CLI. Ask your colleague to approach it that way — narrating
what they understand from the screen, not what they already know about the
Framework internals.

## Before you start

- The entry screen offers two experiences. Read both short descriptions out
  loud before picking one: what does each say it will and will not do?
- Every screen keeps a small badge in the top-left showing which experience you
  are in. Check it after every click in Tasks 1–7 — if it ever seems to say
  something different from what you expected, stop and write down exactly what
  it said, rather than assuming it is a display lag.

## Tasks

### Task 1 — Tell the two experiences apart before running either

Read the entry screen. Without clicking into either card, answer: which one can
produce something you could use in a real project decision, and which one
cannot? Then open **fixture demonstration**.

Observe: does the page say, before you commit to a run, that policy and
determinations here are simulated and cannot be exported as a real record?

### Task 2 — Confirm what a record actually says before opening it

From the fixture run list, open **member-evidence**. Before scrolling to
activities, read the record context screen: model version (content hash, not
filename), handoff (who handed off to whom, at what milestone), Purpose Pack
and requested activities, declared scope.

Observe: is the model version shown as a content identifier rather than a file
name? Does the screen say scope is expanded and admitted by the Framework
rather than by this UI?

### Task 3 — Find a member that was never evaluated, and tell it apart from a pass

Open the **schedules-and-room-data-sheets** activity. Find the member whose
Framework verdict is `UNKNOWN`. Open its evidence.

Observe: does the detail page say in plain words that nothing was evaluated
under this binding yet (not a pass, not a fail, not "no issues")? Separately,
in the same activity's excluded-scope table, find `geo-reference` — does the
page explain why it has no verdict at all, distinctly from the `UNKNOWN`
member above?

### Task 4 — Find two verdicts for the same real-world object and see them kept apart

Switch to the **pair-verdicts** run, open **builders-work-openings**. Find the
element that appears in two different member pairs (refined from the same
source element) with two different Framework verdicts.

Observe: does the page show both pairs as separate rows with their own
verdicts, or does anything on the page collapse them into a single "best" or
"worst" status for the underlying element? Does anything on this page compute
or display an overall readiness percentage?

### Task 5 — Ask the page who should act, and whether that answer is an authorisation

Pick any `BLOCKED` or `UNKNOWN` member and open its evidence. Find the section
that names who should act on it.

Observe: how many distinct role-like fields does the page show, and does it
say plainly that none of them is a dispatched assignment or a real person's
authorisation? Does it say a risk-authorisation step is not implemented yet?

### Task 6 — Find a citation the page refuses to treat as proof

On the **pair-verdicts** run, open **ceiling-and-bulkhead-geometry**, then open
any `READY` member's evidence. Scroll past the evidence path to the section
below it.

Observe: is there a citation shown separately, labelled as background rather
than as support for the verdict above it, with its full text visible without
hovering? Does the page say anywhere that this citation must not be read as
proving the two models line up?

### Task 7 — Compare a recheck without assuming "different" means "fixed"

Open the **recheck-comparison** run, then its recheck comparison view. Find a
member that no longer appears as a pair in the new record.

Observe: does the page explain what happened to that member using words other
than "resolved" or "fixed"? Does it separately say what the old recheck
condition can and cannot be shown to have proven?

### Task 8 — Watch a real refusal, and don't let it look like a pass

Return to the entry screen, open **real input**, and run the one available
scenario.

Observe: does the page say plainly that no assessment record was produced?
Is the refusal text shown once, in full? Does the page avoid presenting this as
zero findings, as `UNKNOWN`, or as any kind of completed run? Does it say that
fixing this refusal is not a guarantee the next attempt will succeed?

### Task 9 — Find what this build refuses to pretend to have

Look for a model or version picker, a Pack or activity catalogue you can
change, a Singapore-checklist view, or any control that lets you dispatch a
task or sign off on a risk. Also check the project's `doctor/README.md`
"Not in this preview" list against what you actually saw.

Observe: does your colleague agree, from the screens alone, on what is not
here — without being told the list in advance?

## Record template

Copy this per session; keep the filled copy outside the repository.

```
session code (self-assigned, not a name):
date:
build under test: a438f5d5195af2186266b7d8bcf1904f0f153d10

for each task 1-9:
  task:
  what the screen showed:
  matched what this script expected? yes / partial / no:
  if partial or no, exact text or screenshot description:
  anything the tester could not explain from the screen alone:

overall:
  did any screen ever show simulated data without the fixture badge visible?
  did any screen ever turn a real refusal into something that looked like a result?
  anything the tester assumed the tool could do that Task 9 shows it cannot?
```

## What was verified while preparing this script

Every task above was walked through against `a438f5d` in a dedicated worktree
before being written down, with `requirements.txt` and `requirements-dev.txt`
installed and the preview served locally. `pytest tests/test_doctor_preview.py
tests/test_doctor_adapter.py` passed (45 passed, 143 subtests) on that same
checkout.

## Defects observed, not fixed

- **Narrow-viewport table wrapping.** `doctor/static/doctor.css` applies
  `overflow-wrap: anywhere` broadly (documented in the CSS as a deliberate
  choice to keep tables inside the viewport rather than overflowing
  horizontally). At laptop-narrow and tablet widths this breaks identifier
  text mid-word — e.g. `IfcBuildingElementProxy` splits across lines as
  `IfcBuildingElementP` / `roxy`, and `out_of_subject_class` splits as
  `out_of_subject_c` / `lass` — and it shrinks the repeated "查看证据与回源"
  detail link into a three-line wrapped tap target in the same conditions.
  Not a correctness defect: no data is wrong. It is a readability and
  tap-target-size concern for a manager reading exact enum values or tapping
  through evidence links on a tablet. Left for product/UI judgement on the next
  UI checkpoint.

## Needs product adjudication

- Whether the narrow-viewport wrapping above is worth a dedicated fix before
  the next commissioned UI checkpoint, or is acceptable for an internal
  preview never intended for a small screen.
- Whether "Task 9" should be extended once F2 (model/version and Pack
  selection) is commissioned, since that task currently only confirms an
  absence.
