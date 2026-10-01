// What the recheck screens say, as plain data. No DOM here, so the wording can be
// exercised without a browser.
//
// Everything below is a lookup or a tally of what the record already holds:
//
// * the four carry-over states, their reasons, the changed aspects, the member
//   dispositions and the condition status are read off the record and worded by
//   vocabulary.js. Nothing here compares a digest, a key or a content id;
// * "which side was re-issued" is `changed_models` looked up against the
//   `producing` / `consuming` keys of the same comparison object, and the role
//   names are the request's handover. No discipline is named in this file;
// * a value this file does not know is carried through as it came and marked
//   unrecognised. It is never mapped to the nearest known one.
//
// The one place the current partition is read is `currentSubscope`, and only for
// an ordinal the Framework itself put in a disposition's `current_ordinals`.
// Where the record gives no such ordinal there is no lookup, by key or otherwise.

import {
  ACTION_GROUPS,
  ASPECT_NOTES,
  ASPECT_ORDER,
  CARRY_OVER_REASONS,
  CARRY_OVER_STATES,
  CHANGED_ASPECTS,
  CITATION_KINDS,
  CONDITION_ENTRIES,
  DISPOSITION_ENTRIES,
  HANDOVER_SIDES,
  KEY_CHANGED,
  NOT_CARRIED,
  ONLY_REKEYED,
  REISSUE_CASES,
  REISSUE_NEUTRAL,
  UNRECOGNISED,
  VERDICT_GROUPS,
} from "./vocabulary.js";

export const RECHECK_KIND = "recheck";

function carries(object, key) {
  return object !== null && typeof object === "object" && Object.hasOwn(object, key);
}

function known(table, value) {
  return typeof value === "string" && Object.hasOwn(table, value);
}

// ---------------------------------------------------------------------------
// Which side was re-issued
// ---------------------------------------------------------------------------

function reissueCase(comparison) {
  if (!carries(comparison, "changed_models") || !Array.isArray(comparison.changed_models)) {
    return "unrecognised";
  }
  const producing = carries(comparison, "producing") ? comparison.producing.model_key : undefined;
  const consuming = carries(comparison, "consuming") ? comparison.consuming.model_key : undefined;
  if (typeof producing !== "string" || typeof consuming !== "string" || producing === consuming) {
    return "unrecognised";
  }
  const changed = comparison.changed_models;
  if (changed.some((key) => key !== producing && key !== consuming)) return "unrecognised";
  const producingChanged = changed.includes(producing);
  const consumingChanged = changed.includes(consuming);
  const name =
    producingChanged && consumingChanged
      ? "both"
      : producingChanged
        ? "producing"
        : consumingChanged
          ? "consuming"
          : "none";
  // `is_current` is the record's own statement of the same fact. When the two
  // disagree, neither is believed over the other.
  if (carries(comparison, "is_current") && comparison.is_current !== (name === "none")) {
    return "unrecognised";
  }
  return name;
}

function fill(template, values) {
  return template.replace(/\{(\w+)\}/g, (_match, name) => values[name]);
}

export function reissueModel(comparison, handover) {
  const name = reissueCase(comparison);
  const entry = REISSUE_CASES[name];
  const role = (key) => (carries(handover, key) && handover[key] !== "" ? handover[key] : NOT_CARRIED);
  const side = (label, roleKey, priorKey, nowKey) => {
    const now = carries(comparison, nowKey) ? comparison[nowKey] : null;
    return {
      label,
      role: role(roleKey),
      prior: carries(comparison, priorKey) ? comparison[priorKey] : null,
      now,
      // null: the case was not recognised, so no side is called re-issued or not.
      reissued:
        name === "unrecognised" || now === null
          ? null
          : comparison.changed_models.includes(now.model_key),
    };
  };
  const sides = [
    side("交出方", "from_role", "prior_producing", "producing"),
    side("接收方", "to_role", "prior_consuming", "consuming"),
  ];
  const modelKey = (index) => (sides[index].now ? sides[index].now.model_key : NOT_CARRIED);
  return {
    name,
    headline: entry.headline,
    detail: fill(entry.detail, {
      from: sides[0].role,
      to: sides[1].role,
      producing: modelKey(0),
      consuming: modelKey(1),
    }),
    caveats: entry.caveats,
    neutral: REISSUE_NEUTRAL,
    sides,
    comparison,
  };
}

// ---------------------------------------------------------------------------
// One carry-over row
// ---------------------------------------------------------------------------

