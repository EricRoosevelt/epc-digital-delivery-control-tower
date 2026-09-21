"""The validation path reaches no network, and does not try to.

IfcTester's ``ids.xsd`` imports three W3C schemas by URL. Loading it therefore
*attempted* three fetches on every ``epc-ct check`` and every ``epc-ct run``,
and ``xmlschema`` only produced the right schema afterwards, by falling back to
the copies it ships. Correctness rested on a third-party fallback that fires on
failure, so the path had two outcomes for two states of a remote server it does
not control:

- refused or unreachable: the fallback fires, and every published byte is right;
- reachable but truncated: ``http.client.IncompleteRead`` propagates and the
  run dies. That is the flake once written off as environmental on
  ``test_bcf_exporter.py::MetadataDrivenTests`` — a test that made the same
  three attempts.

So the claim here is not "blocking the network changes no byte" — that was
already true, and `test_doctor_adapter.py` still pins it for the Doctor
envelopes. The claim is stronger and is what makes the second outcome
impossible: **no connection is attempted at all.** A test that only blocked
connections and compared bytes would pass just as happily on the broken code.

Every measurement below runs in a separate process under an audit hook that
records *and* refuses every non-local connection, then asserts the recording is
empty. The hook watches ``urllib.Request`` as well as the socket events,
because the attempt this is about is made through ``urllib`` and is visible
there before any name lookup happens.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest

from helpers import PROJECT_ROOT


def _imported_names(path) -> set[str]:
    """Every module named by an ``import`` in ``path``, relative ones resolved."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    package = path.relative_to(PROJECT_ROOT).with_suffix("").parts
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                base = ".".join(package[: len(package) - node.level] + (base,)).strip(".")
            names.add(base)
            names.update(f"{base}.{alias.name}" for alias in node.names)
    return names

#: Runs one measurement under an audit hook that refuses every non-local
#: connection and keeps a note of each attempt. ``file://`` is local by
#: definition; every other scheme, and every non-loopback socket address, is
#: an attempt to leave the machine. The report is printed as JSON on the last
#: line of standard output so that whatever the measurement itself prints is
#: harmless.
_DRIVER = r'''
import io, json, os, sys, contextlib

LOOPBACK = {"localhost", "127.0.0.1", "::1", "0.0.0.0", ""}
attempts = []

def _remote_host(host):
    return isinstance(host, str) and host not in LOOPBACK

def hook(event, args):
    if event == "urllib.Request":
        url = args[0]
        if isinstance(url, str) and not url.lower().startswith("file:"):
            attempts.append(url)
            raise OSError("non-local request refused by the audit hook: %r" % (url,))
    elif event in {"socket.connect", "socket.sendto"}:
        address = args[1]
        host = address[0] if isinstance(address, tuple) else address
        if _remote_host(host):
            attempts.append("socket.connect %r" % (address,))
            raise OSError("remote connection refused by the audit hook")
    elif event == "socket.getaddrinfo" and _remote_host(args[0]):
        attempts.append("socket.getaddrinfo %r" % (args[0],))
        raise OSError("remote name lookup refused by the audit hook")

sys.addaudithook(hook)

root = sys.argv[1]
mode = sys.argv[2]
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "tests"))
os.chdir(root)

status = "ok"
detail = ""
noise = io.StringIO()
try:
    with contextlib.redirect_stdout(noise), contextlib.redirect_stderr(noise):
        if mode == "schema":
            # The production entry into IfcTester: parsing a rule document is
            # what forces ``ids.xsd`` to be loaded.
            from pathlib import Path
            from epc_control_tower.checkers.ids_checker import load_ids_rule_source
            load_ids_rule_source(Path(root, "ids", "epc-delivery_v2.2.ids"))
        elif mode == "check":
            from epc_control_tower.cli import main
            code = main(["check"])
            assert code == 0, code
        elif mode == "run":
            import dataclasses
            from epc_control_tower.determinism import sha256_file
            from epc_control_tower.pipeline import execute
            from helpers import shipped_run_config, writable_test_directory
            with writable_test_directory("egress") as scratch:
                execute(
                    dataclasses.replace(
                        shipped_run_config(),
                        processed_data_dir=scratch / "processed",
                        reports_dir=scratch / "reports",
                    )
                )
                detail = json.dumps(
                    {
                        p.relative_to(scratch).as_posix(): sha256_file(p)
                        for p in sorted(scratch.rglob("*"))
                        if p.is_file()
                    }
                )
        elif mode == "generate":
            # The other modes only decode. Writing a rule document encodes
            # through the same schema, which is a different route into it.
            import runpy
            import tempfile
            from pathlib import Path as _Path
            with tempfile.TemporaryDirectory() as tmp:
                out = _Path(tmp, "regenerated.ids")
                sys.argv = ["generate_ids.py", "--output", str(out)]
                runpy.run_path(
                    os.path.join(root, "src", "generate_ids.py"),
                    run_name="__main__",
                )
                detail = out.read_bytes().hex()
        elif mode.startswith("tests:"):
            import importlib
            import unittest
            loader = unittest.TestLoader()
            suite = unittest.TestSuite(
                loader.loadTestsFromModule(importlib.import_module(name))
                for name in mode[len("tests:") :].split(",")
            )
            result = unittest.TextTestRunner(stream=noise, verbosity=0).run(suite)
            assert result.wasSuccessful(), [
                f"{t}: {e}" for t, e in result.errors + result.failures
            ]
        else:
            raise AssertionError("unknown mode %r" % (mode,))
except BaseException as error:  # reported, not raised: the count is the claim
    status = "%s: %s" % (type(error).__name__, error)

sys.__stdout__.write(
    json.dumps({"attempts": attempts, "status": status, "detail": detail})
)
'''


