// The English wording table: the same tables as vocabulary.js, key for key,
// for the screens that are translated. A table that is not here is not
// translated yet, and a screen that needs one is shown in English as "not
// translated yet" rather than in two languages at once (see i18n.js).
//
// Two kinds of entry live here, and the English vocabulary record says which
// is which:
//
// * **originals** — where the Pack, the record or this repository's product
//   documents already say it in English, the English interface shows that
//   text as written, never a translation of the Chinese gloss back into
//   English. What the record carries is read from the record; the rest is
//   copied here and tests compare each one with its source;
// * **written for this interface** — everything else. Wording that states a
//   verdict, an activity, a problem type or a limit is domain content and goes
//   to the BIM reviewer like the Chinese does; none of it has been reviewed yet.
//
// Nothing about a verdict, a count, a provenance tag or a limit may differ
// between the two tables: they are two wordings of one page.

// ---------------------------------------------------------------------------
// Originals
// ---------------------------------------------------------------------------

// Each activity's name is the Pack's `label`; what it needs is the product
// document's "What Architecture does next with it" list, as written there.
export const ACTIVITY_NAMES = {
  "builders-work-openings": {
    name: "Builder's-work openings",
    needs: "Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof.",
  },
  "ceiling-and-bulkhead-geometry": {
    name: "Reflected ceiling and bulkhead layout",
    needs:
      "Needs to know where MEP equipment physically is, in which storey, so ceiling zones and bulkheads can be drawn around it.",
  },
  "schedules-and-room-data-sheets": {
    name: "Room data sheets and equipment schedules",
    needs: "Needs each piece of equipment to carry the project's asset identity, so a schedule can be keyed to it.",
  },
};

// What to do and what a recheck must show, one pair per problem type: the
// English of the Chinese sentences in vocabulary.js, which are the BIM
// reviewer's table and, for the uncovered asset identity, the product's ruling.
// They carry the same obligation in both languages. The record's own route
// words (`next_action`, `recheck_condition`) are a source, not an instruction:
// they stay one fold away on the item pages, labelled as such, and are never
// shown as what to do. No sentence names a Revit parameter or an export
// mapping, or uses the record's internal words.
export const ACTIONS = {
  "missing-project-asset-identity": {
    action:
      "In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-export the model",
    recheck:
      "On the reissued model, this element passes every requirement listed",
  },
  "asset-identity-not-evaluated": {
    action:
      "The existing asset-identity rules do not reach this element, so whether it has an asset identity has not been evaluated, and it cannot be judged to be missing one; " +
      "for the same reason, whether this work can start cannot be decided. First confirm whether the project's convention requires this element to have an asset identity, " +
      "and whether the rules should reach it. Until that is confirmed, this does not mean it must have one.",
    recheck: "Every element in the scope has an evaluation result under the requirements bound to it",
  },
  "in-model-position-not-evaluated": {
    action:
      "This is not a known model defect. Its spatial assignment has not been evaluated yet: the spatial-assignment check rules do not reach this element. " +
      "This step is to extend the rules' scope of application so that the check reaches it, not to change the model; only once it is covered and the check has run will it be known whether the model needs changing",
    recheck: "Every element in the scope has a check result under the requirements bound to it",
  },
  "penetration-not-determined": {
    action:
      "This is not a known model defect. No coordination review has yet determined whether it passes through the receiving side's elements; " +
      "hold a review and record either “no penetration” or which elements it passes through",
    recheck: "A recorded review determination exists for the model versions listed",
  },
  "missing-corresponding-opening": {
    action:
      "In the receiving side's model, model an opening or shaft in the element it passes through, not a void in the handing-over side's model. One opening for each element it passes through",
    recheck:
      "The opening check for this pair reports “opening modelled and cross-referenced”. Modelling the opening alone is not enough",
  },
  "cross-model-alignment-not-confirmed": {
    action:
      "This is not a known misalignment. No one has yet confirmed, by the method the project accepts, that the two models are aligned; do this once against the model versions listed, and record it",
    recheck: "The alignment confirmation has been done and reports the models aligned, naming the model versions",
  },
  "mep-element-not-spatially-assigned": {
    action: "In the source model, place the element on its correct level (and, where the project requires spatial assignment, in its corresponding space), then re-export",
    recheck: "On the reissued model, this element passes its spatial-assignment requirement",
  },
  "cross-model-misalignment": {
    action:
      "Re-acquire the project's shared coordinate datum, re-export against the shared origin (not by moving geometry), then redo the alignment confirmation by the method the project accepts",
    recheck: "The alignment confirmation is redone against the new versions and reports the models aligned",
  },
  "opening-not-verifiably-linked": {
    action:
      "In the receiving side's model, add to the opening a cross-reference back to the element that passes through it. Where several elements pass through one opening, each needs its own",
    recheck: "The cross-reference check for this pair reports the opening cross-referenced",
  },
  "opening-status-not-determined": {
    action:
      "This is not a known missing opening. The review of the opening is not complete: whether it is modelled, and whether it is cross-referenced",
    recheck: "The check gives a definite result (cross-referenced / modelled but not cross-referenced / not modelled)",
  },
};

// The three verdicts, named by the record's own words, and what each means:
// the product document's definitions, as written there.
export const VERDICT_LABELS = {
  READY: "Ready",
  BLOCKED: "Blocked",
  UNKNOWN: "Unknown",
};

export const VERDICT_WORDS = {
  READY:
    "Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can start, within the assessed scope",
  BLOCKED: "A known unmet requirement prevents the activity",
  UNKNOWN:
    "An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified",
};

// An IFC class is shown by its own name in English: there is nothing to add.
export const IFC_CLASS_NAMES = {};

// ---------------------------------------------------------------------------
// Written for this interface
// ---------------------------------------------------------------------------

export const HOME = {
  title: "Items still to be dealt with in a model handover",
  lede:
    "For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, " +
    "which items still need dealing with, which elements each one involves, what it rests on, and what to do next.",
  status:
    "This is an example preview: a Revit file itself (.rvt) cannot be imported, and it gives no overall compliance or ready-to-build conclusion.",
  statusWithWorkspace:
    "Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. " +
    "The workspace check cannot have its model chosen or changed on this page; a Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion.",
  statusWorkspaceUnknown:
    "Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. " +
    "The simulated examples are available as usual. A Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion.",
  example: {
    title: "Look at a simulated example",
    body:
      "Start from a first check: find the items that need dealing with, and see which elements they involve, what to do, who deals with it " +
      "and what a recheck must show; then see how the same item changed after a recheck. What is simulated in the example is marked where it appears.",
    action: "Choose a simulated example",
  },
  attempt: {
    title: "See the check attempt on the bundled project",
    body:
      "The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. " +
      "This entry is not an import: it shows only this sample project, and you cannot swap in another model.",
    action: "See this check attempt",
  },
  cannot: [
    "Import a Revit file itself (.rvt), or choose or change the model in the example and workspace entries",
    "Give an overall compliance, ready-to-build or \"ready to hand over\" conclusion",
    "Write back to a model, upload to the cloud, or open an element in Revit",
  ],
  canHeading: "What you can do now",
  recommended: "Start here",
  cannotHeading: "What you cannot do yet",
  cannotNote: "These are not implemented, so the page has no entry for them.",
};

