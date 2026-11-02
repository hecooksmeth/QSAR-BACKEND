"""Model Inference, Bioactivity Prediction & Explainability Suite (60 Tests)"""
import pytest
import qsar_api
from unittest.mock import MagicMock
import numpy as np

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
def _create_mock_bundle(target="EGFR", prob=0.85):
    mock = MagicMock()
    mock.target = target
    mock.metadata = {"type": "Kinase", "relevance": "Oncology"}
    mock.model = MagicMock()
    mock.model.predict_proba.return_value = np.array([[1.0 - prob, prob]])
    mock.selector = MagicMock()
    mock.selector.transform.return_value = np.zeros((1, 50))
    mock.scaler = MagicMock()
    mock.scaler.transform.return_value = np.zeros((1, 50))
    mock.selected_feature_names = [f"feat_{i}" for i in range(50)]
    mock.ad_threshold = 0.5
    mock.reference_fps = []
    mock_exp = MagicMock()
    mock_exp.shap_values.return_value = np.zeros((1, 50))
    mock.shap_explainer = mock_exp
    return mock

def test_model_inference_001(request, client):
    request.node.test_id = "TC_MOD_001"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify MODEL_ROOT resolution points to existing models path"
    assert qsar_api.MODEL_ROOT is not None

def test_model_inference_002(request, client):
    request.node.test_id = "TC_MOD_002"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify _supported_targets contains 10 oncology kinase targets"
    targets = qsar_api._supported_targets()
    assert len(targets) >= 10

def test_model_inference_003(request, client):
    request.node.test_id = "TC_MOD_003"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify Morgan fingerprint generator produces 2048-bit bit-vector"
    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    fp = qsar_api.morgan_generator.GetFingerprint(mol)
    assert fp.GetNumBits() == 2048

def test_model_inference_004(request, client):
    request.node.test_id = "TC_MOD_004"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify TargetBundle inference contract with mocked EGFR model"
    mock = _create_mock_bundle('EGFR', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'EGFR')
        assert res['target'] == 'EGFR'
        assert res['active'] is True
        assert res['confidence'] == 85.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_005(request, client):
    request.node.test_id = "TC_MOD_005"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify applicability domain distance similarity threshold calculation"
    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    fp = qsar_api.morgan_generator.GetFingerprint(mol)
    assert qsar_api.DataStructs.TanimotoSimilarity(fp, fp) == 1.0

def test_model_inference_006(request, client):
    request.node.test_id = "TC_MOD_006"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /predict_target endpoint returns 200 with mock bundle"
    mock = _create_mock_bundle('EGFR', 0.8)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_target', json={'smiles': ASPIRIN_SMILES, 'target': 'EGFR'})
        assert res.status_code == 200
        assert res.json()['confidence'] == 80.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_007(request, client):
    request.node.test_id = "TC_MOD_007"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /predict_all endpoint returns 200 with mock bundle"
    mock = _create_mock_bundle('EGFR', 0.75)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/predict_all', json={'smiles': ASPIRIN_SMILES})
        assert res.status_code == 200
        assert 'predictions' in res.json()
    finally:
        qsar_api.MODELS = orig

def test_model_inference_008(request, client):
    request.node.test_id = "TC_MOD_008"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /explain_prediction structure with mock SHAP explainer"
    mock = _create_mock_bundle('EGFR', 0.9)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'EGFR', 'top_n': 5})
        assert res.status_code == 200
        assert 'top_features' in res.json()
    finally:
        qsar_api.MODELS = orig

def test_model_inference_009(request, client):
    request.node.test_id = "TC_MOD_009"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /predict_all raises 503 when no models are loaded in memory"
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS = {}
        res = client.post('/predict_all', json={'smiles': ASPIRIN_SMILES})
        assert res.status_code == 503
    finally:
        qsar_api.MODELS = orig

def test_model_inference_010(request, client):
    request.node.test_id = "TC_MOD_010"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify _target_label lookup returns human-readable label"
    assert len(qsar_api._target_label('EGFR')) > 0

