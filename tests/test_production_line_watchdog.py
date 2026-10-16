import unittest
from datetime import datetime, timezone

from scripts.production_line_watchdog import classify_latest_run, parse_time


class ProductionLineWatchdogTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)

    def run_record(self, *, status="completed", conclusion="success", age_minutes=5):
        created = datetime.fromtimestamp(self.now.timestamp() - age_minutes * 60, timezone.utc)
        stamp = created.isoformat().replace("+00:00", "Z")
        return {
            "id": 42,
            "html_url": "https://github.com/MENA1983/Mina-Video/actions/runs/42",
            "head_branch": "main",
            "head_sha": "a" * 40,
            "status": status,
            "conclusion": conclusion,
            "created_at": stamp,
            "run_started_at": stamp,
        }

    def test_no_runs_is_idle_not_a_false_incident(self):
        report = classify_latest_run({"workflow_runs": []}, now=self.now)
        self.assertEqual(report["state"], "IDLE")
        self.assertFalse(report["incident"])

    def test_successful_latest_run_is_healthy(self):
        report = classify_latest_run({"workflow_runs": [self.run_record()]}, now=self.now)
        self.assertEqual(report["state"], "HEALTHY")
        self.assertFalse(report["incident"])

    def test_failed_latest_run_creates_blocking_incident(self):
        report = classify_latest_run(
            {"workflow_runs": [self.run_record(conclusion="failure")]}, now=self.now
        )
        self.assertEqual(report["state"], "DEGRADED")
        self.assertTrue(report["incident"])
        self.assertEqual(report["severity"], "BLOCKING")

    def test_old_in_progress_run_is_stale(self):
        report = classify_latest_run(
            {"workflow_runs": [self.run_record(status="in_progress", conclusion="", age_minutes=31)]},
            now=self.now,
        )
        self.assertEqual(report["state"], "STALE")
        self.assertTrue(report["incident"])

    def test_recent_in_progress_run_is_not_flagged(self):
        report = classify_latest_run(
            {"workflow_runs": [self.run_record(status="in_progress", conclusion="", age_minutes=10)]},
            now=self.now,
        )
        self.assertEqual(report["state"], "RUNNING")
        self.assertFalse(report["incident"])

    def test_newer_success_supersedes_older_failure_for_current_health(self):
        older = self.run_record(conclusion="failure", age_minutes=60)
        newer = self.run_record(conclusion="success", age_minutes=1)
        newer["id"] = 43
        report = classify_latest_run({"workflow_runs": [older, newer]}, now=self.now)
        self.assertEqual(report["run_id"], 43)
        self.assertEqual(report["state"], "HEALTHY")

    def test_unrecognized_state_fails_closed(self):
        report = classify_latest_run(
            {"workflow_runs": [self.run_record(status="mystery", conclusion="") ]},
            now=self.now,
        )
        self.assertEqual(report["state"], "UNKNOWN")
        self.assertTrue(report["incident"])

    def test_invalid_run_payload_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_latest_run({}, now=self.now)

    def test_timestamp_requires_timezone(self):
        with self.assertRaises(ValueError):
            parse_time("2026-10-16T12:00:00")


if __name__ == "__main__":
    unittest.main()
