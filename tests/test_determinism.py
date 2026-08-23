"""Layer one: two runs over unchanged inputs produce identical bytes.

**This file is never updated to make it pass.** Every other expectation in this
suite can legitimately move — a column is added, a rule changes, a count grows.
This one cannot. A failure here means something read a clock, iterated an
unordered collection, or depended on the machine it ran on, and the only
correct response is to find that and fix it.

The rule has been broken twice in this project's short history, both times
invisibly. `dc351c9` fixed CSV line endings that differed by platform. The IDS
reports embedded `datetime.now()` and listed elements in Python set iteration
order for the whole of v1.0.0, and nobody noticed, because continuous
integration never ran the pipeline.
"""

from __future__ import annotations

import ast
import dataclasses
import unittest
from pathlib import Path

from epc_control_tower.determinism import sha256_file
from epc_control_tower.pipeline import execute
from helpers import PROJECT_ROOT, shipped_run_config, writable_test_directory

PACKAGE = PROJECT_ROOT / "epc_control_tower"

#: Calls that make an output depend on when or where it ran.
FORBIDDEN_CALLS = {
    "now": "datetime.now",
    "utcnow": "datetime.utcnow",
    "today": "date.today",
    "time": "time.time",
    "monotonic": "time.monotonic",
    "urandom": "os.urandom",
}


def _run_into(scratch: Path) -> dict[str, str]:
    """Run everything into a scratch tree and digest what came out."""

    config = dataclasses.replace(
        shipped_run_config(),
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    execute(config)
    return {
        path.relative_to(scratch).as_posix(): sha256_file(path)
        for path in sorted(scratch.rglob("*"))
        if path.is_file()
    }


class ByteIdenticalRunTests(unittest.TestCase):
    def test_running_the_whole_pipeline_twice_produces_the_same_bytes(self):
        # Into the same destination both times. The manifests record where each
        # artifact went, so running into two different directories would
        # legitimately differ and prove nothing.
        with writable_test_directory("determinism") as scratch:
            left = _run_into(scratch)
            right = _run_into(scratch)

        self.assertEqual(sorted(left), sorted(right))
        self.assertGreater(len(left), 20)
        for name in sorted(left):
            with self.subTest(artifact=name):
                self.assertEqual(left[name], right[name])

    def test_the_execution_record_never_reaches_a_published_artifact(self):
        # Execution is deliberately unreachable from RunBundle. An exporter
        # that could see a wall-clock timestamp would eventually write one.
        from epc_control_tower.domain import RunBundle, field_names

        self.assertNotIn("execution", field_names(RunBundle))
        with writable_test_directory("determinism-exec") as scratch:
            _run_into(scratch)
            for path in scratch.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_bytes().decode("utf-8", "replace")
                with self.subTest(artifact=path.name):
                    self.assertNotIn("execution_id", text)


class SourceDisciplineTests(unittest.TestCase):
    """The rules that keep the property above true, checked at the source."""

    @staticmethod
    def _modules():
        return sorted(PACKAGE.rglob("*.py"))

    def test_nothing_in_the_package_reads_a_clock_or_the_system_entropy(self):
        for path in self._modules():
            tree = ast.parse(path.read_text("utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                name = getattr(function, "attr", None) or getattr(function, "id", None)
                if name in FORBIDDEN_CALLS:
                    with self.subTest(module=path.name, call=name):
                        self.fail(
                            f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} calls "
                            f"{FORBIDDEN_CALLS[name]}, which would make an output "
                            "depend on when it ran"
                        )

    def test_the_only_randomness_is_the_execution_nonce(self):
        # uuid4 is genuinely needed once — to tell apart two executions that
        # started inside the same clock tick — and that value touches nothing
        # deterministic. Anywhere else it would be a fresh identity on every
        # run, which is the opposite of what identities are for.
        allowed = ("identity.py", "new_execution_nonce")
        for path in self._modules():
            tree = ast.parse(path.read_text("utf-8"))
            enclosing = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for child in ast.walk(node):
                        enclosing[id(child)] = node.name
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                if name != "uuid4":
                    continue
                with self.subTest(module=path.name, line=node.lineno):
                    self.assertEqual(
                        (path.name, enclosing.get(id(node))),
                        allowed,
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} generates "
                        "randomness outside the execution nonce",
                    )

    def test_every_generated_text_format_declares_its_line_endings(self):
        # The writers already emit LF everywhere. This checks that the
        # guarantee is *declared* rather than resting on an implementation
        # detail: without a .gitattributes entry a format falls back to
        # `text=auto`, and a future writer using the platform default would put
        # CRLF into the blob on Windows and break the byte comparison on Linux.
        declared = (PROJECT_ROOT / ".gitattributes").read_text("utf-8")
        generated_suffixes = {
            path.suffix
            for path in (PROJECT_ROOT / "data" / "processed").rglob("*")
            if path.is_file()
        } | {
            path.suffix
            for path in (PROJECT_ROOT / "reports").rglob("*")
            if path.is_file() and path.suffix != ".bcf"  # a ZIP, and binary
        }
        for suffix in sorted(suffix for suffix in generated_suffixes if suffix):
            with self.subTest(suffix=suffix):
                self.assertIn(f"*{suffix} text eol=lf", declared)

    def test_rule_documents_pin_their_bytes_one_way_or_the_other(self):
        # ids/*.ids is deliberately exempt from git's text normalisation. Two
        # different things follow from that, and conflating them is a mistake
        # worth spelling out.
        #
        # The frozen document is CRLF *on purpose*: the published run_id is a
        # digest of its raw bytes, taken from a CRLF working copy, so the
        # exemption is what makes the published baseline reproducible on Linux.
        #
        # A generated document in the same directory has the opposite problem.
        # IfcTester writes XML in text mode, so without an explicit choice the
        # same rules compile to CRLF on Windows and LF elsewhere, and — with
        # normalisation off — the regeneration gate then fails on whichever
        # platform did not write the committed copy. It happened; this is the
        # regression test.
        frozen = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
        self.assertIn(b"\r\n", frozen.read_bytes(), "the frozen byte pin is gone")

        for path in sorted((PROJECT_ROOT / "ids").glob("*.ids")):
            if path == frozen:
                continue
            with self.subTest(document=path.name):
                self.assertNotIn(b"\r\n", path.read_bytes())

    def test_no_archive_is_compressed(self):
        # Compression output depends on the zlib build, so a compressed archive
        # is not reproducible across machines.
        for path in self._modules():
            with self.subTest(module=path.name):
                self.assertNotIn("ZIP_DEFLATED", path.read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
