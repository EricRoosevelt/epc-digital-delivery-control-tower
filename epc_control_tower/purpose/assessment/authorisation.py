"""Whether a project's policy authorises one promotion, asked when it is consumed.

ADR 0003 §4.4 field 5 and §7.2's first two rows fix what a ``CONDITIONAL``
promotion must be able to prove about its authoriser: a role listed under
``overlay.risk_authorisations[]`` for the **exact** ``pack_id::resolution_kind``
the promotion is granted against. This module answers that one question and
nothing else. It does not build a promotion, does not carry §4.4's nine fields,
does not write a successor record, and is reached by no code path in
:mod:`~.evaluator`, :mod:`~.recheck` or :mod:`~.record` — a promotion is a later
checkpoint's, and until one exists nothing consumes this.

**The gate fires on consumption, and that asymmetry with §4.3 is deliberate.**
§4.3's ``team_mapping`` gate is *static*: it reads over the activity's reachable
non-``READY`` leaves before any subscope is assessed, because staffing is a
question every non-``READY`` record must answer. The assignment sentence is
written whichever leaf is reached, so founding it on a demonstration row would
assert a staffing decision nobody took. Authorisation is not that shape. A
``CONDITIONAL`` must originate in a named authorisation event (Framework
invariant 6, Checkpoint B §1), and *the event not having happened* is the normal
state — Checkpoint B §3's live conclusion is that no activity in that handover is
``CONDITIONAL``. A project with no authorisation policy at all is complete and
correct; it simply cannot promote.

Reversing the two is not a tidiness question, because the consequence is
measurable and points the wrong way. Give ``risk_authorisations`` a
``team_mapping``-shaped static gate and ``pcert-sample`` stops producing even one
``BLOCKED`` row: nobody there is authorised to release a missing asset identity,
so the request would be refused before any subscope was assessed, and the system
would decline to say *the equipment schedule is blocked for missing asset
identity* on the grounds that nobody may release it. The gate would suppress the
refusals rather than the releases, and the safety direction would be inverted.
That is why this one is consumption-triggered and §4.3's is not, and why neither
should be "unified" with the other.

**Three answers, and they are three because they send a person to three
different places.**

* :data:`NO_AUTHORISATION_PATH` — no ``overlay.risk_authorisations[]`` row
  addresses this exact ``pack_id::resolution_kind``. There is no authorisation
  path for that deficiency in this project, and creating one is a policy
  decision nobody has taken. Never resolved by reading the route's
  ``default_role``, by any role staffed for resolving work, or by a role listed
  for some other ``resolution_kind``.
* :data:`ROLE_NOT_AUTHORISED` — a decided row exists and does not list the role
  this citation named. ADR 0002 §3.8: that is not a promotion, it is an
  unauthorised release. The policy is real and this citation falls outside it.
* :data:`AUTHORISED` — a decided row exists and lists the cited role. This is the
  only answer a promotion may rest on.

**And two refusals**, for a citation that cannot be resolved against policy at
all rather than one policy answers:

* ``risk-authorisation-decision-basis-illustrative`` — the row exists and reads
  ``illustrative``. Same family as §4.3's ``team_mapping`` gate and §1.2 item
  4's ``accepted_evidence_methods`` gate, and deliberately a third code: the row
  a maintainer must edit is a third row in a third table, and reporting it as
  missing would send them looking for a row already there. A release founded on
  a demonstration row would record a risk-acceptance policy this project never
  decided, which is the fabrication ``decision_basis`` exists to prevent.
* ``risk-authorisation-kind-borrowed`` — the citation was granted under a
  different ``pack_id::resolution_kind``. An authorisation is granted against
  one deficiency; carrying it to another is not a weaker promotion, it is a
  different release nobody authorised. The check is a comparison of both halves,
  not of the role, precisely because a role may legitimately be listed for
  several kinds — in ``pcert-sample`` one role is listed for both of them.

**Every failure here is promotion-scoped.** It refuses the promotion; it never
refuses the assessment request, and the subscope's own ``BLOCKED`` or ``UNKNOWN``
verdict stands unchanged beneath it (§7.2's opening: *the promotion refuses, the
leaf stands*). The request-scoped refusals of §7.1 are untouched by this module.

Deterministic like everything else here: a lookup and two membership tests over
frozen strings, no clock, no unordered iteration, and nothing written anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import PurposeAssessmentError
from ..model import PROJECT_DECISION, ComposedPurposeInputs

__all__ = [
    "AUTHORISED",
    "NO_AUTHORISATION_PATH",
    "RISK_AUTHORISATION_ANSWERS",
    "ROLE_NOT_AUTHORISED",
    "AuthorisationCitation",
    "RiskAuthorisationDecision",
    "resolve_risk_authorisation",
]

#: A decided row lists the cited role. The only answer a promotion may rest on.
AUTHORISED = "authorised"

#: No row addresses this exact ``pack_id::resolution_kind``. Not a defect: a
#: project is entitled to have no way of releasing a given deficiency.
NO_AUTHORISATION_PATH = "no-authorisation-path"

#: A decided row exists and does not list the cited role — an unauthorised
#: release, not a promotion (ADR 0002 §3.8).
ROLE_NOT_AUTHORISED = "role-not-authorised"

#: The closed answer vocabulary. Three, and never collapsed to "not authorised":
#: the second says no policy exists to change, the third says one does.
RISK_AUTHORISATION_ANSWERS = (AUTHORISED, NO_AUTHORISATION_PATH, ROLE_NOT_AUTHORISED)


def _refuse(code: str, message: str) -> None:
    raise PurposeAssessmentError(code, message)


@dataclass(frozen=True, slots=True)
class AuthorisationCitation:
    """The authorisation a promotion cites, as it was granted.

    It carries the ``pack_id`` and ``resolution_kind`` it was granted **under**,
    not the ones being promoted, and that is the whole reason this is a type
    rather than a bare role string. An authorisation is granted against one
    named deficiency; the two are compared, and a citation that does not name
    the deficiency being promoted is refused rather than read as covering it.

    ``role`` is the ``may_authorise_roles`` entry the authoriser acted under —
    ADR 0003 §4.4 field 5. The named authoriser themself is field 4, is recorded
    separately and in full, and is not derived from this one; neither is the
    resolving assignment of §4.3, which is a different person answering a
    different question.
    """

    pack_id: str
    resolution_kind: str
    role: str


@dataclass(frozen=True, slots=True)
class RiskAuthorisationDecision:
    """What this project's policy says about one promotion's authorisation.

    Carries no ``default_role``, no assignee and no authoriser name: those are
    §4.3's and §4.4 field 4's, and a decision object that offered a role of its
    own would be the first place a caller could pick one up as a fallback.
    """

    answer: str
    project_id: str
    pack_id: str
    resolution_kind: str
    cited_role: str
    may_authorise_roles: tuple[str, ...] = ()
    reason: str = ""

    @property
    def supports_promotion(self) -> bool:
        """Exactly one answer does, and the other two do so for different reasons."""

        return self.answer == AUTHORISED

    @property
    def address(self) -> str:
        """The compound reference the policy is keyed on, as §4.4 field 5 words it."""

        return f"{self.pack_id}::{self.resolution_kind}"


def resolve_risk_authorisation(
    *,
    composed: ComposedPurposeInputs,
    pack_id: str,
    resolution_kind: str,
    citation: AuthorisationCitation,
) -> RiskAuthorisationDecision:
    """Resolve one promotion's authorisation against this project's Overlay.

    ``pack_id`` and ``resolution_kind`` are the promotion's — the leaf being
    released. ``citation`` is the authorisation offered for it. The two are
    compared before any policy row is read, because a citation granted elsewhere
    is not weaker evidence for this release, it is evidence about another one.

    Checked in a fixed order, so the answer a caller gets never depends on which
    defect is looked for first:

    1. the promotion's ``pack_id::resolution_kind`` is one this composed
       configuration can actually produce — otherwise
       :data:`NO_AUTHORISATION_PATH` would report a real absence of policy for a
       deficiency that does not exist;
    2. the citation addresses that same address exactly;
    3. a row exists for it — otherwise :data:`NO_AUTHORISATION_PATH`;
    4. that row records a decision this project took;
    5. the row lists the cited role — otherwise :data:`ROLE_NOT_AUTHORISED`.

    Step 4 precedes step 5 deliberately. An unlisted role under a demonstration
    row has two things wrong with it, and reporting the narrower one would leave
    a maintainer fixing the role list on a policy nobody decided.
    """

    pack = None
    for candidate in composed.packs:
        if candidate.pack_id == pack_id:
            pack = candidate
            break
    declared = False
    if pack is not None:
        try:
            pack.route(resolution_kind)
        except KeyError:
            declared = False
        else:
            declared = True
    if not declared:
        detail = (
            f"this project binds no pack {pack_id!r}"
            if pack is None
            else f"pack {pack_id!r} declares no resolution_kind {resolution_kind!r}"
        )
        _refuse(
            "risk-authorisation-resolution-kind-unresolved",
            f"a promotion was offered for {pack_id}::{resolution_kind} and {detail}. "
            "Answering 'no authorisation path' would report an absence of policy for a "
            "deficiency this configuration cannot produce, which is a different and "
            "false statement",
        )

    if citation.pack_id != pack_id or citation.resolution_kind != resolution_kind:
        _refuse(
            "risk-authorisation-kind-borrowed",
            f"the promotion is for {pack_id}::{resolution_kind} and the authorisation "
            f"cited was granted for {citation.pack_id}::{citation.resolution_kind}. An "
            "authorisation is granted against one named deficiency; it is never carried "
            "to another, and a role listed for both kinds does not make it one "
            "authorisation",
        )

    row = None
    for candidate in composed.overlay.risk_authorisations:
        if (candidate.pack_id, candidate.resolution_kind) == (pack_id, resolution_kind):
            row = candidate
            break

    if row is None:
        return RiskAuthorisationDecision(
            answer=NO_AUTHORISATION_PATH,
            project_id=composed.project_id,
            pack_id=pack_id,
            resolution_kind=resolution_kind,
            cited_role=citation.role,
            reason=(
                f"no overlay.risk_authorisations row addresses "
                f"{pack_id}::{resolution_kind}, so this project has no authorisation "
                "path for that deficiency at all. Giving it one is a policy decision, "
                "not a lookup: the route's default_role does not stand in, a role "
                "staffed to resolve the work does not stand in, and a role listed for "
                "another resolution_kind does not stand in"
            ),
        )

    if row.decision_basis != PROJECT_DECISION:
        _refuse(
            "risk-authorisation-decision-basis-illustrative",
            f"the overlay.risk_authorisations row for {pack_id}::{resolution_kind} "
            f"lists {sorted(row.may_authorise_roles)} with decision_basis "
            f"{row.decision_basis!r}. Promoting on it would record a risk-acceptance "
            f"policy project {composed.project_id!r} never decided; the row exists, so "
            "this is not the missing-row case, and the line to edit is in "
            "overlay.risk_authorisations rather than in team_mapping or in "
            "accepted_evidence_methods",
        )

    if citation.role not in row.may_authorise_roles:
        return RiskAuthorisationDecision(
            answer=ROLE_NOT_AUTHORISED,
            project_id=composed.project_id,
            pack_id=pack_id,
            resolution_kind=resolution_kind,
            cited_role=citation.role,
            may_authorise_roles=row.may_authorise_roles,
            reason=(
                f"role {citation.role!r} is not listed in may_authorise_roles "
                f"{sorted(row.may_authorise_roles)} for {pack_id}::{resolution_kind}. "
                "This project decided who may release that deficiency and this is not "
                "one of them, so what was offered is an unauthorised release rather "
                "than a promotion"
            ),
        )

    return RiskAuthorisationDecision(
        answer=AUTHORISED,
        project_id=composed.project_id,
        pack_id=pack_id,
        resolution_kind=resolution_kind,
        cited_role=citation.role,
        may_authorise_roles=row.may_authorise_roles,
    )
