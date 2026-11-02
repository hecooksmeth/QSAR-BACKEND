"""
Input Validation and Error Response Suite
Validates schema enforcement, missing fields, and chemical syntax validation error boundaries.
"""

import pytest


def test_predict_all_missing_body(request, client):
    request.node.test_id = "TC_VAL_001"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /predict_all with missing payload returns 422 Unprocessable Entity"

    res = client.post("/predict_all")
    assert res.status_code == 422


def test_predict_all_empty_json(request, client):
    request.node.test_id = "TC_VAL_002"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /predict_all with empty JSON object returns 422 Unprocessable Entity"

    res = client.post("/predict_all", json={})
    assert res.status_code == 422


def test_predict_all_invalid_type(request, client):
    request.node.test_id = "TC_VAL_003"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P2"
    request.node.test_name = "Verify POST /predict_all with non-string SMILES field returns 422"

    res = client.post("/predict_all", json={"smiles": 123456})
    assert res.status_code == 422


def test_predict_all_invalid_smiles_string(request, client):
    request.node.test_id = "TC_VAL_004"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /predict_all with syntactically invalid SMILES returns HTTP 400"

    res = client.post("/predict_all", json={"smiles": "INVALID_CHEM_NOT_A_SMILES"})
    assert res.status_code == 400
    assert "Invalid SMILES" in res.json().get("detail", "")


def test_predict_target_missing_target_field(request, client):
    request.node.test_id = "TC_VAL_005"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /predict_target with missing target parameter returns 422"

    res = client.post("/predict_target", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    assert res.status_code == 422


def test_predict_target_invalid_smiles(request, client):
    request.node.test_id = "TC_VAL_006"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /predict_target with invalid chemical string returns 400 or 404"

    res = client.post("/predict_target", json={"smiles": "C123BAD_SMILES", "target": "EGFR"})
    assert res.status_code in (400, 404)


def test_explain_prediction_missing_smiles(request, client):
    request.node.test_id = "TC_VAL_007"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /explain_prediction with missing SMILES returns 422"

    res = client.post("/explain_prediction", json={"target": "EGFR", "top_n": 10})
    assert res.status_code == 422


def test_explain_prediction_invalid_smiles(request, client):
    request.node.test_id = "TC_VAL_008"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /explain_prediction with invalid SMILES returns 400 or 404"

    res = client.post("/explain_prediction", json={"smiles": "BAD_MOL_X", "target": "EGFR"})
    assert res.status_code in (400, 404)


def test_similarity_search_invalid_smiles(request, client):
    request.node.test_id = "TC_VAL_009"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /similarity_search with invalid SMILES returns 400"

    res = client.post("/similarity_search", json={"smiles": "NOT_A_SMILES_STRING", "top_n": 5})
    assert res.status_code == 400


def test_drug_likeness_invalid_smiles(request, client):
    request.node.test_id = "TC_VAL_010"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /drug_likeness with invalid SMILES returns 400"

    res = client.post("/drug_likeness", json={"smiles": "ERR_SYNTAX_123"})
    assert res.status_code == 400


def test_chemical_space_empty_list(request, client):
    request.node.test_id = "TC_VAL_011"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P2"
    request.node.test_name = "Verify POST /chemical_space with empty list handles request gracefully"

    res = client.post("/chemical_space", json={"smiles_list": [], "method": "pca"})
    assert res.status_code in (200, 400, 422)


def test_chemical_space_missing_smiles_list(request, client):
    request.node.test_id = "TC_VAL_012"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /chemical_space with missing smiles_list field returns 422"

    res = client.post("/chemical_space", json={"method": "pca"})
    assert res.status_code == 422


def test_filter_batch_missing_smiles_list(request, client):
    request.node.test_id = "TC_VAL_013"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /filter_batch with missing smiles_list returns 422"

    res = client.post("/filter_batch", json={})
    assert res.status_code == 422


def test_dock_missing_required_fields(request, client):
    request.node.test_id = "TC_VAL_014"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /dock with missing smiles or target returns 422"

    res = client.post("/dock", json={"exhaustiveness": 8})
    assert res.status_code == 422


def test_nonexistent_endpoint_returns_404(request, client):
    request.node.test_id = "TC_VAL_015"
    request.node.custom_module = "Input Validation"
    request.node.priority = "P2"
    request.node.test_name = "Verify request to undefined route returns HTTP 404 Not Found"

    res = client.get("/api/v1/non_existent_route")
    assert res.status_code == 404
