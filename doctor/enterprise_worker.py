"""Single-use enterprise check and purpose assessment worker; never tessellates."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "input", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    stage = "starting"

    def emit(value):
        nonlocal stage
        stage = value
        print("BIMDOCTOR_IMPORT " + json.dumps({"stage": value}), flush=True)

    try:
        from internal.doctor_adapter.enterprise_rules import evaluate_rules, parse_package
        from internal.doctor_adapter.purpose_review import assess_evaluation

        context = json.loads((args.output / "context.json").read_bytes())
        metadata = context["metadata"]
        emit("parsing")
        package = parse_package(base64.b64decode(context["package_b64"]), "adopted.zip")
        emit("checking")
        evaluation = evaluate_rules(package, args.input.read_bytes(), context["report"],
                                    context["revision"]["model_id"])
        scope = dict(metadata["scope"])
        if scope["kind"] == "elements":
            mapping = {item.get("review_element_key"): item["element_key"]
                       for item in evaluation["elements"] if item.get("review_element_key")}
            scope["element_keys"] = sorted({mapping.get(key, key)
                                            for key in scope.get("element_keys", [])})
        emit("assessing")
        assessed = assess_evaluation(
            package, evaluation, project_id=metadata["project_id"],
            revision_id=metadata["revision_id"], purpose_id=metadata["purpose_id"],
            scope=scope, responsible_team=context["rule_revision"]["responsible_team"],
            determinations=context["determinations"], prior=context["prior"],
            consumer=context["consumer"],
        )
        rule = context["rule_revision"]
        rule_snapshot = {key: rule.get(key) for key in (
            "package_id", "title", "version", "source", "source_sha256",
            "confirmed_by", "responsible_team",
        )}
        purpose_snapshot = next(item for item in package.manifest["purposes"]
                                if item["purpose_id"] == metadata["purpose_id"])
        result = {**metadata, "scope": scope, "evaluation": evaluation,
                  "rule_snapshot": rule_snapshot, "purpose_snapshot": purpose_snapshot,
                  "determinations": context["determinations"], **assessed}
        emit("serializing")
        (args.output / "result.json").write_text(
            json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")),
            encoding="utf-8",
        )
        emit("complete")
        return 0
    except Exception as error:
        print("BIMDOCTOR_IMPORT " + json.dumps({"error": {
            "code": "purpose_check_failed", "stage": stage, "type": type(error).__name__,
            "message": str(error),
        }}), flush=True)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
