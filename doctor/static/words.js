// The wording every screen imports: each table of vocabulary.js, in the
// language the viewer chose. A table with English is registered with both; a
// table that is language-neutral data (identifiers, codes, a marker) is the
// same in both; a table with no English yet is Chinese in both and marks
// whatever page uses it as not translated (see i18n.js and app.js).
//
// The export list is vocabulary.js's own, one for one, and a test holds it so.

import { LANG, bilingual } from "./i18n.js";
import * as zh from "./vocabulary.js";
import * as en from "./vocabulary-en.js";

export const MODE_LABELS = bilingual("MODE_LABELS", zh.MODE_LABELS, en.MODE_LABELS);
export const RUN_LABELS = bilingual("RUN_LABELS", zh.RUN_LABELS, en.RUN_LABELS);
export const EXAMPLES = bilingual("EXAMPLES", zh.EXAMPLES, en.EXAMPLES);
export const FOLLOW_UP = bilingual("FOLLOW_UP", zh.FOLLOW_UP, zh.FOLLOW_UP);
export const DIRECTORY_NOTE = bilingual("DIRECTORY_NOTE", zh.DIRECTORY_NOTE, en.DIRECTORY_NOTE);
export const EXAMPLE_NOTE = bilingual("EXAMPLE_NOTE", zh.EXAMPLE_NOTE, en.EXAMPLE_NOTE);
export const HOME = bilingual("HOME", zh.HOME, en.HOME);
export const NOT_CARRIED = bilingual("NOT_CARRIED", zh.NOT_CARRIED, en.NOT_CARRIED);
export const EMPTY_STRING = bilingual("EMPTY_STRING", zh.EMPTY_STRING, en.EMPTY_STRING);
export const FIXTURE_MARKER = bilingual("FIXTURE_MARKER", zh.FIXTURE_MARKER, zh.FIXTURE_MARKER);
export const CITATION_PROVENANCE = bilingual("CITATION_PROVENANCE", zh.CITATION_PROVENANCE, en.CITATION_PROVENANCE);
export const CITATION_KINDS = bilingual("CITATION_KINDS", zh.CITATION_KINDS, en.CITATION_KINDS);
export const PROVENANCE_NOTICE = bilingual("PROVENANCE_NOTICE", zh.PROVENANCE_NOTICE, en.PROVENANCE_NOTICE);
export const POLICY_SOURCE_NOTE = bilingual("POLICY_SOURCE_NOTE", zh.POLICY_SOURCE_NOTE);
export const DEMO_NOTICE = bilingual("DEMO_NOTICE", zh.DEMO_NOTICE, en.DEMO_NOTICE);
export const DISPOSITION_ENTRIES = bilingual("DISPOSITION_ENTRIES", zh.DISPOSITION_ENTRIES, en.DISPOSITION_ENTRIES);
export const DISPOSITIONS = bilingual("DISPOSITIONS", zh.DISPOSITIONS, en.DISPOSITIONS);
export const CONDITION_ENTRIES = bilingual("CONDITION_ENTRIES", zh.CONDITION_ENTRIES, en.CONDITION_ENTRIES);
export const CONDITION_STATES = bilingual("CONDITION_STATES", zh.CONDITION_STATES, en.CONDITION_STATES);
export const CARRY_OVER_STATES = bilingual("CARRY_OVER_STATES", zh.CARRY_OVER_STATES, en.CARRY_OVER_STATES);
export const CARRY_OVER_REASONS = bilingual("CARRY_OVER_REASONS", zh.CARRY_OVER_REASONS, en.CARRY_OVER_REASONS);
export const CHANGED_ASPECTS = bilingual("CHANGED_ASPECTS", zh.CHANGED_ASPECTS, en.CHANGED_ASPECTS);
export const ASPECT_ORDER = bilingual("ASPECT_ORDER", zh.ASPECT_ORDER, zh.ASPECT_ORDER);
export const ASPECT_NOTES = bilingual("ASPECT_NOTES", zh.ASPECT_NOTES, en.ASPECT_NOTES);
export const KEY_CHANGED = bilingual("KEY_CHANGED", zh.KEY_CHANGED, en.KEY_CHANGED);
export const ONLY_REKEYED = bilingual("ONLY_REKEYED", zh.ONLY_REKEYED, en.ONLY_REKEYED);
export const REISSUE_CASES = bilingual("REISSUE_CASES", zh.REISSUE_CASES, en.REISSUE_CASES);
export const REISSUE_NEUTRAL = bilingual("REISSUE_NEUTRAL", zh.REISSUE_NEUTRAL, en.REISSUE_NEUTRAL);
export const RECHECK_LIMITS = bilingual("RECHECK_LIMITS", zh.RECHECK_LIMITS, en.RECHECK_LIMITS);
export const RECHECK_CANNOT = bilingual("RECHECK_CANNOT", zh.RECHECK_CANNOT, en.RECHECK_CANNOT);
export const VERDICT_GROUPS = bilingual("VERDICT_GROUPS", zh.VERDICT_GROUPS, en.VERDICT_GROUPS);
export const ACTION_GROUPS = bilingual("ACTION_GROUPS", zh.ACTION_GROUPS, en.ACTION_GROUPS);
export const ITEM_UNIT = bilingual("ITEM_UNIT", zh.ITEM_UNIT, en.ITEM_UNIT);
export const VERDICT_LABELS = bilingual("VERDICT_LABELS", zh.VERDICT_LABELS, en.VERDICT_LABELS);
export const BESIDE = bilingual("BESIDE", zh.BESIDE, en.BESIDE);
export const READY_NOTES = bilingual("READY_NOTES", zh.READY_NOTES, en.READY_NOTES);
export const BASIS_WORDS = bilingual("BASIS_WORDS", zh.BASIS_WORDS, en.BASIS_WORDS);
export const ACTION_TEXT = bilingual("ACTION_TEXT", zh.ACTION_TEXT, en.ACTION_TEXT);
export const ACTION_PACK = bilingual("ACTION_PACK", zh.ACTION_PACK, zh.ACTION_PACK);
export const ACTIONS = bilingual("ACTIONS", zh.ACTIONS);
export const DETAILS_WORDS = bilingual("DETAILS_WORDS", zh.DETAILS_WORDS, en.DETAILS_WORDS);
export const PROJECT_ASSUMPTION = bilingual("PROJECT_ASSUMPTION", zh.PROJECT_ASSUMPTION, zh.PROJECT_ASSUMPTION);
export const FINDING_STATUS = bilingual("FINDING_STATUS", zh.FINDING_STATUS, en.FINDING_STATUS);
export const REASON_GLOSSES = bilingual("REASON_GLOSSES", zh.REASON_GLOSSES, en.REASON_GLOSSES);
export const VERDICT_WORDS = bilingual("VERDICT_WORDS", zh.VERDICT_WORDS, en.VERDICT_WORDS);
export const VERDICT_SCOPE = bilingual("VERDICT_SCOPE", zh.VERDICT_SCOPE, en.VERDICT_SCOPE);
export const REQUIREMENT_CHANGED_NOTE = bilingual("REQUIREMENT_CHANGED_NOTE", zh.REQUIREMENT_CHANGED_NOTE, en.REQUIREMENT_CHANGED_NOTE);
export const LEAF_READINGS = bilingual("LEAF_READINGS", zh.LEAF_READINGS, en.LEAF_READINGS);
export const LEAF_READING_WORDS = bilingual("LEAF_READING_WORDS", zh.LEAF_READING_WORDS, en.LEAF_READING_WORDS);
export const HANDOVER_SIDES = bilingual("HANDOVER_SIDES", zh.HANDOVER_SIDES, en.HANDOVER_SIDES);
export const ELEMENT_WORDS = bilingual("ELEMENT_WORDS", zh.ELEMENT_WORDS, en.ELEMENT_WORDS);
export const IFC_CLASS_NAMES = bilingual("IFC_CLASS_NAMES", zh.IFC_CLASS_NAMES, en.IFC_CLASS_NAMES);
export const ACTIVITY_NAMES = bilingual("ACTIVITY_NAMES", zh.ACTIVITY_NAMES, en.ACTIVITY_NAMES);
export const RESOLUTION_KINDS = bilingual("RESOLUTION_KINDS", zh.RESOLUTION_KINDS, en.RESOLUTION_KINDS);
export const CONSEQUENCE_KINDS = bilingual("CONSEQUENCE_KINDS", zh.CONSEQUENCE_KINDS, en.CONSEQUENCE_KINDS);
export const REFUSAL_REASONS = bilingual("REFUSAL_REASONS", zh.REFUSAL_REASONS);
export const REFUSAL_UNGLOSSED = bilingual("REFUSAL_UNGLOSSED", zh.REFUSAL_UNGLOSSED);
export const FAULT_WORDS = bilingual("FAULT_WORDS", zh.FAULT_WORDS, en.FAULT_WORDS);
export const HOW_TO_READ = bilingual("HOW_TO_READ", zh.HOW_TO_READ, en.HOW_TO_READ);
export const UNRECOGNISED = bilingual("UNRECOGNISED", zh.UNRECOGNISED, en.UNRECOGNISED);
export const REFUSAL_SCOPE_NOTE = bilingual("REFUSAL_SCOPE_NOTE", zh.REFUSAL_SCOPE_NOTE);
export const WORKSPACE_HOME = bilingual("WORKSPACE_HOME", zh.WORKSPACE_HOME, en.WORKSPACE_HOME);
export const WORKSPACE = bilingual("WORKSPACE", zh.WORKSPACE, en.WORKSPACE);
export const TAG_WORDS = bilingual("TAG_WORDS", zh.TAG_WORDS, en.TAG_WORDS);
export const CITATION_GLOSSES = bilingual("CITATION_GLOSSES", zh.CITATION_GLOSSES, en.CITATION_GLOSSES);
export const PRODUCT_VALIDATION = bilingual("PRODUCT_VALIDATION", zh.PRODUCT_VALIDATION, zh.PRODUCT_VALIDATION);
export const RULE_NOTES_FOR = bilingual("RULE_NOTES_FOR", zh.RULE_NOTES_FOR, zh.RULE_NOTES_FOR);
export const RULE_NOTES = bilingual("RULE_NOTES", zh.RULE_NOTES, en.RULE_NOTES);
export const WORKSPACE_COMPARE = bilingual("WORKSPACE_COMPARE", zh.WORKSPACE_COMPARE, en.WORKSPACE_COMPARE);
export const ENVELOPE_WORDS = bilingual("ENVELOPE_WORDS", zh.ENVELOPE_WORDS, en.ENVELOPE_WORDS);
export const WORKSPACE_REFUSAL = bilingual("WORKSPACE_REFUSAL", zh.WORKSPACE_REFUSAL, en.WORKSPACE_REFUSAL);
export const WORKSPACE_REFUSAL_REASONS = bilingual("WORKSPACE_REFUSAL_REASONS", zh.WORKSPACE_REFUSAL_REASONS, en.WORKSPACE_REFUSAL_REASONS);
export const COMMON = bilingual("COMMON", zh.COMMON, en.COMMON);
export const CONTEXT = bilingual("CONTEXT", zh.CONTEXT, en.CONTEXT);
export const DIRECTORY = bilingual("DIRECTORY", zh.DIRECTORY, en.DIRECTORY);
export const FIRST = bilingual("FIRST", zh.FIRST, en.FIRST);
export const READING_GUIDE = bilingual("READING_GUIDE", zh.READING_GUIDE, en.READING_GUIDE);
export const APP = bilingual("APP", zh.APP, en.APP);
export const PAGE = bilingual("PAGE", zh.PAGE, en.PAGE);
export const COPY = bilingual("COPY", zh.COPY, en.COPY);
export const ITEM = bilingual("ITEM", zh.ITEM, en.ITEM);
export const ACTION = bilingual("ACTION", zh.ACTION, en.ACTION);
export const ELEMENT_CARD = bilingual("ELEMENT_CARD", zh.ELEMENT_CARD, en.ELEMENT_CARD);
export const EVIDENCE = bilingual("EVIDENCE", zh.EVIDENCE, en.EVIDENCE);
export const WORK = bilingual("WORK", zh.WORK, en.WORK);
export const RECHECK = bilingual("RECHECK", zh.RECHECK, en.RECHECK);
export const RECHECK_ITEM = bilingual("RECHECK_ITEM", zh.RECHECK_ITEM, en.RECHECK_ITEM);
export const RECHECK_MODEL = bilingual("RECHECK_MODEL", zh.RECHECK_MODEL, en.RECHECK_MODEL);

// A code and its words, or that this interface has none, in the chosen language.
function glossed(table, value) {
  if (Object.hasOwn(table, value)) return { known: true, text: table[value] };
  return { known: false, text: UNRECOGNISED };
}

export const disposition = (value) => glossed(DISPOSITIONS, value);
export const conditionState = (value) => glossed(CONDITION_STATES, value);
export const carryOverReason = (value) => glossed(CARRY_OVER_REASONS, value);

// Absences are read by the member screens only, which are not translated.
export const absence = zh.absence;

/** One citation's provenance, decided as vocabulary.js decides it, worded in the chosen language. */
export function citationProvenance(kind, citation) {
  const entry = zh.citationProvenance(kind, citation);
  if (entry === null || LANG === "zh") return entry;
  const name = Object.keys(zh.CITATION_PROVENANCE).find((key) => zh.CITATION_PROVENANCE[key] === entry);
  return CITATION_PROVENANCE[name];
}