export const WORKSPACE_HOME = {
  title: "See a real check",
  body:
    "The server was started with a workspace holding a check that has already run: each element's result under each requirement. " +
    "If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. " +
    "This page only shows the check that has already run; you cannot choose or change a model on it.",
  action: "See this check",
  unknown: "Could not confirm whether the server was started with a workspace (that does not mean there is none). The error:",
};

export const MODE_LABELS = {
  fixture: "Simulated example",
  real: "Check attempt on the bundled project",
  workspace: "Real check in a workspace",
};

export const RUN_LABELS = {
  "member-evidence": "A first check: the model was handed over, and these items were found",
  "pair-verdicts": "The same check record: conclusions on pairs of elements (simulated example)",
  "recheck-both-reissued": "Recheck record 1 (simulated example)",
  "recheck-comparison": "Recheck record 2 (simulated example)",
  "recheck-consuming-reissued": "Recheck record 3 (simulated example)",
  "recheck-key-change-only": "Recheck record 4 (simulated example)",
  "recheck-member-gone": "Recheck record 5 (simulated example)",
  "recheck-prior-without-basis": "Recheck record 6 (simulated example)",
  "recheck-producing-reissued": "Recheck record 7 (simulated example)",
  "recheck-producing-reissued-content-changed": "Recheck record 8 (simulated example)",
  "recheck-requirement-relaxed": "The models did not change, but a handover conclusion did",
  "recheck-semantics-changed": "Recheck record 10 (simulated example)",
  "real-refusal": "A check attempt on the bundled sample project",
};

export const EXAMPLES = {
  "member-evidence": {
    step: "Step 1",
    question:
      "The handing-over side has handed over its model: which items need dealing with, who deals with each, and what does each one need?",
    given:
      "This example was given: the bundled sample project's two models; the handling teams, and the human determinations " +
      "(whether something passes through, the state of openings, whether the two models are aligned), set by the example.",
  },
  "recheck-requirement-relaxed": {
    step: "Step 2",
    question:
      "The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one changed, and why?",
    given:
      "This example was given: one cited check requirement was relaxed; neither the handing-over nor the receiving side's model version changed.",
  },
};

export const EXAMPLE_NOTE =
  "An example's description is written by whoever built the example and says only what the example was given; it is not a conclusion of any check. " +
  "What the check concluded is on the result page only.";


export const DEMO_NOTICE =
  "Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions; " +
  "the evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination — which one, the \"Basis\" line beside each conclusion says (citation by citation). " +
  "Not for formal project decisions, and no formal check record can be exported.";

export const SOURCE_SUMMARY = {
  lead: "A simulated example shipped with the tool, not your model; project settings such as teams are for demonstration, not for formal project decisions.",
  cites: "This record's conclusions cite {kinds}, labelled citation by citation on the \"Basis\" line beside each conclusion.",
  citesNone: "This record's conclusions cite no evidence.",
  noRecord: "Whether the evidence a conclusion cites is real or simulated is labelled citation by citation on the \"Basis\" line beside it.",
  kinds: {
    "finding-real": "real check output",
    "finding-fixture": "simulated check results",
    "determination-fixture": "simulated human determinations",
    "determination-unmarked": "determinations of unstated source",
  },
  join: ", ",
  lastJoin: " and ",
  more: "About the sources",
};

export const PROVENANCE_NOTICE =
  "Each citation's source label on this page is decided from that citation alone (whether it carries the simulation marker), never inferred for the whole page or record:";

export const CITATION_PROVENANCE = {
  "finding-real": {
    key: "real",
    short: "Real check output",
    long: "A check-result citation without the simulation marker: from a real check run, the product of checking a real IFC model against real rules.",
  },
  "finding-fixture": {
    key: "fixture",
    short: "Simulated check result",
    long: "A check-result citation with the simulation marker (starting with fixture): generated by the example, not the output of any real check run.",
  },
  "determination-fixture": {
    key: "fixture",
    short: "Simulated human determination",
    long: "A determination citation with the simulation marker: supplied by the example; no coordination review ever took place.",
  },
  "determination-unmarked": {
    key: "unmarked",
    short: "Determination of unstated source",
    long:
      "A determination citation without the simulation marker: a determination is not the output of a check run, and this interface has nothing it can verify about where it came from, " +
      "so it says neither real nor simulated.",
  },
};

export const NOT_CARRIED = "Not carried in the record";
export const EMPTY_STRING = "(an empty string in the record)";
export const UNRECOGNISED = "unrecognised value, shown as it came";

export const VERDICT_SCOPE =
  "Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; " +
  "it is not an overall verdict on whether the model is good, nor a statement that some check passed.";

export const ITEM_UNIT =
  "An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. " +
  "The same element can appear in several items, so the number of items is not a number of defects.";

export const HOW_TO_READ = "How to read this page";

export const ACTION_GROUPS = {
  open: {
    label: "Items to deal with",
    summary: "the record gives an action",
    none: "The record gives no action for any item.",
    note: "Each item's page says which elements it involves, what to do, who deals with it and what a recheck must show.",
  },
  unplaced: {
    label: "Items to check by hand",
    summary: "the record gives no current state; check by hand",
    none: "The record gives a current state for every item.",
    note: "The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed.",
  },
  none: {
    label: "Items for which the record gives no follow-up action",
    summary: "the record gives no follow-up action",
    none: "There are no such items.",
    note: "The record gives no follow-up action for the items below. Each line's conclusion stands on its own, with its scope beside it.",
  },
};

export const BESIDE = {
  readyScope: "Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete.",
  unknown: "\"Unknown\" means whether this work can start cannot be decided: it does not mean the element has no problem, and it is not a system error.",
  assetIdentity: "Where the asset-identity value comes from, and which Revit parameter it maps to, the record does not say.",
  team: "The handling team is an entry in the record; it does not mean the work has been assigned.",
  simulatedTeam: "Example handling team",
  noTeam: "Not given in the record",
  defaultRole: "Default handling role (the rule's default, not an assignment)",
  unchanged: "Unchanged by the recheck",
};

export const READY_NOTES = {
  "ceiling-and-bulkhead-geometry": [
    "The rule proves only that the element has a storey or space assignment; it does not check that the receiving model has a matching storey.",
    "This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning marker passing.",
  ],
};

export const BASIS_WORDS = {
  simulated: "This conclusion rests on simulated evidence:",
  real: "Basis of this conclusion:",
  sharedSimulated: "Basis shared by the items in this group, some of it simulated:",
  sharedReal: "Basis shared by the items in this group:",
  none: "This conclusion cites no evidence.",
  gaps: {
    "no-finding": "no check result at all (a real absence)",
    "no-determination": "no determination yet (a real absence)",
    "not-applicable-finding": "there are check results, but the check did not apply and did not cover it",
  },
};

export const RESOLUTION_KINDS = {
  "missing-project-asset-identity": "The project's required asset identity is missing",
  "asset-identity-not-evaluated": "Not a known model defect: the existing asset-identity rules did not cover this element",
  "mep-element-not-spatially-assigned": "It has no storey or space assignment",
  "in-model-position-not-evaluated": "Not a known model defect: the storey or space check did not cover it",
  "cross-model-misalignment": "The two models are not aligned to a common datum",
  "cross-model-alignment-not-confirmed": "Not a known misalignment: nobody has confirmed yet that the two models are aligned",
  "penetration-not-determined":
    "Not a known model defect: no coordination review has determined yet whether it passes through the receiving side's elements",
  "opening-not-verifiably-linked": "The opening is modelled, but not linked to this element that passes through it",
  "missing-corresponding-opening": "No corresponding opening is modelled in the element it passes through",
  "opening-status-not-determined": "Not a known missing opening: the review of the opening has not been completed yet",
};

