"""Cheminformatics, Descriptors, Rules & 2D Vector Generation (70 Tests)"""
import pytest
from rdkit import Chem
import qsar_api

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"
CAFFEINE = "Cn1cnc2c1c(=O)n(c(=O)n2C)C"

def test_qsar_computation_001(request, client):
    request.node.test_id = "TC_CHEM_001"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Aspirin'"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 13

def test_qsar_computation_002(request, client):
    request.node.test_id = "TC_CHEM_002"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Caffeine'"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 14

def test_qsar_computation_003(request, client):
    request.node.test_id = "TC_CHEM_003"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Paracetamol'"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 11

def test_qsar_computation_004(request, client):
    request.node.test_id = "TC_CHEM_004"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Ibuprofen'"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 15

def test_qsar_computation_005(request, client):
    request.node.test_id = "TC_CHEM_005"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Gefitinib'"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 31

def test_qsar_computation_006(request, client):
    request.node.test_id = "TC_CHEM_006"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Erlotinib'"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 29

def test_qsar_computation_007(request, client):
    request.node.test_id = "TC_CHEM_007"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Imatinib'"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 37

def test_qsar_computation_008(request, client):
    request.node.test_id = "TC_CHEM_008"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Metformin'"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 9

def test_qsar_computation_009(request, client):
    request.node.test_id = "TC_CHEM_009"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Diazepam'"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 20

def test_qsar_computation_010(request, client):
    request.node.test_id = "TC_CHEM_010"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify RDKit molecular parsing for compound 'Atorvastatin'"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    assert mol is not None
    assert mol.GetNumHeavyAtoms() == 41

def test_qsar_computation_011(request, client):
    request.node.test_id = "TC_CHEM_011"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Aspirin' #11"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_012(request, client):
    request.node.test_id = "TC_CHEM_012"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Caffeine' #12"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_013(request, client):
    request.node.test_id = "TC_CHEM_013"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Paracetamol' #13"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_014(request, client):
    request.node.test_id = "TC_CHEM_014"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Ibuprofen' #14"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_015(request, client):
    request.node.test_id = "TC_CHEM_015"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Gefitinib' #15"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_016(request, client):
    request.node.test_id = "TC_CHEM_016"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Erlotinib' #16"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_017(request, client):
    request.node.test_id = "TC_CHEM_017"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Imatinib' #17"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_018(request, client):
    request.node.test_id = "TC_CHEM_018"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Metformin' #18"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_019(request, client):
    request.node.test_id = "TC_CHEM_019"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Diazepam' #19"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_020(request, client):
    request.node.test_id = "TC_CHEM_020"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P0"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Atorvastatin' #20"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_021(request, client):
    request.node.test_id = "TC_CHEM_021"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Aspirin' #21"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_022(request, client):
    request.node.test_id = "TC_CHEM_022"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Caffeine' #22"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_023(request, client):
    request.node.test_id = "TC_CHEM_023"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Paracetamol' #23"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_024(request, client):
    request.node.test_id = "TC_CHEM_024"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Ibuprofen' #24"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_025(request, client):
    request.node.test_id = "TC_CHEM_025"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify molecular property calculation (MW, LogP, TPSA) for 'Gefitinib' #25"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    p = qsar_api._mol_properties(mol)
    assert 'mw' in p and 'logp' in p and 'tpsa' in p and 'hbd' in p

def test_qsar_computation_026(request, client):
    request.node.test_id = "TC_CHEM_026"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Erlotinib' #26"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_027(request, client):
    request.node.test_id = "TC_CHEM_027"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Imatinib' #27"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_028(request, client):
    request.node.test_id = "TC_CHEM_028"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Metformin' #28"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_029(request, client):
    request.node.test_id = "TC_CHEM_029"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Diazepam' #29"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_030(request, client):
    request.node.test_id = "TC_CHEM_030"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Atorvastatin' #30"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_031(request, client):
    request.node.test_id = "TC_CHEM_031"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Aspirin' #31"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_032(request, client):
    request.node.test_id = "TC_CHEM_032"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Caffeine' #32"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_033(request, client):
    request.node.test_id = "TC_CHEM_033"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Paracetamol' #33"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_034(request, client):
    request.node.test_id = "TC_CHEM_034"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Ibuprofen' #34"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_035(request, client):
    request.node.test_id = "TC_CHEM_035"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify drug-likeness Lipinski & Veber rules evaluation on 'Gefitinib' #35"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    p = qsar_api._mol_properties(mol)
    dl = qsar_api._drug_likeness(p)
    assert 'lipinski' in dl and 'veber' in dl

def test_qsar_computation_036(request, client):
    request.node.test_id = "TC_CHEM_036"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Erlotinib' #36"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_037(request, client):
    request.node.test_id = "TC_CHEM_037"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Imatinib' #37"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_038(request, client):
    request.node.test_id = "TC_CHEM_038"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Metformin' #38"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_039(request, client):
    request.node.test_id = "TC_CHEM_039"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Diazepam' #39"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_040(request, client):
    request.node.test_id = "TC_CHEM_040"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Atorvastatin' #40"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_041(request, client):
    request.node.test_id = "TC_CHEM_041"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Aspirin' #41"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_042(request, client):
    request.node.test_id = "TC_CHEM_042"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Caffeine' #42"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_043(request, client):
    request.node.test_id = "TC_CHEM_043"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Paracetamol' #43"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_044(request, client):
    request.node.test_id = "TC_CHEM_044"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Ibuprofen' #44"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_045(request, client):
    request.node.test_id = "TC_CHEM_045"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify ADMET heuristic profile estimation on 'Gefitinib' #45"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    p = qsar_api._mol_properties(mol)
    admet = qsar_api._admet_heuristics(p)
    assert 'absorption' in admet and 'bbb' in admet and 'herg' in admet

