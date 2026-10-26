"""A small local SQLite project library for immutable review revisions.

This adapter manages review JSON, meshes and follow-up text. The separate
enterprise adapter can explicitly attach original IFC and purpose evidence in
the same project database. Provider credentials are never stored.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import sqlite3
from uuid import uuid4


class ProjectLibraryError(ValueError):
    """A project input or saved snapshot cannot be used as requested."""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY, name TEXT NOT NULL,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS models (
    model_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    name TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS revisions (
    revision_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES models(model_id),
    review_id TEXT NOT NULL, number INTEGER NOT NULL,
    label TEXT NOT NULL, created_at TEXT NOT NULL,
    filename TEXT NOT NULL, sha256 TEXT NOT NULL,
    summary_json TEXT NOT NULL, report_json BLOB NOT NULL, geometry_json BLOB NOT NULL,
    geometry_sha256 TEXT,
    UNIQUE(model_id, review_id), UNIQUE(model_id, number)
);
CREATE TABLE IF NOT EXISTS followups (
    revision_id TEXT NOT NULL REFERENCES revisions(revision_id),
    finding_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','in_progress','ready_for_recheck')),
    owner TEXT NOT NULL, note TEXT NOT NULL, updated_at TEXT NOT NULL,
    PRIMARY KEY(revision_id, finding_id)
);
"""
_REVISION_COLUMNS = """r.revision_id, r.model_id, m.project_id, r.review_id,
    r.number, r.label, r.created_at, r.filename, r.sha256, r.summary_json"""


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _text(value, label, limit, *, required=False):
    if not isinstance(value, str):
        raise ProjectLibraryError(f"{label} must be text.")
    value = value.strip()
    if required and not value:
        raise ProjectLibraryError(f"{label} is required.")
    if len(value) > limit:
        raise ProjectLibraryError(f"{label} must be at most {limit} characters.")
    return value


