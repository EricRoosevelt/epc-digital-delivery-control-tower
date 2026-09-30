#!/usr/bin/env bash
# Every measurement behind ADR 0005, in one pass.
#
#   CT=<disposable checkout of 4e05c03> PY=<project .venv python> \
#   PROBE_SCRATCH=<scratch dir outside CT> bash run_all.sh
#
# The checkout is restored with `git checkout -- . && git clean -fdq` after
# every scenario and must end clean; nothing here writes outside CT except under
# PROBE_SCRATCH.
set -u
E="$(cd "$(dirname "$0")" && pwd)"
export PROBE_SCRATCH
cd "$CT" || exit 1

probe() { "$PY" "$E/probe.py" "$@"; }
apply() { "$PY" "$E/patches.py" "$@" >/dev/null || exit 1; }
reset() { git checkout -q -- . && git clean -fdq; }
porcelain() { git status --porcelain --untracked-files=all | wc -l | tr -d ' '; }
run() { "$PY" -m epc_control_tower.cli run >/dev/null 2>&1; echo "run exit=$?"; }
snapshot() { "$PY" -m epc_control_tower.cli snapshot >/dev/null 2>&1; echo "snapshot exit=$?"; }
suite() {
  EPC_REQUIRE_IDS_AUDIT=1 "$PY" -m pytest -p no:cacheprovider tests -q -rfE --tb=no 2>&1 \
    > "$PROBE_SCRATCH/suite.txt"
  tail -1 "$PROBE_SCRATCH/suite.txt"
  # Every failing, erroring or subtest-failing line of the short summary, by
  # outcome and file.
  grep -E '^(FAILED|ERROR|SUBFAILED)' "$PROBE_SCRATCH/suite.txt" \
    | awk '{o = $1; sub(/\(.*/, "", o);
            for (i = 1; i <= NF; i++) if ($i ~ /^tests\//) { split($i, a, "::"); print o, a[1]; break }}' \
    | sort | uniq -c
}

echo "### HEAD $(git rev-parse HEAD)"
echo "dirty/untracked: $(porcelain)"

echo; echo "### S0 pristine run"
run
echo "generated files changed: $(porcelain)"
rm -rf "$PROBE_SCRATCH/pristine"; mkdir -p "$PROBE_SCRATCH/pristine"
cp -r data reports ids "$PROBE_SCRATCH/pristine/"
suite
reset

echo; echo "### D normalized digest under each edit (status quo)"
probe digests
reset

echo; echo "### RB findings before/after each facet edit (status quo)"
for e in r002-datatype r005a-optional r005a-datatype; do probe bundle "$e"; echo; reset; done

echo "### RP the real recheck chain (status quo)"
probe recheck r005a-optional; echo; reset
probe recheck r005a-datatype; reset

echo; echo "### SQ what a published run does with an edit today"
for e in r002-datatype r005a-instructions; do
  echo "-- $e"; apply "$e"; run; snapshot; probe published "$PROBE_SCRATCH/pristine"; reset
done

echo; echo "### O1 facet parameters folded into the normalized digest (prototype)"
apply O1
probe digests
run; snapshot
probe published "$PROBE_SCRATCH/pristine"
"$PY" src/validate_dashboard.py --mode core >/dev/null 2>&1; echo "validate_dashboard exit=$?"
"$PY" src/validate_pbip.py >/dev/null 2>&1; echo "validate_pbip exit=$?"
echo "-- version guard against the recorded snapshots"
probe guard
echo "-- composition"
probe compose
echo "-- the recheck chain under O1"
probe recheck r005a-optional
echo
probe recheck r005a-datatype
echo "-- the version guard on the next edit, once O1's digest is recorded"
probe guard-record
for e in r002-datatype r005a-datatype r005a-instructions r005a-reformat; do probe guard "$e"; done
echo "-- test suite under O1 (published tree regenerated)"
suite
reset

echo; echo "### O1i O1 with instructions counted as semantics"
apply O1 O1-instructions
probe digests
reset

echo; echo "### O2 version discipline: bump 2.2 -> 2.3"
apply version-2.3
run; snapshot
probe published "$PROBE_SCRATCH/pristine"
probe guard
probe compose
echo "-- test suite with the bump (published tree regenerated)"
suite
reset
echo "-- the recheck chain when the edit carries the bump"
probe recheck r005a-optional+version-2.3
reset

echo; echo "### O1+2.3 O1 and a version bump together"
apply O1 version-2.3
run
probe published "$PROBE_SCRATCH/pristine"
probe guard
probe compose
reset

echo; echo "### O3 a content digest beside each cited finding_key (prototype)"
apply O3
run; snapshot
probe published "$PROBE_SCRATCH/pristine"
probe recheck r005a-optional
echo
probe recheck r005a-datatype
echo "-- test suite under O3"
suite
reset

echo; echo "### END"
echo "dirty/untracked: $(porcelain)"
