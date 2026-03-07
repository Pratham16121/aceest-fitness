"""
Run pytest programmatically and collect results for UI display.
"""
import pytest


class ResultsCollector:
    """Pytest plugin that collects test outcomes for each test."""

    def __init__(self):
        self.results = []
        self.summary = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
        self.exitstatus = 0

    def pytest_runtest_logreport(self, report):
        if report.when != "call":
            return
        self.results.append(
            {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration": getattr(report, "duration", 0),
                "message": str(report.longrepr) if report.longrepr else None,
            }
        )
        if report.outcome in self.summary:
            self.summary[report.outcome] += 1

    def pytest_sessionfinish(self, session, exitstatus):
        self.exitstatus = exitstatus


def run_tests():
    """Run pytest on tests/ and return collected results and summary."""
    collector = ResultsCollector()
    pytest.main(
        ["tests/", "-v", "--tb=short", "-q", "--no-header"],
        plugins=[collector],
    )
    return {
        "results": collector.results,
        "summary": collector.summary,
        "total": len(collector.results),
        "passed": collector.summary["passed"],
        "failed": collector.summary["failed"],
        "skipped": collector.summary["skipped"],
        "all_passed": collector.exitstatus == 0,
    }