def _id(value, label):
    return _text(value, label, 100, required=True)


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _bytes(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise ProjectLibraryError("The saved review payload is not JSON text or bytes.")


class ProjectLibrary:
    """One SQLite file beneath the server's external local-checks directory."""

    def __init__(self, root: Path, reviews):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "library.sqlite3"
        self.reviews = reviews
        with self._db() as db:
            db.executescript(_SCHEMA)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(revisions)")}
            if "geometry_sha256" not in columns:
                db.execute("ALTER TABLE revisions ADD COLUMN geometry_sha256 TEXT")
            db.execute("CREATE INDEX IF NOT EXISTS revisions_by_review ON revisions(review_id)")
        self.reviews.set_loaders(
            report_loader=self.restore_report, geometry_loader=self.restore_geometry
        )

    @contextmanager
    def _db(self):
        db = None
        try:
            db = sqlite3.connect(self.path, timeout=10)
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            with db:
                yield db
        except sqlite3.DatabaseError as error:
            raise ProjectLibraryError(
                "The local project library could not be read or saved. "
                "Check that its SQLite file is accessible and intact."
            ) from error
        finally:
            if db is not None:
                db.close()

    def projects(self):
        with self._db() as db:
            rows = db.execute("""
                SELECT p.*, COUNT(DISTINCT m.model_id) AS model_count,
                       COUNT(r.revision_id) AS revision_count
                FROM projects p LEFT JOIN models m ON p.project_id=m.project_id
                LEFT JOIN revisions r ON m.model_id=r.model_id
                GROUP BY p.project_id ORDER BY p.updated_at DESC, p.project_id
            """).fetchall()
            return [dict(row) for row in rows]

    def create_project(self, name):
        name = _text(name, "Project name", 160, required=True)
        now = _now()
        project_id = "project-" + uuid4().hex
        with self._db() as db:
            db.execute("INSERT INTO projects VALUES(?,?,?,?)", (project_id, name, now, now))
        return {
            "project_id": project_id,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "model_count": 0,
            "revision_count": 0,
        }

    def detail(self, project_id):
        project_id = _id(project_id, "Project id")
        with self._db() as db:
            project = next((p for p in self.projects() if p["project_id"] == project_id), None)
            if project is None:
                raise KeyError("Project not found in this library.")
            models = []
            for model in db.execute(
                "SELECT * FROM models WHERE project_id=? ORDER BY created_at, model_id",
                (project_id,),
            ):
                rows = db.execute(
                    f"SELECT {_REVISION_COLUMNS} FROM revisions r "
                    "JOIN models m ON m.model_id=r.model_id "
                    "WHERE r.model_id=? ORDER BY r.number DESC",
                    (model["model_id"],),
                )
                models.append(
                    {**dict(model), "revisions": [self._metadata(row) for row in rows]}
                )
            return {"project": project, "models": models}

    @staticmethod
    def _metadata(row):
        metadata = dict(row)
        try:
            metadata["summary"] = json.loads(metadata.pop("summary_json"))
            if not isinstance(metadata["summary"], dict):
                raise ValueError("summary is not an object")
        except (json.JSONDecodeError, ValueError, TypeError) as error:
            raise ProjectLibraryError("The saved review metadata is damaged.") from error
        return metadata

    @staticmethod
    def _existing_revision(db, project_id, model_id, review_id):
        if not db.execute(
            "SELECT 1 FROM projects WHERE project_id=?", (project_id,)
        ).fetchone():
            raise KeyError("Project not found in this library.")
        if model_id is not None:
            model = db.execute(
                "SELECT project_id FROM models WHERE model_id=?", (model_id,)
            ).fetchone()
            if model is None:
                raise KeyError("Model slot not found in this library.")
            if model["project_id"] != project_id:
                raise ProjectLibraryError("The model slot belongs to a different project.")
            row = db.execute(
                "SELECT revision_id FROM revisions WHERE model_id=? AND review_id=?",
                (model_id, review_id),
            ).fetchone()
        else:
            row = db.execute(
                "SELECT r.revision_id FROM revisions r "
                "JOIN models m ON m.model_id=r.model_id "
                "WHERE m.project_id=? AND r.review_id=? "
                "ORDER BY r.created_at LIMIT 1",
                (project_id, review_id),
            ).fetchone()
        return row["revision_id"] if row else None

    def save_revision(self, project_id, review_id, *, model_id=None, model_name=None, label=""):
        project_id, review_id = _id(project_id, "Project id"), _id(review_id, "Review id")
        label = _text(label, "Revision label", 120)
        if model_id is not None:
            model_id = _id(model_id, "Model id")
        if model_name is not None:
            model_name = _text(model_name, "Model name", 160, required=True)
        # Duplicate saves never fetch large geometry. First check without a
        # write transaction, then recheck atomically after out-of-lock I/O.
        with self._db() as db:
            prior = self._existing_revision(db, project_id, model_id, review_id)
        if prior is not None:
            return self.revision(prior)
        report = self.reviews.get(review_id)
        report_json = self.reviews.report_payload(review_id)
        geometry_json = self.reviews.geometry_payload(review_id)
        geometry_sha256 = hashlib.sha256(geometry_json).hexdigest()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            existing_id = self._existing_revision(db, project_id, model_id, review_id)
            if existing_id is None:
                if model_id is None:
                    model_id = "model-" + uuid4().hex
                    name = model_name or report["source"]["filename"][:160] or "Model"
                    db.execute(
                        "INSERT INTO models VALUES(?,?,?,?)",
                        (model_id, project_id, name, _now()),
                    )
                number = db.execute(
                    "SELECT COALESCE(MAX(number),0)+1 FROM revisions WHERE model_id=?",
                    (model_id,),
                ).fetchone()[0]
                existing_id = "revision-" + uuid4().hex
                now = _now()
                db.execute(
                    "INSERT INTO revisions(revision_id,model_id,review_id,number,label,"
                    "created_at,"
                    "filename,sha256,summary_json,report_json,geometry_json,geometry_sha256) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        existing_id,
                        model_id,
                        review_id,
                        number,
                        label or f"Revision {number}",
                        now,
                        report["source"]["filename"],
                        report["source"]["sha256"],
                        _json(report["summary"]),
                        report_json,
                        geometry_json,
                        geometry_sha256,
                    ),
                )
                db.execute(
                    "UPDATE projects SET updated_at=? WHERE project_id=?", (now, project_id)
                )
        return self.revision(existing_id)

    def restore_report(self, review_id: str) -> bytes:
        """Report cache-miss loader. Never SELECT or decode the geometry column."""
        review_id = _id(review_id, "Review id")
        with self._db() as db:
            row = db.execute(
                "SELECT report_json FROM revisions WHERE review_id=? LIMIT 1", (review_id,)
            ).fetchone()
        if row is None:
            raise KeyError("Review not found in this library.")
        payload = _bytes(row["report_json"])
        try:
            if json.loads(payload)["review_id"] != review_id:
                raise ValueError("review identity does not match")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise ProjectLibraryError(
                "The saved review snapshot is damaged or inconsistent."
            ) from error
        return payload

    def restore_geometry(self, review_id: str) -> bytes:
        """Geometry-only cache-miss loader; never expand Python float arrays.

        New saves store bytes plus SHA-256. Legacy TEXT rows get an identity
        check without rewriting historical evidence or recapturing a checksum.
        """
        from .review import _geometry_identity

        review_id = _id(review_id, "Review id")
        with self._db() as db:
            row = db.execute(
                "SELECT geometry_json,geometry_sha256 FROM revisions WHERE review_id=? LIMIT 1",
                (review_id,),
            ).fetchone()
        if row is None:
            raise KeyError("Review not found in this library.")
        payload = _bytes(row["geometry_json"])
        try:
            _geometry_identity(payload, review_id)
            checksum = row["geometry_sha256"]
            if checksum is not None and hashlib.sha256(payload).hexdigest() != checksum:
                raise ValueError("geometry checksum does not match")
        except ValueError as error:
            raise ProjectLibraryError(
                "The saved review geometry is damaged or inconsistent."
            ) from error
        return payload

    def revision(self, revision_id):
        """Reopen report/follow-ups only; geometry remains in SQLite until requested."""
        revision_id = _id(revision_id, "Revision id")
        with self._db() as db:
            row = db.execute(
                f"SELECT {_REVISION_COLUMNS}, r.report_json "
                "FROM revisions r JOIN models m ON m.model_id=r.model_id "
                "WHERE revision_id=?",
                (revision_id,),
            ).fetchone()
            if row is None:
                raise KeyError("Revision not found in this library.")
            data = dict(row)
            followups = [
                dict(item)
                for item in db.execute(
                    "SELECT * FROM followups WHERE revision_id=? ORDER BY finding_id",
                    (revision_id,),
                )
            ]
        try:
            report = self.reviews.admit_report(
                _bytes(data.pop("report_json")), expected_review_id=data["review_id"]
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise ProjectLibraryError(
                "The saved review snapshot is damaged or inconsistent."
            ) from error
        return {"revision": self._metadata(data), "report": report, "followups": followups}

    def update_followup(self, revision_id, finding_id, *, status="open", owner="", note=""):
        revision_id = _id(revision_id, "Revision id")
        finding_id = _id(finding_id, "Finding id")
        if not isinstance(status, str) or status not in {
            "open",
            "in_progress",
            "ready_for_recheck",
        }:
            raise ProjectLibraryError("Status must be open, in_progress, or ready_for_recheck.")
        owner = _text(owner, "Owner", 160)
        note = _text(note, "Note", 4000)
        revision = self.revision(revision_id)
        if not any(item["finding_id"] == finding_id for item in revision["report"]["findings"]):
            raise KeyError("Finding not found in the selected revision.")
        result = {
            "revision_id": revision_id,
            "finding_id": finding_id,
            "status": status,
            "owner": owner,
            "note": note,
            "updated_at": _now(),
        }
        with self._db() as db:
            db.execute(
                "INSERT INTO followups VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(revision_id,finding_id) DO UPDATE SET "
                "status=excluded.status,owner=excluded.owner,note=excluded.note,"
                "updated_at=excluded.updated_at",
                tuple(result.values()),
            )
            db.execute(
                "UPDATE projects SET updated_at=? WHERE project_id=?",
                (result["updated_at"], revision["revision"]["project_id"]),
            )
        return result

    def compare(self, before_id, after_id):
        from .revision_compare import compare_revisions

        before, after = self.revision(before_id), self.revision(after_id)
        if before["revision"]["project_id"] != after["revision"]["project_id"] or (
            before["revision"]["model_id"] != after["revision"]["model_id"]
        ):
            raise ProjectLibraryError(
                "Choose two revisions from the same project and model slot."
            )
        return compare_revisions(before, after)
