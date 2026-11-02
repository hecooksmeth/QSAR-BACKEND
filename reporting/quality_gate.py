"""
Quality Gate Evaluator for QSAR-BACKEND CI/CD Pipeline
Enforces release criteria:
- Executed test pass rate >= 95.0%
- Zero critical unhandled failures
"""

import os
import sys
import json


def evaluate_gate(results_path: str = None) -> bool:
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_path = results_path or os.path.join(backend_root, "Test Results", "JSON", "execution-results.json")

    if not os.path.exists(json_path):
        print(f"Quality gate error: Results file not found at {json_path}")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    results = data.get("results", [])

    executed = meta.get("executed", 0)
    passed = meta.get("passed", 0)
    failed = meta.get("failed", 0)
    pass_rate = meta.get("pass_rate_executed", 0.0)

    print("=======================================================")
    print("QSAR-BACKEND: Evaluate Quality Gate Policies")
    print("=======================================================")
    print(f"Policy 1: Overall Executed Pass Rate >= 95.0% (Actual: {pass_rate}%, Passed: {passed}/{executed})")
    print(f"Policy 2: Zero Critical Failures (Actual Failed: {failed})")

    gate_passed = True
    if pass_rate < 95.0:
        gate_passed = False
        print(f"Gate violation: Pass rate {pass_rate}% fell below 95.0% threshold.")

    if failed > 0:
        gate_passed = False
        print(f"Gate violation: {failed} test failures detected.")

    if gate_passed:
        print(">>> QUALITY GATE RESULT: PASSED <<<")
        return True
    else:
        print(">>> QUALITY GATE RESULT: FAILED <<<")
        return False


if __name__ == "__main__":
    passed = evaluate_gate()
    sys.exit(0 if passed else 1)