export const ELEMENT_WORDS = {
  unnamed: "No name filled in in the model",
  noFacts: "The record returned nothing readable about this element",
  noStorey: "No storey assignment in the model",
  noDiscipline: "The record gives no discipline; this interface does not infer one from a model identifier",
  modelIsNotDiscipline: "This is a model identifier, not a statement of discipline",
  noClassName: "(IFC class)",
  naming:
    "The name is taken from the model file itself; it may be empty or shared with other elements. To find it in the model, use the GlobalId.",
};

export const FAULT_WORDS = {
  fault: "Program fault: no check data was received",
  unavailable: "The check program is unavailable",
  note: "This is a problem of the program itself, not a judgement about any project or model; there are no check results to show.",
};

export const ENVELOPE_WORDS = {
  missing: "outcome={outcome} but {key} is missing",
  unexpected: "outcome={outcome} but it also carries {key}",
};

export const COMMON = {
  colon: ": ",
  aside: " ({text})",
  emptyList: "(an empty list in the record)",
  unknownMode: "Unrecognised entry ({mode})",
  unnamedElement: "Unnamed element",
  and: " and ",
  oneElement: "One element",
  twoElements: "A pair of elements",
  nElements: { one: "{count} element", other: "{count} elements" },
  inModel: " · model ",
};

export const CONTEXT = {
  project: "Project {project}",
  handover: "Handover: {from} → {to} · {milestone}",
  workspaceRun: "Check run",
  noJudgement: "Check results only, no handover judgement",
  noResult: "No check results this time",
  home: "Back to the home page",
};

export const DIRECTORY = {
  realNote:
    "The repository comes with a sample project; below is a check attempt on it. This entry shows only that sample and cannot be switched to another model; to check your own IFC4 files, use \"Check your own IFC model\" on the home page. A Revit file itself cannot be imported.",
  exampleTitle: "Choose a simulated example",
  exampleIntro: "Each example is one check record.",
  empty: "There is nothing to look at under this entry yet.",
  exampleTag: "About this example",
  open: "Open this example's result",
  othersHeading: "Other simulated examples",
  othersNote: "These examples have no description yet, and the recheck records have only a number for now; this round did not touch them.",
};

export const FIRST = {
  back: "← Back to the examples",
  title: "First check result: items to deal with",
  runLine: "{mode}: {run}",
  summary: "This result: {items} in all; to deal with: {todo}",
  items: { one: "{count} item", other: "{count} items" },
  verdictLine: ": the work concerned is ",
  quietLine: ": {summary} (listed further down this page)",
  elementsLine: {
    one: "{unit} This record involves {count} element.",
    other: "{unit} This record involves {count} different elements.",
  },
  action: "What to do",
  problem: "Problem",
  openItem: "See this item: the element, what to do, who deals with it, what a recheck must show",
  cardDetails: "Element details and what to do",
  cardElements: "Element details",
  openCard: "See this item",
  openHeading: { one: "{label}, by handling team ({count} item)", other: "{label}, by handling team ({count} items)" },
  team: "Handling team ",
  teamCount: { one: ": {count} item", other: ": {count} items" },
  columns: { problem: "Problem", work: "Which work: conclusion", count: "Items" },
  quietHeading: { one: "{label} ({count} item)", other: "{label} ({count} items)" },
  separator: " | ",
  nextHeading: "Then: see how this record changed after a recheck",
  nextLink: "Open the example \"{run}\"",
  nextAfter: ". Each item's page also links straight to how that item changed in the recheck.",
  traceSummary: "Tracing: record identity, rule version, record codes",
  recordLink: "This record's requested scope, versions and sources",
  // In English the page behind these links is Chinese only: said before the
  // click, beside the link, not after it.
  notRevised: " (Chinese only: that page has not been translated or revised yet, and still uses internal terms)",
  traceItem: "Item",
  traceOrdinal: "Internal group number",
};

export const READING_GUIDE = {
  verdictWords: "The three conclusion words",
  verdictLine: "{label}: {meaning}.",
  provenance: "How the source of evidence is labelled",
  teams: "Handling team and default handling role",
  teamsBody:
    "The handling team is taken from the staffing in the record; the default handling role is the rule's default, an input to the staffing, not an assignment. The two are shown apart.",
};

export const APP = {
  loading: "Reading the check record…",
  noPage: "There is no such page: {screen}",
  technical: "Technical detail (as given):",
  up: "Back up one level",
  notInMode: "There is no {run} under this entry",
  invalid: "The returned data does not match the agreed shape: {problem}. No result is shown.",
  unknownOutcome: "Unrecognised outcome {outcome}",
  notObject: "The returned data is not an object",
  modeMismatch: "The returned data's mode is {got}, not the entry chosen, {want}",
  missingElements: "The returned data has no elements",
  recordMissing: "outcome=record but record is missing",
  digestMissing: "outcome=record but assessment_digest is missing",
  recordWithRefusal: "outcome=record but it also carries refusal",
  refusalIncomplete: "outcome=refusal but refusal has no code or text",
  refusalWithRecord: "outcome=refusal but it also carries record or assessment_digest",
};

export const PAGE = {
  title: "BIM Doctor preview",
  skip: "Skip to the content",
  contextLabel: "Current mode and context",
};

export const COPY = {
  button: "Copy",
  label: "Copy {value}",
  done: "Copied",
  manual: "Select it to copy by hand",
};

// ---------------------------------------------------------------------------
// The first-check item and the recheck (part 2 of the English path)
// ---------------------------------------------------------------------------

// A check's reason is the record's own English: there is nothing to gloss.
export const REASON_GLOSSES = {};

export const FINDING_STATUS = {
  FAIL: "Fail",
  PASS: "Pass",
  "N/A": "Not applicable",
};

export const ITEM = {
  missing: "The record has no such item",
  back: "← Back to the list of items (to this item's place)",
  kicker: "First-check item · {count}",
  conclusion: "1. Conclusion",
  needs: "What this work needs",
  actionHeading: "2. What to do, who deals with it, what a recheck must show",
  followUpHeading: "2. Follow-up",
  noFollowUp: "The record gives no follow-up action, handling team or default handling role for this item.",
  whichOne: "3. Which element",
  whichTwo: "3. Which two elements",
  details: "4. {heading}",
  nextHeading: "Then: how this item changed after a recheck",
  nextLink: "See this item in the example \"{run}\"",
  nextAfter: ". That is a recheck of this same record, and also a simulated example.",
  basisSummary: "Basis, citation by citation: the evidence this conclusion cites",
  context: "Background citations: not the basis of this conclusion, shown word for word.",
  traceSummary: "Tracing: internal keys and record codes",
  keys: "Internal keys",
  ordinal: "Internal group number",
  leaf: "Final outcome",
  memberLink: "See the full evidence path on the detail page",
};

export const ACTION = {
  what: "What to do",
  team: "Handling team",
  consequence: "What it means for this work",
  recheck: "What a recheck must show",
  noSentence:
    "This interface has written no action for the version this record uses. The source wording the record carries is in the fold below; it is not an instruction.",
  original: "Source wording (as the record carries it): for tracing, not an instruction",
};