def test_qsar_computation_046(request, client):
    request.node.test_id = "TC_CHEM_046"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Erlotinib' #46"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_047(request, client):
    request.node.test_id = "TC_CHEM_047"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Imatinib' #47"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_048(request, client):
    request.node.test_id = "TC_CHEM_048"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Metformin' #48"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_049(request, client):
    request.node.test_id = "TC_CHEM_049"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Diazepam' #49"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_050(request, client):
    request.node.test_id = "TC_CHEM_050"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Atorvastatin' #50"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_051(request, client):
    request.node.test_id = "TC_CHEM_051"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Aspirin' #51"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_052(request, client):
    request.node.test_id = "TC_CHEM_052"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Caffeine' #52"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_053(request, client):
    request.node.test_id = "TC_CHEM_053"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Paracetamol' #53"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_054(request, client):
    request.node.test_id = "TC_CHEM_054"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Ibuprofen' #54"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_055(request, client):
    request.node.test_id = "TC_CHEM_055"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify 2D vector SVG generation for 'Gefitinib' #55"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    svg = qsar_api._mol_svg(mol)
    assert '<svg' in svg and '</svg>' in svg

def test_qsar_computation_056(request, client):
    request.node.test_id = "TC_CHEM_056"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #56"
    mol = qsar_api._mol_from_smiles('COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_057(request, client):
    request.node.test_id = "TC_CHEM_057"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #57"
    mol = qsar_api._mol_from_smiles('Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_058(request, client):
    request.node.test_id = "TC_CHEM_058"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #58"
    mol = qsar_api._mol_from_smiles('CN(C)C(=N)NC(=N)N')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_059(request, client):
    request.node.test_id = "TC_CHEM_059"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #59"
    mol = qsar_api._mol_from_smiles('CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_060(request, client):
    request.node.test_id = "TC_CHEM_060"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #60"
    mol = qsar_api._mol_from_smiles('CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_061(request, client):
    request.node.test_id = "TC_CHEM_061"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #61"
    mol = qsar_api._mol_from_smiles('CC(=O)Oc1ccccc1C(=O)O')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_062(request, client):
    request.node.test_id = "TC_CHEM_062"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #62"
    mol = qsar_api._mol_from_smiles('Cn1cnc2c1c(=O)n(c(=O)n2C)C')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_063(request, client):
    request.node.test_id = "TC_CHEM_063"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #63"
    mol = qsar_api._mol_from_smiles('CC(=O)Nc1ccc(O)cc1')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_064(request, client):
    request.node.test_id = "TC_CHEM_064"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #64"
    mol = qsar_api._mol_from_smiles('CC(C)Cc1ccc(cc1)C(C)C(=O)O')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_065(request, client):
    request.node.test_id = "TC_CHEM_065"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify Murcko scaffold decomposition on compound #65"
    mol = qsar_api._mol_from_smiles('COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1')
    scaffold = qsar_api.MurckoScaffold.GetScaffoldForMol(mol)
    assert scaffold is not None

def test_qsar_computation_066(request, client):
    request.node.test_id = "TC_CHEM_066"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space PCA projection / pharmacophore on compound #66"
    res = client.post('/pharmacophore', json={'smiles': 'COCCOc1cc2c(cc1OCCOC)ncnc2Nc1cccc(c1)C#C'})
    assert res.status_code == 200
    assert 'features' in res.json()

def test_qsar_computation_067(request, client):
    request.node.test_id = "TC_CHEM_067"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space PCA projection / pharmacophore on compound #67"
    res = client.post('/pharmacophore', json={'smiles': 'Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1'})
    assert res.status_code == 200
    assert 'features' in res.json()

def test_qsar_computation_068(request, client):
    request.node.test_id = "TC_CHEM_068"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space PCA projection / pharmacophore on compound #68"
    res = client.post('/pharmacophore', json={'smiles': 'CN(C)C(=N)NC(=N)N'})
    assert res.status_code == 200
    assert 'features' in res.json()

def test_qsar_computation_069(request, client):
    request.node.test_id = "TC_CHEM_069"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space PCA projection / pharmacophore on compound #69"
    res = client.post('/pharmacophore', json={'smiles': 'CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21'})
    assert res.status_code == 200
    assert 'features' in res.json()

def test_qsar_computation_070(request, client):
    request.node.test_id = "TC_CHEM_070"
    request.node.custom_module = "Chemical Structure Processing"
    request.node.priority = "P1"
    request.node.test_name = "Verify chemical space PCA projection / pharmacophore on compound #70"
    res = client.post('/pharmacophore', json={'smiles': 'CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CCC(O)CC(O)CC(=O)O'})
    assert res.status_code == 200
    assert 'features' in res.json()
