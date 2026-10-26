"""Project-local immutable rules, explicitly attached source, and purpose evidence.

These tables share the project database; payloads never enter the geometry LRU.
Adoption, a human statement and a machine assessment are separate stored events.
"""

from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from .project_library import ProjectLibraryError, _id, _json, _now, _text

_SCHEMA = """
CREATE TABLE IF NOT EXISTS enterprise_previews (
    preview_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
    created_at TEXT NOT NULL, filename TEXT NOT NULL, package BLOB NOT NULL,
    preview_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enterprise_rules (
    rule_revision_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    created_at TEXT NOT NULL, package BLOB NOT NULL, snapshot_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS enterprise_rules_project ON enterprise_rules(project_id);
CREATE TABLE IF NOT EXISTS enterprise_sources (
    source_sha256 TEXT PRIMARY KEY, body BLOB NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enterprise_revision_sources (
    revision_id TEXT PRIMARY KEY REFERENCES revisions(revision_id),
    source_sha256 TEXT NOT NULL REFERENCES enterprise_sources(source_sha256)
);
CREATE TABLE IF NOT EXISTS purpose_runs (
    run_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
    revision_id TEXT NOT NULL REFERENCES revisions(revision_id),
    rule_revision_id TEXT NOT NULL REFERENCES enterprise_rules(rule_revision_id),
    created_at TEXT NOT NULL, metadata_json TEXT NOT NULL, result_json BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS purpose_runs_project ON purpose_runs(project_id);
CREATE TABLE IF NOT EXISTS purpose_determinations (
    determination_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
    revision_id TEXT NOT NULL REFERENCES revisions(revision_id),
    rule_revision_id TEXT NOT NULL REFERENCES enterprise_rules(rule_revision_id),
    purpose_id TEXT NOT NULL, created_at TEXT NOT NULL, document_json TEXT NOT NULL
);
"""


def _parse(body, filename):
    from .enterprise_rules import parse_package

    return parse_package(body, filename)