export const ELEMENT_CARD = {
  traceKey: "Internal key for tracing",
  class: "Class",
  storey: "Storey",
  model: "Model",
  disciplineRow: "Discipline",
};

export const CONSEQUENCE_KINDS = {
  "work-cannot-start": "This work cannot start",
  "work-suspended": "This work is held until decided",
  "rework-risk": "Risk of rework",
  "re-identification-and-reissue-risk":
    "Risk of re-identification: documents that cite these identifiers would then have to be reissued too",
};

export const LEAF_READINGS = {
  "asset-identity/satisfied": "The project asset-identity requirements that apply to it passed, and it was actually evaluated",
  "asset-identity/unmet": "The project asset-identity requirement is not met",
  "asset-identity/not-yet-evaluated": "The asset-identity rules did not cover it",
  "in-model-position/satisfied": "It has a storey or space assignment",
  "in-model-position/unmet": "It has no storey or space assignment",
  "in-model-position/not-yet-evaluated": "The storey or space check did not cover it",
  "cross-model-alignment/confirmed":
    "A record confirms the two models are aligned to a common datum (by the method the project accepts, for the listed model versions)",
  "cross-model-alignment/misaligned": "The alignment confirmation found the two models not aligned",
  "cross-model-alignment/not-yet-confirmed": "No alignment confirmation yet",
  "penetration-determination/no-penetration":
    "A coordination-review determination says it passes through no element of the receiving model. With no penetration no opening is needed, so the opening was not assessed — this is not \"the opening is fine\"",
  "penetration-determination/penetration-confirmed":
    "A coordination-review determination says it passes through elements of the receiving model",
  "penetration-determination/not-yet-determined":
    "No coordination review has determined yet whether it passes through elements of the receiving model",
  "opening-status/cross-referenced":
    "This pair: the opening is modelled in the element passed through, and linked to the element passing through it",
  "opening-status/modelled-not-cross-referenced":
    "This pair: the opening is modelled in the element passed through, but not linked to the element passing through it",
  "opening-status/not-modelled": "This pair: no opening is modelled in the element passed through",
  "opening-status/not-yet-determined": "This pair: the review of the opening has not been completed yet",
};

export const LEAF_READING_WORDS = {
  label: "The result this conclusion rests on",
  notCarried: "The record does not give the result this item now rests on",
  unglossed: "This interface has no English for this result; see the tracing details",
};

export const DETAILS_WORDS = {
  heading: "What exactly is missing",
  absent: "Not given in the record: the returned data has no requirement details for this citation.",
  determinations:
    "This conclusion cites human determinations, not check results; a determination has no requirement details. What is missing is said in the conclusion and in \"What to do\" above.",
  nothingCited: "This conclusion cites no check result, so there are no requirement details to show.",
  requirement: "Requirement not met",
  requirementMet: "Requirement",
  rule: "Rule",
  status: "Result of that check",
  reason: "Reason",
  actual: "Value that check observed",
  noActual: "That check observed no value",
  hasActual: "That check observed a value; this page does not show it",
  expected: "The rule's own words",
  source: "Source the rule gives: ",
  projectAssumption: "This is a requirement assumed for this project (ProjectAssumption), not a general one.",
  gap: "What value to fill in, and which Revit parameter it maps to, the record does not say.",
  prior:
    "At the assessment before the recheck, this evidence's requirement and result were as follows. Having this description does not make the row comparable; the row's state is what is written above.",
  currentAbsent: "The corresponding evidence this record cites: its requirement details are not given in the record.",
};

export const EVIDENCE = {
  currentCitation: "Corresponding evidence this record cites: ",
  reason: "Reason: ",
  recordCause: "Reason the record gives (as written): ",
  trace: "Tracing (record codes and content fingerprints)",
  priorDigest: "Content fingerprint before the recheck",
  currentDigest: "Content fingerprint in this record",
  none: "The evidence path before the recheck cites no evidence.",
  rows: { one: " ({count} row)", other: " ({count} rows)" },
  empty: "(empty)",
  glossaryCode: "Code in the record",
  glossarySaid: "What this page says",
  meaning: "What \"{label}\" means",
  dispositionNow: "This item now",
  currentMissing:
    "The record gives this item's current place (internal number #{ordinal}), but it cannot be found in this record; this page does not match it up another way.",
  memberLink: "See every element and piece of evidence assessed with it on the detail page",
  reissueColumns: {
    side: "Side of the handover",
    role: "Role (from this request's handover)",
    model: "Model",
    reissued: "Re-issued?",
  },
  unrecognisedSide: "Cannot be recognised; see above",
  reissued: "Re-issued (new version)",
  notReissued: "Unchanged (original version)",
};

export const WORK = {
  unchanged: "{work}: {before} ({note})",
  changed: "{work}: before the recheck {before} → now {now}",
  missing: "{work}: before the recheck {before}; now: not given in the record",
};

export const RECHECK = {
  title: "Recheck result",
  notRecheck: "This record is not a recheck record, so there is no before-and-after to show.",
  unknownSuccessor:
    "This record follows a sealed record, but not as a recheck this page recognises: successor.kind = ",
  unknownSuccessorAfter: ". This page does not present it as a recheck.",
  resultTitle: "Recheck result: items to deal with",
  summary: { one: "This result: {count} item", other: "This result: {count} items" },
  groupLine: { one: "{count} item", other: "{count} items" },
  groupSummary: ": {summary}",
  models: "Models: {headline}.",
  moved: {
    one: "{count} item's conclusion differs from before the recheck:",
    other: "{count} items' conclusions differ from before the recheck:",
  },
  requirementChanged:
    "Of the old evidence cited before the recheck ({count} in all), the check requirement changed for {edited}.",
  groupHeading: { one: "{label} ({count} item)", other: "{label} ({count} items)" },
  cannotHeading: "What this preview cannot do",
  cannotNote: "These actions are not implemented, so the page has no buttons for them.",
  limitsHeading: "When reading a recheck result",
  sideModel: "{side} model",
  detailsSummary: "Before-and-after details: models, items, old evidence",
  modelsHeading: "Models",
  itemsHeading: {
    one: "The item in the record before the recheck ({count}), and where it stands now",
    other: "The items in the record before the recheck ({count}), and where they stand now",
  },
  evidenceHeading: {
    one: "The old evidence cited before the recheck ({count} row), compared with this record",
    other: "The old evidence cited before the recheck ({count} rows), compared with this record",
  },
  kindsNote: "Check results and human determinations are two kinds of evidence, counted apart and never added together.",
  traceSummary: "Tracing: record identity, model version fingerprints, record codes",
  priorDigest: "Fingerprint of the record before the recheck (assessment digest)",
  currentDigest: "Fingerprint of this record (assessment digest)",
  noChange: "(an empty list in the record: no model changed)",
  versionColumns: { side: "Side", prior: "Record before the recheck", current: "This record" },
  versionNote:
    "A version is a content fingerprint, not a file name. Which side changed is taken from the record's changed_models; this page does not compare fingerprints.",
  glossaryDispositions: "Where items stand now: record codes",
  glossaryConditions: "Conditions left before the recheck: state codes (there is no \"the whole condition is met\")",
  glossaryStates: "Old-evidence comparison: state codes",
  glossaryReasons: "Old-evidence comparison: reason codes",
  glossaryAspects: "Aspects that changed: codes",
};

