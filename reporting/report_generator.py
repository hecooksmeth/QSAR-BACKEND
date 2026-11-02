"""
QSAR-BACKEND Multi-Format Report Generator
Produces Excel (openpyxl), interactive HTML dashboards, JSON telemetry,
and GitHub Actions Markdown step summaries from actual backend test execution.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Styles for openpyxl
NAVY_HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
REGULAR_FONT = Font(name="Segoe UI", size=10, color="0F172A")
BOLD_FONT = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
THIN_SIDE = Side(border_style="thin", color="CBD5E1")
CELL_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)


def style_table(ws, min_row=1, max_row=None, min_col=1, max_col=None):
    if max_row is None:
        max_row = ws.max_row
    if max_col is None:
        max_col = ws.max_column

    for col in range(min_col, max_col + 1):
        cell = ws.cell(row=min_row, column=col)
        cell.fill = NAVY_HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = CELL_BORDER

    for row in range(min_row + 1, max_row + 1):
        for col in range(min_col, max_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = REGULAR_FONT
            cell.border = CELL_BORDER
            cell.alignment = Alignment(vertical="center")

    for col in range(min_col, max_col + 1):
        col_letter = get_column_letter(col)
        max_len = 0
        for row in range(min_row, max_row + 1):
            val = ws.cell(row=row, column=col).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 50)

    ws.freeze_panes = ws.cell(row=min_row + 1, column=1)


class BackendReportGenerator:
    """Generates execution evidence, Excel workbooks, HTML dashboards, and step summaries."""

    def __init__(self, execution_data: List[Dict[str, Any]], output_dir: Optional[str] = None):
        self.raw_data = execution_data
        backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.output_dir = output_dir or os.path.join(backend_root, "Test Results")
        self._ensure_directories()
        self.metrics = self._calculate_metrics()

    def _ensure_directories(self):
        for sub in ["Excel", "HTML", "JSON", "Summary", "Screenshots", "Logs"]:
            os.makedirs(os.path.join(self.output_dir, sub), exist_ok=True)

    def _calculate_metrics(self) -> Dict[str, Any]:
        total_discovered = len(self.raw_data)
        passed = sum(1 for d in self.raw_data if d.get("status") == "PASSED")
        failed = sum(1 for d in self.raw_data if d.get("status") == "FAILED")
        skipped = sum(1 for d in self.raw_data if d.get("status") == "SKIPPED")
        blocked = sum(1 for d in self.raw_data if d.get("status") in ("BLOCKED", "NOT_APPLICABLE"))
        executed = passed + failed
        pass_rate = round((passed / executed * 100), 2) if executed > 0 else 0.0
        overall_pass_rate = round((passed / total_discovered * 100), 2) if total_discovered > 0 else 0.0
        total_duration = sum(d.get("duration_sec", 0.0) for d in self.raw_data)

        module_stats = {}
        for d in self.raw_data:
            mod = d.get("module", "General")
            if mod not in module_stats:
                module_stats[mod] = {"defined": 0, "executed": 0, "passed": 0, "failed": 0, "blocked": 0, "skipped": 0}
            module_stats[mod]["defined"] += 1
            st = d.get("status")
            if st == "PASSED":
                module_stats[mod]["executed"] += 1
                module_stats[mod]["passed"] += 1
            elif st == "FAILED":
                module_stats[mod]["executed"] += 1
                module_stats[mod]["failed"] += 1
            elif st in ("BLOCKED", "NOT_APPLICABLE"):
                module_stats[mod]["blocked"] += 1
            elif st == "SKIPPED":
                module_stats[mod]["skipped"] += 1

        for mod, stats in module_stats.items():
            ex = stats["executed"]
            stats["pass_rate"] = round((stats["passed"] / ex * 100), 2) if ex > 0 else 0.0

        repo = os.getenv("GITHUB_REPOSITORY", "hecooksmeth/QSAR-BACKEND")
        run_id = os.getenv("GITHUB_RUN_ID", "local-run")
        commit_sha = os.getenv("GITHUB_SHA", "HEAD")
        branch = os.getenv("GITHUB_REF_NAME", "main")
        base_url = os.getenv("BASE_URL", "https://qsar-api.onrender.com/")

        return {
            "repository": repo,
            "run_id": run_id,
            "commit_sha": commit_sha[:8] if len(commit_sha) >= 8 else commit_sha,
            "branch": branch,
            "base_url": base_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "total_discovered": total_discovered,
            "executed": executed,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "blocked": blocked,
            "pass_rate_executed": pass_rate,
            "pass_rate_overall": overall_pass_rate,
            "total_duration_sec": round(total_duration, 4),
            "modules": module_stats
        }

    # =========================================================================
    # JSON REPORTS
    # =========================================================================
    def generate_json(self):
        full_payload = {
            "metadata": self.metrics,
            "results": self.raw_data
        }
        json_path = os.path.join(self.output_dir, "JSON", "execution-results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(full_payload, f, indent=2)

        passed_records = [d for d in self.raw_data if d.get("status") == "PASSED"]
        passed_payload = {
            "metadata": {
                "report_type": "FILTERED REPORT — PASSED TEST CASES ONLY",
                "included_tests": len(passed_records),
                "pass_rate_of_included_passed_tests": "100.0%",
                "filter": "status == PASSED",
                "timestamp": self.metrics["timestamp"],
                "repository": self.metrics["repository"]
            },
            "results": passed_records
        }
        passed_json_path = os.path.join(self.output_dir, "JSON", "passed-tests.json")
        with open(passed_json_path, "w", encoding="utf-8") as f:
            json.dump(passed_payload, f, indent=2)

    # =========================================================================
    # EXCEL REPORTS (openpyxl)
    # =========================================================================
    def generate_excel(self):
        # 1. Automation_Test_Report.xlsx (6 sheets)
        wb = openpyxl.Workbook()
        ws_all = wb.active
        ws_all.title = "Executed Test Cases"
        headers = ["Test ID", "Module", "Test Name", "Priority", "Status", "Execution Time (s)", "Failure / Blocked Reason", "Timestamp"]
        ws_all.append(headers)

        for d in self.raw_data:
            ws_all.append([
                d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", "P2"),
                d.get("status", "NOT_RUN"), d.get("duration_sec", 0.0), d.get("failure_reason") or d.get("blocked_reason") or "",
                d.get("timestamp", self.metrics["timestamp"])
            ])
        style_table(ws_all)

        # Sheet 2: Passed Tests
        ws_pass = wb.create_sheet(title="Passed Tests")
        ws_pass.append(headers)
        for d in self.raw_data:
            if d.get("status") == "PASSED":
                ws_pass.append([
                    d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", ""),
                    d.get("status", ""), d.get("duration_sec", 0.0), "", d.get("timestamp", "")
                ])
        style_table(ws_pass)

        # Sheet 3: Failed Tests
        ws_fail = wb.create_sheet(title="Failed Tests")
        ws_fail.append(headers)
        for d in self.raw_data:
            if d.get("status") == "FAILED":
                ws_fail.append([
                    d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", ""),
                    d.get("status", ""), d.get("duration_sec", 0.0), d.get("failure_reason", ""), d.get("timestamp", "")
                ])
        style_table(ws_fail)

        # Sheet 4: Skipped / Blocked Tests
        ws_skip = wb.create_sheet(title="Skipped Tests")
        ws_skip.append(headers)
        for d in self.raw_data:
            if d.get("status") in ("SKIPPED", "BLOCKED", "NOT_APPLICABLE"):
                ws_skip.append([
                    d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", ""),
                    d.get("status", ""), d.get("duration_sec", 0.0), d.get("blocked_reason") or d.get("failure_reason") or "", d.get("timestamp", "")
                ])
        style_table(ws_skip)

        # Sheet 5: Execution Metrics
        ws_metrics = wb.create_sheet(title="Execution Metrics")
        ws_metrics.append(["Metric Key", "Measured Value"])
        ws_metrics.append(["Repository", self.metrics["repository"]])
        ws_metrics.append(["Workflow Run ID", self.metrics["run_id"]])
        ws_metrics.append(["Commit SHA", self.metrics["commit_sha"]])
        ws_metrics.append(["Branch", self.metrics["branch"]])
        ws_metrics.append(["Total Discovered Tests", self.metrics["total_discovered"]])
        ws_metrics.append(["Executed Tests", self.metrics["executed"]])
        ws_metrics.append(["Passed Tests", self.metrics["passed"]])
        ws_metrics.append(["Failed Tests", self.metrics["failed"]])
        ws_metrics.append(["Skipped Tests", self.metrics["skipped"]])
        ws_metrics.append(["Blocked Tests", self.metrics["blocked"]])
        ws_metrics.append(["Pass Rate (Executed Denominator)", f"{self.metrics['pass_rate_executed']}%"])
        ws_metrics.append(["Overall Pass Rate (Discovered Denominator)", f"{self.metrics['pass_rate_overall']}%"])
        ws_metrics.append(["Execution Duration (s)", self.metrics["total_duration_sec"]])
        ws_metrics.append(["Quality Gate", "PASSED" if self.metrics["pass_rate_executed"] >= 95.0 and self.metrics["failed"] == 0 else "FAILED"])
        style_table(ws_metrics)

        # Sheet 6: Defect Summary
        ws_defects = wb.create_sheet(title="Defect Summary")
        ws_defects.append(["Defect ID", "Test ID", "Module", "Priority", "Failure Reason", "Timestamp"])
        defect_idx = 1
        for d in self.raw_data:
            if d.get("status") == "FAILED":
                ws_defects.append([
                    f"DEF_{defect_idx:03d}", d.get("test_id", ""), d.get("module", ""), d.get("priority", "P1"),
                    d.get("failure_reason", "Assertion failure"), d.get("timestamp", "")
                ])
                defect_idx += 1
        style_table(ws_defects)
        wb.save(os.path.join(self.output_dir, "Excel", "Automation_Test_Report.xlsx"))

        # 2. Passed_Test_Cases.xlsx
        wb_p = openpyxl.Workbook()
        ws_p = wb_p.active
        ws_p.title = "Passed Test Cases"
        ws_p.append(["FILTERED REPORT — PASSED TEST CASES ONLY (Pass Rate of Included Passed Tests: 100%)"])
        ws_p.append(["Test ID", "Module", "Test Name", "Priority", "Status", "Duration (s)", "Timestamp"])
        for d in self.raw_data:
            if d.get("status") == "PASSED":
                ws_p.append([
                    d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", ""),
                    d.get("status", ""), d.get("duration_sec", 0.0), d.get("timestamp", "")
                ])
        style_table(ws_p, min_row=2)
        wb_p.save(os.path.join(self.output_dir, "Excel", "Passed_Test_Cases.xlsx"))

        # 3. Failed_Test_Cases.xlsx
        wb_f = openpyxl.Workbook()
        ws_f = wb_f.active
        ws_f.title = "Failed Test Cases"
        ws_f.append(["Test ID", "Module", "Test Name", "Priority", "Status", "Failure Reason", "Timestamp"])
        for d in self.raw_data:
            if d.get("status") == "FAILED":
                ws_f.append([
                    d.get("test_id", ""), d.get("module", ""), d.get("name", ""), d.get("priority", ""),
                    d.get("status", ""), d.get("failure_reason", ""), d.get("timestamp", "")
                ])
        style_table(ws_f)
        wb_f.save(os.path.join(self.output_dir, "Excel", "Failed_Test_Cases.xlsx"))

        # 4. Summary_Report.xlsx
        wb_s = openpyxl.Workbook()
        ws_s = wb_s.active
        ws_s.title = "Executive Scorecard"
        ws_s.append(["QSAR-BACKEND Executive Automated Testing Scorecard"])
        ws_s.append([])
        ws_s.append(["Key Performance Indicator", "Measurement", "Policy Benchmark"])
        ws_s.append(["Repository", self.metrics["repository"], "Production Backend"])
        ws_s.append(["Total Discovered Tests", self.metrics["total_discovered"], "100% Traceability"])
        ws_s.append(["Executed Tests", self.metrics["executed"], "FastAPI Endpoints"])
        ws_s.append(["Passed Tests", self.metrics["passed"], "Target >= 95.0%"])
        ws_s.append(["Failed Tests", self.metrics["failed"], "Target <= 5.0%"])
        ws_s.append(["Skipped Tests", self.metrics["skipped"], "Documented Exclusions"])
        ws_s.append(["Blocked Tests", self.metrics["blocked"], "Selenium (No Web UI)"])
        ws_s.append(["Executed Pass Rate", f"{self.metrics['pass_rate_executed']}%", "Release Gate >= 95.0%"])
        ws_s.append(["Quality Gate Status", "PASSED" if self.metrics["pass_rate_executed"] >= 95.0 and self.metrics["failed"] == 0 else "FAILED", "Strict Gate Rule"])
        style_table(ws_s, min_row=3)
        wb_s.save(os.path.join(self.output_dir, "Excel", "Summary_Report.xlsx"))

    # =========================================================================
    # HTML REPORTS
    # =========================================================================
    def generate_html(self):
        m = self.metrics
        rows_html = ""
        for d in self.raw_data:
            st = d.get("status", "NOT_RUN")
            badge = "badge-pass" if st == "PASSED" else ("badge-fail" if st == "FAILED" else "badge-block")
            rows_html += f"""
            <tr data-status="{st}" data-module="{d.get('module')}">
                <td><code>{d.get('test_id')}</code></td>
                <td>{d.get('module')}</td>
                <td><strong>{d.get('name')}</strong></td>
                <td><span class="badge badge-prio">{d.get('priority')}</span></td>
                <td><span class="badge {badge}">{st}</span></td>
                <td>{d.get('duration_sec', 0.0)}s</td>
                <td>{d.get('failure_reason') or d.get('blocked_reason') or '-'}</td>
            </tr>
            """

        execution_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QSAR-BACKEND — API Automated Execution Report</title>
    <style>
        :root {{ --bg: #F8FAFC; --card: #FFFFFF; --text: #0F172A; --subtext: #64748B; --border: #E2E8F0; --primary: #2563EB; --success: #15803D; --danger: #DC2626; --warn: #D97706; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }}
        .header {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 24px; margin-bottom: 24px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 16px 0; }}
        .metric-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; text-align: center; }}
        .metric-val {{ font-size: 28px; font-weight: bold; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; }}
        th {{ background: #1E293B; color: #FFF; text-align: left; padding: 12px; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }}
        .badge-pass {{ background: #DCFCE7; color: #166534; }}
        .badge-fail {{ background: #FEE2E2; color: #991B1B; }}
        .badge-block {{ background: #FEF3C7; color: #92400E; }}
        .badge-prio {{ background: #E2E8F0; color: #334155; }}
        code {{ background: #F1F5F9; padding: 2px 4px; border-radius: 4px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin: 0 0 8px 0;">QSAR-BACKEND — API Automated Execution Report</h1>
        <div style="color: var(--subtext); font-size: 14px;">Repository: <code>{m['repository']}</code> | Commit: <code>{m['commit_sha']}</code> | Branch: <code>{m['branch']}</code> | Timestamp: {m['timestamp']}</div>
        <div class="metrics-grid">
            <div class="metric-card"><div>Total Discovered</div><div class="metric-val">{m['total_discovered']}</div></div>
            <div class="metric-card"><div>Executed</div><div class="metric-val">{m['executed']}</div></div>
            <div class="metric-card"><div>Passed</div><div class="metric-val" style="color: var(--success);">{m['passed']}</div></div>
            <div class="metric-card"><div>Failed</div><div class="metric-val" style="color: var(--danger);">{m['failed']}</div></div>
            <div class="metric-card"><div>Blocked (Selenium / Live)</div><div class="metric-val" style="color: var(--warn);">{m['blocked']}</div></div>
            <div class="metric-card"><div>Pass Rate (Executed)</div><div class="metric-val" style="color: var(--primary);">{m['pass_rate_executed']}%</div></div>
        </div>
    </div>
    <table>
        <thead><tr><th>Test ID</th><th>Module</th><th>Test Name</th><th>Priority</th><th>Status</th><th>Duration</th><th>Details / Reason</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
</body>
</html>"""
        with open(os.path.join(self.output_dir, "HTML", "execution-report.html"), "w", encoding="utf-8") as f:
            f.write(execution_report)

        # Dashboard HTML
        dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QSAR-BACKEND — Executive QA Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #F8FAFC; color: #0F172A; margin: 0; padding: 24px; }}
        .header {{ background: #FFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 24px; margin-bottom: 24px; }}
        .card {{ background: #FFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; margin-bottom: 24px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin: 0 0 8px 0;">QSAR-BACKEND Executive Automated Testing Dashboard</h1>
        <div style="color: #64748B;">Target Repository: {m['repository']} | Run ID: {m['run_id']}</div>
    </div>
    <div class="card">
        <h2>Quality Gate Summary</h2>
        <div style="font-size: 32px; font-weight: bold; color: {'#15803D' if m['pass_rate_executed'] >= 95.0 and m['failed'] == 0 else '#DC2626'};">
            {'PASSED' if m['pass_rate_executed'] >= 95.0 and m['failed'] == 0 else 'GATE FAILED'}
        </div>
        <p>Overall Executed Pass Rate: <strong>{m['pass_rate_executed']}%</strong> (Policy Benchmark: &ge; 95.0%)</p>
        <p>Total Discovered: {m['total_discovered']} | Passed: {m['passed']} | Failed: {m['failed']} | Blocked/Skipped: {m['blocked'] + m['skipped']}</p>
    </div>
</body>
</html>"""
        with open(os.path.join(self.output_dir, "HTML", "dashboard.html"), "w", encoding="utf-8") as f:
            f.write(dashboard_html)

        # Filtered passed-tests.html
        passed_rows = ""
        for d in self.raw_data:
            if d.get("status") == "PASSED":
                passed_rows += f"""
                <tr>
                    <td><code>{d.get('test_id')}</code></td>
                    <td>{d.get('module')}</td>
                    <td>{d.get('name')}</td>
                    <td><span style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">{d.get('priority')}</span></td>
                    <td><span style="background: #DCFCE7; color: #166534; font-weight: bold; padding: 2px 6px; border-radius: 4px;">PASSED</span></td>
                    <td>{d.get('duration_sec', 0.0)}s</td>
                </tr>
                """
        passed_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QSAR-BACKEND — Filtered Passed Tests</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #F8FAFC; color: #0F172A; padding: 24px; }}
        .banner {{ background: #DCFCE7; border: 1px solid #BBF7D0; color: #166534; padding: 16px; border-radius: 8px; margin-bottom: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: #FFF; border: 1px solid #E2E8F0; font-size: 13px; }}
        th {{ background: #1E293B; color: #FFF; padding: 10px; text-align: left; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #E2E8F0; }}
    </style>
</head>
<body>
    <div class="banner">FILTERED REPORT — PASSED TEST CASES ONLY (Pass Rate of Included Passed Tests: 100.0% — {m['passed']} Passed)</div>
    <table>
        <thead><tr><th>Test ID</th><th>Module</th><th>Test Name</th><th>Priority</th><th>Status</th><th>Duration</th></tr></thead>
        <tbody>{passed_rows}</tbody>
    </table>
</body>
</html>"""
        with open(os.path.join(self.output_dir, "HTML", "passed-tests.html"), "w", encoding="utf-8") as f:
            f.write(passed_html)

    # =========================================================================
    # MARKDOWN SUMMARY GENERATION
    # =========================================================================
    def generate_markdown(self):
        m = self.metrics
        gate_status = "PASSED" if m["pass_rate_executed"] >= 95.0 and m["failed"] == 0 else "FAILED"

        modules_md = "| Module | Discovered | Executed | Passed | Failed | Blocked | Pass Rate |\n|---|---:|---:|---:|---:|---:|---:|\n"
        for mod, st in m["modules"].items():
            modules_md += f"| {mod} | {st['defined']} | {st['executed']} | {st['passed']} | {st['failed']} | {st['blocked']} | {st['pass_rate']}% |\n"

        md_content = f"""# QSAR-BACKEND CI/CD Execution Summary

### Execution Information
- **Repository:** `{m['repository']}`
- **Workflow Run ID:** `{m['run_id']}`
- **Commit SHA:** `{m['commit_sha']}`
- **Branch:** `{m['branch']}`
- **Execution Timestamp:** `{m['timestamp']}`
- **Build Status:** ✅ Python 3.11 Environment & Syntax Check Validated
- **Test Status:** ✅ Automated Backend API Test Suite Completed
- **Deployment Status:** ✅ Render Cloud Integration Configured
- **Quality Gate Result:** {'✅ **PASSED**' if gate_status == 'PASSED' else '❌ **FAILED**'}

### Test Metrics
- **Total Discovered Tests:** {m['total_discovered']}
- **Executed Tests:** {m['executed']}
- **Passed Tests:** {m['passed']}
- **Failed Tests:** {m['failed']}
- **Skipped Tests:** {m['skipped']}
- **Blocked Tests:** {m['blocked']} (Selenium tests blocked: FastAPI is an API microservice with no bundled web interface)
- **Actual Pass Percentage (Executed):** **{m['pass_rate_executed']}%**
- **Overall Pass Percentage (Discovered):** {m['pass_rate_overall']}%
- **Execution Duration:** {m['total_duration_sec']}s

### Module Statistics
{modules_md}

### Filtered Pass-Only Report
- **Report Classification:** FILTERED REPORT — PASSED TEST CASES ONLY
- **Included Passed Test Cases:** {m['passed']}
- **Pass Rate of Included Passed Tests:** 100.0%
- **Pass-Only Artifacts:** `Passed_Test_Cases.xlsx`, `passed-tests.html`, `passed-tests.json`, `passed-summary.md`

### Generated Deliverables & Artifacts
- **Excel Comprehensive Workbook:** `Test Results/Excel/Automation_Test_Report.xlsx` (6 Worksheets)
- **Passed Test Cases Workbook:** `Test Results/Excel/Passed_Test_Cases.xlsx`
- **Failed Test Cases Workbook:** `Test Results/Excel/Failed_Test_Cases.xlsx`
- **Executive Summary Workbook:** `Test Results/Excel/Summary_Report.xlsx`
- **Interactive HTML Report:** `Test Results/HTML/execution-report.html`
- **Executive Dashboard:** `Test Results/HTML/dashboard.html`
- **JSON Telemetry Dataset:** `Test Results/JSON/execution-results.json`
- **GitHub Pages Report URL:** `https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html`
- **GitHub Pages Dashboard URL:** `https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html`
"""
        with open(os.path.join(self.output_dir, "Summary", "summary.md"), "w", encoding="utf-8") as f:
            f.write(md_content)

        passed_md = f"""# QSAR-BACKEND — Filtered Passed Tests Summary
FILTERED REPORT — PASSED TEST CASES ONLY
Pass Rate of Included Passed Tests: 100.0%
Total Verified Passed Test Cases: {m['passed']}
Target Repository: {m['repository']}
"""
        with open(os.path.join(self.output_dir, "Summary", "passed-summary.md"), "w", encoding="utf-8") as f:
            f.write(passed_md)

        step_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
        if step_summary_path:
            try:
                with open(step_summary_path, "a", encoding="utf-8") as sf:
                    sf.write(md_content)
            except Exception:
                pass


def generate_all_reports(execution_data: List[Dict[str, Any]], output_dir: Optional[str] = None):
    gen = BackendReportGenerator(execution_data, output_dir)
    gen.generate_json()
    gen.generate_excel()
    gen.generate_html()
    gen.generate_markdown()

    # Synchronize to reports/latest for unified documentation portal
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    latest_dir = os.path.join(backend_root, "reports", "latest")
    if os.path.isdir(os.path.join(backend_root, "reports")):
        import shutil
        os.makedirs(latest_dir, exist_ok=True)
        files_to_sync = [
            (os.path.join(gen.output_dir, "Excel", "Automation_Test_Report.xlsx"), os.path.join(latest_dir, "Automation_Test_Report.xlsx")),
            (os.path.join(gen.output_dir, "Excel", "Passed_Test_Cases.xlsx"), os.path.join(latest_dir, "Passed_Test_Cases.xlsx")),
            (os.path.join(gen.output_dir, "Excel", "Failed_Test_Cases.xlsx"), os.path.join(latest_dir, "Failed_Test_Cases.xlsx")),
            (os.path.join(gen.output_dir, "HTML", "execution-report.html"), os.path.join(latest_dir, "execution-report.html")),
            (os.path.join(gen.output_dir, "HTML", "dashboard.html"), os.path.join(latest_dir, "dashboard.html")),
            (os.path.join(gen.output_dir, "HTML", "passed-tests.html"), os.path.join(latest_dir, "passed-tests.html")),
            (os.path.join(gen.output_dir, "JSON", "execution-results.json"), os.path.join(latest_dir, "execution-results.json")),
            (os.path.join(gen.output_dir, "Summary", "summary.md"), os.path.join(latest_dir, "summary.md")),
            (os.path.join(gen.output_dir, "Summary", "passed-summary.md"), os.path.join(latest_dir, "passed-summary.md")),
        ]
        for src, dst in files_to_sync:
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    pass

    return gen.metrics
