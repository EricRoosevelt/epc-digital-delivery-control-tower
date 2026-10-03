// The workspace pages' reading of a workspace envelope. No DOM in here, so it
// runs under Node exactly as the browser runs it
// (tests/test_doctor_workspace_screens.py).
//
// It groups and counts what the adapter returned and looks things up in it; it
// compares nothing itself. The pairing of an earlier and a current finding, the
// rows only one run has and the models whose content changed are all the
// adapter's (`comparison`). The one thing done to a pair here is to put it with
// the other pairs that carry the same two statuses, so they can be counted.

import { FINDING_STATUS, PRODUCT_VALIDATION, RULE_NOTES, RULE_NOTES_FOR } from "./words.js";

function has(object, key) {
  return object !== null && typeof object === "object" && Object.hasOwn(object, key);
}

// The order results are listed in: the vocabulary's, then any status it does
// not know, in the order first met. An order of listing, not of merit.
function statusRank(status) {
  const index = Object.keys(FINDING_STATUS).indexOf(status);
  return index < 0 ? Object.keys(FINDING_STATUS).length : index;
}

/** The findings, one group per status, each group in the adapter's order. */
export function statusGroups(findings) {
  const groups = new Map();
  for (const finding of findings) {
    const status = has(finding, "status") ? finding.status : undefined;
    if (!groups.has(status)) groups.set(status, []);
    groups.get(status).push(finding);
  }
  return [...groups]
    .map(([status, rows], first) => ({
      status,
      known: Object.hasOwn(FINDING_STATUS, status),
      count: rows.length,
      findings: rows,
      first,
    }))
    .sort((left, right) => statusRank(left.status) - statusRank(right.status) || left.first - right.first)
    .map(({ first, ...group }) => group);
}

export function findingByKey(envelope, key) {
  return envelope.findings.find((finding) => finding.finding_key === key) ?? null;
}

export function requirementOf(envelope, finding) {
  return has(envelope.requirements, finding.requirement_key)
    ? envelope.requirements[finding.requirement_key]
    : null;
}

export function modelOf(run, modelKey) {
  return (has(run, "models") ? run.models : []).find((model) => model.model_key === modelKey) ?? null;
}

/** The element a finding names, from the run that holds it; null for a model-level one. */
export function elementOf(elements, key) {
  return key && has(elements, key) ? elements[key] : null;
}

/** The rule's Chinese notes, for the one rule set version they were written for.
 *
 * Read off the run's own rule set identifier and version and the requirement's
 * own rule id. Any other rule set, version or rule gets none.
 */
// IFC4 ADD2 TC1 IfcAirTerminalTypeEnum. A PV-001 reason quoting anything else
// quotes the free text of a USERDEFINED type, which the checker compared.
const AIR_TERMINAL_TYPES = new Set(["DIFFUSER", "GRILLE", "LOUVRE", "REGISTER", "USERDEFINED", "NOTDEFINED"]);
const PREDEFINED_TYPE_REASON = /^The predefined type "(.*)" does not meet the required type$/s;

/** True when a reason quotes free text where an enumeration value would stand. */
export function quotesFreeText(reason) {
  const match = typeof reason === "string" ? PREDEFINED_TYPE_REASON.exec(reason) : null;
  return match !== null && !AIR_TERMINAL_TYPES.has(match[1]);
}

export function ruleNotes(run, requirement) {
  const written =
    requirement !== null &&
    has(run, "ruleset") &&
    run.ruleset.id === RULE_NOTES_FOR.ruleset &&
    run.ruleset.version === RULE_NOTES_FOR.version &&
    has(requirement, "rule_id") &&
    Object.hasOwn(RULE_NOTES, requirement.rule_id);
  return written ? RULE_NOTES[requirement.rule_id] : null;
}

/** Whether the requirement's own labels call it a product validation rule. */
export function isProductValidation(requirement) {
  return (
    requirement !== null &&
    has(requirement, "labels") &&
    Array.isArray(requirement.labels) &&
    requirement.labels.includes(PRODUCT_VALIDATION)
  );
}

