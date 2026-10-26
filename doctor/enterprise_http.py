"""The enterprise project routes, using the server's existing origin/body boundary."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

from doctor.import_jobs import ImportBusy

POST_TYPES = {
    "/api/projects/rules/preview": "application/octet-stream",
    "/api/projects/rules/confirm": "application/json",
    "/api/projects/source": "application/octet-stream",
    "/api/projects/purpose/runs": "application/json",
    "/api/projects/purpose/jobs/cancel": "application/json",
    "/api/projects/purpose/determinations": "application/json",
}
GET_PATHS = {
    "/api/projects/rules", "/api/projects/rules/detail", "/api/projects/rules/example",
    "/api/projects/purpose", "/api/projects/purpose/jobs", "/api/projects/purpose/run",
    "/api/projects/purpose/brief",
}


def get(handler, service, path, query, send_json, send_payload):
    def arg(key):
        return (query.get(key) or [""])[0]
    library = service.library
    if path == "/api/projects/rules":
        answer = library.rules(arg("project"))
    elif path == "/api/projects/rules/detail":
        answer = library.rule(arg("rule_revision"))
    elif path == "/api/projects/purpose":
        answer = library.summary(arg("project"))
    elif path == "/api/projects/purpose/jobs":
        answer = service.jobs.get(arg("job"))
    elif path == "/api/projects/purpose/run":
        answer = library.run(arg("run"))
    elif path == "/api/projects/rules/example":
        from tools.enterprise_rules_example import example_package

        _download(handler, example_package(), "application/zip", "enterprise-rules-example.zip")
        return
    elif path == "/api/projects/purpose/brief":
        _download(handler, service.brief(arg("run"), arg("language") or "en").encode(),
                  "text/markdown; charset=utf-8", "purpose-review-brief.md")
        return
    else:
        raise KeyError("Unknown enterprise project endpoint.")
    send_json(handler, 200, answer)


def _download(handler, payload, content_type, filename):
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Request-ID", handler.request_id)
    handler.end_headers()
    handler.wfile.write(payload)


def post(handler, service, path, length, send_json):
    query = parse_qs(urlsplit(handler.path).query)
    def arg(key):
        return (query.get(key) or [""])[0]
    library = service.library
    from internal.doctor_adapter.enterprise_package import MAX_PACKAGE_BYTES

    limit = library.projects.reviews.max_model_bytes if path == "/api/projects/source" \
        else MAX_PACKAGE_BYTES if path.endswith("/preview") else 1024 * 1024
    if length > limit:
        handler.close_connection = True
        send_json(handler, 413, {"error": "The enterprise request exceeds its input limit."})
        return
    body = handler.rfile.read(length)
    if len(body) != length:
        raise ValueError("The enterprise upload was incomplete.")
    if path.endswith("/preview"):
        answer = library.preview(arg("project"), arg("filename"), body)
    elif path == "/api/projects/source":
        answer = library.attach_source(arg("revision"), arg("filename"), body)
    else:
        request = json.loads(body)
        if not isinstance(request, dict):
            raise ValueError("Enterprise request must be a JSON object.")
        if path == "/api/projects/rules/confirm":
            answer = library.confirm(
                request.get("project_id"), request.get("preview_id"),
                confirmed_by=request.get("confirmed_by"),
                responsible_team=request.get("responsible_team"),
            )
        elif path == "/api/projects/purpose/runs":
            try:
                answer = service.submit(request)
            except ImportBusy as error:
                send_json(handler, 409, {"error": str(error), "active_job_id": error.job_id})
                return
            send_json(handler, 202, answer)
            return
        elif path.endswith("/jobs/cancel"):
            answer = service.jobs.cancel(request.get("job_id"))
        elif path == "/api/projects/purpose/determinations":
            answer = library.determination(
                request.get("run_id"), request.get("evidence_id"),
                subject_keys=request.get("subject_keys", []), outcome=request.get("outcome"),
                method_id=request.get("method_id"), determiner=request.get("determiner"),
                basis=request.get("basis"), reference=request.get("reference"),
                context_digest=request.get("context_digest"),
            )
        else:
            raise KeyError("Unknown enterprise project endpoint.")
    send_json(handler, 200, answer)
