"""Conformance against buildingSMART's own IDS 1.0 implementer test cases.

Every gate this repository had before this file was self-referential. The
determinism tests assert that two runs of our code agree with each other; the
characterization tests assert that our code agrees with what our code produced
last time. All of that is worth having, and none of it can tell you whether the
interpretation being frozen so carefully is the *right* one. This file is the
first gate with an outside judge: 199 `.ids`/`.ifc` pairs published by
buildingSMART, each named for the outcome the standard expects.

Three things are asserted, in order of what they are worth:

1. The vendored bytes are the upstream bytes (`SHA256SUMS`). Under a
   NoDerivatives license this is a licensing obligation as much as a technical
   one, and it is also what makes the rest of the file mean anything: a
   conformance rate against a corpus that has drifted measures nothing.
2. Each case's verdict matches its filename prefix, with a short, explicit list
   of the cases that do not — every one classified and explained.
3. Our N/A normalization is not what causes any divergence. This is the claim
   that would otherwise be assumed, and it turns out the corpus can neither
   confirm nor refute it; see :meth:`ScopeTests` for why that is stated rather
   than glossed over.

**These are conformance fixtures, not project fixtures.** They live under
`third_party/` precisely so that `discover_project_manifests`, which globs
`projects/*/project.toml`, cannot see them. They are not models this project
delivers; they are the yardstick it is measured with.

Reading the filename prefixes
-----------------------------

`pass-` and `fail-` are unambiguous: the specification must be reported as
passing or failing. `invalid-` marks a document the standard considers invalid,
and buildingSMART does not say in prose what a validator should then report.
The upstream case titles do say it — "Invalid attribute names always fail",
"Derived attributes cannot be checked and always fail", "Specifying a float
when the value is an integer is invalid" — so the prefix is read here as *must
not report a pass*. That is the conservative reading and the only safe one: a
tool that returns green on a specification the standard rejects is worse than
one that returns red, because the green is what gets published.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import ifcopenshell
from ifctester import ids, reporter

from epc_control_tower.checkers.ids_checker import IdsChecker
from helpers import PROJECT_ROOT

VENDORED = PROJECT_ROOT / "third_party" / "buildingsmart" / "ids" / "1.0"
TESTCASES = VENDORED / "testcases"

#: Facet directories copied from upstream. The other six were left there; see
#: `SOURCE.md` for what was taken and why only this much.
SUBSETS = ("attribute", "classification", "partof", "property")

#: Total cases and the number that agree with the standard, pinned so that both
#: a regression and an upstream fix are visible rather than silent. 194/199 is
#: 97.49%.
TOTAL_CASES = 199
CONFORMING_CASES = 194


#: Every case whose verdict does not match its filename prefix, with the
#: verdict actually observed and what is responsible for it.
#:
#: The point of writing them out is that "97% conformant" is not a finding —
#: *which* 3% is. Each entry below was traced to a specific line of behaviour,
#: and none of them is in this repository's code.
KNOWN_DIVERGENCES = {
    # --- IfcTester casts IDS value literals instead of typing them ----------
    #
    # All three cases give a value the standard says is invalid for the
    # declared data type — an integer written with a decimal point — and expect
    # the specification to be rejected rather than evaluated. IfcTester casts
    # the literal to a number and compares numerically, so `42.0` matches the
    # stored integer `42` and the specification comes back green.
    #
    # This is IfcTester's behaviour, not ours: our status is identical to the
    # raw status it reported, and no normalization of ours is reached. It is
    # also the clearest argument for a separate syntax gate. A validator this
    # lenient will happily execute a document that is not a valid IDS, and the
    # only way to notice is to have something else read the document first.
    "attribute/invalid-integers_cannot_be_expressed_as_floating_point_numbers_2_2": (
        "PASS",
        "ifctester",
        "IDS requires NumberOfRisers == '42.0' against a stored integer 42; "
        "IfcTester casts the literal rather than rejecting it for the type.",
    ),
    "property/invalid-integer_values_cannot_be_stored_with_decimal_2_4": (
        "PASS",
        "ifctester",
        "IDS declares dataType IFCINTEGER with the literal '42.'; IfcTester "
        "casts it to 42 and matches.",
    ),
    "property/invalid-integer_values_cannot_be_stored_with_decimal_3_4": (
        "PASS",
        "ifctester",
        "IDS declares dataType IFCINTEGER with the literal '42.0'; IfcTester "
        "casts it to 42 and matches.",
    ),
    # --- IfcTester's optional cardinality misses a present-but-null value ---
    #
    # `ifctester/facet.py` Attribute.__call__ takes the optional branch only
    # when the attribute is absent as a forward attribute. For `Name=$` the
    # value list is `[None]`, which is truthy, so the branch is skipped and the
    # later emptiness check fails the element. The standard expects an optional
    # attribute facet to pass when the attribute is null.
    "attribute/pass-an_optional_attribute_passes_if_null": (
        "FAIL",
        "ifctester",
        "cardinality='optional' with a null attribute; IfcTester's optional "
        "branch only fires when the attribute is absent, not when it is null.",
    ),
    # --- IfcTester reads the wrong IFC2X3 attribute -------------------------
    #
    # `facet.py` get_properties() returns `pset.Properties` for anything that
    # is_a IfcMaterialProperties. In IFC2X3, IfcExtendedMaterialProperties is
    # such a subtype but names its collection `ExtendedProperties`, so the
    # lookup raises. Outside this checker's declared envelope in any case:
    # IdsChecker.capabilities lists IFC4 only.
    "property/pass-material_properties_are_supported_under_ifc2x3"
    "_via_extendedmaterialproperties": (
        "ERROR",
        "ifctester",
        "AttributeError inside IfcTester: IFC2X3 IfcExtendedMaterialProperties "
        "stores ExtendedProperties, not Properties.",
    ),
}


def _cases() -> list[tuple[str, Path]]:
    """Every vendored case as ``(name, ids_path)``, in a stable order."""

    found = []
    for subset in SUBSETS:
        for path in sorted((TESTCASES / subset).glob("*.ids")):
            found.append((f"{subset}/{path.stem}", path))
    return found


def _run(ids_path: Path) -> dict:
    """Evaluate one case the way this project evaluates a specification.

    Deliberately not a full pipeline run: a case has no project manifest, no
    inventory and no provenance hash, and inventing them would put this
    project's plumbing between the standard and the answer. What is under test
    is the interpretation — IfcTester's report, read through
    ``IdsChecker._specification_status``, which is the whole of this project's
    normalization of a specification outcome.
    """

    document = ids.open(str(ids_path))
    document.validate(ifcopenshell.open(str(ids_path.with_suffix(".ifc"))))

    json_reporter = reporter.Json(document)
    json_reporter.report()
    results = json.loads(json.dumps(json_reporter.results, default=str))

    specifications = results["specifications"]
    if len(specifications) != 1:
        raise AssertionError(
            f"{ids_path.name}: expected one specification, found "
            f"{len(specifications)}"
        )
    specification = specifications[0]
    return {
        "ours": IdsChecker._specification_status(specification).value,
        "raw": "PASS" if specification.get("status") else "FAIL",
        "applicable": int(specification.get("total_applicable", 0) or 0),
    }


def _verdicts() -> dict[str, dict]:
    verdicts = {}
    for name, path in _cases():
        try:
            verdicts[name] = _run(path)
        except Exception as exc:  # noqa: BLE001 - the failure is the datum
            verdicts[name] = {
                "ours": "ERROR",
                "raw": "ERROR",
                "applicable": 0,
                "detail": f"{type(exc).__name__}: {exc}",
            }
    return verdicts


def _conforms(prefix: str, verdict: str) -> bool:
    if prefix == "pass":
        return verdict == "PASS"
    if prefix == "fail":
        return verdict == "FAIL"
    if prefix == "invalid":
        return verdict != "PASS"
    raise AssertionError(f"unrecognised case prefix {prefix!r}")


class VendoredCorpusTests(unittest.TestCase):
    """The corpus is the upstream corpus, unmodified."""

    def test_every_vendored_file_matches_its_recorded_digest(self):
        recorded = {}
        for line in (VENDORED / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            digest, _, relative = line.partition("  ")
            recorded[relative] = digest

        present = {
            path.relative_to(VENDORED).as_posix()
            for path in VENDORED.rglob("*")
            if path.is_file() and path.name not in {"SHA256SUMS", "SOURCE.md"}
        }
        self.assertEqual(present, set(recorded))

        for relative, digest in sorted(recorded.items()):
            with self.subTest(file=relative):
                actual = hashlib.sha256((VENDORED / relative).read_bytes()).hexdigest()
                # A mismatch here is most likely `.gitattributes` having lost
                # the `-text` line for this directory, which rewrites every
                # line ending on a Windows checkout.
                self.assertEqual(actual, digest)

    def test_the_manifest_covers_the_license_and_every_case_file(self):
        # 398 case files plus the upstream LICENSE.
        lines = (VENDORED / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2 * TOTAL_CASES + 1)

    def test_the_manifest_itself_is_the_one_source_md_records(self):
        # Without this, the digest `SOURCE.md` quotes is decorative. With it,
        # the manifest's own line endings are load-bearing: `.gitattributes`
        # pins this file to LF because the hash below was taken over LF, and a
        # Windows checkout that reverted to CRLF would fail here rather than
        # leaving a documented hash that nothing verifies.
        raw = (VENDORED / "SHA256SUMS").read_bytes()
        self.assertNotIn(b"\r\n", raw)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "948e80fef0432b0e70389e3a6e10d4b9a28ff761edf773ea02c59731aab2068a",
        )

    def test_every_case_is_a_document_and_a_model(self):
        for name, path in _cases():
            with self.subTest(case=name):
                self.assertTrue(path.with_suffix(".ifc").is_file())
                self.assertIn(name.split("/")[1].split("-", 1)[0], {"pass", "fail", "invalid"})

    def test_the_corpus_is_not_discovered_as_a_project(self):
        # A conformance fixture is not a deliverable. If these ever showed up
        # in `projects/`, the pipeline would try to inventory 199 toy models
        # and publish findings about them.
        from epc_control_tower.config import discover_project_manifests

        discovered = discover_project_manifests(PROJECT_ROOT / "projects")
        self.assertTrue(discovered)
        for manifest in discovered:
            with self.subTest(manifest=manifest.name):
                self.assertNotIn("third_party", manifest.parts)


class ConformanceTests(unittest.TestCase):
    """Each case's verdict against the outcome its filename declares."""

    @classmethod
    def setUpClass(cls):
        cls.verdicts = _verdicts()

    def test_each_case_agrees_with_the_standard_or_is_a_known_divergence(self):
        for name, result in sorted(self.verdicts.items()):
            prefix = name.split("/")[1].split("-", 1)[0]
            with self.subTest(case=name):
                if _conforms(prefix, result["ours"]):
                    self.assertNotIn(name, KNOWN_DIVERGENCES)
                    continue
                self.assertIn(name, KNOWN_DIVERGENCES)
                self.assertEqual(result["ours"], KNOWN_DIVERGENCES[name][0])

    def test_no_recorded_divergence_has_quietly_been_fixed(self):
        # The list is a statement about the world, so it has to be wrong when
        # the world changes. An upstream fix should break this file and be
        # reported, not be absorbed in silence.
        for name in sorted(KNOWN_DIVERGENCES):
            with self.subTest(case=name):
                self.assertIn(name, self.verdicts)
                prefix = name.split("/")[1].split("-", 1)[0]
                self.assertFalse(_conforms(prefix, self.verdicts[name]["ours"]))

    def test_the_conformance_rate_is_what_was_reported(self):
        conforming = sum(
            1
            for name, result in self.verdicts.items()
            if _conforms(name.split("/")[1].split("-", 1)[0], result["ours"])
        )
        self.assertEqual(len(self.verdicts), TOTAL_CASES)
        self.assertEqual(conforming, CONFORMING_CASES)

    def test_every_divergence_is_attributed_to_the_library_not_to_us(self):
        # The finding, stated as an assertion. Every case where this project
        # disagrees with the standard, it disagrees because IfcTester does; not
        # one is caused by anything this repository decided.
        for name, (_status, blame, _why) in sorted(KNOWN_DIVERGENCES.items()):
            with self.subTest(case=name):
                self.assertEqual(blame, "ifctester")


class ScopeTests(unittest.TestCase):
    """What this corpus can and cannot tell us about our own normalization."""

    @classmethod
    def setUpClass(cls):
        cls.verdicts = _verdicts()

    def test_our_normalization_changes_no_verdict_in_this_corpus(self):
        for name, result in sorted(self.verdicts.items()):
            with self.subTest(case=name):
                self.assertEqual(result["ours"], result["raw"])

    def test_the_corpus_never_exercises_the_zero_applicable_rule(self):
        # Stated as a test because it is a limit on the evidence, and a limit
        # nobody states is a limit nobody remembers. Every case here selects at
        # least one element, so the one normalization this project applies —
        # reporting a specification with no applicable elements as N/A instead
        # of as a pass — is never reached. The 97.49% therefore says nothing
        # about whether that rule is right. What justifies it is separate and
        # unchanged: counting "nothing to check" as compliance inflates every
        # published pass rate.
        #
        # If a future subset does exercise it, this test fails, and the
        # conformance numbers above have to be re-read in that light.
        for name, result in sorted(self.verdicts.items()):
            with self.subTest(case=name):
                if result["ours"] == "ERROR":
                    continue
                self.assertGreater(result["applicable"], 0)


if __name__ == "__main__":
    unittest.main()