class EnterpriseLibrary:
    def __init__(self, projects):
        self.projects = projects
        self.root = projects.root
        with self.projects._db() as db:
            db.executescript(_SCHEMA)

    def _project(self, project_id):
        project_id = _id(project_id, "Project id")
        with self.projects._db() as db:
            row = db.execute("SELECT 1 FROM projects WHERE project_id=?",
                             (project_id,)).fetchone()
            if row is None:
                raise KeyError("Project not found.")
        return project_id

    def rules(self, project_id):
        project_id = self._project(project_id)
        with self.projects._db() as db:
            rules = db.execute(
                "SELECT snapshot_json FROM enterprise_rules WHERE project_id=? "
                "ORDER BY created_at DESC,rule_revision_id", (project_id,),
            ).fetchall()
            previews = db.execute(
                "SELECT preview_json FROM enterprise_previews WHERE project_id=? "
                "ORDER BY created_at DESC,preview_id LIMIT 20", (project_id,),
            ).fetchall()
        return {"rule_revisions": [json.loads(row[0]) for row in rules],
                "previews": [json.loads(row[0]) for row in previews]}

    def preview(self, project_id, filename, body):
        project_id = self._project(project_id)
        package = _parse(body, filename)
        result = package.preview()
        # The adapter's normalized fields remain readable beside the exact source hash.
        result.update({"project_id": project_id, "filename": filename,
                       "preview_id": "preview-" + uuid4().hex, "created_at": _now()})
        result.setdefault("source_sha256", hashlib.sha256(body).hexdigest())
        result.setdefault("can_confirm", True)
        result.setdefault("unsupported", [check for check in result.get("checks", [])
                                          if check["support"] == "unsupported"])
        result["version_reused"] = any(
            row["package_id"] == result["package_id"] and row["version"] == result["version"]
            and row["source_sha256"] != result["source_sha256"]
            for row in self.rules(project_id)["rule_revisions"]
        )
        with self.projects._db() as db:
            db.execute("INSERT INTO enterprise_previews VALUES(?,?,?,?,?,?)", (
                result["preview_id"], project_id, result["created_at"], filename, body,
                _json(result),
            ))
        return result

    def confirm(self, project_id, preview_id, *, confirmed_by, responsible_team):
        project_id = self._project(project_id)
        confirmed_by = _text(confirmed_by, "Confirmed by", 160, required=True)
        responsible_team = _text(responsible_team, "Responsible reviewer/team", 160,
                                 required=True)
        with self.projects._db() as db:
            row = db.execute(
                "SELECT * FROM enterprise_previews WHERE preview_id=?", (_id(preview_id,
                                                                          "Preview id"),),
            ).fetchone()
            if row is None:
                raise KeyError("Rule preview not found.")
            if row["project_id"] != project_id:
                raise ProjectLibraryError("The preview belongs to a different project.")
            result = json.loads(row["preview_json"])
            if not result.get("can_confirm", True):
                raise ProjectLibraryError("Resolve package structure errors before adoption.")
            result.update({"rule_revision_id": "rules-" + uuid4().hex,
                           "confirmed_by": confirmed_by, "responsible_team": responsible_team,
                           "created_at": _now()})
            db.execute("INSERT INTO enterprise_rules VALUES(?,?,?,?,?)", (
                result["rule_revision_id"], project_id, result["created_at"], row["package"],
                _json(result),
            ))
        return result

    def rule(self, rule_revision_id):
        with self.projects._db() as db:
            row = db.execute(
                "SELECT snapshot_json FROM enterprise_rules WHERE rule_revision_id=?",
                (_id(rule_revision_id, "Rule revision id"),),
            ).fetchone()
        if row is None:
            raise KeyError("Adopted rule revision not found.")
        return json.loads(row[0])

    def package_bytes(self, rule_revision_id):
        with self.projects._db() as db:
            row = db.execute("SELECT package FROM enterprise_rules WHERE rule_revision_id=?",
                             (_id(rule_revision_id, "Rule revision id"),)).fetchone()
        if row is None:
            raise KeyError("Adopted rule revision not found.")
        return bytes(row[0])

    def source_available(self, revision_id):
        with self.projects._db() as db:
            return db.execute("SELECT 1 FROM enterprise_revision_sources WHERE revision_id=?",
                              (_id(revision_id, "Revision id"),)).fetchone() is not None

    def attach_source(self, revision_id, filename, body):
        revision = self.projects.revision(revision_id)["revision"]
        if not str(filename).lower().endswith(".ifc") or not body:
            raise ProjectLibraryError("Choose the original nonempty IFC for this revision.")
        if len(body) > self.projects.reviews.max_model_bytes:
            raise ProjectLibraryError("The IFC exceeds the configured upload limit.")
        digest = hashlib.sha256(body).hexdigest()
        if digest != revision["sha256"]:
            raise ProjectLibraryError(
                "The source SHA-256 does not match this revision. Import changed IFC as a new "
                "model revision; this saved evidence cannot be replaced."
            )
        with self.projects._db() as db:
            db.execute("INSERT OR IGNORE INTO enterprise_sources VALUES(?,?,?)",
                       (digest, body, _now()))
            db.execute("INSERT OR IGNORE INTO enterprise_revision_sources VALUES(?,?)",
                       (revision_id, digest))
        return {"revision_id": revision_id, "source_available": True,
                "source_sha256": digest, "retention": "project-local-source-for-rule-rechecks"}

    def source(self, revision_id):
        revision = self.projects.revision(revision_id)["revision"]
        with self.projects._db() as db:
            row = db.execute(
                "SELECT s.body FROM enterprise_sources s JOIN enterprise_revision_sources r "
                "ON r.source_sha256=s.source_sha256 WHERE r.revision_id=?", (revision_id,),
            ).fetchone()
        if row is None:
            raise ProjectLibraryError(
                "Attach the SHA-matching original IFC before executing new rules."
            )
        body = bytes(row[0])
        if hashlib.sha256(body).hexdigest() != revision["sha256"]:
            raise ProjectLibraryError("The retained IFC source hash is inconsistent.")
        return body

    def summary(self, project_id):
        project_id = self._project(project_id)
        with self.projects._db() as db:
            sources = db.execute(
                "SELECT r.revision_id,r.model_id,r.filename,"
                "CASE WHEN s.revision_id IS NULL THEN 0 ELSE 1 END AS source_available "
                "FROM revisions r JOIN models m ON m.model_id=r.model_id "
                "LEFT JOIN enterprise_revision_sources s ON s.revision_id=r.revision_id "
                "WHERE m.project_id=? ORDER BY r.created_at DESC", (project_id,),
            ).fetchall()
            runs = db.execute(
                "SELECT metadata_json FROM purpose_runs WHERE project_id=? "
                "ORDER BY created_at DESC,run_id", (project_id,),
            ).fetchall()
        return {"rule_revisions": self.rules(project_id)["rule_revisions"],
                "sources": [{**dict(row), "source_available": bool(row["source_available"])}
                            for row in sources],
                "assessments": [json.loads(row[0]) for row in runs]}

    def publish_run(self, result):
        project_id = self._project(result["project_id"])
        revision = self.projects.revision(result["revision_id"])["revision"]
        rule = self.rule(result["rule_revision_id"])
        if revision["project_id"] != project_id or rule["project_id"] != project_id:
            raise ProjectLibraryError("The assessment inputs belong to different projects.")
        result = dict(result)
        with self.projects._db() as db:
            old = db.execute("SELECT result_json FROM purpose_runs WHERE run_id=?",
                             (_id(result["run_id"], "Run id"),)).fetchone()
            if old is not None:
                stored = json.loads(old[0])
                result.setdefault("created_at", stored["created_at"])
                if stored != result:
                    raise ProjectLibraryError("A published purpose run is immutable.")
                return {"run_id": result["run_id"]}
            result.setdefault("created_at", _now())
            metadata = {key: result.get(key) for key in (
                "run_id", "project_id", "revision_id", "rule_revision_id", "purpose_id",
                "scope", "prior_run_id", "consuming_revision_id", "created_at", "conclusion",
            )}
            db.execute("INSERT INTO purpose_runs VALUES(?,?,?,?,?,?,?)", (
                result["run_id"], project_id, result["revision_id"], result["rule_revision_id"],
                result["created_at"], _json(metadata), _json(result).encode("utf-8"),
            ))
        return {"run_id": result["run_id"]}

    def run(self, run_id):
        with self.projects._db() as db:
            row = db.execute("SELECT result_json FROM purpose_runs WHERE run_id=?",
                             (_id(run_id, "Run id"),)).fetchone()
        if row is None:
            raise KeyError("Purpose assessment not found.")
        return json.loads(row[0])

    def determination(self, run_id, evidence_id, *, subject_keys, outcome, method_id,
                      determiner, basis, reference, context_digest=None):
        run = self.run(run_id)
        subject = sorted(_id(key, "Subject key") for key in subject_keys)
        evidence = next((item for item in run.get("evidence_requests", [])
                         if item["evidence_id"] == evidence_id
                         and sorted(item.get("subject_keys", [])) == subject), None)
        if evidence is None or evidence.get("execution") != "manual":
            raise ProjectLibraryError("This run has no matching manual evidence request.")
        if context_digest is not None and context_digest != evidence["context_digest"]:
            raise ProjectLibraryError("The evidence context does not match the cited run.")
        if method_id != evidence["method_id"] or outcome not in evidence["outcomes"]:
            raise ProjectLibraryError("Choose an accepted method and declared outcome.")
        document = {
            "determination_id": "determination-" + uuid4().hex,
            "evidence_id": evidence_id, "subject_keys": subject, "outcome": outcome,
            "method_id": method_id, "determiner": _text(determiner, "Recorder", 160,
                                                        required=True),
            "basis": _text(basis, "Evidence basis", 8000, required=True),
            "reference": _text(reference, "Evidence reference", 1000, required=True),
            "context_digest": evidence["context_digest"], "created_at": _now(),
            "run_id": run_id, "standing": "user-recorded-not-authenticated-signature",
        }
        with self.projects._db() as db:
            db.execute("INSERT INTO purpose_determinations VALUES(?,?,?,?,?,?,?)", (
                document["determination_id"], run["project_id"], run["revision_id"],
                run["rule_revision_id"], run["purpose_id"], document["created_at"],
                _json(document),
            ))
        return document

    def judgments(self, project_id, revision_id, rule_revision_id, purpose_id):
        with self.projects._db() as db:
            rows = db.execute(
                "SELECT document_json FROM purpose_determinations WHERE project_id=? "
                "AND revision_id=? AND rule_revision_id=? AND purpose_id=? ORDER BY created_at",
                (project_id, revision_id, rule_revision_id, purpose_id),
            ).fetchall()
        latest = {}
        for row in rows:
            item = json.loads(row[0])
            key = (item["evidence_id"], tuple(item["subject_keys"]), item["context_digest"])
            latest[key] = item
        return list(latest.values())
