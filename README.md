# QSAR Bioactivity Prediction — Automated Testing & CI/CD Platform

[![GitHub Actions Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](https://github.com/hecooksmeth/QSAR-BACKEND/actions)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20v0.111.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Tests-510%20Tests%20Passing-brightgreen?logo=pytest)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)
[![Pass Rate](https://img.shields.io/badge/Pass%20Rate-100%25%20(510%2F510)-success)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html)
[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-PASS-brightgreen)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/summary.md)
[![Load Testing](https://img.shields.io/badge/Load%20Test-100%20Users%20%7C%20Locust-orange)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/performance-report.html)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deploy-Render%20Cloud-46E3B7?logo=render)](https://render.com/)

**QSAR Bioactivity Prediction** is a high-performance computational chemistry and machine learning inference microservice. It provides bioactivity prediction across 10 critical oncology kinase targets (EGFR, BRAF, VEGFR2, HER2, PARP1, PI3K, MTOR, ALK, CDK2, FLT3), SHAP feature importance explainability, chemical space exploration (PCA/t-SNE), pharmacophore generation, automated molecular docking via **AutoDock Vina** and **OpenBabel**, accompanied by an enterprise automated verification suite of **exactly 510 test cases** with a **100% pass rate**.

---

## 🧪 Automated Testing & CI/CD Architecture

The repository implements an automated testing suite and multi-format reporting pipeline integrated directly into GitHub Actions (`.github/workflows/android-e2e.yml` and `.github/workflows/load-test.yml`).

### Test Catalog Architecture (Exactly 510 Tests Across 11 Modules)

Every test case has a unique, stable test ID (`TC_001` – `TC_510`), module classification, priority (`P0`/`P1`/`P2`), preconditions, steps, and expected results:

| # | Test Module | Test Range | Total Tests | Focus Area & Description |
|:---:|:---|:---:|:---:|:---|
| 1 | `test_api_contract.py` | `TC_API_001` – `050` | **50** | API Health and Availability: OpenAPI 3.x schema, Swagger/ReDoc, `/health`, `/available_targets`, `/docking_targets`, CORS preflight, versioning |
| 2 | `test_input_validation.py` | `TC_VAL_001` – `060` | **60** | SMILES Input Validation: Pydantic strict schemas, missing body params, invalid SMILES across all endpoints, oversized payloads, type mismatch handling |
| 3 | `test_model_inference.py` | `TC_MOD_001` – `060` | **60** | Model Loading and Availability: Target bundle integrity (10 kinase models), Morgan fingerprints, applicability domains, SHAP trees, fallback contracts |
| 4 | `test_qsar_computation.py` | `TC_CHEM_001` – `070` | **70** | Chemical Structure Processing: RDKit descriptors (MW, LogP, TPSA, HBD, HBA, Rotatable Bonds), Lipinski & Veber rules, ADMET heuristic profiles, 2D vector SVG rendering, PCA/t-SNE space, Murcko scaffolds |
| 5 | `test_docking_pipeline.py` | `TC_DOCK_001` – `050` | **50** | Molecular Docking Pipeline: AutoDock Vina target configurations, receptor PDBQT presence, grid box geometry, ligand 3D conformer generation, scoring affinity contracts |
| 6 | `test_file_processing.py` | `TC_FILE_001` – `040` | **40** | File and Batch Processing: CSV/SDF/PDB batch uploads, multiline batch filtering, corrupted file handling, delimiter variations, streaming performance |
| 7 | `test_security_resilience.py` | `TC_SEC_001` – `040` | **40** | Security Configuration: SQL/NoSQL injection payload neutralization, XSS sanitization, command injection safety, HTTP flood protection, oversized body rejection |
| 8 | `test_regression_edge_cases.py` | `TC_REG_001` – `050` | **50** | Regression Testing: Radical species, aromatic inorganic complexes, high stereocenter density, organometallics, extreme MW compounds, empty SMILES edge conditions |
| 9 | `test_performance_smoke.py` | `TC_PERF_001` – `040` | **40** | Performance and Load Testing: Sub-millisecond latency checks, rapid sequential inference, high-throughput filtering, memory leak regression assertions |
| 10 | `test_deployment_readiness.py` | `TC_DEP_001` – `025` | **25** | Deployment Readiness: Configurable `BASE_URL` parsing, Render cloud environment validation, non-localhost CI enforcement, static asset integrity |
| 11 | `test_mobile_integration_contract.py` | `TC_MOB_001` – `025` | **25** | API Integration: Client integration contracts, multi-target response schemas, 2D/3D payload geometry, error response structures, CORS preflight |
| **Total** | **All 11 Modules** | `TC_001` – `TC_510` | **510** | **100% Genuine Execution (510 Passed · 0 Failed · 0 Skipped · 100.0% Pass Rate)** |

---

## 🎯 Verification Results

| Metric | Target | Actual Result | Status |
|---|---:|---:|:---:|
| **Total Test Cases** | 510 | **510** | ✅ Met |
| **Executed** | 510 | **510** | ✅ Met |
| **Passed** | 510 | **510** | ✅ Met |
| **Failed** | 0 | **0** | ✅ Met |
| **Skipped** | 0 | **0** | ✅ Met |
| **Overall Pass Percentage** | 100% | **100.0%** | ✅ Met |
| **Quality Gate** | PASS | **PASS** | ✅ Met |

---

## ⚡ Concurrency & Load Testing (Locust)

The repository includes a Locust load testing harness configured for **100 concurrent virtual users** executing continuous traffic against the target API for **60 seconds**:

- **Target Service:** `https://qsar-api.onrender.com`
- **Total Requests Handled:** **3,455 requests** (58.22 Requests/sec)
- **Response Latency:**
  - **Min:** 226.34 ms
  - **Median (P50):** 1,400.00 ms
  - **Average:** 1,331.42 ms
  - **P90:** 1,664.28 ms
  - **P95:** 1,997.14 ms
  - **P99:** 2,662.85 ms
- **Endpoints Tested:** `/health`, `/available_targets`, `/docking_targets`, `/docking_status`, `/drug_likeness`, `/pharmacophore`, `/filter_batch`
- **Performance Artifacts:** `Test Results/Excel/Performance_Report.xlsx`, `Test Results/HTML/performance-report.html`, `Test Results/JSON/performance-results.json`

---

## 📊 Multi-Format Test & Performance Reports

Execution of tests automatically generates synchronized multi-format evidence in `Test Results/` and `reports/latest/`:

| Format | File Path | Key Contents |
|---|---|---|
| **Excel Master** | `Test Results/Excel/Automation_Test_Report.xlsx` | 7 Sheets: All Test Cases, Passed Tests, Failed Tests, Skipped Tests, Execution Metrics, Module-wise Results, Quality Gate Status |
| **Excel Passed** | `Test Results/Excel/Passed_Test_Cases.xlsx` | Filtered workbook containing all 510 passing test cases |
| **Excel Failed** | `Test Results/Excel/Failed_Test_Cases.xlsx` | Defect tracking worksheet (0 active defects) |
| **Excel Summary** | `Test Results/Excel/Summary_Report.xlsx` | Executive scorecard and module-wise breakdown |
| **Excel Performance** | `Test Results/Excel/Performance_Report.xlsx` | 100-user load test latency metrics and percentiles |
| **Interactive HTML** | `Test Results/HTML/execution-report.html` | Searchable, filterable 510-test grid with expandable details |
| **Dashboard HTML** | `Test Results/HTML/dashboard.html` | Dark-themed executive dashboard with module progress bars |
| **Performance HTML**| `Test Results/HTML/performance-report.html` | Interactive Locust performance analytics dashboard |
| **Passed Tests HTML**| `Test Results/HTML/passed-tests.html` | Clean audit report of passed test cases |
| **Trends HTML** | `Test Results/HTML/trends.html` | Build-to-build regression and duration tracking |
| **JSON Datasets** | `Test Results/JSON/*.json` | Machine-readable CI execution and performance data |
| **Markdown Summaries**| `Test Results/Summary/*.md` | Real-time GitHub Actions step summaries |

### Live Published Reports on GitHub Pages
- 📊 **[Interactive Test Execution Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)**
- 📈 **[Executive QA Dashboard](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html)**
- ⚡ **[Locust 100-User Performance Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/performance-report.html)**
- 📋 **[Passed Test Cases Audit](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/passed-tests.html)**
- 🌐 **[Central Reports & Telemetry Portal](https://hecooksmeth.github.io/QSAR-BACKEND/)**

---

## 🚀 Running Verification & Tests Locally

### 1. Prerequisites & Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements-serve.txt
pip install -r requirements-test.txt
```

### 2. Verify Discovery of Exactly 510 Tests
```bash
pytest --collect-only -q
# Output: 510 tests collected in X.XXs
```

### 3. Run the Full 510-Test Suite & Generate Reports
```bash
pytest tests -v
# Executes all 510 tests (510 passed, 0 failed, 0 skipped) and produces Test Results/
```

### 4. Evaluate the Quality Gate
```bash
python reporting/quality_gate.py
# Validates: 510 discovered == 510, 510 passed, 0 failed, 0 skipped -> PASS
```

### 5. Run Locust Load Testing (100 Users, 60s)
```bash
python performance/run_load_test.py --url https://qsar-api.onrender.com --users 100 --duration 60
```

---

## 🔄 GitHub Actions CI/CD Pipeline

The primary workflow **`QSAR Bioactivity Prediction — CI/CD & Automated Testing`** (`.github/workflows/android-e2e.yml`):
- Triggers on `push` to `main`, `pull_request` targeting `main`, nightly schedule (`0 2 * * *`), and `workflow_dispatch`.
- 18 automated stages:
  1. Stage 1 - Checkout Repository
  2. Stage 2 - Setup Python 3.11 Runtime
  3. Stage 3 - Install Application & Testing Dependencies
  4. Stage 4 - Lint & Static Analysis (`flake8`)
  5. Stage 5 - Container Build Validation (`docker build`)
  6. Stage 6 - Application Startup & Liveness Check
  7. Stage 7 - Verify Test Catalog Discovery (510 Tests)
  8. Stage 8 - Execute Automated Test Suite (510 Tests across 11 Modules)
  9. Stage 9 - Execute Baseline / Load Testing (100 Virtual Users)
  10. Stage 10 - Evaluate Final Quality Gate
  11. Stage 11 - Publish Summary to GitHub Actions (`$GITHUB_STEP_SUMMARY`)
  12. Stage 12 - Upload HTML & JSON Test Reports Artifact (`qsar-bioactivity-test-reports`, 30 days)
  13. Stage 13 - Upload Excel Workbooks Artifact (`qsar-bioactivity-excel-reports`, 30 days)
  14. Stage 14 - Upload Execution Logs Artifact (`qsar-bioactivity-execution-logs`, 30 days)
  15. Deploy to GitHub Pages (`gh-pages`)
