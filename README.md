# QSAR-BACKEND — AI-Driven Chemoinformatics & Molecular Docking Engine

[![GitHub Actions Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github-actions)](https://github.com/hecooksmeth/QSAR-BACKEND/actions)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20v0.111.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deploy-Render%20Cloud-46E3B7?logo=render)](https://render.com/)

**QSAR-BACKEND** is a high-performance computational chemistry and bioactivity prediction microservice developed for the **ResistAI** drug discovery platform. It provides machine learning inference across 10 critical oncology kinase targets, SHAP feature importance explainability, chemical space exploration (PCA/t-SNE), pharmacophore generation, and automated molecular docking using **AutoDock Vina** and **OpenBabel**.

---

## 📚 DevOps, CI/CD & Automation Documentation

For detailed engineering reports on our continuous integration pipelines, mobile automation suites, security audits, and report publishing, explore our technical documentation under [`docs/`](file:///c:/final_year_project/backend/docs/README.md):

| Report Title | Workflow | Status | Description & Link |
| :--- | :--- | :---: | :--- |
| **ResistAI — Android Appium E2E Automation & CI/CD Pipeline** | [`android-e2e.yml`](file:///c:/final_year_project/backend/.github/workflows/android-e2e.yml) | 🟢 Active | 21-stage macOS pipeline, Android 13 emulator, 510 Appium tests, 7-sheet Excel & interactive HTML reports. [**Read Report**](file:///c:/final_year_project/backend/docs/android-appium-e2e-cicd.md) |
| **ResistAI — Backend Security Review & DevSecOps Audit** | [`security-review.yml`](file:///c:/final_year_project/backend/.github/workflows/security-review.yml) | 🟡 Proposed | Bandit Python SAST, pip-audit dependency scanner, TruffleHog secrets detection, container security audit. [**Read Report**](file:///c:/final_year_project/backend/docs/backend-security-devsecops-audit.md) |
| **ResistAI — CI/CD Build · Deploy · E2E Selenium Tests** | [`ci-cd-e2e.yml`](file:///c:/final_year_project/backend/.github/workflows/ci-cd-e2e.yml) | 🟡 Proposed | Multi-stage Docker build, Render deployment webhook, post-deployment synthetic health probes. [**Read Report**](file:///c:/final_year_project/backend/docs/cicd-build-deploy-selenium-e2e.md) |
| **ResistAI — Deploy Mobile Automation Reports to GitHub Pages** | [`deploy-reports.yml`](file:///c:/final_year_project/backend/.github/workflows/deploy-reports.yml) | 🟢 Active | Decoupled report publishing pipeline, artifact packaging, `gh-pages` synchronization, and live web portal. [**Read Report**](file:///c:/final_year_project/backend/docs/mobile-automation-github-pages.md) |

👉 **[Access the Full Documentation Portal](file:///c:/final_year_project/backend/docs/README.md)**

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

pip install -r requirements.txt
uvicorn qsar_api:app --host 0.0.0.0 --port 8080 --reload
```

### 2. Docker Container Execution
```bash
docker build -t qsar-backend:latest .
docker run -p 8080:8080 qsar-backend:latest
```

---

## ☁️ Cloud Deployment Configuration

The repository is configured for automated cloud deployment to **Render** via [`render.yaml`](file:///c:/final_year_project/backend/render.yaml):
- **Service Name:** `qsar-api`
- **Runtime:** `python:3.11.0`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn qsar_api:app --host 0.0.0.0 --port $PORT`