export const RECHECK_ITEM = {
  missing: "The recheck record has no such item",
  back: "← Back to the recheck items (to this item's place)",
  kicker: "Recheck item · {count}",
  pairNote:
    "These two elements are no longer paired for checking: the penetration determination is now \"no penetration\" (see the reason the record gives below). " +
    "This does not mean the opening has been built, nor that the opening defect has been fixed.",
  model: "Models",
  actionHeading: "2. What to do, who deals with it, what a recheck must show",
  whichOne: "3. Which element",
  whichTwo: "3. Which two elements",
  noCurrent:
    "The record does not give this item's current place, so this page has no action, handling team or default handling role to show. " +
    "Those details from the record before the recheck did not come back with the recheck record either.",
  conditionHeading: "4. Was the exit condition left before the recheck reached this time?",
  priorCondition: "The exit condition left before the recheck: {text}",
  end: ".",
  conditionNote:
    "This says only how far the exit condition left before the recheck has been shown to be reached; read it apart from the conclusion now. A changed conclusion does not mean the original condition is met.",
  originalSummary: "Source wording and record codes: for tracing, not an instruction",
  conditionBasis: "condition_basis (as written)",
  evidenceHeading: "5. The evidence before the recheck",
  evidenceCount: {
    one: "{count} piece of old evidence was assessed together with this item",
    other: "{count} pieces of old evidence were assessed together with this item",
  },
  requirementChanged: {
    one: ", and for {count} of them the check requirement changed",
    other: ", and for {count} of them the check requirement changed",
  },
  priorSources: "Evidence cited before the recheck, by source: ",
  currentSources: "Corresponding evidence this record cites, by source: ",
  rowsSummary: "See each piece of old evidence and how it compared",
  shared: {
    one: "The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} item shares the rows below.",
    other: "The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} items share the rows below.",
  },
  noEvidence: "The group's evidence path before the recheck cites no evidence.",
  priorOrdinal: "Internal group number before the recheck",
  currentLine: "Current internal group number, verdict and final outcome",
};

export const RECHECK_MODEL = {
  producing: "Handing-over side",
  consuming: "Receiving side",
  listSeparator: ", ",
  aspectsChanged: "{list} changed",
  aspectsSame: "; {list} unchanged",
  end: ".",
  unrecognisedAspect: "\"{code}\" ({unrecognised})",
  unrecognisedKey: "key_changed = \"{value}\" ({unrecognised})",
  onlyRekeyed: "{rekeyed}: neither the evidence content nor the comparison basis changed.",
};

export const REQUIREMENT_CHANGED_NOTE =
  "The record also shows that, among the old evidence assessed together with this item, the check requirement changed for {count}; the record does not say whether it was relaxed or tightened. " +
  "Read this conclusion with that in mind; row by row, see \"The evidence before the recheck\".";

export const RECHECK_CANNOT = [
  "Start a new recheck or upload a new model",
  "Mark an item resolved, closed or risk-accepted",
  "Assign or notify anyone",
  "Open or locate an element in Revit",
  "Export a recheck record",
];

export const RECHECK_LIMITS = [
  "\"Comparison basis unchanged\" does not mean the whole handover needs no review.",
  "An element that is gone, or evidence with no counterpart, does not mean the problem was fixed.",
  "A model re-issued (on either side) does not mean a fix has happened.",
  "\"Only the model version changed\" does not mean the check result's content changed.",
  "\"Cannot be compared\" is not \"evidence missing\": where the old record kept no comparison basis, this page says honestly that it cannot compare.",
];

export const HANDOVER_SIDES = {
  producing: "the handing-over side's model in this handover",
  consuming: "the receiving side's model in this handover",
};

export const CITATION_KINDS = {
  finding: "Check-result citation",
  determination: "Determination citation",
};

export const CARRY_OVER_STATES = {
  equivalent: {
    label: "Comparison basis unchanged",
    meaning: "This old evidence has exactly one counterpart in this record, and every aspect compared is the same. ",
    caveat: "It only means the evidence need not be gathered again because its citation changed key; it does not mean the whole handover needs no review.",
  },
  changed: {
    label: "Comparison basis changed",
    meaning: "This old evidence has exactly one counterpart in this record, but at least one aspect differs. ",
    caveat: "Even if the result reads the same, it still counts as changed; which aspects changed is said on the row.",
  },
  "no-counterpart": {
    label: "No counterpart found",
    meaning: "It can be compared, but this record cites no evidence corresponding to it. ",
    caveat: "No counterpart does not mean the problem was fixed.",
  },
  "not-provable": {
    label: "Not enough basis to compare",
    meaning: "The comparison itself cannot be made, so it can be called neither unchanged nor changed. ",
    caveat: "This is \"cannot be compared\", not \"evidence missing\", and not \"no counterpart\".",
  },
};

export const CARRY_OVER_REASONS = {
  "finding-equivalent":
    "There is exactly one corresponding check result; model version, check result content, check requirement and checker are the same, aspect by aspect.",
  "finding-changed": "There is exactly one corresponding check result; compared aspect by aspect, at least one differs.",
  "no-counterpart-in-the-cited-run":
    "In the validation run this record rests on, this element has no check result under this requirement.",
  "counterpart-not-cited-under-the-current-binding":
    "The validation run has a corresponding check result, but this record does not cite it.",
  "sealed-citation-has-no-comparison-basis":
    "When the original record was sealed it kept no comparison basis for this citation (a record from an older version). This page will not make one up from the current rules, so it can only say honestly that it cannot compare.",
  "comparison-basis-version-unknown": "The comparison basis the original record kept is of a version this system does not recognise.",
  "subject-not-present":
    "The element this evidence is about is no longer in this record (where it went: see \"the reason the record gives\"). An element that is gone is not fixed.",
  "counterpart-not-unique":
    "This time there is more than one candidate corresponding check result, and the system does not choose between them (all candidates: see \"the reason the record gives\").",
  "requirement-semantics-basis-unavailable": "The sealed side or the current side has no comparison basis for the check requirement.",
  "comparison-basis-incomplete":
    "The sealed side or the current side lacks part of the comparison basis (model version, check result content digest or checker fingerprint).",
  "determination-same-reference-same-content": "The same determination: the same reference and the same content digest.",
  "determination-content-changed-under-the-same-reference":
    "The same reference, but the determination's content is no longer what the original record read (made again, re-attributed or re-signed). The new determination is read as evidence as usual; it just cannot be called the same determination as the original.",
  "determination-not-cited-by-this-record":
    "The model version did not change, and this record no longer cites this determination: another determination replaced it.",
  "determination-not-attributable-to-this-context":
    "The model version has changed, and the original determination was made against the old version, so it cannot be attributed to the current one. The evidence is not missing and the original determination is not wrong; a determination against the current version is needed.",
};

export const CHANGED_ASPECTS = {
  "model-version": "model version",
  "finding-content": "check result content",
  "requirement-semantics": "check requirement",
  checker: "checker",
};

export const ASPECT_NOTES = {
  onlyModelVersion:
    "Only the model version changed; that does not mean the check result's content changed. Nor does the record conclude whether this evidence can carry over to the new version.",
  semanticsSameOutcome:
    "The check requirement was edited, and the check result reads the same as before — but it was reached under the edited requirement and cannot be treated as the same evidence.",
  semanticsAndContent:
    "The check requirement was edited and the check result content changed too: the change in result may come from the edit to the requirement (for example a relaxed requirement), so it cannot be taken to mean the model was fixed. The record does not say whether the requirement was relaxed or tightened.",
  contentUnderSameRequirement:
    "The check requirement did not change, and the check result content did. This row does not record whether the result got better or worse; see the current conclusion.",
  checker: "The checker (the check program or its configuration) version differs: the same model and requirement may give a different result.",
  unrecognised: "There is an unrecognised aspect of change, so this page does not list the unchanged aspects.",
};

