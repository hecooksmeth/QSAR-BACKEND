# QSAR-BACKEND — AI-Driven Chemoinformatics, Docking & Enterprise QA Engine

[![GitHub Actions Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](https://github.com/hecooksmeth/QSAR-BACKEND/actions)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20v0.111.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Tests-510%20Catalog%20Tests-brightgreen?logo=pytest)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)
[![Pass Rate](https://img.shields.io/badge/Pass%20Rate-100%25%20Executed-success)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html)
[![Load Testing](https://img.shields.io/badge/Load%20Test-100%20Users%20%7C%20Locust-orange)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/performance-report.html)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deploy-Render%20Cloud-46E3B7?logo=render)](https://render.com/)

**QSAR-BACKEND** is a high-performance computational chemistry and bioactivity prediction microservice developed for the **ResistAI** drug discovery platform. It provides machine learning inference across 10 critical oncology kinase targets, SHAP feature importance explainability, chemical space exploration (PCA/t-SNE), pharmacophore generation, automated molecular docking via **AutoDock Vina** and **OpenBabel**, accompanied by an enterprise-grade automated testing system featuring **510 test cases** and high-concurrency **Locust load testing**.

---

## 🧪 Comprehensive Automated Testing & CI/CD (Phase 7)

The repository implements an enterprise-grade automated testing suite, Locust concurrency benchmarks, and multi-format evidence reporting pipeline integrated directly into GitHub Actions (`.github/workflows/android-e2e.yml` and `.github/workflows/load-test.yml`).

### Test Catalog Architecture (Exactly 510 Test Cases / 11 Modules)

Every test case has a unique identifier, priority (`P0`/`P1`/`P2`), category tag, and structured documentation:

| # | Test Module | Test Range | Total Tests | Focus Area & Description |
|:---:|:---|:---:|:---:|:---|
| 1 | `test_api_contract.py` | `TC_API_001` – `050` | **50** | OpenAPI 3.x schema, Swagger/ReDoc, `/health`, `/available_targets`, `/docking_targets`, CORS preflight, versioning, header contracts |
| 2 | `test_input_validation.py` | `TC_VAL_001` – `060` | **60** | Pydantic strict schemas, missing body params, invalid SMILES across all endpoints, oversized payloads, type mismatch handling |
| 3 | `test_model_inference.py` | `TC_MOD_001` – `060` | **60** | Target bundle integrity (EGFR, BRAF, VEGFR2, HER2, PARP1, PI3K, AKT1, ALK, CDK2, FLT3), Morgan fingerprints, applicability domains, SHAP trees |
| 4 | `test_qsar_computation.py` | `TC_CHEM_001` – `070` | **70** | RDKit descriptors (MW, LogP, TPSA, HBD, HBA, Rotatable Bonds), Lipinski & Veber rules, ADMET heuristic profiles, 2D vector SVG rendering, PCA/t-SNE space, Murcko scaffolds, pharmacophore features |
| 5 | `test_docking_pipeline.py` | `TC_DOCK_001` – `050` | **50** | AutoDock Vina target configurations, receptor PDBQT presence, grid box geometry, ligand 3D conformer generation, scoring affinity contracts |
| 6 | `test_file_processing.py` | `TC_FILE_001` – `040` | **40** | CSV/SDF/PDB batch uploads, multiline batch filtering, corrupted file handling, delimiter variations, streaming performance |
| 7 | `test_security_resilience.py` | `TC_SEC_001` – `040` | **40** | SQL/NoSQL injection payload neutralization, XSS sanitization, command injection safety in docking runners, HTTP flood protection, oversized body rejection |
| 8 | `test_regression_edge_cases.py` | `TC_REG_001` – `050` | **50** | Radical species, aromatic inorganic complexes, high stereocenter density, organometallics, extreme MW compounds, empty SMILES edge conditions |
| 9 | `test_performance_smoke.py` | `TC_PERF_001` – `040` | **40** | Sub-millisecond latency checks, rapid sequential inference, high-throughput filtering, memory leak regression assertions |
| 10 | `test_deployment_readiness.py` | `TC_DEP_001` – `025` | **25** | Configurable `BASE_URL` parsing, Render cloud environment validation, non-localhost CI enforcement, static asset integrity |
| 11 | `test_mobile_integration_contract.py` | `TC_MOB_001` – `025` | **25** | REST contracts supporting mobile React Native/Expo client; 10 physical device Appium tests tagged `NOT_APPLICABLE`/`BLOCKED` with architectural decoupling justification |
| **Total** | **All 11 Modules** | `TC_001` – `TC_510` | **510** | **100% Discoverable via Pytest (500 Passed · 10 Mobile-Mapped Skipped · 0 Failed)** |

---

## ⚡ High-Concurrency Load Testing (Locust)

The repository includes a dedicated Locust load testing engine configured for **100 concurrent virtual users** executing continuous traffic against the target API for **60 seconds**:

- **Target Service:** `https://qsar-api.onrender.com`
- **Total Requests Generated:** **3,455 requests** (58.22 Requests/sec)
- **Measured Response Latency:**
  - **Min:** 226.34 ms
  - **Median (P50):** 1,400.00 ms
  - **Average:** 1,331.42 ms
  - **P90:** 1,664.28 ms
  - **P95:** 1,997.14 ms
  - **P99:** 2,662.85 ms
  - **Max:** 7,609.52 ms
- **Endpoints Exercised:** `/health`, `/available_targets`, `/docking_targets`, `/docking_status`, `/drug_likeness`, `/pharmacophore`, `/filter_batch`
- **Performance Artifacts:** `Test Results/Excel/Performance_Report.xlsx`, `Test Results/HTML/performance-report.html`, `Test Results/JSON/performance-results.json`

---

## 📊 Multi-Format Test & Performance Reports

Execution of tests and load testing automatically generates rich multi-format evidence in `Test Results/` and continuously synchronizes with `reports/latest/`:

| Format | File Path | Key Contents |
|---|---|---|
| **Excel Master** | `Test Results/Excel/Automation_Test_Report.xlsx` | 7 Sheets: Executive Summary, Test Suite Details, Module Breakdown, Severity Analysis, Performance Metrics, Execution Environment, Load Test Telemetry |
| **Excel Passed** | `Test Results/Excel/Passed_Test_Cases.xlsx` | Filtered workbook containing 500 successful test cases |
| **Excel Failed** | `Test Results/Excel/Failed_Test_Cases.xlsx` | Isolated defect register with failure details |
| **Excel Summary** | `Test Results/Excel/Summary_Report.xlsx` | Compact management summary workbook |
| **Excel Performance** | `Test Results/Excel/Performance_Report.xlsx` | 100-user load test latency metrics and percentiles |
| **Interactive HTML** | `Test Results/HTML/execution-report.html` | Searchable, filterable 510-test grid with expandable details |
| **Dashboard HTML** | `Test Results/HTML/dashboard.html` | Visual analytics with Donut pass/fail charts and module bars |
| **Performance HTML**| `Test Results/HTML/performance-report.html` | Full interactive Locust performance analytics dashboard |
| **Passed-Only HTML**| `Test Results/HTML/passed-tests.html` | Clean audit report of passed test cases |
| **Trends HTML** | `Test Results/HTML/trends.html` | Build-to-build regression and duration tracking |
| **JSON Datasets** | `Test Results/JSON/*.json` | Machine-readable CI execution and performance data |
| **Markdown Summaries**| `Test Results/Summary/*.md` | Real-time GitHub Actions step summaries |

### Live GitHub Pages Links
- 📊 **[Interactive Test Execution Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)**
- 📈 **[Executive QA Dashboard](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html)**
- ⚡ **[Locust 100-User Performance Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/performance-report.html)**
- 📋 **[Passed Test Cases Audit](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/passed-tests.html)**
- 🌐 **[Central Reports Portal](https://hecooksmeth.github.io/QSAR-BACKEND/)**

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
# Executes 500 passed, 10 skipped, 0 failed and produces Test Results/
```

### 4. Run Locust Load Testing (100 Users, 60s)
```bash
# Against live cloud deployment:
python performance/run_load_test.py --url https://qsar-api.onrender.com --users 100 --duration 60

# Quick 5-second smoke verification:
python performance/run_load_test.py --smoke
```

### 5. Evaluate the Enterprise Quality Gate
```bash
python reporting/quality_gate.py
# Validates >= 95% pass rate, 0 critical failures, and catalog completeness
```

---

## 🔄 GitHub Actions CI/CD Pipelines

The repository includes two continuous integration workflows:

1. **Master Test & Reporting Pipeline (`.github/workflows/android-e2e.yml`)**:
   - Triggers on `push` to `main`, `pull_request`, nightly cron (`0 2 * * *`), and `workflow_dispatch`.
   - 18 automated stages: Linting (`flake8`), Docker container build verification, fast startup probe, 510-test suite execution, Locust load testing, quality gate validation, 30-day artifact archival, and deployment to GitHub Pages (`gh-pages`).
2. **Dedicated Performance Load Test Workflow (`.github/workflows/load-test.yml`)**:
   - Triggers via `workflow_dispatch` with configurable inputs (`base_url`, `users`, `duration`, `spawn_rate`) or weekly Sunday schedule.
   - Executes Locust load test, compiles multi-format reports, publishes summary to GitHub Actions, and uploads 30-day downloadable artifacts.

---

## 🔬 Core API Capabilities

The backend exposes high-performance RESTful cheminformatics endpoints:

- `GET /health` — Microservice heartbeat and loaded model status
- `GET /available_targets` — List of 10 supported oncology kinase targets
- `POST /predict_target` — Evaluates molecular SMILES against a specific target
- `POST /predict_all` — Profiling against all 10 targets simultaneously
- `POST /explain_prediction` — Computes SHAP values and feature contributions
- `POST /dock` — Prepares 3D conformers and runs AutoDock Vina molecular docking
- `POST /docking_targets` — Lists receptor PDBQT targets and grid box coordinates
- `POST /chemical_space` — Generates PCA and t-SNE projections from Morgan fingerprints
- `POST /drug_likeness` — Computes Lipinski Rule of 5 and Veber drug-likeness metrics
- `POST /pharmacophore` — Detects hydrogen bond donors, acceptors, aromatics, and hydrophobes
- `POST /filter_batch` — High-throughput molecular property filtering across batches

---

## 🐳 Containerization & Deployment

```bash
# Build Docker container:
docker build -t qsar-backend:latest .

# Run container locally:
docker run -p 8080:8080 -e PORT=8080 qsar-backend:latest
```
Live Production Deployment: **[https://qsar-api.onrender.com](https://qsar-api.onrender.com)**
