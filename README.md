# QSAR-BACKEND — AI-Driven Chemoinformatics & Molecular Docking Engine

[![GitHub Actions Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](https://github.com/hecooksmeth/QSAR-BACKEND/actions)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20v0.111.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Tests-55%20Tests%20Passing-brightgreen?logo=pytest)](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deploy-Render%20Cloud-46E3B7?logo=render)](https://render.com/)

**QSAR-BACKEND** is a high-performance computational chemistry and bioactivity prediction microservice developed for the **ResistAI** drug discovery platform. It provides machine learning inference across 10 critical oncology kinase targets, SHAP feature importance explainability, chemical space exploration (PCA/t-SNE), pharmacophore generation, and automated molecular docking using **AutoDock Vina** and **OpenBabel**.

---

## 🧪 Automated Testing & Continuous Integration (Phase 7)

The repository features an enterprise-grade automated testing suite and multi-format evidence reporting pipeline integrated directly into GitHub Actions (`.github/workflows/ci-cd-e2e.yml`).

### Test Suite Architecture (55 Tests / 5 Modules)
- **API Contract & Discovery (`test_api_contract.py` — 10 Tests):** Validates OpenAPI 3.x schema generation, `/health`, `/available_targets`, `/docking_targets`, Swagger UI (`/docs`), ReDoc (`/redoc`), CORS preflight, and application release versioning.
- **Input Validation & Security Boundaries (`test_input_validation.py` — 15 Tests):** Enforces strict Pydantic schemas, handles missing parameters, tests invalid SMILES across all endpoints, malformed JSON, and verifies standard HTTP 400/404/422 responses.
- **QSAR Computation & Cheminformatics (`test_qsar_computation.py` — 15 Tests):** Validates RDKit molecule parsing (Aspirin, Caffeine, Paracetamol), Lipinski Rule of 5, Veber rules, ADMET heuristic profiles, 2D vector SVG generation, PCA chemical space projection, similarity searches with Tanimoto coefficients, pharmacophore feature extraction, and Murcko scaffold decomposition.
- **Model Inference & Explainability (`test_model_inference.py` — 10 Tests):** Validates target bundle contracts, Morgan fingerprint generation (2048-bit bit-vectors), isolated inference with mocked bundles, applicability domain distance thresholding, SHAP tree explainability, and 503 fallback when no models are loaded.
- **Live Deployment & Integration (`test_live_backend.py` — 5 Tests):** Validates configurable `BASE_URL` parsing, strictly enforces non-localhost endpoints in CI, explicitly documents Selenium web UI non-applicability for pure REST microservices, verifies live cloud probes, and asserts quality gate threshold rules.

### Running Tests Locally
```bash
# Install dependencies
pip install -r requirements-serve.txt
pip install -r requirements-test.txt

# Run full test suite and automatically generate reports in Test Results/
pytest tests -v

# Run quality gate verification
python reporting/quality_gate.py
```

### Multi-Format Test Reports Generated
Executing the test suite automatically produces multi-format evidence in `Test Results/` and synchronizes with `reports/latest/`:
- **Excel Comprehensive Workbook:** `Test Results/Excel/Automation_Test_Report.xlsx` (6 Worksheets: Executive Summary, Test Suite Details, Module Breakdown, Severity Analysis, Performance Metrics, Execution Environment)
- **Passed Test Cases Workbook:** `Test Results/Excel/Passed_Test_Cases.xlsx` (Filtered view with 100% pass rate)
- **Failed Test Cases Workbook:** `Test Results/Excel/Failed_Test_Cases.xlsx`
- **Interactive HTML Test Report:** `Test Results/HTML/execution-report.html` (Searchable, filterable by status/priority, expandable stack traces)
- **Executive Dashboard:** `Test Results/HTML/dashboard.html`
- **Pass-Only HTML Report:** `Test Results/HTML/passed-tests.html` (Labeled "FILTERED REPORT — PASSED TEST CASES ONLY")
- **JSON Telemetry Datasets:** `Test Results/JSON/execution-results.json` and `passed-tests.json`
- **Markdown Summaries:** `Test Results/Summary/summary.md` and `passed-summary.md` (Published to `$GITHUB_STEP_SUMMARY`)

### Live Published Reports on GitHub Pages
- 📊 **[Interactive Test Execution Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/execution-report.html)**
- 📈 **[Executive QA Dashboard](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/dashboard.html)**
- 📋 **[Filtered Passed-Only Report](https://hecooksmeth.github.io/QSAR-BACKEND/reports/latest/passed-tests.html)**

---

## 📚 DevOps, CI/CD & Automation Documentation

For detailed engineering reports on our continuous integration pipelines, security audits, and report publishing, explore our technical documentation under [`docs/`](docs/README.md):

| Report Title | Workflow | Status | Description & Link |
| :--- | :--- | :---: | :--- |
| **ResistAI — Complete Enterprise CI/CD Pipeline & Automated Test Suite** | [`ci-cd-e2e.yml`](.github/workflows/ci-cd-e2e.yml) | 🟢 Active | 19-stage pipeline, Python 3.11, Docker build, 55 automated tests, multi-format Excel/HTML/JSON reports, Render deploy webhook, and GitHub Pages publishing. |
| **ResistAI — Backend Security Review & DevSecOps Audit** | [`security-review.yml`](.github/workflows/security-review.yml) | 🟡 Proposed | Bandit Python SAST, pip-audit dependency scanner, TruffleHog secrets detection, container security audit. [**Read Report**](docs/backend-security-devsecops-audit.md) |
| **ResistAI — Deploy Automation Reports to GitHub Pages** | [`deploy-reports.yml`](.github/workflows/deploy-reports.yml) | 🟢 Active | Decoupled report publishing pipeline, artifact packaging, `gh-pages` synchronization, and live web portal. [**Read Report**](docs/mobile-automation-github-pages.md) |

---

## 🔬 Core Capabilities & API Endpoints

The backend is built with FastAPI and RDKit, exposing RESTful endpoints:

- **Target Prediction:** `POST /predict_target` — Evaluates molecular SMILES against specific kinase models (EGFR, BRAF, VEGFR2, HER2, PARP1, PI3K, MTOR, ALK, CDK2, FLT3) and returns bioactivity probabilities and pIC50 estimates.
- **Multi-Target Profiling:** `POST /predict_all` — Evaluates a compound simultaneously across all 10 kinase targets.
- **Explainable AI (XAI):** `POST /explain_prediction` — Computes SHAP (SHapley Additive exPlanations) values to highlight molecular substructures driving prediction.
- **Automated Molecular Docking:** `POST /dock` — Prepares 3D ligands via RDKit, converts structures via OpenBabel, and executes receptor-ligand docking via AutoDock Vina with configurable timeouts (`OBABEL_TIMEOUT_SECONDS=120`, `VINA_TIMEOUT_SECONDS=600`).
- **Chemical Space & Diversity:** `POST /chemical_space` — Computes PCA and t-SNE projections from Morgan molecular fingerprints.
- **Drug-Likeness Scoring:** `POST /drug_likeness` — Evaluates Lipinski's Rule of Five (MW, LogP, HBD, HBA, TPSA).
- **System Health:** `GET /health` — Liveness and model availability probe.

---

## 🐳 Quick Start & Local Execution

### 1. Local Python Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements-serve.txt
pip install -r requirements-test.txt
uvicorn qsar_api:app --host 0.0.0.0 --port 8080 --reload
```

### 2. Docker Container Execution
```bash
docker build -t qsar-backend:latest .
docker run -p 8080:8080 qsar-backend:latest
```

---

## ☁️ Cloud Deployment Configuration

The repository is configured for automated cloud deployment to **Render** via [`render.yaml`](render.yaml):
- **Service Name:** `qsar-api`
- **Runtime:** `python:3.11.0`
- **Build Command:** `pip install -r requirements-serve.txt`
- **Start Command:** `uvicorn qsar_api:app --host 0.0.0.0 --port $PORT`