/** What can be said about one element's IFC Tag.
 *
 * `tag` when the element carries one. Otherwise why not, from the model's
 * `tag_source`: a readable file that states no Tag for it, a file that could
 * not be found, or a file that is not the version the run read.
 */
export function tagReading(element, model) {
  if (element === null) return { kind: "model-level" };
  if (has(element, "tag")) return { kind: "tag", value: element.tag };
  if (!has(model, "tag_source")) return { kind: "not-carried" };
  return { kind: "source", value: model.tag_source };
}

/** The adapter's pairs, one group per (earlier status, current status).
 *
 * Groups whose two statuses differ come first; within each half, the order is
 * the vocabulary's for the earlier status and then the current one. The rows
 * only one run has are not here: they are listed apart and never counted with
 * the pairs.
 */
export function transitions(comparison) {
  const groups = new Map();
  for (const pair of comparison.pairs) {
    const key = JSON.stringify([pair.prior.status, pair.current.status]);
    if (!groups.has(key)) {
      groups.set(key, {
        prior: pair.prior.status,
        current: pair.current.status,
        differs: pair.prior.status !== pair.current.status,
        pairs: [],
      });
    }
    groups.get(key).pairs.push(pair);
  }
  const ordered = [...groups.values()].sort(
    (left, right) =>
      Number(right.differs) - Number(left.differs) ||
      statusRank(left.prior) - statusRank(right.prior) ||
      statusRank(left.current) - statusRank(right.current),
  );
  const count = (rows) => rows.reduce((total, group) => total + group.pairs.length, 0);
  const differing = ordered.filter((group) => group.differs);
  const same = ordered.filter((group) => !group.differs);
  return {
    differing,
    same,
    differingCount: count(differing),
    sameCount: count(same),
    pairCount: comparison.pairs.length,
    notReEvaluatedCount: comparison.not_re_evaluated.length,
    newlyAppearingCount: comparison.newly_appearing.length,
  };
}

/** Where the comparison places one current finding: a pair, a new row, or nowhere. */
export function comparisonOf(comparison, findingKey) {
  const pair = comparison.pairs.find((row) => row.current.finding_key === findingKey);
  if (pair) return { kind: "pair", row: pair };
  const newly = comparison.newly_appearing.find((row) => row.current.finding_key === findingKey);
  if (newly) return { kind: "newly", row: newly };
  return { kind: "none" };
}

/** The models the adapter lists as changed, and the others, each with its run entry. */
export function modelChanges(comparison, run) {
  const changed = new Map(comparison.changed_models.map((row) => [row.model_key, row]));
  const models = has(run, "models") ? run.models : [];
  return {
    changed: comparison.changed_models.map((row) => ({ row, model: modelOf(run, row.model_key) })),
    unchanged: models.filter((model) => !changed.has(model.model_key)),
  };
}

/** The element a comparison row names, from whichever inventory still holds it. */
export function comparisonElement(envelope, row) {
  if (!row.element_key) return { element: null, run: envelope.run };
  if (has(envelope.elements, row.element_key)) {
    return { element: envelope.elements[row.element_key], run: envelope.run };
  }
  const prior = envelope.comparison.prior_elements;
  return {
    element: has(prior, row.element_key) ? prior[row.element_key] : null,
    run: envelope.comparison.prior_run,
    missing: !has(prior, row.element_key),
  };
}

/** Whether a free-text query matches one finding's element, by Tag, name or GlobalId. */
export function matches(element, finding, query) {
  const wanted = query.trim().toLowerCase();
  if (!wanted) return true;
  const said = [finding.model_key];
  if (element !== null) {
    for (const key of ["tag", "name", "global_id"]) {
      if (has(element, key)) said.push(String(element[key]));
    }
  }
  return said.some((text) => text.toLowerCase().includes(wanted));
}
