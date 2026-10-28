"""Run the BIM Doctor workspace and project library on this machine only.

Run from the repository root::

    python doctor/serve.py            # http://127.0.0.1:8765/
    python doctor/serve.py --workspace <dir> [--prior <dir>]
    python doctor/serve.py --checks-dir <dir>

The established handover routes project the internal adapter's envelopes. The
review API checks uploaded IFC, extracts actual geometry and offers local rule
guidance or explicitly requested AI advice. The project API persists immutable
reports, geometry snapshots and separate follow-up records in an external SQLite
library. These runtime records may contain timestamps; canonical published
pipeline artifacts are not rewritten. The application binds to loopback only.

The established local check (``/api/local/…``) receives
a model file and the choice of rule set and disciplines. What arrives is handed
to :class:`internal.doctor_adapter.local_check.LocalChecks`, which keeps it — and
every check run on it — under a checks directory outside any checkout, named at
start-up and reported in every answer. Because a page on any other site can
also make a browser send a request to this machine, every ``/api/`` request must
name this server's own loopback address as its ``Host``, and a request that
sends anything must carry a JSON or binary body (which a cross-site page cannot
send without asking first, and nothing here answers that question) and, if it
says where it comes from, come from this server's own origin.

The established handover seam is :class:`Source`: which runs a mode offers, and
the envelope for one of them. :func:`adapter_source` calls A1. The review workspace
has a separate explicit public-example action; missing adapters or failed model
loads do not silently substitute a sample result.
"""

from __future__ import annotations

import argparse
import functools
import json
import logging
import select
import socket
import sys
import threading
import time
from collections.abc import Callable
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Protocol
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

STATIC = Path(__file__).resolve().parent / "static"
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from doctor import enterprise_http  # noqa: E402

#: The experiences. Anything else is refused before a source is asked.
#: ``workspace`` offers a run only when the server was started with one.
MODES = ("fixture", "real", "workspace")

#: The one run the workspace mode offers: the workspace named at start-up.
WORKSPACE_RUN = "workspace"

#: The ``Host`` names a request may use: this server's own loopback addresses.
LOOPBACK_NAMES = ("127.0.0.1", "localhost", "[::1]")

#: The body type each endpoint that is sent something takes. Neither can be
#: sent cross-site without the browser asking first, and nothing here answers.
POSTED_TYPES = {
    **enterprise_http.POST_TYPES,
    "/api/review/imports": "application/octet-stream",
    "/api/review/imports/cancel": "application/json",
    "/api/review/advice": "application/json",
    "/api/projects": "application/json",
    "/api/projects/revisions": "application/json",
    "/api/projects/followup": "application/json",
    "/api/local/models": "application/octet-stream",
    "/api/review/models": "application/octet-stream",
    "/api/local/plan": "application/json",
    "/api/local/checks": "application/json",
}

#: A plan or check request is a few model choices, not a model.
MAX_REQUEST_BYTES = 1 << 20

#: How much of a refused upload is read and thrown away before the answer.
#:
#: A browser still sending when the server closes the connection reports the
#: connection as dropped and never reads the refusal: measured with a
#: 179,727-byte model against a 100,000-byte limit, Chrome and Edge both got
#: ``net::ERR_CONNECTION_ABORTED``. Reading the rest first lets the refusal
#: through. Past this bound the connection is closed unread, as before; the page
#: itself does not send a file over the limit.
REFUSED_UPLOAD_DRAIN_BYTES = 64 << 20


class _Counted:
    """A request body that counts what has been read from it."""

    def __init__(self, stream) -> None:
        self.stream = stream
        self.consumed = 0

    def read(self, size: int = -1) -> bytes:
        block = self.stream.read(size)
        self.consumed += len(block)
        return block


