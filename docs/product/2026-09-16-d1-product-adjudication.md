# D1 product adjudication

Date: 2026-09-16. Owner: Product Manager.
Original requirement: [dual-track commission](2026-09-16-dual-track-delivery-plan.md),
commit `bdd67b5719d1dd4f48af3af992ed0cb150035104`.
Design: PR #11, `967b9aab53f3193185fc5731437c8bc9985e1aba`.

## Evidence and approval boundary

Inputs were the Tech and BIM reviews of `782c63e` and the UI revision handoff,
forwarded by the user in this PM conversation. This file records the PM's
adopted constraints and decisions, not a verbatim archive of those reviews or
of the unavailable original task packet. Do not cite it as such an archive.
The revised design itself preserves the eight constraints in section 4.

PM read the revised design and `purpose/assessment/reading.py`, checked the
revision's whitespace diff, and inspected PR CI run `35073646343` at the exact
new head: both platforms passed every step. This is not a new domain audit or
an executed UI acceptance test. Latest-head Tech/BIM targeted closure remains
required before merging PR #11; no wholesale redesign is requested.

## Product decisions

1. D1 requires member-level coverage for this Pack, not a whole-model history
   of every element's evaluation. F1's element-level coverage extension is
   deferred, not a D1 dependency. Reopen if another Pack's bindings need it or
   a concrete user workflow requires that claim.
2. Display existing reading distinctions at their binding scope: no finding,
   not-applicable finding, and evaluated reading. Do not claim an element has
   never been evaluated by any rule. This Pack-specific interpretation is not
   a universal checker promise; no new engine outcome is commissioned.
3. F8 is not a prerequisite for the first prototype. Display the complete
   exception text once until Framework exposes separate message text. Never
   parse formatted exception strings to classify errors or remove prefixes.
4. For the first prototype, omit the optional baseline limitation table unless
   trusted provenance is available. No new baseline-detection subsystem is
   required merely to show explanatory text. Show the actual refusal and the
   limitation that it is not an exhaustive diagnosis.
5. Singapore dispositions remain BIM recommendations pending separate PM
   adjudication. This UI review does not approve the research shortlist.
6. English remains the default for README, ADRs and shared Framework contracts.
   Chinese is permitted for product/UI working designs and this user-facing
   workflow. Keep identifiers unchanged and link authoritative sources; do
   not maintain mandatory duplicate translations or rewrite PR #11 for language.

## Adopted domain constraints (corrected summary)

These eight constraints are the PM-adopted D1 baseline, superseding any earlier
member/element conflation in conversation. They do not replace technical proof.

1. The zero-finding acceptance scenario is a member under its actual binding.
   Use the chimney in schedules/ceiling; geo-reference belongs in exclusions.
2. Preserve member pairs and their individual verdicts; no best/worst element
   roll-up. Keep refinement and correspondence visible.
3. Show exclusions per activity, by default, without verdicts or assignees.
4. Refusal is no assessment record, not an empty successful run. Fixing the
   first refusal does not guarantee that subsequent evaluation will succeed.
5. Keep R-010's full limitation in contextual evidence, never alignment proof.
6. Recheck member disposition, current verdict and old-condition evidence are
   distinct. READY caused by a changed determination is not repaired geometry.
7. Separate default resolving role, policy mapping and actual authorisation;
   neither a mapping nor a determination signature invents an authorisation.
8. Singapore research is a separate, unimplemented experience without verdicts,
   execution controls or completed-check statistics.

Empty storey values display the recorded lack of storey attribution, not an
automatic modelling defect. Real execution and fixture demonstration stay
explicitly separated, including after refusal or a settings change.

## Next commission after targeted closure

Tech should commission a minimal internal adapter and a runnable Doctor slice
as separate owned changes, not wait for all F1-F8 items. Framework owns the
adapter and existing records/digests; UI owns presentation. Demonstrate the
scoped fixture flow, the member evidence gap, separate pair verdicts, real
sample refusal, and the recheck counterexample. No real policy is rewritten.

F2/F3 and the fixture/refusal portion of F7 are necessary integration inputs.
Full F4 diagnostics, precise Revit navigation in F5, F6 lifecycle capabilities,
and arbitrary real-model intake in F7 are not prerequisites. Preserve visible
unsupported states. Existing E2 design work remains independent; this decision
does not authorize its implementation or E2.5-E4.

The Tech packet must fix the exact base, interface ownership and acceptance
evidence. Stop at a runnable reviewed preview, not release or customer claims.
