"""
Locust Performance & Load Testing Specification for QSAR-BACKEND
Simulates 100 concurrent computational chemists and bioinformaticians
querying QSAR prediction, molecular docking metadata, and cheminformatics endpoints.
"""

import random
from locust import HttpUser, task, between


SAMPLE_SMILES = [
    "CC(=O)Oc1ccccc1C(=O)O",                # Aspirin
    "Cn1cnc2c1c(=O)n(c(=O)n2C)C",           # Caffeine
    "CC(=O)Nc1ccc(O)cc1",                   # Paracetamol
    "CC(C)Cc1ccc(cc1)C(C)C(=O)O",           # Ibuprofen
    "COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1"  # Gefitinib
]

TARGETS = ["EGFR", "BRAF", "VEGFR2", "HER2", "PARP1", "PI3K", "MTOR", "ALK", "CDK2", "FLT3"]


class QSARUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(25)
    def health_check(self):
        self.client.get("/health", name="[GET] /health")

    @task(15)
    def available_targets(self):
        self.client.get("/available_targets", name="[GET] /available_targets")

    @task(15)
    def docking_targets(self):
        self.client.get("/docking_targets", name="[GET] /docking_targets")

    @task(10)
    def docking_status(self):
        self.client.get("/docking_status", name="[GET] /docking_status")

    @task(20)
    def drug_likeness(self):
        smi = random.choice(SAMPLE_SMILES)
        self.client.post("/drug_likeness", json={"smiles": smi}, name="[POST] /drug_likeness")

    @task(10)
    def pharmacophore(self):
        smi = random.choice(SAMPLE_SMILES)
        self.client.post("/pharmacophore", json={"smiles": smi}, name="[POST] /pharmacophore")

    @task(5)
    def filter_batch(self):
        self.client.post("/filter_batch", json={"smiles_list": SAMPLE_SMILES[:3], "filters": {}}, name="[POST] /filter_batch")