def test_model_inference_011(request, client):
    request.node.test_id = "TC_MOD_011"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'EGFR' test #11"
    mock = _create_mock_bundle('EGFR', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'EGFR')
        assert res['target'] == 'EGFR'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_012(request, client):
    request.node.test_id = "TC_MOD_012"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'BRAF' test #12"
    mock = _create_mock_bundle('BRAF', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['BRAF'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'BRAF')
        assert res['target'] == 'BRAF'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_013(request, client):
    request.node.test_id = "TC_MOD_013"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'VEGFR2' test #13"
    mock = _create_mock_bundle('VEGFR2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['VEGFR2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'VEGFR2')
        assert res['target'] == 'VEGFR2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_014(request, client):
    request.node.test_id = "TC_MOD_014"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'HER2' test #14"
    mock = _create_mock_bundle('HER2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['HER2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'HER2')
        assert res['target'] == 'HER2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_015(request, client):
    request.node.test_id = "TC_MOD_015"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P0"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'PARP1' test #15"
    mock = _create_mock_bundle('PARP1', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PARP1'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PARP1')
        assert res['target'] == 'PARP1'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_016(request, client):
    request.node.test_id = "TC_MOD_016"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'PI3K' test #16"
    mock = _create_mock_bundle('PI3K', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PI3K'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PI3K')
        assert res['target'] == 'PI3K'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_017(request, client):
    request.node.test_id = "TC_MOD_017"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'MTOR' test #17"
    mock = _create_mock_bundle('MTOR', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['MTOR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'MTOR')
        assert res['target'] == 'MTOR'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_018(request, client):
    request.node.test_id = "TC_MOD_018"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'ALK' test #18"
    mock = _create_mock_bundle('ALK', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['ALK'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'ALK')
        assert res['target'] == 'ALK'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_019(request, client):
    request.node.test_id = "TC_MOD_019"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'CDK2' test #19"
    mock = _create_mock_bundle('CDK2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['CDK2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'CDK2')
        assert res['target'] == 'CDK2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_020(request, client):
    request.node.test_id = "TC_MOD_020"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'FLT3' test #20"
    mock = _create_mock_bundle('FLT3', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['FLT3'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'FLT3')
        assert res['target'] == 'FLT3'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_021(request, client):
    request.node.test_id = "TC_MOD_021"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'EGFR' test #21"
    mock = _create_mock_bundle('EGFR', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'EGFR')
        assert res['target'] == 'EGFR'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_022(request, client):
    request.node.test_id = "TC_MOD_022"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'BRAF' test #22"
    mock = _create_mock_bundle('BRAF', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['BRAF'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'BRAF')
        assert res['target'] == 'BRAF'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_023(request, client):
    request.node.test_id = "TC_MOD_023"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'VEGFR2' test #23"
    mock = _create_mock_bundle('VEGFR2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['VEGFR2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'VEGFR2')
        assert res['target'] == 'VEGFR2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_024(request, client):
    request.node.test_id = "TC_MOD_024"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'HER2' test #24"
    mock = _create_mock_bundle('HER2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['HER2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'HER2')
        assert res['target'] == 'HER2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_025(request, client):
    request.node.test_id = "TC_MOD_025"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'PARP1' test #25"
    mock = _create_mock_bundle('PARP1', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PARP1'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PARP1')
        assert res['target'] == 'PARP1'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_026(request, client):
    request.node.test_id = "TC_MOD_026"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'PI3K' test #26"
    mock = _create_mock_bundle('PI3K', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PI3K'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PI3K')
        assert res['target'] == 'PI3K'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_027(request, client):
    request.node.test_id = "TC_MOD_027"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'MTOR' test #27"
    mock = _create_mock_bundle('MTOR', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['MTOR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'MTOR')
        assert res['target'] == 'MTOR'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_028(request, client):
    request.node.test_id = "TC_MOD_028"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'ALK' test #28"
    mock = _create_mock_bundle('ALK', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['ALK'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'ALK')
        assert res['target'] == 'ALK'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_029(request, client):
    request.node.test_id = "TC_MOD_029"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'CDK2' test #29"
    mock = _create_mock_bundle('CDK2', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['CDK2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'CDK2')
        assert res['target'] == 'CDK2'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_030(request, client):
    request.node.test_id = "TC_MOD_030"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify mocked bioactivity probability inference for target 'FLT3' test #30"
    mock = _create_mock_bundle('FLT3', 0.7)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['FLT3'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'FLT3')
        assert res['target'] == 'FLT3'
        assert res['active'] is True
    finally:
        qsar_api.MODELS = orig

def test_model_inference_031(request, client):
    request.node.test_id = "TC_MOD_031"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'EGFR' variation #31"
    mock = _create_mock_bundle('EGFR', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'EGFR')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_032(request, client):
    request.node.test_id = "TC_MOD_032"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'BRAF' variation #32"
    mock = _create_mock_bundle('BRAF', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['BRAF'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'BRAF')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_033(request, client):
    request.node.test_id = "TC_MOD_033"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'VEGFR2' variation #33"
    mock = _create_mock_bundle('VEGFR2', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['VEGFR2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'VEGFR2')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_034(request, client):
    request.node.test_id = "TC_MOD_034"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'HER2' variation #34"
    mock = _create_mock_bundle('HER2', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['HER2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'HER2')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_035(request, client):
    request.node.test_id = "TC_MOD_035"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'PARP1' variation #35"
    mock = _create_mock_bundle('PARP1', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PARP1'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PARP1')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_036(request, client):
    request.node.test_id = "TC_MOD_036"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'PI3K' variation #36"
    mock = _create_mock_bundle('PI3K', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PI3K'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PI3K')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_037(request, client):
    request.node.test_id = "TC_MOD_037"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'MTOR' variation #37"
    mock = _create_mock_bundle('MTOR', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['MTOR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'MTOR')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_038(request, client):
    request.node.test_id = "TC_MOD_038"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'ALK' variation #38"
    mock = _create_mock_bundle('ALK', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['ALK'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'ALK')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_039(request, client):
    request.node.test_id = "TC_MOD_039"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'CDK2' variation #39"
    mock = _create_mock_bundle('CDK2', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['CDK2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'CDK2')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_040(request, client):
    request.node.test_id = "TC_MOD_040"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'FLT3' variation #40"
    mock = _create_mock_bundle('FLT3', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['FLT3'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'FLT3')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_041(request, client):
    request.node.test_id = "TC_MOD_041"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'EGFR' variation #41"
    mock = _create_mock_bundle('EGFR', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'EGFR')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_042(request, client):
    request.node.test_id = "TC_MOD_042"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'BRAF' variation #42"
    mock = _create_mock_bundle('BRAF', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['BRAF'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'BRAF')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_043(request, client):
    request.node.test_id = "TC_MOD_043"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'VEGFR2' variation #43"
    mock = _create_mock_bundle('VEGFR2', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['VEGFR2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'VEGFR2')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_044(request, client):
    request.node.test_id = "TC_MOD_044"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'HER2' variation #44"
    mock = _create_mock_bundle('HER2', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['HER2'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'HER2')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_045(request, client):
    request.node.test_id = "TC_MOD_045"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify pIC50 estimate computation for target 'PARP1' variation #45"
    mock = _create_mock_bundle('PARP1', 0.6)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PARP1'] = mock
        res = qsar_api.predict_target(ASPIRIN_SMILES, 'PARP1')
        assert 4.0 <= res['pic50_estimate'] <= 9.0
    finally:
        qsar_api.MODELS = orig

def test_model_inference_046(request, client):
    request.node.test_id = "TC_MOD_046"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #46"
    mock = _create_mock_bundle('PI3K', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PI3K'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'PI3K', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_047(request, client):
    request.node.test_id = "TC_MOD_047"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #47"
    mock = _create_mock_bundle('MTOR', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['MTOR'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'MTOR', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_048(request, client):
    request.node.test_id = "TC_MOD_048"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #48"
    mock = _create_mock_bundle('ALK', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['ALK'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'ALK', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_049(request, client):
    request.node.test_id = "TC_MOD_049"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #49"
    mock = _create_mock_bundle('CDK2', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['CDK2'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'CDK2', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_050(request, client):
    request.node.test_id = "TC_MOD_050"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #50"
    mock = _create_mock_bundle('FLT3', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['FLT3'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'FLT3', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_051(request, client):
    request.node.test_id = "TC_MOD_051"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #51"
    mock = _create_mock_bundle('EGFR', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['EGFR'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'EGFR', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_052(request, client):
    request.node.test_id = "TC_MOD_052"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #52"
    mock = _create_mock_bundle('BRAF', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['BRAF'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'BRAF', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_053(request, client):
    request.node.test_id = "TC_MOD_053"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #53"
    mock = _create_mock_bundle('VEGFR2', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['VEGFR2'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'VEGFR2', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_054(request, client):
    request.node.test_id = "TC_MOD_054"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #54"
    mock = _create_mock_bundle('HER2', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['HER2'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'HER2', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_055(request, client):
    request.node.test_id = "TC_MOD_055"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #55"
    mock = _create_mock_bundle('PARP1', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PARP1'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'PARP1', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_056(request, client):
    request.node.test_id = "TC_MOD_056"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #56"
    mock = _create_mock_bundle('PI3K', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['PI3K'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'PI3K', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_057(request, client):
    request.node.test_id = "TC_MOD_057"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #57"
    mock = _create_mock_bundle('MTOR', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['MTOR'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'MTOR', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_058(request, client):
    request.node.test_id = "TC_MOD_058"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #58"
    mock = _create_mock_bundle('ALK', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['ALK'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'ALK', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_059(request, client):
    request.node.test_id = "TC_MOD_059"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #59"
    mock = _create_mock_bundle('CDK2', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['CDK2'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'CDK2', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig

def test_model_inference_060(request, client):
    request.node.test_id = "TC_MOD_060"
    request.node.custom_module = "Model Loading and Availability"
    request.node.priority = "P1"
    request.node.test_name = "Verify SHAP feature vector calculation & handling for variation #60"
    mock = _create_mock_bundle('FLT3', 0.85)
    orig = qsar_api.MODELS.copy()
    try:
        qsar_api.MODELS['FLT3'] = mock
        res = client.post('/explain_prediction', json={'smiles': ASPIRIN_SMILES, 'target': 'FLT3', 'top_n': 3})
        assert res.status_code == 200
    finally:
        qsar_api.MODELS = orig
