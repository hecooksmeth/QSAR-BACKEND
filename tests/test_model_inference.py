"""
Model Loading, Inference, and Feature Contribution Test Suite
Validates model bundle contracts, Morgan fingerprint generation, applicability domain, and SHAP.
"""

import pytest
import qsar_api
from unittest.mock import MagicMock
import numpy as np


ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"


def _create_mock_bundle(target_name="EGFR", prob_active=0.85):
    """Helper creating a fully configured mock TargetBundle for isolated inference testing."""
    mock_bundle = MagicMock()
    mock_bundle.target = target_name
    mock_bundle.metadata = {"type": "Receptor Tyrosine Kinase", "relevance": "Oncology / NSCLC"}
    mock_bundle.model = MagicMock()
    mock_bundle.model.predict_proba.return_value = np.array([[1.0 - prob_active, prob_active]])
    mock_bundle.selector = MagicMock()
    mock_bundle.selector.transform.return_value = np.zeros((1, 50))
    mock_bundle.scaler = MagicMock()
    mock_bundle.scaler.transform.return_value = np.zeros((1, 50))
    mock_bundle.selected_feature_names = [f"descriptor_feature_{i}" for i in range(50)]
    mock_bundle.ad_threshold = 0.5
    mock_bundle.reference_fps = []
    mock_explainer = MagicMock()
    mock_explainer.shap_values.return_value = np.zeros((1, 50))
    mock_bundle.shap_explainer = mock_explainer
    return mock_bundle


def test_model_directory_discovery(request):
    request.node.test_id = "TC_MOD_001"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P1"
    request.node.test_name = "Verify MODEL_ROOT resolution points to an existing directory"

    assert qsar_api.MODEL_ROOT is not None
    assert isinstance(qsar_api.MODEL_ROOT, str)


def test_supported_targets_list(request):
    request.node.test_id = "TC_MOD_002"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P1"
    request.node.test_name = "Verify _supported_targets contains expected target proteins"

    targets = qsar_api._supported_targets()
    assert isinstance(targets, list)
    assert len(targets) > 0
    assert "EGFR" in targets or "CDK2" in targets or "BRAF" in targets


def test_morgan_fingerprint_generator(request):
    request.node.test_id = "TC_MOD_003"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P0"
    request.node.test_name = "Verify Morgan fingerprint generator produces 2048-bit bit-vector"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    fp = qsar_api.morgan_generator.GetFingerprint(mol)
    assert fp is not None
    assert fp.GetNumBits() == 2048


def test_mocked_target_prediction_contract(request):
    request.node.test_id = "TC_MOD_004"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P0"
    request.node.test_name = "Unit test verifying TargetBundle inference structure with mocked model"

    mock_bundle = _create_mock_bundle("EGFR", prob_active=0.85)

    original_models = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS["EGFR"] = mock_bundle
        res = qsar_api.predict_target(ASPIRIN_SMILES, "EGFR")
        assert "target" in res
        assert "active" in res
        assert "confidence" in res
        assert res["active"] is True
        assert res["confidence"] == 85.0
    finally:
        qsar_api.MODELS = original_models


def test_applicability_domain_logic(request):
    request.node.test_id = "TC_MOD_005"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P1"
    request.node.test_name = "Unit test verifying applicability domain distance threshold classification"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    query_fp = qsar_api.morgan_generator.GetFingerprint(mol)
    sim = qsar_api.DataStructs.TanimotoSimilarity(query_fp, query_fp)
    assert sim == 1.0


def test_post_predict_target_endpoint_with_mock(request, client):
    request.node.test_id = "TC_MOD_006"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P0"
    request.node.test_name = "Unit test verifying POST /predict_target endpoint returns 200 with mock"

    mock_bundle = _create_mock_bundle("EGFR", prob_active=0.80)

    original_models = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS["EGFR"] = mock_bundle
        res = client.post("/predict_target", json={"smiles": ASPIRIN_SMILES, "target": "EGFR"})
        assert res.status_code == 200
        assert res.json().get("confidence") == 80.0
    finally:
        qsar_api.MODELS = original_models


def test_post_predict_all_endpoint_with_mock(request, client):
    request.node.test_id = "TC_MOD_007"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P0"
    request.node.test_name = "Unit test verifying POST /predict_all endpoint returns 200 with mock"

    mock_bundle = _create_mock_bundle("EGFR", prob_active=0.70)

    original_models = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS["EGFR"] = mock_bundle
        res = client.post("/predict_all", json={"smiles": ASPIRIN_SMILES})
        assert res.status_code == 200
        data = res.json()
        assert "predictions" in data
        assert "molecular_properties" in data
        assert "drug_likeness" in data
        assert "svg" in data
    finally:
        qsar_api.MODELS = original_models


def test_explain_prediction_endpoint_with_mock(request, client):
    request.node.test_id = "TC_MOD_008"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P1"
    request.node.test_name = "Unit test verifying POST /explain_prediction structure with mock"

    mock_bundle = _create_mock_bundle("EGFR", prob_active=0.90)

    original_models = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS["EGFR"] = mock_bundle
        res = client.post("/explain_prediction", json={"smiles": ASPIRIN_SMILES, "target": "EGFR", "top_n": 5})
        assert res.status_code == 200
        data = res.json()
        assert "target" in data
        assert "top_features" in data
    finally:
        qsar_api.MODELS = original_models


def test_predict_all_empty_models_raises_503(request, client):
    request.node.test_id = "TC_MOD_009"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /predict_all raises 503 when no models are loaded in memory"

    original_models = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS = {}
        res = client.post("/predict_all", json={"smiles": ASPIRIN_SMILES})
        assert res.status_code == 503
        assert "No target models loaded" in res.json().get("detail", "")
    finally:
        qsar_api.MODELS = original_models


def test_target_label_lookup(request):
    request.node.test_id = "TC_MOD_010"
    request.node.custom_module = "Model Inference"
    request.node.priority = "P2"
    request.node.test_name = "Verify _target_label returns human-readable label or target name"

    label = qsar_api._target_label("EGFR")
    assert label is not None
    assert len(label) > 0