def _measure(mode: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-c", _DRIVER, str(PROJECT_ROOT), mode],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout.splitlines()[-1])


class NoEgressFromTheValidationPathTests(unittest.TestCase):
    """Zero attempts — not "attempts that were harmlessly blocked"."""

    def assertNoAttempt(self, observed: dict) -> None:
        self.assertEqual(
            observed["attempts"],
            [],
            "the validation path tried to leave the machine; a truncated "
            "response on any of these is an IncompleteRead, not a fallback",
        )
        self.assertEqual(observed["status"], "ok")

    def test_loading_the_ids_schema_attempts_nothing(self):
        self.assertNoAttempt(_measure("schema"))

    def test_check_attempts_nothing(self):
        self.assertNoAttempt(_measure("check"))

    def test_run_attempts_nothing_and_still_writes_the_published_bytes(self):
        observed = _measure("run")
        self.assertNoAttempt(observed)
        self.assertTrue(json.loads(observed["detail"]), "the run wrote nothing")

    def test_writing_a_rule_document_attempts_nothing_and_writes_the_same_bytes(self):
        observed = _measure("generate")
        self.assertNoAttempt(observed)
        self.assertEqual(
            bytes.fromhex(observed["detail"]),
            (PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids").read_bytes(),
            "the published rule document is a SHA-256 over these bytes",
        )

    def test_the_tests_that_reach_ifctester_attempt_nothing(self):
        """Including the observed flake.

        ``test_bcf_exporter`` is where the truncated response was seen and
        written off as environmental. The other two reach IfcTester directly
        rather than through the package — deliberately, since they compare our
        behaviour against IfcTester's own — so they are the modules a fix
        confined to the pipeline would have missed.
        """

        self.assertNoAttempt(
            _measure(
                "tests:test_bcf_exporter,test_ids_checker,test_ids_conformance"
            )
        )

    def test_no_module_reaches_ifctester_without_the_local_loader(self):
        """The structural half: the measurements above only cover what they run.

        A new module that imports IfcTester and forgets
        ``epc_control_tower.ids_schema`` silently restores the fetch. Test
        modules are exempt because ``tests/conftest.py`` installs the loader
        for all of them.
        """

        offenders = []
        for path in sorted(
            list((PROJECT_ROOT / "epc_control_tower").rglob("*.py"))
            + list((PROJECT_ROOT / "src").rglob("*.py"))
        ):
            if path.name == "ids_schema.py":
                continue
            names = _imported_names(path)
            if any(n == "ifctester" or n.startswith("ifctester.") for n in names):
                if not any(n.endswith("ids_schema") for n in names):
                    offenders.append(path.relative_to(PROJECT_ROOT).as_posix())
        self.assertEqual(offenders, [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