def _drain(stream, remaining: int, bound: int = REFUSED_UPLOAD_DRAIN_BYTES) -> int:
    """Read and discard what is left of a body, if no more than ``bound``."""

    if remaining <= 0 or remaining > bound:
        return 0
    drained = 0
    while drained < remaining:
        block = stream.read(min(1 << 16, remaining - drained))
        if not block:
            break
        drained += len(block)
    return drained

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

    def __init__(
        self, adapter, workspace: Path | None = None, prior: Path | None = None
    ) -> None:
        self._adapter = adapter
        self._workspace = workspace
        self._prior = prior

    def runs(self, mode: str) -> list[dict[str, str]]:
        if mode == "workspace":
            # Named when the server was started, or not offered at all.
            # Nothing is looked for.
            return [] if self._workspace is None else [{"run_id": WORKSPACE_RUN}]
        return [
            {"run_id": scenario["name"]}
            for scenario in self._adapter.scenario_index()
            if scenario["mode"] == mode
        ]

    def envelope(self, mode: str, run_id: str) -> dict[str, object]:
        # Asked again rather than reused from ``runs``: that call answers "what
        # may this experience offer", this one answers "is this run one of them".
        # Folding them together would let a listing certify itself.
        if mode == "workspace":
            if self._workspace is None or run_id != WORKSPACE_RUN:
                raise KeyError(f"{run_id!r} is not a {mode!r} run of this server")
            return self._adapter.workspace_envelope(self._workspace, self._prior)
        declared = {item["name"]: item["mode"] for item in self._adapter.scenario_index()}
        if declared.get(run_id) != mode:
            raise KeyError(f"{run_id!r} is not a {mode!r} scenario")
        return self._adapter.scenario_envelope(run_id)


def adapter_source(workspace: Path | None = None, prior: Path | None = None) -> Source:
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
    return AdapterSource(doctor_adapter, workspace, prior)


def local_checks(checks_dir: Path | None = None, max_model_bytes: int | None = None):
    """The adapter's local checks, kept in ``checks_dir`` or where it says by default."""

    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    from internal.doctor_adapter.local_check import LocalChecks, resolve_checks_root

    root = checks_dir if checks_dir is not None else resolve_checks_root(REPOSITORY_ROOT)
    options = {} if max_model_bytes is None else {"max_model_bytes": max_model_bytes}
    return LocalChecks(root, repository_root=REPOSITORY_ROOT, **options)


def _payload(handler, status, payload, content_type="application/json; charset=utf-8"):
    """Write immutable bytes once; a disconnected peer cannot receive a second error."""
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Request-ID", getattr(handler, "request_id", ""))
    started = getattr(handler, "request_started", time.monotonic())
    handler.send_header("Server-Timing", f"review;dur={(time.monotonic()-started)*1000:.1f}")
    try:
        handler.end_headers()
        handler.wfile.write(payload)
    except (ConnectionError, OSError):
        logging.getLogger(__name__).warning(
            "Response disconnected request_id=%s endpoint=%s bytes=%s",
            getattr(handler, "request_id", ""), urlsplit(handler.path).path, len(payload),
        )


def _json(handler: BaseHTTPRequestHandler, status: HTTPStatus, body: object) -> None:
    _payload(handler, status, json.dumps(body, ensure_ascii=False, allow_nan=False).encode())


def configure_import_loaders(manager, library=None):
    """Saved SQLite evidence wins; recent unsaved imports have bounded disk backing."""
    def load(identity, geometry=False):
        if library is not None:
            try:
                loader = library.restore_geometry if geometry else library.restore_report
                return loader(identity)
            except KeyError:
                pass
        return (manager.geometry_payload if geometry else manager.report_payload)(identity)

    manager.reviews.set_loaders(
        report_loader=lambda identity: load(identity),
        geometry_loader=lambda identity: load(identity, True),
    )


