"""Project inputs and supervised check-only purpose runs; no geometry work."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from doctor.import_jobs import ImportJobs
from internal.doctor_adapter.project_library import ProjectLibraryError, _id


def _model_context(saved):
    report = saved["report"]
    return {"revision": saved["revision"], "report": {
        key: report[key] for key in ("review_id", "source", "models", "elements")
    }}


class EnterpriseService:
    def __init__(self, library, reviews, *, timeout_seconds=600, worker_script=None):
        self.library = library
        self.jobs = ImportJobs(
            reviews, library.root / "purpose-jobs", timeout_seconds=timeout_seconds,
            worker_script=worker_script or Path(__file__).with_name("enterprise_worker.py"),
            output_files=("result.json",), result_handler=self._publish,
            max_artifacts=2, max_artifact_bytes=64 * 1024 * 1024,
        )

    def _publish(self, outputs):
        return self.library.publish_run(json.loads(outputs["result.json"]))

    def submit(self, request):
        library = self.library
        project_id = library._project(request.get("project_id"))
        saved = library.projects.revision(request.get("revision_id"))
        rule = library.rule(request.get("rule_revision_id"))
        if saved["revision"]["project_id"] != project_id or rule["project_id"] != project_id:
            raise ProjectLibraryError("The selected inputs belong to different projects.")
        purpose_id = _id(request.get("purpose_id"), "Purpose id")
        if not any(item["purpose_id"] == purpose_id for item in rule["purposes"]):
            raise ProjectLibraryError("The adopted package does not declare this purpose.")
        scope = request.get("scope")
        if not isinstance(scope, dict) or scope.get("kind") not in {
            "all", "classes", "elements",
        }:
            raise ProjectLibraryError("Declare all, class or element scope before assessment.")
        if any(not isinstance(scope.get(field, []), list)
               for field in ("classes", "element_keys")):
            raise ProjectLibraryError("Scope classes and object keys must be lists.")
        scope = {"kind": scope["kind"],
                 "classes": sorted(set(scope.get("classes", []))),
                 "element_keys": sorted(set(scope.get("element_keys", [])))}
        if any(not isinstance(item, str) for item in scope["classes"] + scope["element_keys"]):
            raise ProjectLibraryError("Scope classes and object keys must be text.")
        prior_id = request.get("prior_run_id")
        prior = library.run(prior_id) if prior_id else None
        if prior and (prior["project_id"] != project_id
                      or prior["purpose_id"] != purpose_id):
            raise ProjectLibraryError("Choose a prior assessment of this project and purpose.")
        consumer = None
        consumer_id = request.get("consuming_revision_id") or None
        if consumer_id:
            consumer = _model_context(library.projects.revision(consumer_id))
            if consumer["revision"]["project_id"] != project_id:
                raise ProjectLibraryError("The counterpart belongs to another project.")
            if consumer["revision"]["model_id"] == saved["revision"]["model_id"]:
                raise ProjectLibraryError("A counterpart must be a distinct actual model slot.")
        body = library.source(saved["revision"]["revision_id"])
        job_id = self.jobs._identity(request.get("job_id"))
        # Stable client task id makes a lost POST response safe to query/retry.
        metadata = {
            "run_id": "purpose-" + job_id, "project_id": project_id,
            "revision_id": saved["revision"]["revision_id"],
            "rule_revision_id": rule["rule_revision_id"], "purpose_id": purpose_id,
            "scope": scope, "consuming_revision_id": consumer_id,
            "prior_run_id": prior_id or None,
        }
        context = {
            "metadata": metadata, **_model_context(saved), "rule_revision": rule,
            "package_b64": base64.b64encode(
                library.package_bytes(rule["rule_revision_id"]),
            ).decode(),
            "prior": prior, "consumer": consumer,
            "determinations": library.judgments(project_id, saved["revision"]["revision_id"],
                                                rule["rule_revision_id"], purpose_id),
        }
        return self.jobs.submit(saved["revision"]["filename"], body,
                                job_id=job_id, context=context)

    def brief(self, run_id, language="en"):
        run = self.library.run(run_id)
        zh = language == "zh"
        lines = ["# " + ("用途审查简报" if zh else "Purpose review brief"), "",
                 ("用途" if zh else "Purpose") + ": " + run["purpose_id"],
                 ("结论" if zh else "Conclusion") + ": " + run["conclusion"]["status"],
                 "Run: " + run["run_id"], "Revision: " + run["revision_id"],
                 "Rules: " + run["rule_revision_id"], "",
                 "## " + ("受阻及未确定事项" if zh else "Blockers and unknowns"), ""]
        for block in run.get("blockers", []):
            lines += [f"- {block['verdict']}: {block['title']} — {block['reason']}",
                      "  " + block.get("next_action", "")]
        lines += ["", "## " + ("人工记录" if zh else "User-recorded evidence"), ""]
        for claim in run.get("determinations", []):
            lines.append(f"- {claim['determiner']}: {claim['outcome']} — {claim['reference']}; "
                         + claim["basis"])
        lines += ["", "## " + ("复检变化" if zh else "Recheck changes"), "",
                  json.dumps(run.get("change_summary", {}), ensure_ascii=False, indent=2), "",
                  ("用户记录不是认证签署；结论仅适用于列明的版本、规则和范围。" if zh else
                   "User records are not authenticated signatures. Conclusions apply only to "
                   "the cited model, rules and scope."), ""]
        return "\n".join(lines)

    def close(self):
        self.jobs.close()