function stateModel(row) {
  if (!carries(row, "state")) {
    return { code: null, known: false, label: NOT_CARRIED, meaning: "", caveat: "" };
  }
  if (!known(CARRY_OVER_STATES, row.state)) {
    return { code: row.state, known: false, label: UNRECOGNISED, meaning: "", caveat: "" };
  }
  return { code: row.state, known: true, ...CARRY_OVER_STATES[row.state] };
}

function reasonModel(row) {
  if (!carries(row, "reason")) return { code: null, known: false, text: NOT_CARRIED };
  if (!known(CARRY_OVER_REASONS, row.reason)) {
    return { code: row.reason, known: false, text: UNRECOGNISED };
  }
  return { code: row.reason, known: true, text: CARRY_OVER_REASONS[row.reason] };
}

/** The concrete fact a `changed` finding row states, and what follows from it. */
function aspectsModel(aspects) {
  const recognised = ASPECT_ORDER.filter((code) => aspects.includes(code));
  const unrecognised = aspects.filter((code) => !known(CHANGED_ASPECTS, code));
  const changed = [
    ...recognised.map((code) => CHANGED_ASPECTS[code]),
    ...unrecognised.map((code) => `“${code}”（${UNRECOGNISED}）`),
  ];
  const notes = [];
  let sentence = `${changed.join("、")}变了`;
  if (unrecognised.length) {
    // The unchanged aspects are the rest of a closed list. With a value outside
    // that list on the row, this file no longer knows the list, and says so.
    sentence += "。";
    notes.push(ASPECT_NOTES.unrecognised);
  } else {
    const same = ASPECT_ORDER.filter((code) => !aspects.includes(code)).map(
      (code) => CHANGED_ASPECTS[code],
    );
    sentence += same.length ? `，${same.join("、")}未变。` : "。";
  }
  const has = (code) => aspects.includes(code);
  if (!unrecognised.length && recognised.length === 1 && has("model-version")) {
    notes.push(ASPECT_NOTES.onlyModelVersion);
  }
  if (has("requirement-semantics")) {
    notes.push(has("finding-content") ? ASPECT_NOTES.semanticsAndContent : ASPECT_NOTES.semanticsSameOutcome);
  } else if (has("finding-content") && !unrecognised.length) {
    notes.push(ASPECT_NOTES.contentUnderSameRequirement);
  }
  if (has("checker")) notes.push(ASPECT_NOTES.checker);
  return { sentence, notes };
}

function keyChangedSentence(row) {
  if (!carries(row, "key_changed")) return null;
  return known(KEY_CHANGED, row.key_changed)
    ? KEY_CHANGED[row.key_changed]
    : `key_changed = “${row.key_changed}”（${UNRECOGNISED}）`;
}

export function evidenceModel(row) {
  const state = stateModel(row);
  const reason = reasonModel(row);
  const facts = [];
  const notes = [];
  // The concrete fact, said right beside the state: which aspects moved and
  // which did not, or that only the key did.
  let brief = "";
  if (state.code === "equivalent") {
    if (row.key_changed === "yes") {
      brief = ONLY_REKEYED;
      facts.push(`${ONLY_REKEYED}：证据内容和比较依据都没有变。`);
    } else {
      const sentence = keyChangedSentence(row);
      if (sentence) facts.push(sentence);
    }
  } else if (state.code === "changed") {
    if (carries(row, "changed_aspects") && Array.isArray(row.changed_aspects) && row.changed_aspects.length) {
      const aspects = aspectsModel(row.changed_aspects);
      brief = aspects.sentence;
      notes.push(...aspects.notes);
    }
    const sentence = keyChangedSentence(row);
    if (sentence) facts.push(sentence);
  }
  return { row, state, reason, brief, facts, notes };
}

// ---------------------------------------------------------------------------
// Tallies: counts of rows as recorded. Not a score, and in no order of merit.
// ---------------------------------------------------------------------------

function tally(entries, table, label) {
  const counts = new Map();
  for (const code of entries) counts.set(code, (counts.get(code) ?? 0) + 1);
  const ordered = [
    ...Object.keys(table).filter((code) => counts.has(code)),
    ...[...counts.keys()].filter((code) => !known(table, code)),
  ];
  return ordered.map((code) => ({
    code,
    known: known(table, code),
    label: known(table, code) ? label(table[code]) : UNRECOGNISED,
    count: counts.get(code),
  }));
}

const stateTally = (rows) =>
  tally(
    rows.map((item) => item.state.code),
    CARRY_OVER_STATES,
    (entry) => entry.label,
  );

