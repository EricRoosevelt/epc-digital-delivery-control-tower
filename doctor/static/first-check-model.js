// What the first-check screens say about a record that succeeds nothing, as
// plain data. No DOM here, so it can be exercised without a browser.
//
// Everything below selects, groups and counts what the record already holds:
//
// * one **item** per member of a subscope: an element, or a pair of elements,
//   under one activity of the receiving side. The unit of every count is the
//   item, never a defect — one element can sit in several items;
// * an item is **to do** when its subscope carries a next action. Its verdict is
//   the subscope's own word, counted under that word and never merged with
//   another: a known unmet requirement and a missing piece of evidence are two
//   different things;
// * the **basis** of a verdict is every citation and every named absence on the
//   subscope's path. Whether a citation is simulated is read off that citation's
//   own marker by the caller; nothing here infers it from the record's mode;
// * items are grouped by the **team** the record's assignment names. A subscope
//   without one is grouped under "not carried"; no other field stands in for it.
//
// Nothing here decides a verdict, and a value this file does not know is
// carried through as it came.

function carries(object, key) {
  return object !== null && typeof object === "object" && Object.hasOwn(object, key);
}

function carried(object, key) {
  return carries(object, key) ? object[key] : undefined;
}

function shortName(activityRef) {
  const index = activityRef.indexOf("::");
  return index >= 0 ? activityRef.slice(index + 2) : activityRef;
}

function sameKeys(left, right) {
  return left.length === right.length && left.every((key, index) => key === right[index]);
}

/** Every citation and named absence on one subscope's path, in the record's order.
 *
 * Without `keys` this is the whole path — the basis the members of the subscope
 * share. With `keys` it is one member's: at each node, the readings the record
 * took on exactly that member, and where the node has none of its own (a reading
 * taken on the whole scope, or on the element a pair was refined from) every
 * reading of that node.
 */
export function basisOf(subscope, keys = null) {
  const basis = { findings: [], determinations: [], gaps: [], context: [] };
  for (const step of carries(subscope, "path") ? subscope.path : []) {
    if (carries(step, "context_citations")) basis.context.push(...step.context_citations);
    const readings = carries(step, "readings") ? step.readings : [];
    const own = keys === null ? [] : readings.filter((reading) => sameKeys(reading.subject.keys, keys));
    for (const reading of own.length ? own : readings) {
      if (carries(reading, "finding_keys")) basis.findings.push(...reading.finding_keys);
      if (carries(reading, "cited_determinations")) {
        for (const cited of reading.cited_determinations) {
          if (carries(cited, "reference")) basis.determinations.push(cited.reference);
        }
      }
      if (carries(reading, "absence")) basis.gaps.push(reading.absence);
    }
  }
  return basis;
}

/** Every citation a record's conclusions rest on, anywhere in the document.
 *
 * What the head of an example page summarises: which sources this one record
 * cites, so the summary names the kinds it actually has. The whole document is
 * walked, so a first check's readings, a recheck's earlier and current readings
 * and both sides of each carry-over row are all in it. Context citations are
 * consulted at a node and are never a reading (`PathStep.context_citations`), so
 * they are not a conclusion's basis and are left out. Whether a citation is
 * simulated is still read off the citation itself, by the caller.
 */
export function recordCitations(document) {
  const found = { findings: [], determinations: [] };
  const strings = (values) => values.filter((value) => typeof value === "string" && value !== "");
  const walk = (value) => {
    if (Array.isArray(value)) {
      value.forEach(walk);
      return;
    }
    if (value === null || typeof value !== "object") return;
    if (Array.isArray(value.finding_keys)) found.findings.push(...strings(value.finding_keys));
    if (Array.isArray(value.cited_determinations)) {
      found.determinations.push(...strings(value.cited_determinations.map((cited) => carried(cited, "reference"))));
    }
    if (value.citation_kind === "finding" || value.citation_kind === "determination") {
      const sides = strings([carried(value, "citation"), carried(value, "current_citation")]);
      (value.citation_kind === "finding" ? found.findings : found.determinations).push(...sides);
    }
    for (const [key, inner] of Object.entries(value)) {
      if (key !== "context_citations") walk(inner);
    }
  };
  walk(document);
  return found;
}

/** The reading at the end of the path: which evidence requirement, which outcome. */
export function leafOf(subscope) {
  const path = carries(subscope, "path") ? subscope.path : [];
  const step = path.length ? path[path.length - 1] : null;
  if (step === null) return null;
  return {
    requirement: carried(step, "evidence_requirement_id"),
    outcome: carried(step, "outcome"),
  };
}

export function firstCheckModel(document) {
  const items = [];
  document.activities.forEach((activity, activityIndex) => {
    for (const subscope of activity.subscopes) {
      const route = carried(subscope, "route");
      const assignment = carried(subscope, "assignment");
      subscope.members.forEach((member, memberIndex) => {
        items.push({
          activityIndex,
          activityRef: activity.activity_ref,
          activity: shortName(activity.activity_ref),
          ordinal: subscope.ordinal,
          memberIndex,
          keys: member.keys,
          subscope,
          verdict: carried(subscope, "verdict"),
          kind: carried(subscope, "resolution_kind"),
          route,
          assignment,
          // The team is the assignment's and nothing else's.
          team: carried(assignment, "assigned_team_or_person"),
          role: carried(route, "default_role"),
          todo: carries(route, "next_action"),
          basis: basisOf(subscope, member.keys),
          leaf: leafOf(subscope),
        });
      });
    }
  });

  const todo = items.filter((item) => item.todo);
  const quiet = items.filter((item) => !item.todo);

  // Counted under the record's own verdict word, in the order first met.
  const verdicts = [];
  for (const item of todo) {
    let entry = verdicts.find((candidate) => candidate.verdict === item.verdict);
    if (!entry) {
      entry = { verdict: item.verdict, count: 0 };
      verdicts.push(entry);
    }
    entry.count += 1;
  }

  // Team first, then what the team is asked about: one row per problem type
  // under one activity, with its verdict word and its items.
  const teams = [];
  for (const item of todo) {
    let team = teams.find((candidate) => candidate.team === item.team);
    if (!team) {
      team = { team: item.team, roles: [], count: 0, rows: [] };
      teams.push(team);
    }
    team.count += 1;
    if (item.role !== undefined && !team.roles.includes(item.role)) team.roles.push(item.role);
    let row = team.rows.find(
      (candidate) =>
        candidate.kind === item.kind &&
        candidate.activity === item.activity &&
        candidate.verdict === item.verdict,
    );
    if (!row) {
      row = { kind: item.kind, activity: item.activity, verdict: item.verdict, role: item.role, items: [] };
      team.rows.push(row);
    }
    row.items.push(item);
  }

  const elements = new Set(items.flatMap((item) => item.keys));
  return {
    items,
    todo,
    quiet,
    verdicts,
    teams,
    counts: { items: items.length, todo: todo.length, quiet: quiet.length, elements: elements.size },
  };
}

/** One item of the record, by the three numbers its address carries. */
export function firstCheckItem(model, activityIndex, ordinal, memberIndex) {
  return (
    model.items.find(
      (item) =>
        item.activityIndex === activityIndex &&
        item.ordinal === ordinal &&
        item.memberIndex === memberIndex,
    ) ?? null
  );
}
