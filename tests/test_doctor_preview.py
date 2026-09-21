"""The Doctor preview server passes envelopes through and decides nothing.

What is pinned here is the server's side of the seam, not the screens: an
envelope reaches the browser exactly as the adapter returned it, a missing
adapter is reported as unavailable rather than replaced by sample data, and the
static tree carries no result of its own. Rendering is reviewed in a browser.
"""

from __future__ import annotations

import importlib.util
import json
import re
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from helpers import PROJECT_ROOT

_SPEC = importlib.util.spec_from_file_location(
    "doctor_serve", PROJECT_ROOT / "doctor" / "serve.py"
)
serve = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(serve)

STATIC = PROJECT_ROOT / "doctor" / "static"


class _Opaque:
    """A source whose payload is deliberately not envelope-shaped.

    The server must not care what an envelope contains, so the test proves the
    pass-through with a value no screen could render.
    """

    payload = {"opaque": ["kept", 1, None, {"nested": "as returned"}]}

    def runs(self, mode):
        return [{"run_id": f"{mode}-only", "label": "opaque"}]

    def envelope(self, mode, run_id):
        return {"mode_seen": mode, "run_seen": run_id, **self.payload}


class _Server:
    def __init__(self, factory):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(factory))
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def __exit__(self, *exception):
        self.httpd.shutdown()
        self.httpd.server_close()


