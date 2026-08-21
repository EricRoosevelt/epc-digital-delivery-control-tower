"""An IDS document read by something other than the library that wrote it.

Every check on the rule documents so far has been performed by IfcTester, which
is also what produced one of them. That is a closed loop: a document IfcTester
writes and IfcTester accepts tells you the two agree, not that either is right.
`ids-tool` is a separate implementation, in a different language, by a different
author, published by buildingSMART. It reads the document against the IDS
schema and against the standard's content rules and says yes or no.

The conformance corpus already showed why this matters. Three of the five cases
where this project disagrees with the standard are documents whose value
literal does not match its declared data type — `42.0` where the type says
IFCINTEGER — and IfcTester executes them anyway, casts, and reports a pass.
`ids-tool` rejects all three by name (error 305). A validator that lenient will
happily return green on a document that is not valid IDS, and the only way to
find out is to have something else read the document first. That is this file.

No code is copied from the audit tool. It is invoked as an external process at
a pinned version; see `docs/open_source_adoption.md`.

**Skipping is a supported local behaviour and a build failure in CI.** A gate
that quietly disappears when its tool is missing is not a gate, so continuous
integration sets `EPC_REQUIRE_IDS_AUDIT=1` and this file fails rather than
skips when the tool cannot be found.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path

from helpers import PROJECT_ROOT

IDS_DIR = PROJECT_ROOT / "ids"

#: Both rule documents: the frozen one the legacy adapters publish, and the one
#: compiled from `rules/epc-delivery/` by every run.
DOCUMENTS = (
    "epc_delivery_requirements_v0.1.ids",
    "epc-delivery_v2.2.ids",
)

#: `ids-tool` exits 0 for a clean audit and a non-zero status per error class
#: (16 is a content error). Only "clean" is acceptable here, so the exact code
#: matters less than the fact that it is not zero — but it is reported, because
#: `errorcode <n>` turns it back into a sentence.
_CLEAN = 0


def _tool() -> str | None:
    return shutil.which("ids-tool")


def _audit(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_tool(), "audit", str(target)],
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
    )


class IdsSyntaxAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if _tool() is not None:
            return
        if os.environ.get("EPC_REQUIRE_IDS_AUDIT"):
            raise AssertionError(
                "EPC_REQUIRE_IDS_AUDIT is set but `ids-tool` is not on PATH. "
                "Continuous integration installs it; if this fires there, the "
                "install step failed and the audit gate is not running."
            )
        raise unittest.SkipTest(
            "`ids-tool` is not installed. Install it with:\n"
            "  dotnet tool install --global ids-tool.CommandLine --version 1.0.124"
        )

    def test_every_rule_document_passes_an_independent_audit(self):
        for name in DOCUMENTS:
            with self.subTest(document=name):
                result = _audit(IDS_DIR / name)
                self.assertEqual(
                    result.returncode,
                    _CLEAN,
                    f"{name} failed the IDS audit:\n{result.stdout}{result.stderr}",
                )

    def test_the_audit_covers_every_document_in_the_directory(self):
        # Nothing may be added to `ids/` and quietly escape the gate.
        present = sorted(p.name for p in IDS_DIR.glob("*.ids"))
        self.assertEqual(present, sorted(DOCUMENTS))

    def test_the_gate_can_actually_fail(self):
        # A gate nobody has seen reject anything is a gate nobody knows works.
        # This document is one of the vendored conformance cases, and it is the
        # exact defect IfcTester was found to wave through: an IFCINTEGER value
        # written as `42.0`.
        known_bad = (
            PROJECT_ROOT
            / "third_party"
            / "buildingsmart"
            / "ids"
            / "1.0"
            / "property"
            / "invalid-integer_values_cannot_be_stored_with_decimal_3_4.ids"
        )
        result = _audit(known_bad)
        self.assertNotEqual(result.returncode, _CLEAN)
        self.assertIn("XsInteger", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
