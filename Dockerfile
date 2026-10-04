# ── Stage: runtime ────────────────────────────────────────────────────────────
FROM python:3.11-slim

# System dependencies:
#   - RDKit / scientific Python stack: libxrender1 libxext6 libglib2.0-0 libsm6 libexpat1 gcc g++
#   - AutoDock Vina:                   autodock-vina
#   - OpenBabel (mol → pdbqt):         openbabel
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libxext6 \
    libglib2.0-0 \
    libsm6 \
    libexpat1 \
    gcc \
    g++ \
    autodock-vina \
    openbabel \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies first (layer cache friendly)
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

# Copy all backend source and model artifacts
COPY qsar_api.py .
COPY qsar_file.py .
COPY models/ ./models/
COPY data/ ./data/
COPY CHEMBL_DATASET.csv .
COPY qsar_model.h5 .
COPY scaler.pkl .
COPY selector.pkl .

# Copy docking package (Python module + vina_runner.py)
COPY docking/ ./docking/

# Copy receptor PDBQT files for all 10 targets
COPY proteins/ ./proteins/

# Cloud Run injects $PORT (default 8080); uvicorn reads it at runtime
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn qsar_api:app --host 0.0.0.0 --port ${PORT}"]