/** The same rows, counted apart by kind of evidence, then state, then fact.
 *
 * A check result and a determination are different evidence and can come out
 * differently in one recheck — after a re-issue of the consuming model alone the
 * check results are equivalent under new keys while the determinations cannot be
 * attributed to the new context. Counting them together would let one read as
 * the other, so they are never added up across kinds.
 */
function evidenceGroups(rows) {
  const kinds = [];
  for (const item of rows) {
    const kind = carries(item.row, "citation_kind") ? item.row.citation_kind : null;
    let group = kinds.find((entry) => entry.kind === kind);
    if (!group) {
      group = {
        kind,
        known: known(CITATION_KINDS, kind),
        label: known(CITATION_KINDS, kind) ? CITATION_KINDS[kind] : UNRECOGNISED,
        count: 0,
        rows: [],
      };
      kinds.push(group);
    }
    group.count += 1;
    group.rows.push(item);
  }
  // Check results first, then determinations, then anything unrecognised in
  // the order it was met: the order of the vocabulary, not of the rows.
  const order = Object.keys(CITATION_KINDS);
  const rank = (entry) => (entry.known ? order.indexOf(entry.kind) : order.length);
  kinds.sort((left, right) => rank(left) - rank(right));
  return kinds.map(({ rows: members, ...group }) => ({
    ...group,
    states: stateTally(members).map((entry) => {
      const facts = new Map();
      for (const item of members) {
        if (item.state.code !== entry.code) continue;
        // What is said beside the state: the concrete fact when the row has
        // one, otherwise the reason's own sentence.
        const text = item.brief || (item.reason.known ? item.reason.text : "");
        if (text) facts.set(text, (facts.get(text) ?? 0) + 1);
      }
      return { ...entry, facts: [...facts].map(([text, count]) => ({ text, count })) };
    }),
  }));
}

// ---------------------------------------------------------------------------
// The successor, laid out as work items: one per sealed member
// ---------------------------------------------------------------------------

/** The current subscope the Framework named for a present member, or null.
 *
 * Called only with an ordinal out of a disposition's `current_ordinals`: the
 * correspondence is the record's. A member the record gives no ordinal for is
 * not looked up here or anywhere else.
 */
function currentSubscope(document, activityRef, ordinal) {
  const activityIndex = document.activities.findIndex((item) => item.activity_ref === activityRef);
  if (activityIndex < 0) return null;
  const subscope = document.activities[activityIndex].subscopes.find((item) => item.ordinal === ordinal);
  return subscope ? { activityIndex, subscope } : null;
}

// ---------------------------------------------------------------------------
// Work to do: which items the record gives a next step for
// ---------------------------------------------------------------------------

function carried(object, key) {
  return carries(object, key) ? object[key] : undefined;
}

/** Whether the record gives this item a next step, no current place, or neither.
 *
 * Read off the places the record itself named for the item: it is "open" when
 * one of them carries a next action. The verdict word is not consulted, and
 * nothing here says an item is fine — only that the record asks nothing of it.
 */
function actionKind(current) {
  if (current === null) return "unplaced";
  const asked = current.some(
    (entry) => entry.located !== null && carries(carried(entry.located.subscope, "route"), "next_action"),
  );
  return asked ? "open" : "none";
}

function actionGroups(items) {
  return Object.keys(ACTION_GROUPS).map((kind) => {
    const members = items.filter((item) => item.action === kind);
    const entry = ACTION_GROUPS[kind];
    return {
      kind,
      label: entry.label,
      summary: entry.summary,
      count: members.length,
      note: members.length ? entry.note : entry.none,
      items: members.map((item) => [item.subscopeIndex, item.memberIndex]),
    };
  });
}

/** Which side of the handover a model is on, or null when the record cannot say.
 *
 * A lookup of one model key against the comparison's own `producing` and
 * `consuming`. A side is a role in this handover, not a discipline.
 */
export function handoverSide(comparison, modelKey) {
  const key = (side) => (carries(comparison, side) ? comparison[side].model_key : undefined);
  const sides = Object.keys(HANDOVER_SIDES).filter((side) => key(side) === modelKey);
  return typeof modelKey === "string" && sides.length === 1 ? sides[0] : null;
}

function conditionModel(outcome) {
  if (!carries(outcome, "condition_status")) {
    return { code: null, known: false, text: NOT_CARRIED, plain: NOT_CARRIED };
  }
  const code = outcome.condition_status;
  if (!known(CONDITION_ENTRIES, code)) {
    return { code, known: false, text: UNRECOGNISED, plain: UNRECOGNISED };
  }
  return { code, known: true, ...CONDITION_ENTRIES[code] };
}

