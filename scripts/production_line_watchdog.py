#!/usr/bin/env python3
"""Classify the latest Mina-Video render workflow run without changing it."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp is required")
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def classify_latest_run(
    payload: dict[str, Any],
    *,
    now: datetime,
    stale_after_minutes: int = 30,
) -> dict[str, Any]:
    if stale_after_minutes < 1:
        raise ValueError("stale_after_minutes must be positive")
    runs = payload.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("workflow_runs must be a list")

    if not runs:
        return {
            "state": "IDLE",
            "incident": False,
            "severity": "INFO",
            "reason": "No render runs have been recorded; no action was taken.",
        }

    valid_runs = [run for run in runs if isinstance(run, dict) and run.get("created_at")]
    if not valid_runs:
        return {
            "state": "UNKNOWN",
            "incident": True,
            "severity": "ATTENTION",
            "reason": "Render run records are missing usable identity or timestamps.",
        }

    latest = max(valid_runs, key=lambda run: parse_time(run["created_at"]))
    status = str(latest.get("status", "")).strip().lower()
    conclusion = str(latest.get("conclusion") or "").strip().lower()
    started = latest.get("run_started_at") or latest.get("created_at")
    age_minutes = max(0, int((now.astimezone(timezone.utc) - parse_time(started)).total_seconds() // 60))

    base = {
        "run_id": latest.get("id"),
        "run_url": latest.get("html_url", ""),
        "branch": latest.get("head_branch", ""),
        "head_sha": latest.get("head_sha", ""),
        "status": status,
        "conclusion": conclusion,
        "age_minutes": age_minutes,
    }

    if status in {"queued", "in_progress"}:
        stale = age_minutes >= stale_after_minutes
        return {
            **base,
            "state": "STALE" if stale else "RUNNING",
            "incident": stale,
            "severity": "BLOCKING" if stale else "INFO",
            "reason": (
                f"Latest render run has remained {status} for {age_minutes} minutes."
                if stale
                else f"Latest render run is {status} and within the {stale_after_minutes}-minute observation window."
            ),
        }

    if status == "completed" and conclusion in {"success", "skipped"}:
        return {
            **base,
            "state": "HEALTHY" if conclusion == "success" else "SKIPPED",
            "incident": False,
            "severity": "INFO",
            "reason": f"Latest render run completed with conclusion {conclusion}.",
        }

    if status == "completed" and conclusion in {"failure", "timed_out", "action_required", "cancelled"}:
        severity = "ATTENTION" if conclusion == "cancelled" else "BLOCKING"
        return {
            **base,
            "state": "DEGRADED",
            "incident": True,
            "severity": severity,
            "reason": f"Latest render run completed with conclusion {conclusion}.",
        }

    return {
        **base,
        "state": "UNKNOWN",
        "incident": True,
        "severity": "ATTENTION",
        "reason": f"Unrecognized render run state: status={status or 'missing'}, conclusion={conclusion or 'missing'}.",
    }


def write_report(report: dict[str, Any], *, summary_path: str, output_path: str, report_path: str) -> None:
    Path(report_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Mina-Video Production Line Health",
        "",
        f"- State: **{report.get('state', 'UNKNOWN')}**",
        f"- Incident: **{str(bool(report.get('incident'))).lower()}**",
        f"- Severity: **{report.get('severity', 'ATTENTION')}**",
        f"- Reason: {report.get('reason', 'No reason provided.')}",
    ]
    if report.get("run_url"):
        lines.extend([
            f"- Latest run: {report['run_url']}",
            f"- Branch: {report.get('branch', '')}",
            f"- Commit: {report.get('head_sha', '')}",
            f"- Age (minutes): {report.get('age_minutes', '')}",
        ])
    Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(output_path).write_text(f"incident={'true' if report.get('incident') else 'false'}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-file", required=True)
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--report-file", required=True)
    parser.add_argument("--now")
    parser.add_argument("--stale-after-minutes", type=int, default=30)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs_file).read_text(encoding="utf-8"))
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    report = classify_latest_run(payload, now=now, stale_after_minutes=args.stale_after_minutes)
    write_report(
        report,
        summary_path=args.summary_file,
        output_path=args.output_file,
        report_path=args.report_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
