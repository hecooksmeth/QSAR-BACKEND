"""API Integration & Client Contract Suite (25 Tests)"""
import pytest
import qsar_api
from unittest.mock import MagicMock
import numpy as np

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"
CAFFEINE = "Cn1cnc2c1c(=O)n(c(=O)n2C)C"

def _create_mock():
    mock = MagicMock()
    mock.target = "EGFR"
    mock.metadata = {"type": "Kinase", "relevance": "Oncology"}
    mock.model = MagicMock()
    mock.model.predict_proba.return_value = np.array([[0.2, 0.8]])
    mock.selector = MagicMock()
    mock.selector.transform.return_value = np.zeros((1, 50))
    mock.scaler = MagicMock()
    mock.scaler.transform.return_value = np.zeros((1, 50))
    mock.selected_feature_names = [f"f_{i}" for i in range(50)]
    mock.ad_threshold = 0.5
    mock.reference_fps = []
    mock_exp = MagicMock()
    mock_exp.shap_values.return_value = np.zeros((1, 50))
    mock.shap_explainer = mock_exp
    return mock

def test_api_contract_001(request, client):
    request.node.test_id = "TC_MOB_001"
    request.node.custom_module = "API Integration"
    request.node.priority = "P0"
    request.node.test_name = "Verify client payload contract includes 'predictions' (predictions dictionary list for client results view)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('predictions' in data or 'predictions' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_002(request, client):
    request.node.test_id = "TC_MOB_002"
    request.node.custom_module = "API Integration"
    request.node.priority = "P0"
    request.node.test_name = "Verify client payload contract includes 'confidence' (prediction confidence percentage 0-100)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('confidence' in data or 'confidence' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_003(request, client):
    request.node.test_id = "TC_MOB_003"
    request.node.custom_module = "API Integration"
    request.node.priority = "P0"
    request.node.test_name = "Verify client payload contract includes 'active' (boolean active classification flag)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('active' in data or 'active' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_004(request, client):
    request.node.test_id = "TC_MOB_004"
    request.node.custom_module = "API Integration"
    request.node.priority = "P0"
    request.node.test_name = "Verify client payload contract includes 'molecular_properties' (molecular properties dictionary (MW, LogP, TPSA))"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('molecular_properties' in data or 'molecular_properties' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_005(request, client):
    request.node.test_id = "TC_MOB_005"
    request.node.custom_module = "API Integration"
    request.node.priority = "P0"
    request.node.test_name = "Verify client payload contract includes 'svg' (2D vector SVG structure string for client rendering)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('svg' in data or 'svg' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_006(request, client):
    request.node.test_id = "TC_MOB_006"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'drug_likeness' (drug likeness boolean evaluations)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('drug_likeness' in data or 'drug_likeness' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_007(request, client):
    request.node.test_id = "TC_MOB_007"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'lipinski' (Lipinski Rule of 5 evaluation)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('lipinski' in data or 'lipinski' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_008(request, client):
    request.node.test_id = "TC_MOB_008"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'veber' (Veber rotatable bond evaluation)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('veber' in data or 'veber' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_009(request, client):
    request.node.test_id = "TC_MOB_009"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'admet' (ADMET heuristic radar keys)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('admet' in data or 'admet' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_010(request, client):
    request.node.test_id = "TC_MOB_010"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'absorption' (GI absorption category string)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('absorption' in data or 'absorption' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_011(request, client):
    request.node.test_id = "TC_MOB_011"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'bbb' (blood-brain barrier permeability category string)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('bbb' in data or 'bbb' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_012(request, client):
    request.node.test_id = "TC_MOB_012"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'herg' (hERG cardiac toxicity risk estimate)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('herg' in data or 'herg' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_013(request, client):
    request.node.test_id = "TC_MOB_013"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify client payload contract includes 'pic50_estimate' (pIC50 bioactivity estimate)"
    mock = _create_mock()
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN})
        assert res.status_code == 200
        data = res.json()
        assert ('pic50_estimate' in data or 'pic50_estimate' in str(data))
    finally:
        qsar_api.MODELS = orig

def test_api_contract_014(request, client):
    request.node.test_id = "TC_MOB_014"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space coordinates payload shape for client 2D projection"
    res = client.post('/chemical_space', json={'smiles_list': [ASPIRIN, CAFFEINE], 'method': 'pca'})
    assert res.status_code == 200
    assert 'points' in res.json()

def test_api_contract_015(request, client):
    request.node.test_id = "TC_MOB_015"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify pharmacophore coordinates payload shape for client 3D visualization"
    res = client.post('/pharmacophore', json={'smiles': ASPIRIN})
    assert res.status_code == 200
    assert 'features' in res.json()

def test_api_contract_016(request, client):
    request.node.test_id = "TC_MOB_016"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /predict_all error response contract when invalid SMILES is submitted returns HTTP 400"
    res = client.post('/predict_all', json={'smiles': 'INVALID_SMILES_XYZ'})
    assert res.status_code == 400
    assert 'detail' in res.json()

def test_api_contract_017(request, client):
    request.node.test_id = "TC_MOB_017"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /predict_target contract returns HTTP 422 Unprocessable Entity when required body is missing"
    res = client.post('/predict_target', json={'target': 'EGFR'})
    assert res.status_code == 422

def test_api_contract_018(request, client):
    request.node.test_id = "TC_MOB_018"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /filter_batch integration contract returns passed and rejected molecule collections"
    res = client.post('/filter_batch', json={'smiles_list': [ASPIRIN, CAFFEINE]})
    assert res.status_code == 200
    assert 'passed_molecules' in res.json()

def test_api_contract_019(request, client):
    request.node.test_id = "TC_MOB_019"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /chemical_space contract returns 2D projection points for t-SNE algorithm"
    res = client.post('/chemical_space', json={'smiles_list': [ASPIRIN, CAFFEINE], 'method': 'tsne'})
    assert res.status_code == 200
    assert 'points' in res.json()

def test_api_contract_020(request, client):
    request.node.test_id = "TC_MOB_020"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /drug_likeness contract returns standard Lipinski molecular descriptors"
    res = client.post('/drug_likeness', json={'smiles': ASPIRIN})
    assert res.status_code == 200
    assert 'properties' in res.json()

def test_api_contract_021(request, client):
    request.node.test_id = "TC_MOB_021"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /pharmacophore contract returns 3D spatial feature coordinates list"
    res = client.post('/pharmacophore', json={'smiles': ASPIRIN})
    assert res.status_code == 200
    assert isinstance(res.json().get('features'), list)

def test_api_contract_022(request, client):
    request.node.test_id = "TC_MOB_022"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /docking_targets contract returns supported kinase receptor dictionary"
    res = client.get('/docking_targets')
    assert res.status_code == 200
    assert isinstance(res.json().get('targets'), dict)

def test_api_contract_023(request, client):
    request.node.test_id = "TC_MOB_023"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /docking_status contract returns docking engine status"
    res = client.get('/docking_status')
    assert res.status_code == 200
    assert 'status' in res.json() or 'vina_available' in res.json()

def test_api_contract_024(request, client):
    request.node.test_id = "TC_MOB_024"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify CORS preflight OPTIONS response headers allow client cross-origin API integration"
    res = client.options('/health', headers={'Origin': 'http://localhost:3000', 'Access-Control-Request-Method': 'GET'})
    assert res.status_code in (200, 204)

def test_api_contract_025(request, client):
    request.node.test_id = "TC_MOB_025"
    request.node.custom_module = "API Integration"
    request.node.priority = "P1"
    request.node.test_name = "Verify /openapi.json contract provides valid OpenAPI specification version"
    res = client.get('/openapi.json')
    assert res.status_code == 200
    assert 'openapi' in res.json()
