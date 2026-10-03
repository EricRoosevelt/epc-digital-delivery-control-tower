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

// What to do and what a recheck must show come from the record itself: each
// subscope's route carries the Pack's own `next_action` and
// `recheck_condition`, in English. The Chinese sentences in vocabulary.js
// gloss them for one Pack version; in English the record's words are shown.
export const ACTION_TEXT = { source: "record" };

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
    "This is an example preview: you cannot import your own Revit model yet, and it gives no overall compliance or ready-to-build conclusion.",
  statusWithWorkspace:
    "Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. " +
    "You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion.",
  statusWorkspaceUnknown:
    "Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. " +
    "The simulated examples are available as usual. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion.",
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
      "It is not an import, and you cannot swap in your own model.",
    action: "See this check attempt",
  },
  cannot: [
    "Import, choose or change a model on the page, including your own Revit or IFC model",
    "Give an overall compliance, ready-to-build or \"ready to hand over\" conclusion",
    "Write back to a model, upload to the cloud, or open an element in Revit",
  ],
  canHeading: "What you can do now",
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

export const DIRECTORY_NOTE =
  "Each example is one check record. The evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination; " +
  "which one it is, the \"Basis\" line beside each conclusion on the result and item pages says, citation by citation. " +
  "The project settings in the examples, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions.";

export const DEMO_NOTICE =
  "Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions; " +
  "the evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination — which one, the \"Basis\" line beside each conclusion says (citation by citation). " +
  "Not for formal project decisions, and no formal check record can be exported.";

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
  emptyList: "(an empty list in the record)",
  unknownMode: "Unrecognised entry ({mode})",
  unnamedElement: "Unnamed element",
  and: " and ",
  oneElement: "One element",
  twoElements: "A pair of elements",
  nElements: "{count} elements",
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
    "The repository comes with a sample project; below is a check attempt on it. You cannot choose another model yet, nor import your own.",
  exampleTitle: "Choose a simulated example",
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
  summary: "This result: {items} items, {todo} of which need dealing with",
  items: "{count} items",
  verdictLine: ": the work concerned is ",
  quietLine: ": {summary} (listed further down this page)",
  elementsLine: "{unit} This record involves {count} different elements.",
  action: "What to do",
  problem: "Problem",
  openItem: "See this item: the element, what to do, who deals with it, what a recheck must show",
  openHeading: "{label}, by handling team ({count} items)",
  team: "Handling team ",
  teamCount: ": {count} items",
  columns: { problem: "Problem", work: "Which work: conclusion", count: "Items" },
  quietHeading: "{label} ({count} items)",
  separator: " | ",
  nextHeading: "Then: see how this record changed after a recheck",
  nextLink: "Open the example \"{run}\"",
  nextAfter: ". Each item's page also links straight to how that item changed in the recheck.",
  traceSummary: "Tracing: record identity, rule version, record codes",
  recordLink: "This record's requested scope, versions and sources",
  notRevised: " (that page has not been revised yet and still uses internal terms)",
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
