"""Bounded, observable IFC imports supervised outside the HTTP process.

Cancellation is a process termination followed by a confirmed exit, never just a
disconnected browser. Only complete worker output can enter the review cache.
"""

from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from uuid import uuid4

TERMINAL = {"succeeded", "failed", "cancelled", "timed_out"}
EVENT_PREFIX = "BIMDOCTOR_IMPORT "


class ImportBusy(ValueError):
    def __init__(self, job_id):
        super().__init__("Another IFC import is active; wait or cancel that task first.")
        self.job_id = job_id


@dataclass
class _Job:
    identity: str
    state: str = "queued"
    stage: str = "uploading"
    completed: int = 0
    total: int = 0
    started: float = field(default_factory=time.monotonic)
    finished_at: float | None = None
    key: tuple | None = None
    directory: Path | None = None
    process: subprocess.Popen | None = None
    reason: str | None = None
    review_id: str | None = None
    result: dict | None = None
    error: dict | None = None
    worker_exited: bool = False
    done: threading.Event = field(default_factory=threading.Event)
    stop_lock: threading.Lock = field(default_factory=threading.Lock)
    diagnostics: deque = field(default_factory=lambda: deque(maxlen=20))
    readers: int = 0
    readers_done: threading.Event = field(default_factory=threading.Event)

    def __post_init__(self):
        self.readers_done.set()


