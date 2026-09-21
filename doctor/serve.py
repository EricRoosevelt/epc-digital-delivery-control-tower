"""Serve the BIM Doctor D1 preview on this machine only.

Run from the repository root::

    python doctor/serve.py            # http://127.0.0.1:8765/

Nothing here evaluates anything. The server hands the browser the envelopes the
internal adapter (A1) returns — unchanged — and the static files that lay them
out. It writes no file, reads no clock, and binds to the loopback interface,
because this is an internal preview and not a service.

The one seam is :class:`Source`: which runs a mode offers, and the envelope for
one of them. :func:`adapter_source` is the only implementation that ships, and
it is a thin call into A1. There is deliberately no bundled sample data to fall
back on: a preview whose adapter is missing says so instead of showing
something that looks like a result.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Protocol
from urllib.parse import parse_qs, urlsplit

STATIC = Path(__file__).resolve().parent / "static"
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

#: The two experiences. Anything else is refused before a source is asked.
MODES = ("fixture", "real")

#: Extensions served, with explicit types. Not ``mimetypes``: on Windows it reads
#: the registry and can hand ES modules to the browser as ``text/plain``.
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


class Source(Protocol):
    def runs(self, mode: str) -> list[dict[str, str]]:
        """``[{"run_id", "label"}]`` the adapter offers for ``mode``, in its order."""

    def envelope(self, mode: str, run_id: str) -> dict[str, object]:
        """The adapter's envelope for one run, exactly as the adapter returned it."""


class SourceUnavailable(RuntimeError):
    """The adapter could not be reached. Shown as such, never as a result."""


class AdapterSource:
    """``internal.doctor_adapter``, asked for its scenarios and their envelopes.

    ``scenario_index()`` runs nothing and declares each scenario's mode, which is
    what lets the two experiences be listed separately before either has been
    run. The declaration is not trusted to *be* the envelope's mode: the browser
    checks the envelope's own ``mode`` against the chosen one and refuses to
    render a mismatch, and the adapter's own tests hold the two equal.
    """

    def __init__(self, adapter) -> None:
        self._adapter = adapter

    def runs(self, mode: str) -> list[dict[str, str]]:
        return [
            {"run_id": scenario["name"]}
            for scenario in self._adapter.scenario_index()
            if scenario["mode"] == mode
        ]

    def envelope(self, mode: str, run_id: str) -> dict[str, object]:
        declared = {item["name"]: item["mode"] for item in self._adapter.scenario_index()}
        if declared.get(run_id) != mode:
            raise KeyError(f"{run_id!r} is not a {mode!r} scenario")
        return self._adapter.scenario_envelope(run_id)


def adapter_source() -> Source:
    """The internal adapter (A1), imported only when a request needs it."""

    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    try:
        from internal import doctor_adapter
    except ImportError as missing:
        raise SourceUnavailable(
            "The internal adapter (internal.doctor_adapter) could not be imported, so "
            f"there is nothing to show: {missing}. No sample data is bundled in its place."
        ) from missing
    return AdapterSource(doctor_adapter)


def _json(handler: BaseHTTPRequestHandler, status: HTTPStatus, body: object) -> None:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


def make_handler(source_factory: Callable[[], Source]) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "epc-doctor-preview"

        def log_message(self, format: str, *args: object) -> None:
            return None

        def do_GET(self) -> None:
            parts = urlsplit(self.path)
            if parts.path.startswith("/api/"):
                self._api(parts.path, parse_qs(parts.query))
                return
            self._static(parts.path)

        def _api(self, path: str, query: dict[str, list[str]]) -> None:
            mode = (query.get("mode") or [""])[0]
            if mode not in MODES:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": f"unknown mode {mode!r}"})
                return
            try:
                source = source_factory()
                if path == "/api/runs":
                    _json(self, HTTPStatus.OK, {"mode": mode, "runs": source.runs(mode)})
                    return
                if path == "/api/envelope":
                    run_id = (query.get("run") or [""])[0]
                    _json(self, HTTPStatus.OK, source.envelope(mode, run_id))
                    return
            except SourceUnavailable as unavailable:
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(unavailable)})
                return
            except Exception as failure:  # reported, never swallowed
                _json(
                    self,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"{type(failure).__name__}: {failure}"},
                )
                return
            _json(self, HTTPStatus.NOT_FOUND, {"error": f"no such endpoint {path!r}"})

        def _static(self, path: str) -> None:
            name = "index.html" if path in ("", "/") else path.lstrip("/")
            target = (STATIC / name).resolve()
            if (
                STATIC not in target.parents
                or not target.is_file()
                or target.suffix not in CONTENT_TYPES
            ):
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            payload = target.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", CONTENT_TYPES[target.suffix])
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8765)
    arguments = parser.parse_args(argv)
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", arguments.port), make_handler(adapter_source))
    print(f"BIM Doctor preview: http://127.0.0.1:{arguments.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
