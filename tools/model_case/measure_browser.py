"""Wrap the real browser case with independent server-process memory sampling.

  python tools/model_case/measure_browser.py private-config.json --pid <server-pid>
The config names a private output_dir and the authorized source IFC. Install
the repository's pinned QA Playwright dependency and browser before this tool.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

from memory import MemorySampler


def stage_memory(samples, start, end):
    if start is None or end is None:
        return None
    prior = [sample for sample in samples if sample["epoch_ms"] <= start]
    selected = [sample for sample in samples if start <= sample["epoch_ms"] <= end]
    after = next((sample for sample in samples if sample["epoch_ms"] >= end), None)
    if prior:
        selected.insert(0, prior[-1])
    if after:
        selected.append(after)
    if not selected:
        return None
    baseline = selected[0]["rss_bytes"]
    return {
        "baseline_rss_bytes": baseline,
        "sampled_peak_rss_bytes": max(sample["rss_bytes"] for sample in selected),
        "sampled_peak_delta_bytes": max(s["rss_bytes"] for s in selected) - baseline,
        "end_rss_bytes": selected[-1]["rss_bytes"], "sample_count": len(selected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--node", default="node")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    output = Path(config["output_dir"]).resolve()
    checkout = Path(__file__).resolve().parents[2]
    if output.is_relative_to(checkout):
        parser.error("Raw evidence must be outside checkout")
    output.mkdir(parents=True, exist_ok=True)
    label = config["label"]
    sampler = MemorySampler(args.pid)
    sampler.start()
    while len(sampler.samples) < 10 and not sampler.errors:
        time.sleep(0.01)
    baseline_count = len(sampler.samples)
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [args.node, str(Path(__file__).with_name("browser.cjs")), str(args.config)],
            capture_output=True, check=False,
        )
    finally:
        sampler.stop()
    (output / f"{label}-browser-stdout.txt").write_bytes(completed.stdout)
    (output / f"{label}-browser-stderr.txt").write_bytes(completed.stderr)
    browser_file = output / f"{label}-browser.json"
    browser = (
        json.loads(browser_file.read_text(encoding="utf-8")) if browser_file.exists() else {}
    )
    phases = browser.get("phases", {})
    result = {
        "schema_version": 1, "label": label, "context": config.get("context"),
        "server_pid": args.pid, "browser_exit_code": completed.returncode,
        "browser_process_wall_ms": (time.perf_counter() - started) * 1000,
        "memory": sampler.summary(baseline_count),
        "pre_browser_baseline_private_bytes": statistics.median(
            sample["private_bytes"] for sample in sampler.samples[:baseline_count]
            if sample["private_bytes"] is not None
        ) if sampler.samples[0]["private_bytes"] is not None else None,
        "stages": {
            "upload_through_browser_geometry_ready": stage_memory(
                sampler.samples, phases.get("upload_start_epoch_ms"),
                phases.get("geometry_ready_epoch_ms"),
            ),
            "save_revision_snapshot": stage_memory(
                sampler.samples, phases.get("save_start_epoch_ms"),
                phases.get("save_end_epoch_ms"),
            ),
        },
        "samples": sampler.samples,
        "scope": "50ms sampled operation peaks; OS lifetime peak is reported separately. "
                 "Server RSS is not browser heap or GPU memory.",
    }
    (output / f"{label}-server-memory.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8",
    )
    public = {key: result[key] for key in ("label", "context", "browser_exit_code", "memory",
                                         "stages")}
    print(json.dumps(public, indent=2))
    if completed.returncode:
        print("Browser run failed. Inspect its private stderr file; no raw paths are printed.")
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
