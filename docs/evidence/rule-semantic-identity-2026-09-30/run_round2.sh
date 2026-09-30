#!/usr/bin/env bash
# Round 2 measurements behind ADR 0005's revision (2026-10-01), in one pass.
#
#   CT=<disposable checkout of c9cf3b2> PY=<project .venv python> \
#   PROBE_SCRATCH=<scratch dir outside CT> bash run_round2.sh
#
# Round 1 (run_all.sh) is left exactly as audited. The coverage record `run`
# has written since c9cf3b2 is directed into PROBE_SCRATCH, so nothing lands in
# the user's state directory. The checkout is restored after every scenario
# and must end clean.
set -u
E="$(cd "$(dirname "$0")" && pwd)"
export PROBE_SCRATCH
export EPC_CT_COVERAGE_DIR="$PROBE_SCRATCH/coverage"
cd "$CT" || exit 1

probe() { "$PY" "$E/probe_r2.py" "$@"; }
apply() { "$PY" "$E/patches_r2.py" "$@" >/dev/null || exit 1; }
reset() { git checkout -q -- . && git clean -fdq; }
porcelain() { git status --porcelain --untracked-files=all | wc -l | tr -d ' '; }
suite() {
  EPC_REQUIRE_IDS_AUDIT=1 "$PY" -m pytest -p no:cacheprovider tests -q -rfE --tb=no 2>&1 \
    > "$PROBE_SCRATCH/suite.txt"
  tail -1 "$PROBE_SCRATCH/suite.txt"
  grep -E '^(FAILED|ERROR|SUBFAILED)' "$PROBE_SCRATCH/suite.txt" \
    | awk '{o = $1; sub(/\(.*/, "", o);
            for (i = 1; i <= NF; i++) if ($i ~ /^tests\//) { n = split($i, a, "::"); print o, a[1] "::" a[n]; break }}' \
    | sort
}

echo "### HEAD $(git rev-parse HEAD)"
echo "dirty/untracked: $(porcelain)"
echo "rules tree $(git rev-parse HEAD:rules/epc-delivery)"
for c in 11e4163 4e05c03; do echo "rules tree at $c $(git rev-parse $c:rules/epc-delivery)"; done
"$PY" -c "from pathlib import Path; from epc_control_tower.coverage import rule_definitions_digest as d; print('rule_definitions_digest', d(Path('rules/epc-delivery')))"

echo; echo "### P3a normalized digest under each edit (status quo)"
probe digests
reset

echo; echo "### P3b what the display-text and R-010 edits do to findings (status quo)"
for e in r005a-title r005a-description r005a-instructions r010-instructions r010-applicability; do
  probe bundle "$e"; echo; reset
done

echo "### P3c which semantics digests move (O1 as P-3 ruled it: O1 + O1b)"
apply O1 O1b
for e in r005a-instructions r010-instructions r005a-title r005a-description r010-applicability \
         r005a-reformat r005a-datatype r005a-optional r002-datatype; do
  probe semantics "$e"
done
reset

echo; echo "### C the four-state comparison (O1 + O1b + C prototype)"
apply O1 O1b C
for s in relax retype unrelated pre-1.7-record reissue reissue-deleted ambiguous; do
  probe carry "$s"; echo; reset; apply O1 O1b C
done
echo "-- test suite under O1 + O1b + C (published tree regenerated)"
"$PY" -m epc_control_tower.cli run >/dev/null 2>&1; echo "run exit=$?"
suite
reset

echo; echo "### END"
echo "dirty/untracked: $(porcelain)"
