"""
Quality Gate Evaluator for QSAR Bioactivity Prediction CI/CD Pipeline
Enforces release criteria:
- Exactly 510 unique test cases in catalog
- 100% test execution pass rate (510 passed, 0 failed, 0 skipped)
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
    catalog_entries = meta.get("catalog_entries", 510)
    discovered = meta.get("total_discovered", 0)
    executed = meta.get("executed", 0)
    passed = meta.get("passed", 0)
    failed = meta.get("failed", 0)
    skipped = meta.get("skipped", 0)
    blocked = meta.get("blocked", 0)
    pass_rate = meta.get("pass_rate_executed", 0.0)

    print("================================================================================")
    print(" QSAR Bioactivity Prediction — Quality Gate Policy Evaluation")
    print("================================================================================")
    print(f"Policy 1: Catalog Integrity == 510 Tests (Discovered: {discovered}/{catalog_entries})")
    print(f"Policy 2: Executed Pass Rate == 100.0% (Actual: {pass_rate}%, Passed: {passed}/{executed})")
    print(f"Policy 3: Zero Test Failures (Actual Failed: {failed})")
    print(f"Policy 4: Zero Skipped / Blocked Tests (Skipped: {skipped}, Blocked: {blocked})")

    gate_passed = True
    if discovered != 510:
        gate_passed = False
        print(f"Gate violation: Discovered test count {discovered} did not match required 510 catalog entries.")

    if executed != 510 or passed != 510:
        gate_passed = False
        print(f"Gate violation: Passed tests {passed}/510 did not meet 100% required target.")

    if failed > 0:
        gate_passed = False
        print(f"Gate violation: {failed} test failures detected.")

    if skipped > 0 or blocked > 0:
        gate_passed = False
        print(f"Gate violation: {skipped + blocked} skipped/blocked tests detected.")

    if gate_passed:
        print(">>> QUALITY GATE RESULT: PASS <<<")
        return True
    else:
        print(">>> QUALITY GATE RESULT: FAIL <<<")
        return False


if __name__ == "__main__":
    is_pass = evaluate_gate()
    sys.exit(0 if is_pass else 1)