def _get(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.status, response.headers.get("Content-Type"), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type"), error.read()


class PassThroughTests(unittest.TestCase):
    def test_the_envelope_is_returned_as_the_source_returned_it(self):
        with _Server(_Opaque) as base:
            status, content_type, body = _get(f"{base}/api/envelope?mode=real&run=x")
        self.assertEqual(status, 200)
        self.assertTrue(content_type.startswith("application/json"))
        self.assertEqual(
            json.loads(body), {"mode_seen": "real", "run_seen": "x", **_Opaque.payload}
        )

    def test_runs_are_listed_per_mode(self):
        with _Server(_Opaque) as base:
            status, _, body = _get(f"{base}/api/runs?mode=fixture")
        self.assertEqual(status, 200)
        self.assertEqual(
            json.loads(body)["runs"], [{"run_id": "fixture-only", "label": "opaque"}]
        )

    def test_an_unknown_mode_is_refused_before_the_source_is_asked(self):
        asked = []

        def factory():
            asked.append(True)
            return _Opaque()

        with _Server(factory) as base:
            status, _, _ = _get(f"{base}/api/envelope?mode=demo&run=x")
        self.assertEqual(status, 400)
        self.assertEqual(asked, [])

    def test_a_missing_adapter_is_reported_as_unavailable_not_replaced(self):
        """No bundled sample data stands in for the adapter."""

        def unavailable():
            raise serve.SourceUnavailable("the adapter is not here")

        with _Server(unavailable) as base:
            status, _, body = _get(f"{base}/api/runs?mode=fixture")
        self.assertEqual(status, 503)
        self.assertIn("the adapter is not here", json.loads(body)["error"])

    def test_the_shipped_source_serves_the_adapter_scenarios_by_declared_mode(self):
        with _Server(serve.adapter_source) as base:
            fixture = json.loads(_get(f"{base}/api/runs?mode=fixture")[2])["runs"]
            real = json.loads(_get(f"{base}/api/runs?mode=real")[2])["runs"]
        self.assertEqual(
            [run["run_id"] for run in fixture],
            ["member-evidence", "pair-verdicts", "recheck-comparison"],
        )
        self.assertEqual([run["run_id"] for run in real], ["real-refusal"])

    def test_a_scenario_is_never_served_under_the_other_mode(self):
        """The declared mode gates the request before the entry is called."""

        with _Server(serve.adapter_source) as base:
            status, _, _ = _get(f"{base}/api/envelope?mode=fixture&run=real-refusal")
        self.assertEqual(status, 500)

    def test_the_adapters_envelope_reaches_the_browser_unchanged(self):
        from internal.doctor_adapter import scenario_envelope

        with _Server(serve.adapter_source) as base:
            served = json.loads(_get(f"{base}/api/envelope?mode=real&run=real-refusal")[2])
        self.assertEqual(served, scenario_envelope("real-refusal"))
        self.assertEqual(served["mode"], "real")
        self.assertEqual(served["outcome"], "refusal")

    def test_a_source_failure_is_reported_not_swallowed(self):
        class Failing(_Opaque):
            def envelope(self, mode, run_id):
                raise ValueError("adapter broke")

        with _Server(Failing) as base:
            status, _, body = _get(f"{base}/api/envelope?mode=fixture&run=x")
        self.assertEqual(status, 500)
        self.assertIn("adapter broke", json.loads(body)["error"])


class StaticTreeTests(unittest.TestCase):
    def test_modules_are_served_as_javascript(self):
        with _Server(_Opaque) as base:
            for name, expected in (
                ("/", "text/html"),
                ("/app.js", "text/javascript"),
                ("/doctor.css", "text/css"),
            ):
                with self.subTest(path=name):
                    status, content_type, _ = _get(base + name)
                    self.assertEqual(status, 200)
                    self.assertTrue(content_type.startswith(expected))

    def test_nothing_outside_the_static_tree_is_served(self):
        with _Server(_Opaque) as base:
            for path in ("/../serve.py", "/%2e%2e/serve.py", "/serve.py", "/missing.js"):
                with self.subTest(path=path):
                    self.assertEqual(_get(base + path)[0], 404)

    def test_the_static_tree_carries_no_result_of_its_own(self):
        """No bundled record, digest, element key or refusal text to fall back on."""

        self.assertEqual(
            sorted(path.suffix for path in STATIC.iterdir()),
            [".css", ".html", ".js", ".js", ".js", ".js"],
        )
        for path in sorted(STATIC.iterdir()):
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotRegex(text, r"[0-9a-f]{64}")
                self.assertNotRegex(text, r"\b(hvac|architecture)::")
                self.assertNotIn("innerHTML", text)

    def test_the_limitations_table_is_keyed_on_mode_and_code_only(self):
        source = (STATIC / "screens.js").read_text(encoding="utf-8")
        refusal = source[source.index("function refusal(") :]
        self.assertIn(
            'envelope.mode === "real" && envelope.refusal.code === BASELINE_REFUSAL_CODE',
            refusal,
        )
        self.assertNotIn("project_id", refusal)
        self.assertIn("所提交的请求上下文尚未随拒绝返回", refusal)
        self.assertIsNone(
            re.search(r"refusal\.text\.(split|slice|replace|match|substring)", source)
        )

    def test_no_screen_joins_a_recheck_disposition_to_the_current_partition(self):
        """Where the Framework records no correspondence, the page constructs none.

        A ``pairing-no-longer-derived`` member has no current subscope because
        the pair no longer exists. Looking its ``refined_from`` element up in the
        current partition, or annotating a workbench row from the successor,
        would be the page inventing the correspondence the record declines.
        """

        source = (STATIC / "screens.js").read_text(encoding="utf-8")
        recheck = source[source.index("function recheck(") : source.index("function refusal(")]
        for name in ("successor.subscopes", ".dispositions"):
            with self.subTest(read=name):
                self.assertGreater(recheck.count(name), 0)
                self.assertEqual(source.count(name), recheck.count(name))
        self.assertNotIn("refined_from", recheck)
        self.assertNotRegex(recheck, r"document\.activities")

    def test_an_omitted_key_is_words_and_never_a_value_shaped_blank(self):
        """Optional keys are read through the helper that names both absences.

        The record omits keys rather than carrying empty ones — three of eight
        subscopes carry no ``route``, ``assignment`` or ``resolution_kind`` at
        all — and an omitted key rendered as ``null``, ``""``, ``0``, ``false``
        or a dash would read as a recorded value. A carried empty string is a
        different fact and keeps its own wording.
        """

        source = (STATIC / "screens.js").read_text(encoding="utf-8")
        optional = (
            "resolution_kind",
            "route",
            "assignment",
            "refined_from",
            "absence",
            "binding",
            "cause",
            "current_ordinals",
            "sealed_content_digest",
            "current_content_digest",
            "context_citations",
            "named_outcome",
            "prior_resolution_kind",
        )
        guarded = re.findall(r'(?:field|carries)\(\s*[\w.]+,\s*"(\w+)"', source)
        for key in optional:
            with self.subTest(key=key):
                self.assertIn(key, guarded)
                # Only ever read by name; a dotted read would skip the helper.
                # The three exceptions are counts and spreads taken inside a
                # carries() guard on the same key.
                dotted = len(re.findall(rf"[.]{key}", source))
                counted = ("refined_from", "context_citations", "current_ordinals")
                self.assertLessEqual(dotted, 1 if key in counted else 0)
        rendered = [
            line for line in source.splitlines() if not line.lstrip().startswith("//")
        ]
        rendered = "\n".join(rendered)
        for fallback in ('|| ""', '?? ""', "|| 0", "|| []", '"—', "'—"):
            with self.subTest(fallback=fallback):
                self.assertNotIn(fallback, rendered)

    def test_every_citation_carries_its_own_provenance_label(self):
        """Per citation, not per page, and keyed only on the envelope's mode.

        One fixture record mixes the two: its finding keys are a real validation
        run's output and its determinations are the fixture's. A page-level
        banner would understate the findings or overstate the determinations,
        so the label sits beside each citation, with the full sentence in a
        legend on the same page rather than behind a hover.
        """

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        for kind in ("finding", "determination", "policy"):
            with self.subTest(kind=kind):
                self.assertIn(f"  {kind}: {{", vocabulary)
                self.assertIn(f'provenance(state, "{kind}")', screens)
        # The tag is emitted beside citations in the workbench, the evidence
        # path, the roles table and the carry-over table.
        self.assertGreaterEqual(screens.count("provenance(state,"), 5)
        provenance = screens[screens.index("function provenance(") :]
        provenance = provenance[: provenance.index("function provenanceLegend(")]
        self.assertIn('state.envelope.mode !== "fixture"', provenance)
        for forbidden in ("record", "refusal", "project_id", "code"):
            with self.subTest(read=forbidden):
                self.assertNotIn(forbidden, provenance)
        self.assertNotIn("title:", (STATIC / "dom.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