export const KEY_CHANGED = {
  yes: "The citation changed key (the new key is the \"corresponding evidence this record cites\" above). A change of key is not itself a change.",
  no: "The citation's key did not change.",
};

export const ONLY_REKEYED = "Only the citation's key changed";

export const CONDITION_STATES = {
  "named-outcome-observed": "Only the named outcome observed; the rest of the condition not checked",
  "named-outcome-not-observed": "Named outcome not observed",
  "no-machine-checkable-part": "The condition has no machine-checkable part; a person must read it",
  "not-comparable": "Cannot be compared: the corresponding elements are incomplete",
  "no-recheck-condition": "The original record had no recheck condition",
};

export const CONDITION_ENTRIES = {
  "named-outcome-observed": {
    text: "Only the named outcome observed; the rest of the condition not checked",
    plain:
      "The outcome named in the original recheck condition is now observed. The rest of the condition was not checked by machine and needs a person to confirm it against the original condition; this is not \"the whole condition is met\".",
  },
  "named-outcome-not-observed": {
    text: "Named outcome not observed",
    plain: "The outcome named in the original recheck condition is not observed now: the original condition is not reached.",
  },
  "no-machine-checkable-part": {
    text: "The condition has no machine-checkable part; a person must read it",
    plain:
      "The original recheck condition has no part a machine can check; a person needs to read the original condition and judge it. The record draws no conclusion on it.",
  },
  "not-comparable": {
    text: "Cannot be compared: the corresponding elements are incomplete",
    plain:
      "No conclusion can be drawn on the original recheck condition: some of the original elements are no longer in this record, so the condition has no complete subject to check. This does not mean the condition is met.",
  },
  "no-recheck-condition": {
    text: "The original record had no recheck condition",
    plain: "The original record had no recheck condition: the original conclusion left nothing outstanding.",
    plainNotReady: "The original record gave no recheck condition.",
  },
};

export const DISPOSITIONS = {
  present: "Still in this check's scope; conclusion and condition are read separately",
  "element-deleted-in-reissued-model": "Deleted in the re-issued model; that is not a fix",
  "element-out-of-subject-class": "No longer of this activity's subject classes; that is not a fix",
  "pairing-no-longer-derived": "These two elements are no longer paired for checking; that does not mean the opening was added",
  "outside-declared-scope": "This scope was not declared this time; that does not mean the problem is gone",
};

export const DISPOSITION_ENTRIES = {
  present: {
    text: "Still in this check's scope; conclusion and condition are read separately",
    next: "See the current place the record gives below: the conclusion now, the next step and the handling role all follow it.",
  },
  "element-deleted-in-reissued-model": {
    text: "Deleted in the re-issued model; that is not a fix",
    next:
      "The record gives no next step for a deleted element. Check in the source model whether this deletion was an intended design change; this preview cannot record that confirmation.",
  },
  "element-out-of-subject-class": {
    text: "No longer of this activity's subject classes; that is not a fix",
    next:
      "The record gives no next step for it. Check whether the element's class (the export mapping) was changed on purpose; a changed class only means this activity no longer checks it.",
  },
  "pairing-no-longer-derived": {
    text: "These two elements are no longer paired for checking; that does not mean the opening was added",
    next:
      "The record gives no next step for this pair. Check whether the basis that stopped them being paired (see \"the reason the record gives\") is a conclusion you accept; the original problem has not been shown to be fixed.",
  },
  "outside-declared-scope": {
    text: "This scope was not declared this time; that does not mean the problem is gone",
    next: "This element was not checked again this time. For a conclusion, a new recheck that includes it is needed; this preview cannot start one.",
  },
};

export const VERDICT_GROUPS = {
  changed: {
    label: "Conclusions that changed",
    none: "No conclusion changed.",
    notes: {
      none: "Neither model was re-issued, yet these conclusions changed: the change does not come from a model edit. Each item's old evidence says what changed.",
      reissued: "A model was re-issued. A changed conclusion does not say what became of the original problem; each item's old evidence says what changed.",
      unrecognised: "A changed conclusion does not say what became of the original problem; each item's old evidence says what changed.",
    },
  },
  unplaced: {
    label: "Items whose current place the record does not give",
    none: "The record gives a current place for every item.",
    note: "The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed.",
  },
  unchanged: {
    label: "Conclusions that did not change",
    none: "No conclusion stayed the same.",
    note: "An unchanged conclusion does not mean the evidence is unchanged; see each item for the old evidence.",
  },
};

export const REISSUE_CASES = {
  none: {
    headline: "Neither model was re-issued (versions unchanged)",
    detail: "This recheck uses the same pair of model versions as the original record, so the differences below do not come from model edits.",
    caveats: [],
  },
  producing: {
    headline: "The handing-over side's model was re-issued; the receiving side's model did not change",
    detail: "The handing-over side's ({from}) model {producing} is a new version; the receiving side's ({to}) model {consuming} is the original version.",
    caveats: [
      "Re-issuing on the handing-over side may have changed what passes through what, or which elements are involved; it cannot be taken to mean the receiving side's work (for example the openings) is done.",
      "A determination made against an old version cannot be attributed to the new one.",
    ],
  },
  consuming: {
    headline: "The receiving side's model was re-issued; the handing-over side's model did not change",
    detail: "The receiving side's ({to}) model {consuming} is a new version; the handing-over side's ({from}) model {producing} is the original version.",
    caveats: [
      "Re-issuing on the receiving side may be the way to a fix, but it does not mean the fix has happened (for example that the opening is complete).",
      "Likewise, a determination made against an old version cannot be attributed to the new one.",
    ],
  },
  both: {
    headline: "Both the handing-over and the receiving side's models were re-issued",
    detail: "The handing-over side's ({from}) model {producing} and the receiving side's ({to}) model {consuming} are both new versions.",
    caveats: [
      "Both sides changed at once: this page attributes no change in any evidence to either side.",
      "A re-issue does not mean a fix has happened; a determination made against an old version cannot be attributed to the new one.",
    ],
  },
  unrecognised: {
    headline: "The record's model version comparison cannot be recognised; shown as it came",
    detail: "The changed models the record gives do not match this record's handing-over and receiving sides, or the two fields contradict each other. This page does not guess which side.",
    caveats: [],
  },
};

export const REISSUE_NEUTRAL =
  "This page only says which side changed and what the record shows; it does not judge good or bad from the direction of a re-issue.";

// ---------------------------------------------------------------------------
// The workspace pages: one real check, its comparison, a refused comparison
// ---------------------------------------------------------------------------

// The rule's citation is the returned data's own English: nothing to gloss.
export const CITATION_GLOSSES = {};