class ImportJobs:
    """One native worker, finite task history and finite temporary output storage."""

    def __init__(
        self, reviews, directory=None, *, timeout_seconds=600, max_history=16,
        max_artifacts=4, max_artifact_bytes=256 * 1024 * 1024, worker_script=None,
        output_files=("report.json", "geometry.json"), result_handler=None,
    ):
        if timeout_seconds <= 0 or max_history < 1 or max_artifacts < 1:
            raise ValueError("Import limits must be positive.")
        self.reviews = reviews
        self.timeout_seconds = timeout_seconds
        self.max_history = max_history
        self.max_artifacts = max_artifacts
        self.max_artifact_bytes = max_artifact_bytes
        self.worker_script = Path(worker_script or Path(__file__).with_name("import_worker.py"))
        self.output_files = tuple(output_files)
        if any(Path(name).name != name or not name.endswith(".json")
               for name in self.output_files):
            raise ValueError("Worker outputs must be JSON filenames in its task directory.")
        self.result_handler = result_handler
        self._temporary = tempfile.TemporaryDirectory(prefix="bim-doctor-imports-") \
            if directory is None else None
        self.root = Path(directory or self._temporary.name).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._jobs: OrderedDict[str, _Job] = OrderedDict()
        self._active: str | None = None
        self._lock = threading.RLock()
        self._closed = False

    @staticmethod
    def _identity(value):
        value = uuid4().hex if value is None else value
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
            raise ValueError("Invalid import task identifier.")
        return value

    def _view(self, job):
        return {
            "job_id": job.identity, "state": job.state, "stage": job.stage,
            "completed": job.completed, "total": job.total,
            "elapsed_seconds": round((job.finished_at or time.monotonic()) - job.started, 3),
            "deadline_seconds": self.timeout_seconds, "review_id": job.review_id,
            "result": job.result,
            "worker_pid": job.process.pid if job.process else None,
            "worker_exited": job.worker_exited, "error": job.error,
            "diagnostics": list(job.diagnostics)
            if job.state in {"failed", "timed_out"} else [],
        }

    def get(self, identity):
        with self._lock:
            return self._view(self._jobs[identity])

    def snapshot(self):
        with self._lock:
            return {
                "jobs": [self._view(job) for job in self._jobs.values()],
                "limits": {"workers": 1, "history": self.max_history,
                           "artifacts": self.max_artifacts,
                           "artifact_bytes": self.max_artifact_bytes},
            }

    def _remove_files(self, job):
        path = job.directory
        if path is not None:
            resolved = path.resolve()
            if resolved == self.root or not resolved.is_relative_to(self.root):
                raise ValueError("Import cleanup must remain in its owned task directory.")
            shutil.rmtree(resolved, ignore_errors=False)
            job.directory = None

    def _trim(self):
        # Called with the metadata lock, never while native IFC work is running here.
        artifacts = [job for job in self._jobs.values()
                     if job.state == "succeeded" and job.directory]
        sizes = {job.identity: sum(p.stat().st_size for p in job.directory.glob("*.json"))
                 for job in artifacts}
        while artifacts and (len(artifacts) > self.max_artifacts
                             or sum(sizes.values()) > self.max_artifact_bytes):
            oldest = next((job for job in artifacts if not job.readers), None)
            if oldest is None:
                break  # An in-flight disk read is pinned until its file handle closes.
            artifacts.remove(oldest)
            sizes.pop(oldest.identity)
            self._remove_files(oldest)
        while len(self._jobs) > self.max_history:
            oldest = next((j for j in self._jobs.values()
                           if j.state in TERMINAL and not j.readers
                           and j.identity != self._active), None)
            if oldest is None:
                break
            self._remove_files(oldest)
            del self._jobs[oldest.identity]

    def submit(self, filename, body, *, job_id=None, context=None):
        identity = self._identity(job_id)
        filename = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
        if not filename.lower().endswith(".ifc") or not body:
            raise ValueError("Choose a nonempty .ifc STEP model file.")
        if len(body) > self.reviews.max_model_bytes:
            raise ValueError("The model exceeds the configured upload limit.")
        context_bytes = json.dumps(
            context, sort_keys=True, allow_nan=False, ensure_ascii=False,
        ).encode("utf-8") if context is not None else b""
        key = (filename, hashlib.sha256(body).hexdigest(),
               hashlib.sha256(context_bytes).hexdigest())
        with self._lock:
            if self._closed:
                raise ValueError("The import supervisor is shutting down.")
            prior = self._jobs.get(identity)
            if prior:
                if prior.key is not None and prior.key != key:
                    raise ValueError("This task identifier already names a different upload.")
                return self._view(prior)
            if self._active is not None:
                raise ImportBusy(self._active)
            job = _Job(identity, key=key)
            # Re-selecting an already completed payload need not retessellate it.
            for old in reversed(self._jobs.values()):
                if old.key == key and old.state == "succeeded" and old.directory:
                    job.state, job.stage = "succeeded", "complete"
                    job.review_id, job.worker_exited = old.review_id, True
                    job.result = old.result
                    job.finished_at = time.monotonic()
                    job.done.set()
                    self._jobs[identity] = job
                    self._trim()
                    return self._view(job)
            self._jobs[identity] = job
            self._active = identity
        try:
            directory = Path(tempfile.mkdtemp(prefix="task-", dir=self.root))
            with self._lock:
                job.directory = directory
            (directory / "input.ifc").write_bytes(body)
            if context_bytes:
                (directory / "context.json").write_bytes(context_bytes)
            (directory / "tmp").mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
            env.update({"PYTHONUTF8": "1", "TMP": str(directory / "tmp"),
                        "TEMP": str(directory / "tmp"), "TMPDIR": str(directory / "tmp")})
            with self._lock:
                if job.state == "cancelled":
                    self._remove_files(job)
                    return self._view(job)
                job.process = subprocess.Popen(
                    [sys.executable, "-u", str(self.worker_script),
                     "--root", str(self.reviews.root),
                     "--input", str(directory / "input.ifc"), "--output", str(directory),
                     "--filename", filename],
                    cwd=self.reviews.root, env=env, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                    start_new_session=os.name != "nt",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                job.state, job.stage = "running", "starting"
                threading.Thread(target=self._watch, args=(job,), daemon=True).start()
                return self._view(job)
        except Exception:
            with self._lock:
                if self._active == identity:
                    self._active = None
                if job.reason != "cancel":
                    job.state, job.stage = "failed", "starting"
                    job.error = {"code": "start_failed", "stage": "starting",
                                 "message": "The IFC worker could not be started."}
                job.done.set()
                job.finished_at = time.monotonic()
                self._remove_files(job)
            raise

    def _read_events(self, job):
        with job.process.stdout as stream:
            for line in stream:
                with self._lock:
                    job.diagnostics.append(line.rstrip()[-2000:])
                    if not line.startswith(EVENT_PREFIX):
                        continue
                    try:
                        event = json.loads(line[len(EVENT_PREFIX):])
                    except ValueError:
                        continue
                    if job.state != "running":
                        continue
                    if "error" in event:
                        job.error = event["error"]
                    else:
                        job.stage = event["stage"]
                        job.completed = event.get("completed", 0)
                        job.total = event.get("total", 0)

    @staticmethod
    def _stop(job):
        # A user cancellation and the deadline may arrive together.
        with job.stop_lock:
            ImportJobs._stop_process(job.process)

    @staticmethod
    def _stop_process(process):
        if process.poll() is None:
            if os.name == "nt":
                # A venv python.exe can be a launcher. Terminating only that PID
                # leaves the actual native computation alive in its child.
                result = subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if result.returncode and process.poll() is None:
                    raise RuntimeError("The IFC worker process tree could not be stopped.")
                process.wait(timeout=2)
                return
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            # A descendant may ignore SIGTERM even after its parent exits.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)

    def _watch(self, job):
        reader = threading.Thread(target=self._read_events, args=(job,), daemon=True)
        reader.start()
        try:
            while job.process.poll() is None:
                if time.monotonic() - job.started >= self.timeout_seconds:
                    with self._lock:
                        if job.reason is None:
                            job.reason, job.state = "deadline", "cancelling"
                    self._stop(job)
                time.sleep(0.05)
            reader.join(timeout=2)
            job.worker_exited = True
            with self._lock:
                reason = job.reason
            if reason:
                with self._lock:
                    job.state = "timed_out" if reason == "deadline" else "cancelled"
                    if reason == "deadline":
                        job.error = {
                            "code": "deadline_exceeded", "stage": job.stage,
                            "message": "The IFC import exceeded its backend time limit.",
                        }
                return
            if job.process.returncode or job.error:
                with self._lock:
                    job.state = "failed"
                    job.error = job.error or {
                        "code": "worker_exited", "stage": job.stage,
                        "message": f"The IFC worker exited with code {job.process.returncode}.",
                    }
                return
            if sum((job.directory / name).stat().st_size for name in self.output_files) \
                    > self.max_artifact_bytes:
                raise ValueError("Import output exceeds the temporary artifact budget.")
            outputs = {name: (job.directory / name).read_bytes() for name in self.output_files}
            with self._lock:
                # Whichever wins this short commit section decides cancel vs success.
                if job.reason is not None:
                    job.state = "cancelled"
                    return
                job.stage = "publishing"
                if self.result_handler is None:
                    accepted = self.reviews.admit_serialized(
                        outputs["report.json"], outputs["geometry.json"],
                    )
                    job.review_id = accepted["review_id"]
                else:
                    job.result = self.result_handler(outputs)
                job.state, job.stage = "succeeded", "complete"
        except Exception as error:
            with self._lock:
                job.state = "failed"
                job.error = {"code": "publication_failed", "stage": job.stage,
                             "type": type(error).__name__, "message": str(error)}
        finally:
            with self._lock:
                self._active = None if self._active == job.identity else self._active
                try:
                    if job.directory:
                        if job.state == "succeeded":
                            (job.directory / "input.ifc").unlink(missing_ok=True)
                            (job.directory / "context.json").unlink(missing_ok=True)
                            scratch = job.directory / "tmp"
                            if scratch.exists():
                                shutil.rmtree(scratch)
                        else:
                            self._remove_files(job)
                    self._trim()
                finally:
                    job.finished_at = time.monotonic()
                    job.done.set()

    def cancel(self, identity):
        identity = self._identity(identity)
        with self._lock:
            job = self._jobs.get(identity)
            if job is None:
                # A browser can cancel before its upload acknowledgement arrives.
                job = _Job(identity, state="cancelled", stage="uploading", worker_exited=True)
                job.finished_at = time.monotonic()
                job.done.set()
                self._jobs[identity] = job
                self._trim()
                return self._view(job)
            if job.state in TERMINAL:
                return self._view(job)
            job.reason, job.state = "cancel", "cancelling"
            process = job.process
            if process is None:
                job.state, job.worker_exited = "cancelled", True
                job.finished_at = time.monotonic()
                if self._active == identity:
                    self._active = None
                job.done.set()
                return self._view(job)
        self._stop(job)
        job.done.wait(timeout=3)
        return self.get(identity)

    def wait(self, identity, timeout=0.1):
        with self._lock:
            event = self._jobs[identity].done
        event.wait(timeout)
        return self.get(identity)

    def _artifact(self, review_id, name):
        with self._lock:
            if self._closed:
                raise KeyError("The import supervisor is closed.")
            for job in reversed(self._jobs.values()):
                if job.state == "succeeded" and job.review_id == review_id and job.directory:
                    path = job.directory / name
                    job.readers += 1
                    job.readers_done.clear()
                    break
            else:
                raise KeyError(
                    "This unsaved import has expired; reopen a saved revision or reimport."
                )
        try:
            return path.read_bytes()
        finally:
            with self._lock:
                job.readers -= 1
                if not job.readers:
                    job.readers_done.set()
                self._trim()

    def report_payload(self, review_id):
        return self._artifact(review_id, "report.json")

    def geometry_payload(self, review_id):
        return self._artifact(review_id, "geometry.json")

    def close(self):
        with self._lock:
            self._closed = True
            active = self._active
        if active:
            self.cancel(active)
        with self._lock:
            jobs = list(self._jobs.values())
        for job in jobs:
            if job.process is not None:
                self._stop(job)
                job.done.wait()
            job.readers_done.wait()
            with self._lock:
                self._remove_files(job)
        if self._temporary:
            self._temporary.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