def make_handler(
    source_factory: Callable[[], Source],
    local_factory: Callable[[], object] | None = None,
    review_factory: Callable[[], object] | None = None,
    advice_factory: Callable[[], object] | None = None,
    project_factory: Callable[[], object] | None = None,
    import_factory: Callable[[], object] | None = None,
    enterprise_factory: Callable[[], object] | None = None,
) -> type[BaseHTTPRequestHandler]:
    """The request handler; ``local_factory`` enables the local check endpoints."""

    import_holder = {}
    import_lock = threading.Lock()

    def enterprise():
        if enterprise_factory is not None:
            return enterprise_factory()
        with import_lock:
            if "enterprise" not in import_holder:
                from doctor.enterprise_service import EnterpriseService
                from internal.doctor_adapter.enterprise_library import EnterpriseLibrary

                if project_factory is None or review_factory is None:
                    raise SourceUnavailable("This server has no enterprise project library.")
                import_holder["enterprise"] = EnterpriseService(
                    EnterpriseLibrary(project_factory()), review_factory(),
                )
            return import_holder["enterprise"]

    def imports():
        if import_factory is not None:
            return import_factory()
        if review_factory is None:
            raise SourceUnavailable("This server was started without IFC review.")
        with import_lock:
            if "jobs" not in import_holder:
                from doctor.import_jobs import ImportJobs

                manager = ImportJobs(review_factory())
                library = project_factory() if project_factory else None
                configure_import_loaders(manager, library)
                import_holder["jobs"] = manager
            return import_holder["jobs"]

    class Handler(BaseHTTPRequestHandler):
        server_version = "epc-doctor-preview"

        def log_message(self, format: str, *args: object) -> None:
            return None

        def _own_host(self) -> str | None:
            """This request's ``Host`` if it names this server on loopback, else ``None``."""

            host = self.headers.get("Host", "")
            port = self.server.server_address[1]
            allowed = {f"{name}:{port}" for name in LOOPBACK_NAMES}
            return host if host in allowed else None

        def do_GET(self) -> None:
            self.request_id, self.request_started = uuid4().hex, time.monotonic()
            parts = urlsplit(self.path)
            if parts.path.startswith("/api/"):
                if self._own_host() is None:
                    _json(self, HTTPStatus.FORBIDDEN, {"error": "not this server's address"})
                    return
                if parts.path == "/api/local" or parts.path.startswith("/api/local/"):
                    self._local_get(parts.path, parse_qs(parts.query))
                    return
                if parts.path == "/api/projects" or parts.path.startswith("/api/projects/"):
                    self._project_get(parts.path, parse_qs(parts.query))
                    return
                if parts.path.startswith("/api/review/"):
                    self._review_get(parts.path, parse_qs(parts.query))
                    return
                self._api(parts.path, parse_qs(parts.query))
                return
            self._static(parts.path)

        def do_POST(self) -> None:
            self.request_id, self.request_started = uuid4().hex, time.monotonic()
            parts = urlsplit(self.path)
            # Whatever is refused here, its body is not read, so the connection
            # cannot be reused.
            host = self._own_host()
            if host is None:
                self.close_connection = True
                _json(self, HTTPStatus.FORBIDDEN, {"error": "not this server's address"})
                return
            origin = self.headers.get("Origin")
            if origin is not None and origin != f"http://{host}":
                self.close_connection = True
                _json(self, HTTPStatus.FORBIDDEN, {"error": f"not accepted from {origin!r}"})
                return
            wanted = POSTED_TYPES.get(parts.path)
            if wanted is None:
                self.close_connection = True
                _json(self, HTTPStatus.NOT_FOUND, {"error": f"no such endpoint {parts.path!r}"})
                return
            given = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if given != wanted:
                self.close_connection = True
                _json(
                    self,
                    HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                    {"error": f"{parts.path} takes {wanted}, not {given or 'nothing'}"},
                )
                return
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                self.close_connection = True
                _json(self, HTTPStatus.LENGTH_REQUIRED, {"error": "Content-Length is required"})
                return
            if length < 0:
                self.close_connection = True
                _json(self, HTTPStatus.BAD_REQUEST, {"error": "Negative Content-Length"})
                return
            if parts.path in {"/api/review/models", "/api/review/imports"}:
                self._review_post(parse_qs(parts.query), length,
                                  asynchronous=parts.path == "/api/review/imports")
                return
            if parts.path == "/api/review/imports/cancel":
                self._cancel_import(length)
                return
            if parts.path == "/api/review/advice":
                self._advice_post(length)
                return
            if parts.path in enterprise_http.POST_TYPES:
                try:
                    enterprise_http.post(self, enterprise(), parts.path, length, _json)
                except KeyError as error:
                    _json(self, 404, {"error": str(error)})
                except (ValueError, TypeError) as error:
                    _json(self, 400, {"error": str(error)})
                except SourceUnavailable as error:
                    _json(self, 503, {"error": str(error)})
                except Exception as error:
                    logging.getLogger(__name__).exception(
                        "Enterprise request %s", self.request_id,
                    )
                    _json(self, 500, {"error": f"{type(error).__name__}: {error}"})
                return
            if parts.path == "/api/projects" or parts.path.startswith("/api/projects/"):
                self._project_post(parts.path, length)
                return
            self._local_post(parts.path, parse_qs(parts.query), length)

        def _projects(self):
            if project_factory is None:
                raise SourceUnavailable("This server was started without a project library.")
            return project_factory()

        def _project_get(self, path: str, query: dict[str, list[str]]) -> None:
            try:
                if path in enterprise_http.GET_PATHS:
                    enterprise_http.get(self, enterprise(), path, query, _json, _payload)
                    return
                library = self._projects()
                if path == "/api/projects":
                    answer = {"projects": library.projects()}
                elif path == "/api/projects/detail":
                    answer = library.detail((query.get("project") or [""])[0])
                elif path == "/api/projects/revision":
                    answer = library.revision((query.get("revision") or [""])[0])
                elif path == "/api/projects/compare":
                    answer = library.compare((query.get("before") or [""])[0],
                                             (query.get("after") or [""])[0])
                elif path == "/api/projects/brief":
                    from doctor.project_brief import project_brief

                    body = project_brief(
                        library, (query.get("project") or [""])[0],
                        (query.get("language") or ["en"])[0],
                    ).encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                    self.send_header("Content-Disposition",
                                     'attachment; filename="bim-doctor-project-brief.md"')
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(body)
                    return
                else:
                    _json(self, HTTPStatus.NOT_FOUND, {"error": "Unknown project endpoint."})
                    return
                _json(self, HTTPStatus.OK, answer)
            except KeyError as error:
                _json(self, HTTPStatus.NOT_FOUND, {"error": str(error)})
            except ValueError as error:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except SourceUnavailable as error:
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            except Exception as error:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR,
                      {"error": f"{type(error).__name__}: {error}"})

        def _project_post(self, path: str, length: int) -> None:
            if length > MAX_REQUEST_BYTES:
                self.close_connection = True
                _json(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                      {"error": "Project request is too large."})
                return
            try:
                request = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(request, dict):
                    raise ValueError("Project request must be a JSON object.")
                library = self._projects()
                if path == "/api/projects":
                    answer = library.create_project(request.get("name"))
                elif path == "/api/projects/revisions":
                    retain_source = request.get("retain_source", False)
                    if type(retain_source) is not bool:
                        raise ValueError("retain_source must be a boolean.")
                    source_body = None
                    if retain_source and not library.source_available(request.get("review_id")):
                        try:
                            source_body = imports().source_payload(request.get("review_id"))
                        except KeyError:
                            # The atomic save reports expired source without a ghost revision.
                            pass
                    answer = library.save_revision(
                        request.get("project_id"), request.get("review_id"),
                        model_id=request.get("model_id"), model_name=request.get("model_name"),
                        label=request.get("label", ""),
                        retain_source=retain_source, source_body=source_body,
                    )
                elif path == "/api/projects/followup":
                    answer = library.update_followup(
                        request.get("revision_id"), request.get("finding_id"),
                        status=request.get("status", "open"),
                        owner=request.get("owner", ""), note=request.get("note", ""),
                    )
                else:
                    _json(self, HTTPStatus.NOT_FOUND, {"error": "Unknown project endpoint."})
                    return
                _json(self, HTTPStatus.OK, answer)
            except KeyError as error:
                _json(self, HTTPStatus.NOT_FOUND, {"error": str(error)})
            except (ValueError, UnicodeDecodeError) as error:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except SourceUnavailable as error:
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            except Exception as error:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR,
                      {"error": f"{type(error).__name__}: {error}"})

        def _review(self):
            if review_factory is None:
                raise SourceUnavailable("This server was started without IFC review.")
            return review_factory()

        def _review_get(self, path: str, query: dict[str, list[str]]) -> None:
            try:
                if path == "/api/review/imports":
                    identity = (query.get("job") or [None])[0]
                    answer = imports().get(identity) if identity else imports().snapshot()
                    _json(self, HTTPStatus.OK, answer)
                    return
                if path == "/api/review/cache":
                    _json(self, HTTPStatus.OK, self._review().stats())
                    return
                if path == "/api/review/ai":
                    _json(self, HTTPStatus.OK, self._advice().describe())
                    return
                store = self._review()
                if path == "/api/review/demo":
                    answer = store.demo()
                elif path == "/api/review/report":
                    answer = store.get((query.get("review") or [""])[0])
                elif path == "/api/review/source-status":
                    identity = (query.get("review") or [""])[0]
                    report = store.get(identity)
                    single = (report.get("source", {}).get("kind") == "upload"
                              and len(report.get("models", [])) == 1)
                    retained = (single and project_factory is not None
                                and self._projects().source_available(identity))
                    temporary = single and not retained and imports().source_available(identity)
                    answer = {"review_id": identity, "source_available": bool(retained),
                              "retainable": bool(retained or temporary),
                              "reason": "federated_demo" if not single else "retained"
                              if retained else "temporary" if temporary else "expired"}
                elif path == "/api/review/geometry":
                    payload = store.geometry_payload((query.get("review") or [""])[0])
                    _payload(self, HTTPStatus.OK, payload)
                    return
                else:
                    _json(self, HTTPStatus.NOT_FOUND, {"error": "Unknown review endpoint"})
                    return
                _json(self, HTTPStatus.OK, answer)
            except KeyError as error:
                _json(self, HTTPStatus.NOT_FOUND,
                      {"error": str(error) or "Review or import task not found."})
            except SourceUnavailable as error:
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            except Exception as error:
                logging.getLogger(__name__).exception(
                    "Review request failed request_id=%s endpoint=%s", self.request_id, path
                )
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR,
                      {"error": f"{type(error).__name__}: {error}",
                       "diagnostic": {"request_id": self.request_id,
                                      "phase": "geometry_load" if path.endswith("geometry")
                                      else "review_load"}})

        def _advice(self):
            if advice_factory is None:
                raise SourceUnavailable("This server was started without review advice.")
            return advice_factory()

        def _advice_post(self, length: int) -> None:
            from doctor.advice import AdviceUnavailable

            if length > MAX_REQUEST_BYTES:
                self.close_connection = True
                _json(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                      {"error": "Advice request is too large."})
                return
            try:
                request = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(request, dict):
                    raise ValueError("Advice request must be a JSON object.")
                review_id, finding_id = request.get("review_id"), request.get("finding_id")
                if not isinstance(review_id, str) or not isinstance(finding_id, str):
                    raise ValueError("Select a review and a finding before requesting advice.")
                answer = self._advice().explain(
                    review_id, finding_id, language=request.get("language", "en"),
                    use_ai=request.get("use_ai", False),
                )
                _json(self, HTTPStatus.OK, answer)
            except (ValueError, UnicodeDecodeError) as error:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except KeyError:
                _json(self, HTTPStatus.NOT_FOUND,
                      {"error": "The selected review or finding is not in this session."})
            except (AdviceUnavailable, SourceUnavailable) as error:
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            except Exception as error:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR,
                      {"error": f"{type(error).__name__}: {error}"})

        def _cancel_import(self, length):
            if length > MAX_REQUEST_BYTES:
                self.close_connection = True
                _json(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                      {"error": "Import control request is too large."})
                return
            try:
                request = json.loads(self.rfile.read(length))
                identity = request.get("job_id") if isinstance(request, dict) else None
                if not isinstance(identity, str) or not identity:
                    raise ValueError("Select an import task to cancel.")
                _json(self, HTTPStatus.OK, imports().cancel(identity))
            except (ValueError, TypeError) as error:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})

        def _client_disconnected(self):
            try:
                readable, _, _ = select.select([self.connection], [], [], 0)
                return bool(readable) and not self.connection.recv(1, socket.MSG_PEEK)
            except (OSError, ValueError):
                return True

        def _review_post(
            self, query: dict[str, list[str]], length: int, *, asynchronous=False,
        ) -> None:
            from doctor.import_jobs import ImportBusy, TERMINAL

            try:
                store = self._review()
                if length > store.max_model_bytes:
                    _drain(self.rfile, length)
                    self.close_connection = True
                    _json(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                          {"error": f"The model exceeds {store.max_model_bytes} bytes."})
                    return
                body = self.rfile.read(length)
                if len(body) != length:
                    raise ValueError("The model upload was incomplete.")
                manager = imports()
                job = manager.submit(
                    (query.get("filename") or [""])[0], body,
                    job_id=(query.get("job") or [None])[0],
                )
                if asynchronous:
                    _json(self, HTTPStatus.ACCEPTED, job)
                    return
                # Compatibility API: wait without native work or a cache lock in this process.
                while job["state"] not in TERMINAL:
                    if self._client_disconnected():
                        manager.cancel(job["job_id"])
                        return
                    job = manager.wait(job["job_id"])
                if job["state"] == "succeeded":
                    _payload(self, HTTPStatus.OK, store.report_payload(job["review_id"]))
                else:
                    status = HTTPStatus.GATEWAY_TIMEOUT if job["state"] == "timed_out" \
                        else HTTPStatus.BAD_REQUEST
                    _json(self, status, {"error": (job["error"] or {}).get(
                        "message", f"Import {job['state']}."), "job_id": job["job_id"]})
            except ImportBusy as error:
                _json(self, HTTPStatus.CONFLICT,
                      {"error": str(error), "active_job_id": error.job_id})
            except SourceUnavailable as error:
                self.close_connection = True
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            except ValueError as error:
                _json(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
            except Exception as error:
                _json(self, HTTPStatus.INTERNAL_SERVER_ERROR,
                      {"error": f"{type(error).__name__}: {error}"})

        def _local(self):
            if local_factory is None:
                raise SourceUnavailable("This server was started without local checks.")
            return local_factory()

        def _local_get(self, path: str, query: dict[str, list[str]]) -> None:
            try:
                local = self._local()
                if path == "/api/local":
                    _json(self, HTTPStatus.OK, local.describe())
                    return
                if path == "/api/local/checks":
                    _json(self, HTTPStatus.OK, {"checks": local.checks()})
                    return
                if path == "/api/local/envelope":
                    run_id = (query.get("run") or [""])[0]
                    prior = (query.get("prior") or [None])[0]
                    try:
                        envelope = local.envelope(run_id, prior)
                    except KeyError as missing:
                        _json(self, HTTPStatus.NOT_FOUND, {"error": str(missing)})
                        return
                    _json(self, HTTPStatus.OK, envelope)
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

        def _local_post(self, path: str, query: dict[str, list[str]], length: int) -> None:
            try:
                local = self._local()
                if path == "/api/local/models":
                    filename = (query.get("filename") or [""])[0]
                    body = _Counted(self.rfile)
                    answer = local.stage_model(filename, body, length)
                    if answer["outcome"] != "staged":
                        # Refused before or while reading. What is left of the
                        # body is read first, within a bound, so a browser that
                        # is still sending gets this answer; the connection is
                        # not reused either way.
                        _drain(self.rfile, length - body.consumed)
                        self.close_connection = True
                    _json(self, HTTPStatus.OK, answer)
                    return
                if length > MAX_REQUEST_BYTES:
                    self.close_connection = True
                    too_large = HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                    _json(self, too_large, {"error": "request too large"})
                    return
                try:
                    request = json.loads(self.rfile.read(length).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as malformed:
                    _json(self, HTTPStatus.BAD_REQUEST, {"error": f"not JSON: {malformed}"})
                    return
                handler = local.plan if path == "/api/local/plan" else local.run
                try:
                    answer = handler(request)
                except local.MalformedRequest as malformed:
                    _json(self, HTTPStatus.BAD_REQUEST, {"error": str(malformed)})
                    return
                _json(self, HTTPStatus.OK, answer)
            except SourceUnavailable as unavailable:
                self.close_connection = True
                _json(self, HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(unavailable)})
            except Exception as failure:  # reported, never swallowed
                self.close_connection = True
                _json(
                    self,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"{type(failure).__name__}: {failure}"},
                )

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
            root = STATIC
            if path.startswith("/vendor/three/"):
                root = REPOSITORY_ROOT / "third_party/three/0.186.1"
                name = path.removeprefix("/vendor/three/")
            target = (root / name).resolve()
            if (
                root not in target.parents
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
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="A workspace outside this checkout holding a finished `epc-ct run`.",
    )
    parser.add_argument(
        "--prior",
        type=Path,
        default=None,
        help="An earlier run of the same scope, to compare the workspace's run with.",
    )
    parser.add_argument(
        "--checks-dir",
        type=Path,
        default=None,
        help=(
            "Where local checks keep the models they are given and their results; "
            "outside any checkout. Defaults to $EPC_DOCTOR_CHECKS_DIR, or "
            "epc-control-tower/doctor-checks in the user's state directory."
        ),
    )
    parser.add_argument(
        "--import-timeout-seconds", type=float, default=600,
        help="Backend hard time limit for each isolated IFC import worker (default: 600).",
    )
    parser.add_argument(
        "--max-model-bytes",
        type=int,
        default=None,
        help="The largest model file a local check accepts.",
    )
    arguments = parser.parse_args(argv)
    if arguments.import_timeout_seconds <= 0:
        parser.error("--import-timeout-seconds must be positive")
    if arguments.prior is not None and arguments.workspace is None:
        parser.error("--prior needs --workspace")
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    source = functools.partial(adapter_source, arguments.workspace, arguments.prior)
    local = local_checks(arguments.checks_dir, arguments.max_model_bytes)
    from internal.doctor_adapter.review import ReviewStore

    review_options = {} if arguments.max_model_bytes is None else {
        "max_model_bytes": arguments.max_model_bytes
    }
    reviews = ReviewStore(REPOSITORY_ROOT, **review_options)
    from doctor.advice import AdviceService

    advice = AdviceService(reviews)
    from internal.doctor_adapter.project_library import ProjectLibrary

    projects = ProjectLibrary(local.root / "projects", reviews)
    from doctor.import_jobs import ImportJobs

    imports = ImportJobs(
        reviews, local.root / "import-jobs", timeout_seconds=arguments.import_timeout_seconds,
    )
    configure_import_loaders(imports, projects)
    from doctor.enterprise_service import EnterpriseService
    from internal.doctor_adapter.enterprise_library import EnterpriseLibrary

    enterprise = EnterpriseService(EnterpriseLibrary(projects), reviews,
                                   timeout_seconds=arguments.import_timeout_seconds)
    server = ThreadingHTTPServer(
        ("127.0.0.1", arguments.port),
        make_handler(source, lambda: local, lambda: reviews, lambda: advice, lambda: projects,
                     lambda: imports, lambda: enterprise),
    )
    print(f"BIM Doctor preview: http://127.0.0.1:{arguments.port}/")
    print(f"3D IFC review: http://127.0.0.1:{arguments.port}/review.html")
    print(f"Local checks are kept in {local.root}")
    print(f"Project library: {projects.path}")
    print(f"IFC import worker: one process, hard limit {arguments.import_timeout_seconds:g}s")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        enterprise.close()
        imports.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