export const WORKSPACE = {
  directoryNote: "A workspace can only be named when the server is started; you cannot choose, upload or change a model here.",
  directoryNone:
    "The server was started without a workspace, so there is no check to look at here. To look at one, restart the server with this command:",
  startCommand: "python doctor/serve.py --workspace <workspace directory> [--prior <earlier run directory>]",
  openRun: "Open this check's results",
  back: "← Back to the home page",
  backToList: "← Back to the list of results",
  contextNoJudgement: "Check results only, no handover judgement",
  contextRun: "Check run",
  resultTitle: "Results of a real check",
  noJudgement:
    "These are the results of a check, not a handover judgement: the page says only whether each element passed, failed or was not applicable under each requirement, and concludes nothing about whether any work can start.",
  summary: { one: "This result: {count} check result", other: "This result: {count} check results" },
  unit:
    "The unit is one result: one element under one requirement; where a model has no element the requirement applies to, it is one result for the whole model.",
  compareLink: "See the comparison with the earlier run",
  compareTeaser: "The server was also started with an earlier run. Before and after:",
  checkedHeading: "What was checked",
  ruleTitle: "Requirement",
  rulePredicate: "What this rule asks",
  ruleExpected: "The rule's own words",
  ruleOrigin: "Source (the returned data's citation, as written)",
  ruleLabels: "Labels in the returned data",
  productValidation: "The label in the returned data (ProductValidation) says: this is a product validation rule.",
  noRuleNotes: "This interface has written no notes for this rule; the rule's own words in the returned data are what counts.",
  noRequirement: "The returned data has no description of the requirement this result belongs to.",
  listHeading: "Results, one by one",
  filterLabel: "Find by IFC Tag, name or GlobalId",
  filterAll: "All",
  filterNone: "No result matches the filter.",
  filterShown: "Showing {shown} of {count}",
  columns: {
    status: "Result",
    tag: "IFC Tag",
    name: "Name",
    class: "Class",
    storey: "Storey (IFC)",
    model: "Model",
  },
  pickOne: "Choose a result from the list to see its details here.",
  detailKicker: "One result of a real check",
  wholeModel: "Whole model",
  resultHeading: "Result",
  findHeading: "Which object to find in Revit",
  actionHeading: "What to change",
  actionWhat: "Change it to",
  actionReads: "Where the checker reads",
  actionRevise: "Where to change it in Revit",
  actionUndecided: "Not decided yet",
  requirementHeading: "The requirement, and what this check observed",
  reason: "Reason (as the check result gives it)",
  actual: "Observed value",
  actualEmpty: "Empty in the check result.",
  actualHidden: "The check result carries an observed value; this page does not show it.",
  recheckHeading: "What to look at in a recheck",
  passHeading: "What this pass proves",
  passProves: "It proves: ",
  passDoesNotProve: "It does not prove:",
  passNoValue: "A passing check result does not carry the value it read: it records only \"Requirement satisfied.\"",
  passUnwritten:
    "A pass says only that this requirement was judged met; how far that goes, this interface has written no notes for this rule — see the rule's own words.",
  notApplicable: "Not applicable: this model has no element the requirement applies to. Not applicable is not a pass.",
  failNotDefect:
    "Not meeting this product validation rule is not a delivery defect of the original project. Where this rule comes from is what the returned data's label (ProductValidation) and the citation as written say.",
  noFinding: "This check has no such result.",
  identityHeading: "Tracing: this check's run identifier, rule set version and model files",
  findingTrace: "Tracing: this result's internal keys",
  identity: {
    run: "Check run identifier",
    ruleset: "Rule set",
    asOf: "Logical date (given by the run configuration, not when it ran)",
    checkers: "Checkers",
    models: "Models",
    modelId: "Model",
    declaredDiscipline: "Discipline declared in the project manifest",
    filename: "File",
    digest: "File content digest (SHA-256)",
    tagSource: "Where the IFC Tag comes from",
    elementKey: "Internal key for tracing",
    findingKey: "Check result key",
    requirementKey: "Requirement key",
  },
  element: {
    name: "Name",
    class: "Class",
    storey: "Storey (IFC)",
    model: "Model",
    file: "Model file",
    globalId: "GlobalId",
  },
};

export const TAG_WORDS = {
  note:
    "The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId. To check: in Revit, use \"Select by ID\" with this ID and see whether the selected object's name and class match this page; if they do, work from it; if they do not, do not change anything by this Tag: locate the object by its GlobalId in an IFC viewer, read its name, type and location, find the object in Revit by these and check it, then make the change in the source model.",
  byIdNotStorey:
    "Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule.",
  storeyFromIfc:
    "The storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule; do not look for the object by storey alone.",
  sources: {
    "model-file": "The model file has no Tag for this element.",
    "model-file-not-located": "The model file this check read was not found, so the Tag cannot be read.",
    "model-file-differs": "The model file in the workspace is no longer the version this check read, so the Tag is not read.",
  },
  sourceNotCarried: "The returned data does not say where this model's Tags are read from, so there is no Tag.",
  modelLevel: "This result is about the whole model; there is no single element to find.",
  useGlobalId: "To find it in the IFC, use the GlobalId.",
  short: {
    "model-file": "No Tag in the file",
    "model-file-not-located": "Model file not found",
    "model-file-differs": "Model file version differs",
    notCarried: "Source not stated",
    modelLevel: "Whole model",
  },
};

export const RULE_NOTES = {
  "PV-001": {
    title: "Air terminals declare one of four predefined types",
    predicate:
      "Every applicable air terminal (IfcAirTerminal) declares a predefined type of DIFFUSER, GRILLE, LOUVRE or REGISTER. " +
      "IFC4 also admits USERDEFINED and NOTDEFINED; not accepting them is this rule's own decision, and a model using them is still valid IFC4.",
    passProves:
      "The one value the checker took in its reading order (the type's value first; a USERDEFINED type's free text; the element instance only when the type says nothing, and with no type, a USERDEFINED instance's free text too) is, character for character, one of DIFFUSER, GRILLE, LOUVRE and REGISTER.",
    passDoesNotProve: [
      "That the value is right: any of the four passes; GRILLE passes too.",
      "That the type and the element instance agree: when the type carries one of the four, the instance's value is not compared; type LOUVRE with instance DIFFUSER also passes.",
      "That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text; with no type, an element instance that declares USERDEFINED is compared by its free text as well. The comparison is character for character and case-sensitive; text that happens to be LOUVRE passes, while louvre, Louvre or text with leading or trailing spaces does not.",
      "That the wall has a corresponding opening.",
      "That the air terminal's model and the model of the wall it sits in are aligned.",
      "That any work can start, including ceiling and opening work.",
    ],
    action: {
      what:
        "Go back to the Revit source model and make this air terminal's exported predefined type one of DIFFUSER, GRILLE, LOUVRE and REGISTER; re-export the IFC and check again. NOTDEFINED states nothing.",
      reads:
        "The checker looks first at its type object in the exported IFC: if the type carries one of the four, the type's value is compared; if the type declares USERDEFINED, its free text is compared; only when the type says nothing is the element instance's own value read. This is the order in which the checker reads the IFC, not where to make the change in Revit.",
      revise:
        "Where this value is written from in Revit (type or instance, which parameter, which export setting), the returned data does not record, and this page does not say. Confirm it in Revit before changing anything; if you decide to change it on the type, the change applies to every instance of that type. One Revit type may correspond to more than one IFC type object; count instances by the Revit type.",
      undecided:
        "Which value to use, and who decides and makes the change, the returned data does not say. The rule asks only for one of the four values and does not judge which is right.",
    },
    recheck:
      "Check again with the same rule set version, the same set of models and the same export settings, and look at this element's result under this requirement.",
    gaps: [
      "The opening in the wall the air terminal sits in: a coordination-review determination is needed, made against the air terminal's model and the model of that wall; this check does not compare elements across the two models.",
      "Whether the air terminal's model and the model of the wall it sits in are aligned: an alignment confirmation record is needed.",
      "Whether the value chosen is right: the classification decision has to be recorded separately; a pass cannot prove in reverse that the classification is right.",
    ],
    reasonFreeText:
      "What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text; with no type, the same holds for an element instance that declares USERDEFINED.",
  },
};

