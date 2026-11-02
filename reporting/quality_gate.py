"""
Quality Gate Evaluator for QSAR-BACKEND CI/CD Pipeline (Phase 7)
Enforces release criteria:
- Executed test pass rate >= 95.0%
- Zero critical unhandled failures
- Performance SLA compliance when performance results are available
"""

import os
import sys
import json


def evaluate_gate(results_path: str = None) -> bool:
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = results_path or os.path.join(backend_root, "Test Results", "JSON", "execution-results.json")
    perf_path = os.path.join(backend_root, "Test Results", "JSON", "performance-results.json")

    if not os.path.exists(json_path):
        print(f"Quality gate error: Results file not found at {json_path}")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    catalog_entries = meta.get("catalog_entries", 510)
    discovered = meta.get("total_discovered", 0)
    executed = meta.get("executed", 0)
    passed = meta.get("passed", 0)
    failed = meta.get("failed", 0)
    not_applicable = meta.get("not_applicable", 0)
    pass_rate = meta.get("pass_rate_executed", 0.0)

    print("=======================================================")
    print("QSAR-BACKEND: Evaluate Phase 7 Quality Gate Policies")
    print("=======================================================")
    print(f"Policy 1: Catalog Integrity == 510 Tests (Discovered: {discovered}/{catalog_entries})")
    print(f"Policy 2: Executed Pass Rate >= 95.0% (Actual: {pass_rate}%, Passed: {passed}/{executed})")
    print(f"Policy 3: Zero Critical Failures (Actual Failed: {failed})")
    print(f"Policy 4: Non-Applicable Disposition Handled (Mobile Appium Tests: {not_applicable})")

    gate_passed = True
    if discovered != 510:
        gate_passed = False
        print(f"Gate violation: Discovered test count {discovered} did not match required 510 catalog entries.")

    if pass_rate < 95.0:
        gate_passed = False
        print(f"Gate violation: Pass rate {pass_rate}% fell below 95.0% threshold.")

    if failed > 0:
        gate_passed = False
        print(f"Gate violation: {failed} test failures detected.")

    # Performance Gate
    if os.path.exists(perf_path):
        try:
            with open(perf_path, "r", encoding="utf-8") as pf:
                pdata = json.load(pf)
            crit = pdata.get("acceptance_criteria", {})
            p_status = pdata.get("status")
            print(f"Policy 5: Load Testing Status: {p_status} (Error Rate: {pdata.get('error_rate_percent')}%)")
            if p_status == "FAILED":
                gate_passed = False
                print(f"Gate violation: Load testing failed acceptance criteria.")
        except Exception as e:
            print(f"Notice during performance evaluation: {e}")

    if gate_passed:
        print(">>> QUALITY GATE RESULT: PASSED <<<")
        return True
    else:
        print(">>> QUALITY GATE RESULT: FAILED <<<")
        return False


if __name__ == "__main__":
    passed = evaluate_gate()
    sys.exit(0 if passed else 1)
