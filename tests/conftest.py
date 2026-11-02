"""
Pytest configuration for QSAR-BACKEND
Provides FastAPI TestClient fixture and records execution telemetry for multi-format reporting.
"""

import os
import sys
import time
import pytest
from typing import List, Dict, Any

# Ensure backend root is on sys.path
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import qsar_api
from fastapi.testclient import TestClient
from reporting.report_generator import generate_all_reports

EXECUTION_RECORDS: List[Dict[str, Any]] = []


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Session-scoped FastAPI test client."""
    return TestClient(qsar_api.app)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" or (report.when == "setup" and report.skipped):
        test_id = getattr(item, "test_id", None)
        if not test_id:
            test_id = item.name.split("[")[0]

        mod_name = getattr(item, "custom_module", None)
        if not mod_name:
            module = getattr(item, "module", None)
            if hasattr(module, "__name__"):
                mod_name = module.__name__
            elif isinstance(module, str):
                mod_name = module
            else:
                mod_name = item.nodeid.split("/")[1].replace(".py", "") if "/" in item.nodeid else "General"

        if mod_name.startswith("test_"):
            mod_name = mod_name.replace("test_", "").replace("_", " ").title()

        priority = getattr(item, "priority", "P2")
        name = getattr(item, "test_name", item.name)

        if report.passed:
            status = "PASSED"
            failure_reason = None
        elif report.skipped:
            was_blocked = getattr(item, "is_blocked", False)
            status = "BLOCKED" if was_blocked else "SKIPPED"
            failure_reason = getattr(item, "blocked_reason", report.longreprtext if report.longrepr else "Skipped")
        else:
            status = "FAILED"
            failure_reason = str(report.longrepr) if report.longrepr else "AssertionError"

        record = {
            "test_id": test_id,
            "module": mod_name,
            "name": name,
            "priority": priority,
            "status": status,
            "duration_sec": round(report.duration, 4),
            "failure_reason": failure_reason,
            "blocked_reason": getattr(item, "blocked_reason", None),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        EXECUTION_RECORDS.append(record)


def pytest_sessionfinish(session, exitstatus):
    print(f"\n[QSAR-BACKEND] Session finished. Generating reports for {len(EXECUTION_RECORDS)} test records...")
    try:
        generate_all_reports(EXECUTION_RECORDS)
        print("[QSAR-BACKEND] Reports generated successfully in Test Results/")
    except Exception as e:
        print(f"[QSAR-BACKEND] Report generation notice: {e}")