export const WORKSPACE_COMPARE = {
  title: "Recheck comparison: the same check, two runs",
  lede: "The pairs, the rows not re-evaluated and the newly appearing rows below are the returned data's; the page only counts and arranges them.",
  runsHeading: "The two runs",
  prior: "The run named as the earlier one (given with --prior at start-up)",
  current: "This run (given with --workspace at start-up)",
  order: "Which run came first is what the server was told at start-up; the returned data itself cannot prove the order.",
  same:
    "The two runs have the same rule set, the same predicate for each requirement, the same checkers, the same logical date and the same set of models; were any of them different, the system would refuse the comparison and give neither side's results.",
  changedHeading: "1. What changed",
  differs: { one: "Results that differ between the runs: {count}", other: "Results that differ between the runs: {count}" },
  differsNone: "No result differs between the runs.",
  unchanged: { one: "Results that are the same in both runs: {count}", other: "Results that are the same in both runs: {count}" },
  unchangedNone: "No result is the same in both runs.",
  transition: { one: "{prior} → {current}: {count} row", other: "{prior} → {current}: {count} rows" },
  rows: { one: "{count} row", other: "{count} rows" },
  notReEvaluated: {
    label: {
      one: "With a result in the earlier run only (not re-evaluated this time): {count}",
      other: "With a result in the earlier run only (not re-evaluated this time): {count}",
    },
    note: "These have a result from the earlier run only and were not re-evaluated this time. They are not passes.",
  },
  newlyAppearing: {
    label: {
      one: "With a result in this run only (newly appearing): {count}",
      other: "With a result in this run only (newly appearing): {count}",
    },
    note: "The earlier run did not have these results.",
  },
  inCurrent: {
    true: "The element is still in this run's list of elements",
    false: "The element is not in this run's list of elements",
    null: "A result for the whole model, not for an element",
  },
  inPrior: {
    true: "The element is in the earlier run's list of elements",
    false: "The element is not in the earlier run's list of elements",
    null: "A result for the whole model, not for an element",
  },
  whyHeading: "2. Why it changed: what the returned data can say",
  changedModels: "Models whose content changed between the runs (listed by the returned data):",
  noChangedModels: "The returned data lists no model whose content changed: both runs read the same model files.",
  unchangedModels: "Models whose content did not change:",
  why:
    "The two runs have the same rule set, requirement predicates, checkers and logical date. Of the inputs the returned data compared, the only difference between the runs is the content of the model files listed above; what changed inside those files, the returned data does not list item by item.",
  notInData: "What was changed in Revit, who decided the value and who made the change, the returned data does not record.",
  gapsHeading: "3. What evidence is still missing",
  passLink: "What a pass proves and does not prove: see the details of the passing results.",
  open: "Open",
  detailHeading: "Compared with the earlier run",
  detailPrior: "Earlier result",
  detailCurrent: "This result",
  detailNewly: "The earlier run has no such result: it is newly appearing.",
  detailNone: "The returned data's comparison does not include this result.",
  priorReason: "Earlier reason (as written)",
  currentReason: "This reason (as written)",
  noComparison:
    "The server was started without an earlier run, so there is no comparison. To compare, add --prior at start-up.",
  elementMissing: "The returned data has nothing readable about this element",
};

// The bundled project's check attempt, refused before any assessment. What the
// reason means and what is needed are this interface's sentences, the same
// obligations as the Chinese; the system's own text stays in the fold as it came.
export const REFUSAL_REASONS = {
  "team-mapping-decision-basis-illustrative": {
    title: "Project condition not met: who deals with what is not a decision the project has made",
    text:
      "In the project settings this request used, the arrangement of which team fills which role is demonstration placeholder content, not a decision the project has made. " +
      "The system therefore produces no assessment: otherwise the handling teams in the result would be taken for the project's real arrangement.",
    action: [
      "On a real project, for the check to be able to start: the project lead has to actually decide who fills each role that the system's own text (folded below) names, and record it as decided. " +
        "This is a staffing decision, not a change of label.",
      "If this request used the bundled public sample: it has no project lead. For it, this refusal is the correct result; its settings do not need to be changed, and should not be.",
    ],
  },
};

export const REFUSAL_UNGLOSSED = {
  title: "The system refused this request",
  text: "This interface has no English explanation for this reason; open what the system returned below.",
  action: [],
};

export const REFUSAL_SCOPE_NOTE =
  "Dealing with the current reason for refusal does not guarantee that an assessment can follow; the other limitations have not been verified by this run.";

export const REFUSAL_PAGE = {
  title: "This check attempt did not start an assessment",
  lede:
    "The system refused this request before the assessment started, and gave its reason. This is an answer about the request's conditions: not a program fault, and not a check result.",
  whyHeading: "Why it did not start",
  needHeading: "What is needed for the check to start",
  onlyOne: "Only this one reason was returned; there is no diagnosis of any other stage.",
  noConclusion:
    "No conclusion on any item, no zero-problem count and no completion ratio: a refusal is not \"Unknown\", and not a check without problems.",
  original: "What the system returned (as written) and the refusal code",
  attempt: "Check attempt",
  code: "Refusal code",
  contextMissing: "The context of the request that was submitted has not been returned with the refusal yet.",
};

export const WORKSPACE_REFUSAL = {
  title: "These two runs cannot be compared",
  lede:
    "The system refused this comparison and listed every reason. This is an answer about the request's conditions — not a program fault and not a check result: neither side's results were returned.",
  reasonsHeading: "Why they cannot be compared",
  actionHeading: "What a comparison needs",
  action: [
    "Both runs must use the same rule set (the same version and content), the same set of requirements, the same checkers, the same logical date and the same set of models; between the runs only the content of the model files may differ.",
    "Make sure the run given with --prior at start-up really is the earlier run of the same check; or restart the server without --prior and look at this check's results alone.",
  ],
  scope: "Whether they can be compared once these reasons are dealt with is for the next answer to say.",
  original: "What the system returned (as written) and the refusal code",
  code: "Refusal code",
  unglossed: "This interface has no English for this reason; see what the system returned below.",
  noResult: "No result, no zero-problem count and no completion ratio: a refused comparison is not a check without problems.",
};

export const WORKSPACE_REFUSAL_REASONS = {
  "ruleset-id-differs": "The two runs did not use the same rule set.",
  "ruleset-version-differs": "The two runs used different rule set versions.",
  "ruleset-digest-differs": "The two runs used different rule set content (the content digests differ).",
  "requirement-set-differs": "The two runs did not evaluate the same set of requirements.",
  "requirement-semantics-not-recorded":
    "One run did not record the predicate digest of a requirement, so it cannot be shown that both are the same check.",
  "requirement-semantics-differs": "The same requirement has a different predicate in the two runs: what is checked was changed.",
  "checker-differs": "The two runs used different checkers, versions or configuration.",
  "as-of-differs": "The two runs have different logical dates.",
  "model-set-differs": "The two runs did not check the same set of models.",
};
