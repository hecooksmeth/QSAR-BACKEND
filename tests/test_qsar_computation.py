"""
QSAR Cheminformatics and Molecular Property Computation Suite
Validates RDKit molecule parsing, 2D descriptors, drug-likeness rules, ADMET, and chemical space.
"""

import pytest
from rdkit import Chem
import qsar_api


ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
CAFFEINE_SMILES = "Cn1cnc2c1c(=O)n(c(=O)n2C)C"
PARACETAMOL_SMILES = "CC(=O)Nc1ccc(O)cc1"


def test_rdkit_molecular_parsing_aspirin(request):
    request.node.test_id = "TC_CHEM_001"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit accurately parses Aspirin canonical SMILES into Mol object"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    assert mol is not None
    assert mol.GetNumAtoms() == 13
    assert mol.GetNumHeavyAtoms() == 13


def test_rdkit_molecular_parsing_caffeine(request):
    request.node.test_id = "TC_CHEM_002"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify RDKit accurately parses Caffeine SMILES with bicyclic purine ring"

    mol = qsar_api._mol_from_smiles(CAFFEINE_SMILES)
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 14


def test_rdkit_molecular_parsing_paracetamol(request):
    request.node.test_id = "TC_CHEM_003"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify RDKit parses Paracetamol aromatic amide and phenol motifs"

    mol = qsar_api._mol_from_smiles(PARACETAMOL_SMILES)
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 11


def test_molecular_property_calculation(request):
    request.node.test_id = "TC_CHEM_004"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P0"
    request.node.test_name = "Verify _mol_properties computes MW, LogP, TPSA, HBD, HBA for Aspirin"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    props = qsar_api._mol_properties(mol)
    assert "mw" in props
    assert "logp" in props
    assert "tpsa" in props
    assert "hbd" in props
    assert "hba" in props
    assert 170.0 < props["mw"] < 190.0
    assert 0.5 < props["logp"] < 2.0


def test_drug_likeness_lipinski_evaluation(request):
    request.node.test_id = "TC_CHEM_005"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify _drug_likeness evaluates Lipinski Rule of 5 compliance"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    props = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(props)
    assert "lipinski" in dl
    assert dl["lipinski"] is True
    assert "bioavailability_score" in dl


def test_veber_rule_evaluation(request):
    request.node.test_id = "TC_CHEM_006"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P2"
    request.node.test_name = "Verify _drug_likeness evaluates Veber rotatable bond constraints"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    props = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(props)
    assert "veber" in dl
    assert dl["veber"] is True


def test_admet_heuristics_evaluation(request):
    request.node.test_id = "TC_CHEM_007"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify _admet_heuristics estimates absorption and permeability profiles"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    props = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(props)
    assert "absorption" in admet
    assert "bbb" in admet
    assert "herg" in admet


def test_svg_structure_generation(request):
    request.node.test_id = "TC_CHEM_008"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P2"
    request.node.test_name = "Verify _mol_svg generates 2D vector depiction of molecule"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    svg = qsar_api._mol_svg(mol)
    assert svg is not None
    assert "<svg" in svg
    assert "</svg>" in svg


def test_post_drug_likeness_endpoint(request, client):
    request.node.test_id = "TC_CHEM_009"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P0"
    request.node.test_name = "Verify POST /drug_likeness returns 200 with complete evaluation"

    res = client.post("/drug_likeness", json={"smiles": ASPIRIN_SMILES})
    assert res.status_code == 200
    data = res.json()
    assert "drug_likeness" in data or "lipinski" in str(data).lower()


def test_post_chemical_space_endpoint(request, client):
    request.node.test_id = "TC_CHEM_010"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /chemical_space computes PCA coordinate projections"

    res = client.post("/chemical_space", json={"smiles_list": [ASPIRIN_SMILES, CAFFEINE_SMILES], "method": "pca"})
    assert res.status_code == 200
    data = res.json()
    assert "points" in data
    assert len(data["points"]) == 2


def test_similarity_search_endpoint(request, client):
    request.node.test_id = "TC_CHEM_011"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /similarity_search returns ranked reference compounds"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    orig_fps = list(qsar_api.reference_fps)
    orig_smiles = list(qsar_api.reference_smiles)
    try:
        qsar_api.reference_fps.append(qsar_api.morgan_generator.GetFingerprint(mol))
        qsar_api.reference_smiles.append(CAFFEINE_SMILES)
        res = client.post("/similarity_search", json={"smiles": ASPIRIN_SMILES, "top_n": 5})
        assert res.status_code == 200
        data = res.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) >= 1
    finally:
        qsar_api.reference_fps = orig_fps
        qsar_api.reference_smiles = orig_smiles


def test_similarity_scores_bounded_range(request, client):
    request.node.test_id = "TC_CHEM_012"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P2"
    request.node.test_name = "Verify similarity score coefficients fall within [0.0, 1.0]"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    orig_fps = list(qsar_api.reference_fps)
    orig_smiles = list(qsar_api.reference_smiles)
    try:
        qsar_api.reference_fps.append(qsar_api.morgan_generator.GetFingerprint(mol))
        qsar_api.reference_smiles.append(CAFFEINE_SMILES)
        res = client.post("/similarity_search", json={"smiles": ASPIRIN_SMILES, "top_n": 3})
        assert res.status_code == 200
        for item in res.json().get("results", []):
            score = item.get("tanimoto", 0.0)
            assert 0.0 <= score <= 1.0
    finally:
        qsar_api.reference_fps = orig_fps
        qsar_api.reference_smiles = orig_smiles


def test_pharmacophore_filtering_endpoint(request, client):
    request.node.test_id = "TC_CHEM_013"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /pharmacophore returns feature coordinates and counts"

    res = client.post("/pharmacophore", json={"smiles": ASPIRIN_SMILES})
    assert res.status_code == 200
    data = res.json()
    assert "features" in data
    assert "feature_counts" in data
    assert "pharmacophore_score" in data


def test_filter_batch_endpoint(request, client):
    request.node.test_id = "TC_CHEM_014"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P1"
    request.node.test_name = "Verify POST /filter_batch applies property thresholds across compound list"

    res = client.post("/filter_batch", json={"smiles_list": [ASPIRIN_SMILES, CAFFEINE_SMILES], "filters": {}})
    assert res.status_code == 200
    data = res.json()
    assert "passed_molecules" in data
    assert data.get("total_input") == 2


def test_murcko_scaffold_extraction(request):
    request.node.test_id = "TC_CHEM_015"
    request.node.custom_module = "Cheminformatics"
    request.node.priority = "P2"
    request.node.test_name = "Verify Murcko Scaffold decomposition extracts benzene core from Aspirin"

    mol = qsar_api._mol_from_smiles(ASPIRIN_SMILES)
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None
    assert Chem.MolToSmiles(scaffold) == "c1ccccc1"