function dispositionModel(item) {
  if (!carries(item, "disposition")) {
    return { code: null, known: false, text: NOT_CARRIED, next: "" };
  }
  const code = item.disposition;
  if (!known(DISPOSITION_ENTRIES, code)) return { code, known: false, text: UNRECOGNISED, next: "" };
  return { code, known: true, ...DISPOSITION_ENTRIES[code] };
}

/** The sealed verdict beside the verdict(s) the record gives now.
 *
 * Both are the record's. This only says whether they are the same word, so the
 * items can be grouped; it is not a status and it explains nothing — a verdict
 * can move because a model was re-issued, because a rule was edited, or because
 * a determination stopped being attributable, and the evidence rows say which.
 */
function verdictChange(outcome, current) {
  const from = carries(outcome, "prior_verdict") ? outcome.prior_verdict : null;
  if (current === null) return { kind: "unplaced", from, to: [] };
  const to = current.map((item) => (item.verdict === undefined ? null : item.verdict));
  const same = from !== null && to.length > 0 && to.every((verdict) => verdict === from);
  return { kind: same ? "unchanged" : "changed", from, to };
}

function verdictGroups(items, reissueName) {
  return Object.keys(VERDICT_GROUPS).map((kind) => {
    const members = items.filter((item) => item.verdictChange.kind === kind);
    const transitions = [];
    for (const item of members) {
      const { from, to } = item.verdictChange;
      const key = JSON.stringify([from, to]);
      let transition = transitions.find((entry) => entry.key === key);
      if (!transition) {
        transition = { key, from, to, items: [] };
        transitions.push(transition);
      }
      transition.items.push(item);
    }
    const entry = VERDICT_GROUPS[kind];
    const note =
      kind === "changed"
        ? entry.notes[
            reissueName === "none" ? "none" : reissueName === "unrecognised" ? "unrecognised" : "reissued"
          ]
        : entry.note;
    return {
      kind,
      label: entry.label,
      count: members.length,
      note: members.length ? note : entry.none,
      transitions: transitions.map(({ key: _key, items: grouped, ...rest }) => ({
        ...rest,
        count: grouped.length,
        items: grouped.map((item) => [item.subscopeIndex, item.memberIndex]),
      })),
    };
  });
}

export function recheckModel(document) {
  const successor = document.successor;
  if (!successor) return null;
  const kind = carries(successor, "kind") ? successor.kind : null;
  if (kind !== RECHECK_KIND) return { kind, recognised: false };

  const handover = document.request.model_version_context.handover;
  const subscopes = successor.subscopes.map((outcome, subscopeIndex) => {
    const evidence = outcome.evidence_carry_over.map(evidenceModel);
    const condition = conditionModel(outcome);
    const items = outcome.dispositions.map((item, memberIndex) => {
      const current = carries(item, "current_ordinals")
        ? item.current_ordinals.map((ordinal, index) => ({
            ordinal,
            verdict: carries(item, "current_verdicts") ? item.current_verdicts[index] : undefined,
            leafOutcome: carries(item, "current_leaf_outcomes")
              ? item.current_leaf_outcomes[index]
              : undefined,
            located: currentSubscope(document, outcome.activity_ref, ordinal),
          }))
        : null;
      return {
        subscopeIndex,
        memberIndex,
        outcome,
        entry: item,
        disposition: dispositionModel(item),
        condition,
        current,
        action: actionKind(current),
        verdictChange: verdictChange(outcome, current),
      };
    });
    return {
      subscopeIndex,
      outcome,
      condition,
      evidence,
      evidenceTally: stateTally(evidence),
      evidenceGroups: evidenceGroups(evidence),
      items,
    };
  });

  const items = subscopes.flatMap((subscope) => subscope.items);
  const reissue = reissueModel(successor.model_version_context_comparison, handover);
  return {
    kind,
    recognised: true,
    reissue,
    subscopes,
    items,
    actionGroups: actionGroups(items),
    verdictGroups: verdictGroups(items, reissue.name),
    evidenceTally: stateTally(subscopes.flatMap((subscope) => subscope.evidence)),
    evidenceGroups: evidenceGroups(subscopes.flatMap((subscope) => subscope.evidence)),
    dispositionTally: tally(
      items.map((item) => item.disposition.code),
      DISPOSITION_ENTRIES,
      (entry) => entry.text,
    ),
    conditionTally: tally(
      subscopes.map((subscope) => subscope.condition.code),
      CONDITION_ENTRIES,
      (entry) => entry.text,
    ),
  };
}
