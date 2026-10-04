import sys as _sys
import io
import json
import logging
import os
import re
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


import joblib
import numpy as np
import pandas as pd
import requests
import shap
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, Draw, rdMolDescriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


# ── Logging setup: write to both stderr and a persistent log file ─────────────
_LOG_FILE = os.path.join(os.path.abspath(os.sep), 'tmp', 'qsar_backend.log')
try:
    _fh = logging.FileHandler(_LOG_FILE, encoding='utf-8')
except Exception:
    _fh = None

_handlers = [logging.StreamHandler()]
if _fh:
    _handlers.append(_fh)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=_handlers
)
logger = logging.getLogger("qsar-backend")
logger.info("QSAR backend starting. Log file: %s", _LOG_FILE)

app = FastAPI(title="QSAR Discovery Suite v3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# When bundled with PyInstaller (frozen), __file__ is unreliable in windowless
# (console=False) mode. sys._MEIPASS always points to the correct _internal/
# extraction directory regardless of console mode.
if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
    BASE_DIR = _sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_ROOT = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
logger.info("BASE_DIR resolved to: %s", BASE_DIR)
logger.info("MODEL_ROOT: %s (exists=%s)", MODEL_ROOT, os.path.exists(MODEL_ROOT))
logger.info("frozen=%s MEIPASS=%s", getattr(_sys,'frozen',False), getattr(_sys,'_MEIPASS','N/A'))

SUPPORTED_TARGETS = ["EGFR", "BRAF", "VEGFR2", "HER2", "PARP1", "PI3K", "MTOR", "ALK", "CDK2", "FLT3"]
TARGET_ALIASES = {
    "PARP": "PARP1",
    "PIK3CA": "PI3K",
    "PI3CA": "PI3K",
    "MTOR": "MTOR",
    "MTORC1": "MTOR",
}
TARGET_DISPLAY_NAMES = {
    "MTOR": "mTOR",
}

TARGET_INFO = {
    "EGFR": {"type": "Tyrosine Kinase", "relevance": "Lung/Breast Cancer"},
    "BRAF": {"type": "Ser/Thr Kinase", "relevance": "Melanoma"},
    "VEGFR2": {"type": "Angiogenesis Receptor", "relevance": "Tumor Vascularization"},
    "HER2": {"type": "Growth Receptor", "relevance": "Breast Cancer"},
    "PARP1": {"type": "DNA Repair Enzyme", "relevance": "Ovarian/Breast Cancer"},
    "PI3K": {"type": "Lipid Kinase", "relevance": "Cancer Survival"},
    "MTOR": {"type": "Protein Kinase", "relevance": "Cell Growth"},
    "ALK": {"type": "Receptor Tyrosine Kinase", "relevance": "Lung Cancer"},
    "CDK2": {"type": "Cyclin-Dependent Kinase", "relevance": "Cell Cycle Regulation"},
    "FLT3": {"type": "Receptor Tyrosine Kinase", "relevance": "Acute Myeloid Leukemia"},
}

FP_SIZE = 2048
RADIUS = 2
ACTIVE_THRESHOLD = 0.5
REFERENCE_FP_LIMIT = 5000
AD_SAMPLE_LIMIT = 2000

descriptor_names = [desc[0] for desc in Descriptors._descList]
feature_names = np.array(descriptor_names + [f"morgan_{i}" for i in range(FP_SIZE)])
descriptor_calculator = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)
morgan_generator = GetMorganGenerator(radius=RADIUS, fpSize=FP_SIZE)


@dataclass
class TargetBundle:
    target: str
    model: Any
    scaler: Any
    selector: Any
    model_dir: str
    metadata: Dict[str, Any]
    selected_feature_names: List[str]
    reference_fps: List[Any] = field(default_factory=list)
    reference_smiles: List[str] = field(default_factory=list)
    ad_threshold: Optional[float] = None
    shap_explainer: Optional[Any] = None


MODELS: Dict[str, TargetBundle] = {}
reference_fps: List[Any] = []
reference_smiles: List[str] = []


# -----------------------------------------------------------------------------
# Request models
# -----------------------------------------------------------------------------
class PredictRequest(BaseModel):
    smiles: str


class TargetPredictRequest(BaseModel):
    smiles: str
    target: str


class ExplainRequest(BaseModel):
    smiles: str
    target: str = "EGFR"
    top_n: int = 15


class BatchRequest(BaseModel):
    smiles_list: List[str]
    target_filter: str = "EGFR"


class SimilarityRequest(BaseModel):
    smiles: str
    top_n: int = 10


class ChemSpaceRequest(BaseModel):
    smiles_list: List[str]
    method: str = "pca"


class DockingRequest(BaseModel):
    smiles: str
    target: str = "CDK2"
    exhaustiveness: int = 8


class PharmacophoreFilter(BaseModel):
    hbd_min: int = 0
    hbd_max: int = 99
    hba_min: int = 0
    hba_max: int = 99
    aromatic_min: int = 0
    aromatic_max: int = 99
    hydrophobic_min: int = 0


class MolPropertyFilter(BaseModel):
    mw_min: float = 0
    mw_max: float = 1000
    logp_min: float = -10
    logp_max: float = 10
    tpsa_min: float = 0
    tpsa_max: float = 300
    hbd_max: int = 99
    hba_max: int = 99
    rotatable_max: int = 99
    aromatic_min: int = 0
    heavy_min: int = 0
    heavy_max: int = 200


class DrugLikenessFilter(BaseModel):
    lipinski: bool = False
    veber: bool = False
    ghose: bool = False
    egan: bool = False
    muegge: bool = False


class AdmetFilter(BaseModel):
    absorption: Optional[str] = None
    bbb: Optional[str] = None
    herg: Optional[str] = None
    hepatotoxicity: Optional[str] = None
    toxicity: Optional[str] = None
    cyp_inhibition: Optional[str] = None


class FilterRequest(BaseModel):
    smiles_list: List[str]
    mol_properties: MolPropertyFilter = MolPropertyFilter()
    pharmacophore: PharmacophoreFilter = PharmacophoreFilter()
    drug_likeness: DrugLikenessFilter = DrugLikenessFilter()
    admet: AdmetFilter = AdmetFilter()


# -----------------------------------------------------------------------------
# Model loading and feature generation
# -----------------------------------------------------------------------------
def _target_key(target: str) -> str:
    key = target.upper().replace(" ", "").replace("-", "").replace("_", "")
    return TARGET_ALIASES.get(key, key)


def _target_label(target: str) -> str:
    return TARGET_DISPLAY_NAMES.get(target, target)


def _target_name_variants(target: str) -> List[str]:
    canonical = _target_key(target)
    variants = [
        canonical,
        _target_label(canonical),
        canonical.lower(),
        canonical.capitalize(),
        target,
        target.lower(),
        target.upper(),
    ]
    variants.extend(alias for alias, alias_target in TARGET_ALIASES.items() if alias_target == canonical)

    seen = set()
    unique = []
    for variant in variants:
        if variant and variant not in seen:
            unique.append(variant)
            seen.add(variant)
    return unique


def _target_model_dir(target: str) -> str:
    canonical = _target_key(target)
    exact = os.path.join(MODEL_ROOT, canonical)
    if os.path.exists(exact):
        return exact

    if os.path.isdir(MODEL_ROOT):
        for entry in os.listdir(MODEL_ROOT):
            path = os.path.join(MODEL_ROOT, entry)
            if os.path.isdir(path) and _target_key(entry) == canonical:
                return path

    return exact


def _complete_artifact_dir(model_dir: str) -> Optional[Dict[str, str]]:
    paths = {
        "model": os.path.join(model_dir, "model.pkl"),
        "scaler": os.path.join(model_dir, "scaler.pkl"),
        "selector": os.path.join(model_dir, "selector.pkl"),
    }
    if all(os.path.exists(path) for path in paths.values()):
        return paths
    return None


def _discover_trained_targets() -> List[str]:
    discovered = []
    if os.path.isdir(MODEL_ROOT):
        for entry in os.listdir(MODEL_ROOT):
            model_dir = os.path.join(MODEL_ROOT, entry)
            if os.path.isdir(model_dir) and _complete_artifact_dir(model_dir):
                discovered.append(_target_key(entry))

    for target in SUPPORTED_TARGETS:
        if _artifact_paths(target):
            discovered.append(_target_key(target))

    ordered = []
    for target in SUPPORTED_TARGETS + sorted(discovered):
        canonical = _target_key(target)
        if canonical not in ordered and canonical in discovered:
            ordered.append(canonical)
    return ordered


def _supported_targets() -> List[str]:
    discovered = _discover_trained_targets()
    ordered = []
    for target in SUPPORTED_TARGETS + discovered:
        canonical = _target_key(target)
        if canonical not in ordered:
            ordered.append(canonical)
    return ordered


def _legacy_artifact_paths(target: str) -> Optional[Dict[str, str]]:
    """Developer convenience fallback for this workspace.

    Production deployment should use models/<TARGET>/model.pkl, scaler.pkl,
    selector.pkl as requested.
    """
    prefix = target.lower()
    paths = {
        "model": os.path.join(BASE_DIR, f"{prefix}_xgb_model.pkl"),
        "scaler": os.path.join(BASE_DIR, f"{prefix}_scaler.pkl"),
        "selector": os.path.join(BASE_DIR, f"{prefix}_selector.pkl"),
    }
    if all(os.path.exists(path) for path in paths.values()):
        return paths
    return None


def _artifact_paths(target: str) -> Optional[Dict[str, str]]:
    model_dir = _target_model_dir(target)
    paths = _complete_artifact_dir(model_dir)
    if paths:
        return paths
    return _legacy_artifact_paths(target)


def _cleaned_data_path(target: str) -> Optional[str]:
    candidates = []
    for name in _target_name_variants(target):
        candidates.extend(
            [
                os.path.join(DATA_DIR, f"clean_{name}.csv"),
                os.path.join(DATA_DIR, f"{name}_cleaned.csv"),
                os.path.join(BASE_DIR, f"{name}_cleaned.csv"),
            ]
        )
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _load_reference_fps_for_target(target: str) -> tuple[List[Any], List[str], Optional[float]]:
    path = _cleaned_data_path(target)
    if not path:
        return [], [], None

    try:
        df = pd.read_csv(path, usecols=["SMILES"])
        fps = []
        smiles = []
        for smi in df["SMILES"].dropna().astype(str).head(REFERENCE_FP_LIMIT):
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            fps.append(morgan_generator.GetFingerprint(mol))
            smiles.append(smi)

        threshold = _estimate_ad_threshold(fps)
        logger.info("Loaded %s reference fingerprints for %s", len(fps), target)
        return fps, smiles, threshold
    except Exception as exc:
        logger.warning("Reference fingerprint load failed for %s: %s", target, exc)
        return [], [], None


def _estimate_ad_threshold(fps: List[Any]) -> Optional[float]:
    if len(fps) < 3:
        return None

    sample = fps[: min(len(fps), AD_SAMPLE_LIMIT)]
    nearest_distances = []
    for idx, fp in enumerate(sample):
        sims = DataStructs.BulkTanimotoSimilarity(fp, sample)
        sims[idx] = -1.0
        nearest_distances.append(1.0 - max(sims))

    return float(np.mean(nearest_distances) * 1.5)


def _load_target_bundle(target: str) -> Optional[TargetBundle]:
    paths = _artifact_paths(target)
    if not paths:
        logger.warning("No complete model artifacts found for %s", target)
        return None

    try:
        model = joblib.load(paths["model"])
        scaler = joblib.load(paths["scaler"])
        selector = joblib.load(paths["selector"])
        support = selector.get_support()
        selected_names = feature_names[support].tolist()
        refs, ref_smiles, ad_threshold = _load_reference_fps_for_target(target)

        return TargetBundle(
            target=target,
            model=model,
            scaler=scaler,
            selector=selector,
            model_dir=os.path.dirname(paths["model"]),
            metadata=TARGET_INFO.get(target, {}),
            selected_feature_names=selected_names,
            reference_fps=refs,
            reference_smiles=ref_smiles,
            ad_threshold=ad_threshold,
        )
    except Exception as exc:
        logger.exception("Failed to load target bundle for %s: %s", target, exc)
        return None


@app.on_event("startup")
async def load_artifacts() -> None:
    """Load ML models immediately, then load CHEMBL reference DB in a background thread."""
    import asyncio
    
    logger.info("=== STARTUP: Loading ML models ===")
    logger.info("MODEL_ROOT=%s exists=%s", MODEL_ROOT, os.path.exists(MODEL_ROOT))
    
    MODELS.clear()
    trained_targets = _discover_trained_targets()
    for target in trained_targets:
        logger.info("Loading target: %s", target)
        try:
            bundle = _load_target_bundle(target)
            if bundle is not None:
                MODELS[target] = bundle
                logger.info("[OK] Loaded %s model from %s", target, bundle.model_dir)
            else:
                logger.error("[FAIL] Bundle returned None for %s", target)
        except Exception as exc:
            logger.exception("[FAIL] Exception loading %s: %s", target, exc)
    
    logger.info("=== Models loaded: %d/%d ===", len(MODELS), len(trained_targets))
    
    # Load CHEMBL reference DB in background so startup completes immediately
    def _bg_load():
        try:
            _load_similarity_reference_db()
        except Exception as exc:
            logger.exception("Background CHEMBL load failed: %s", exc)
    
    t = threading.Thread(target=_bg_load, daemon=True)
    t.start()


def _load_similarity_reference_db() -> None:
    reference_fps.clear()
    reference_smiles.clear()

    chembl_path = os.path.join(BASE_DIR, "CHEMBL_DATASET.csv")
    if os.path.exists(chembl_path):
        try:
            df = pd.read_csv(chembl_path, sep=";", usecols=["Smiles"], nrows=5000)
            smiles_iter = df["Smiles"].dropna().astype(str)
        except Exception as exc:
            logger.warning("CHEMBL reference DB load failed: %s", exc)
            smiles_iter = []
    else:
        smiles = []
        for target in MODELS or _discover_trained_targets():
            path = _cleaned_data_path(target)
            if path:
                try:
                    smiles.extend(pd.read_csv(path, usecols=["SMILES"])["SMILES"].dropna().astype(str).head(2000))
                except Exception:
                    pass
        smiles_iter = smiles

    for smi in smiles_iter:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            continue
        reference_fps.append(morgan_generator.GetFingerprint(mol))
        reference_smiles.append(str(smi))

    logger.info("Loaded %s global similarity fingerprints", len(reference_fps))


def _mol_from_smiles(smiles: str):
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None:
        raise HTTPException(400, "Invalid SMILES")
    return mol


def _descriptor_array(mol) -> np.ndarray:
    raw = descriptor_calculator.CalcDescriptors(mol)
    arr = np.array(raw, dtype=np.float64).reshape(1, -1)
    arr = np.nan_to_num(arr, nan=0.0, posinf=1e6, neginf=-1e6)
    arr = np.clip(arr, -1e6, 1e6)
    return arr.astype(np.float32)


def _fingerprint_array(mol) -> np.ndarray:
    fp = morgan_generator.GetFingerprint(mol)
    arr = np.zeros((FP_SIZE,), dtype=np.int8)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr.reshape(1, -1).astype(np.float32)


def _feature_matrix_from_mol(mol) -> np.ndarray:
    return np.hstack([_descriptor_array(mol), _fingerprint_array(mol)])


def _scaled_features(mol, bundle: TargetBundle) -> np.ndarray:
    features = _feature_matrix_from_mol(mol)
    selected = bundle.selector.transform(features)
    return bundle.scaler.transform(selected)


def _applicability_domain(mol, bundle: TargetBundle) -> Dict[str, Any]:
    if not bundle.reference_fps or bundle.ad_threshold is None:
        return {"inside_domain": None, "distance": None, "threshold": None}

    query_fp = morgan_generator.GetFingerprint(mol)
    sims = DataStructs.BulkTanimotoSimilarity(query_fp, bundle.reference_fps)
    distance = 1.0 - max(sims) if sims else None
    inside = distance <= bundle.ad_threshold if distance is not None else None
    return {
        "inside_domain": inside,
        "distance": round(float(distance), 4) if distance is not None else None,
        "threshold": round(float(bundle.ad_threshold), 4),
    }


def predict_target(smiles: str, target: str) -> Dict[str, Any]:
    target = _target_key(target)
    if target not in MODELS:
        raise HTTPException(404, f"No loaded model for target {target}")

    mol = _mol_from_smiles(smiles)
    bundle = MODELS[target]
    x_scaled = _scaled_features(mol, bundle)
    prob = float(bundle.model.predict_proba(x_scaled)[0][1])
    ad = _applicability_domain(mol, bundle)

    return {
        "target": target,
        "type": bundle.metadata.get("type", "Unknown"),
        "relevance": bundle.metadata.get("relevance", "Unknown"),
        "confidence": round(prob * 100, 2),
        "active": bool(prob >= ACTIVE_THRESHOLD),
        "pic50_estimate": round(4.0 + prob * 5.0, 2),
        **ad,
    }


# -----------------------------------------------------------------------------
# Chemistry helpers
# -----------------------------------------------------------------------------
def _mol_properties(mol):
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rot = Descriptors.NumRotatableBonds(mol)
    rings = Descriptors.RingCount(mol)
    arom = rdMolDescriptors.CalcNumAromaticRings(mol)
    fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)
    mw_exact = Descriptors.ExactMolWt(mol)
    heavy = mol.GetNumHeavyAtoms()
    charge = sum(a.GetFormalCharge() for a in mol.GetAtoms())
    mr = round(Descriptors.MolMR(mol), 2) if hasattr(Descriptors, "MolMR") else 0.0
    return dict(
        mw=round(mw, 2),
        logp=round(logp, 2),
        hbd=hbd,
        hba=hba,
        tpsa=round(tpsa, 2),
        rotatable_bonds=rot,
        rings=rings,
        aromatic_rings=arom,
        fsp3=round(fsp3, 3),
        exact_mw=round(mw_exact, 4),
        heavy_atom_count=heavy,
        formal_charge=charge,
        molar_refractivity=mr,
    )


def _drug_likeness(props):
    mw, logp, hbd, hba, tpsa, rot = (
        props["mw"],
        props["logp"],
        props["hbd"],
        props["hba"],
        props["tpsa"],
        props["rotatable_bonds"],
    )
    mr = props.get("molar_refractivity", 0)
    heavy = props.get("heavy_atom_count", 0)

    lipinski = (mw <= 500) and (logp <= 5) and (hbd <= 5) and (hba <= 10)
    veber = (rot <= 10) and (tpsa <= 140)
    ghose = (160 <= mw <= 480) and (-0.4 <= logp <= 5.6) and (40 <= mr <= 130) and (20 <= heavy <= 70)
    egan = (logp <= 5.88) and (tpsa <= 131.6)
    muegge = (200 <= mw <= 600) and (-2 <= logp <= 5) and (tpsa <= 150) and (rot <= 15) and (hbd <= 5) and (hba <= 10)
    bio_score = round((1 if lipinski else 0) * 0.4 + (1 if veber else 0) * 0.3 + (1 if ghose else 0) * 0.3, 2)

    return dict(lipinski=lipinski, veber=veber, ghose=ghose, egan=egan, muegge=muegge, bioavailability_score=bio_score)


def _admet_heuristics(props):
    logp, tpsa, mw, hbd = props["logp"], props["tpsa"], props["mw"], props["hbd"]
    absorption = "High" if tpsa <= 140 and logp <= 5 else "Low"
    bbb = "Permeable" if tpsa < 90 and logp > 1 and mw < 450 else "Impermeable"
    herg = "Risk" if logp > 3.7 and mw > 400 else "Low Risk"
    hepatotox = "Risk" if logp > 5 or hbd > 5 else "Low Risk"
    cyp = "Possible Inhibitor" if logp > 3 else "Unlikely"
    toxicity = "Flagged" if logp > 5 else "Safe"
    return dict(absorption=absorption, toxicity=toxicity, bbb=bbb, herg=herg, hepatotoxicity=hepatotox, cyp_inhibition=cyp)


def _mol_svg(mol):
    try:
        drawer = Draw.rdMolDraw2D.MolDraw2DSVG(300, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        return drawer.GetDrawingText()
    except Exception:
        return ""


def _patch_xgb_base_score(model):
    """Workaround for XGBoost 2.x + old SHAP incompatibility.

    XGBoost 2.x stores base_score internally as '[5E-1]' or '[6.8950707E-1]'
    (bracketed scientific-notation). Older SHAP does float(base_score) which
    crashes on the brackets.

    The ONLY reliable fix is a JSON roundtrip:
      1. Dump the booster to a temp JSON file via save_model()
      2. Regex-replace every bracketed base_score e.g. '[5E-1]' -> '0.5'
      3. Load a fresh Booster from the patched JSON
    This ensures the internal config SHAP reads is already corrected.
    """
    import tempfile
    import xgboost as xgb

    booster = model.get_booster() if hasattr(model, 'get_booster') else model

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        tmp_path = f.name

    try:
        booster.save_model(tmp_path)

        with open(tmp_path, 'r', encoding='utf-8') as f:
            raw_json = f.read()

        # "[5E-1]" -> "0.5",  "[6.8950707E-1]" -> "0.6895070695877075"
        patched_json = re.sub(
            r'("base_score"\s*:\s*")\[([^\]]+)\](")',
            lambda m: m.group(1) + str(float(m.group(2).strip())) + m.group(3),
            raw_json,
        )

        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(patched_json)

        fresh = xgb.Booster()
        fresh.load_model(tmp_path)
        logger.info("XGB base_score JSON-patched for SHAP compatibility")
        return fresh
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# -----------------------------------------------------------------------------
# Health and model discovery
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "3.0",
        "loaded_model_count": len(MODELS),
        "targets": list(MODELS.keys()),
        "reference_db_size": len(reference_fps),
    }


@app.get("/available_targets")
def available_targets():
    loaded = {}
    for target in _supported_targets():
        bundle = MODELS.get(target)
        loaded[target] = {
            "loaded": bundle is not None,
            "display_name": _target_label(target),
            "metadata": TARGET_INFO.get(target, {}),
            "model_dir": bundle.model_dir if bundle else _target_model_dir(target),
            "feature_count": len(bundle.selected_feature_names) if bundle else None,
            "reference_fingerprints": len(bundle.reference_fps) if bundle else 0,
            "ad_threshold": bundle.ad_threshold if bundle else None,
        }
    return {"loaded_models": list(MODELS.keys()), "targets": loaded}


# -----------------------------------------------------------------------------
# Prediction endpoints
# -----------------------------------------------------------------------------
@app.post("/predict_target")
def predict_target_endpoint(req: TargetPredictRequest):
    return predict_target(req.smiles, req.target)


@app.post("/predict_all")
def predict_all(req: PredictRequest):
    mol = _mol_from_smiles(req.smiles)
    if not MODELS:
        raise HTTPException(503, "No target models loaded")

    results = [predict_target(req.smiles, target) for target in MODELS]
    results.sort(key=lambda x: x["confidence"], reverse=True)
    best = results[0]["target"] if results and results[0]["active"] else "None (Inactive)"

    props = _mol_properties(mol)
    dl = _drug_likeness(props)
    admet = _admet_heuristics(props)
    svg = _mol_svg(mol)

    return {
        "predictions": results,
        "best_target": best,
        "molecular_properties": props,
        "drug_likeness": dl,
        "lipinski_pass": dl["lipinski"],
        "admet": admet,
        "svg": svg,
    }


@app.post("/predict_batch")
def predict_batch(req: BatchRequest):
    target = _target_key(req.target_filter)
    if target not in MODELS:
        raise HTTPException(404, f"No loaded model for target {target}")

    out = []
    invalid_smiles = 0
    failed_predictions = 0
    total_input = 0

    for smi in req.smiles_list[:1000]:
        smi = smi.strip()
        if not smi:
            continue
        total_input += 1
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            invalid_smiles += 1
            continue
        try:
            pred = predict_target(smi, target)
            props = _mol_properties(mol)
            out.append({"smiles": smi, **pred, **props})
        except Exception as exc:
            failed_predictions += 1
            logger.warning("Prediction failed for %s: %s", smi[:30], exc)

    out.sort(key=lambda x: x["confidence"], reverse=True)
    return {
        "total_input": total_input,
        "total_processed": len(out),
        "invalid_smiles": invalid_smiles,
        "failed_predictions": failed_predictions,
        "top_50": out[:50],
    }


@app.post("/explain_prediction")
def explain_prediction(req: ExplainRequest):
    target = _target_key(req.target)
    if target not in MODELS:
        raise HTTPException(404, f"No loaded model for target {target}")

    top_n = max(1, min(req.top_n, 50))
    mol = _mol_from_smiles(req.smiles)
    bundle = MODELS[target]
    x_scaled = _scaled_features(mol, bundle)

    if bundle.shap_explainer is None:
        try:
            bundle.shap_explainer = shap.TreeExplainer(bundle.model)
        except (ValueError, TypeError) as exc:
            # XGBoost 2.x stores base_score as '[float]' which older SHAP
            # cannot parse. Patch the booster and retry.
            logger.warning(
                "TreeExplainer failed for %s (%s). Retrying with patched booster.",
                target, exc
            )
            patched = _patch_xgb_base_score(bundle.model)
            bundle.shap_explainer = shap.TreeExplainer(patched)

    shap_values = bundle.shap_explainer.shap_values(x_scaled)
    # Handle different SHAP output shapes:
    #   ndarray of shape (1, n_features)         -> multiclass disabled
    #   list of two arrays [(1,n), (1,n)]        -> binary XGBoost multi-output
    if isinstance(shap_values, np.ndarray):
        values = shap_values[0]
    elif isinstance(shap_values, list):
        # Binary classification: index 1 = positive class
        arr = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        values = arr[0] if arr.ndim == 2 else arr
    else:
        values = np.array(shap_values[0])
    ranked_idx = np.argsort(np.abs(values))[::-1][:top_n]

    features = []
    for idx in ranked_idx:
        name = bundle.selected_feature_names[idx] if idx < len(bundle.selected_feature_names) else f"feature_{idx}"
        features.append(
            {
                "feature": name,
                "importance": round(float(abs(values[idx])), 6),
                "shap_value": round(float(values[idx]), 6),
                "direction": "increases_activity" if values[idx] > 0 else "decreases_activity",
            }
        )

    pred = predict_target(req.smiles, target)
    return {
        "target": target,
        "confidence": pred["confidence"],
        "active": pred["active"],
        "top_features": features,
        "summary": f"Top feature for {target} is {features[0]['feature'] if features else 'N/A'}; confidence is {pred['confidence']}%.",
    }


# -----------------------------------------------------------------------------
# Pharmacophore and cheminformatics endpoints
# -----------------------------------------------------------------------------
@app.post("/pharmacophore")
def pharmacophore(req: PredictRequest):
    mol = _mol_from_smiles(req.smiles)
    mol3d = Chem.AddHs(mol)
    try:
        AllChem.EmbedMolecule(mol3d, AllChem.ETKDG())
        conf = mol3d.GetConformer()
        has_3d = True
    except Exception:
        has_3d = False
        conf = None

    features = []
    counts = {"hbd": 0, "hba": 0, "aromatic": 0, "hydrophobic": 0, "pos_ionizable": 0, "neg_ionizable": 0}

    for atom in mol.GetAtoms():
        idx = atom.GetIdx()
        sym = atom.GetSymbol()
        pos = list(conf.GetAtomPosition(idx)) if has_3d else [0, 0, 0]

        if sym in ("N", "O") and atom.GetTotalNumHs() > 0:
            features.append({"type": "hbd", "atom_idx": idx, "label": "HBD", "color": "#3B82F6", "coords": pos})
            counts["hbd"] += 1
        elif sym in ("N", "O", "F") and atom.GetTotalNumHs() == 0:
            features.append({"type": "hba", "atom_idx": idx, "label": "HBA", "color": "#EF4444", "coords": pos})
            counts["hba"] += 1

    for ring in mol.GetRingInfo().AtomRings():
        if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring):
            center = [0, 0, 0]
            if has_3d:
                ps = [conf.GetAtomPosition(i) for i in ring]
                center = [sum(p.x for p in ps) / len(ps), sum(p.y for p in ps) / len(ps), sum(p.z for p in ps) / len(ps)]
            features.append({"type": "aromatic", "atom_idx": list(ring), "label": "ARO", "color": "#F59E0B", "coords": center})
            counts["aromatic"] += 1

    for atom in mol.GetAtoms():
        if atom.GetSymbol() == "C" and not atom.GetIsAromatic():
            nb_syms = [n.GetSymbol() for n in atom.GetNeighbors()]
            if all(s in ("C", "H") for s in nb_syms):
                idx = atom.GetIdx()
                pos = list(conf.GetAtomPosition(idx)) if has_3d else [0, 0, 0]
                features.append({"type": "hydrophobic", "atom_idx": idx, "label": "HYD", "color": "#10B981", "coords": pos})
                counts["hydrophobic"] += 1

    score = round(counts["hbd"] * 0.2 + counts["hba"] * 0.2 + counts["aromatic"] * 0.3 + counts["hydrophobic"] * 0.1, 2)
    return {"features": features, "feature_counts": counts, "pharmacophore_score": min(score, 10.0), "has_3d_coords": has_3d, "svg": _mol_svg(mol)}


@app.post("/similarity_search")
def similarity_search(req: SimilarityRequest):
    mol = _mol_from_smiles(req.smiles)
    if not reference_fps:
        raise HTTPException(503, "Reference DB not loaded")

    query_fp = morgan_generator.GetFingerprint(mol)
    sims = DataStructs.BulkTanimotoSimilarity(query_fp, reference_fps)
    ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)

    top_n = min(req.top_n, 20)
    results = []
    seen = set()
    for idx, score in ranked:
        smi = reference_smiles[idx]
        if smi in seen or smi == req.smiles:
            continue
        seen.add(smi)
        ref_mol = Chem.MolFromSmiles(smi)
        props = _mol_properties(ref_mol) if ref_mol else {}
        results.append({"smiles": smi, "tanimoto": round(float(score), 4), "properties": props})
        if len(results) >= top_n:
            break

    return {"query": req.smiles, "top_n": len(results), "results": results}


@app.get("/prepare_docking")
def prepare_docking(smiles: str, format: str = "pdb"):
    mol = _mol_from_smiles(smiles)
    mol3d = Chem.AddHs(mol)
    try:
        AllChem.EmbedMolecule(mol3d, AllChem.ETKDG())
        AllChem.MMFFOptimizeMolecule(mol3d)
        AllChem.ComputeGasteigerCharges(mol3d)
    except Exception as exc:
        raise HTTPException(500, f"3D generation failed: {exc}") from exc

    fmt = format.lower()
    if fmt == "mol":
        return PlainTextResponse(Chem.MolToMolBlock(mol3d), media_type="chemical/x-mdl-molfile")
    if fmt == "sdf":
        buf = io.StringIO()
        writer = Chem.SDWriter(buf)
        writer.write(mol3d)
        writer.close()
        return PlainTextResponse(buf.getvalue(), media_type="chemical/x-sdf")
    return PlainTextResponse(Chem.MolToPDBBlock(mol3d), media_type="chemical/x-pdb")


@app.post("/chemical_space")
def chemical_space(req: ChemSpaceRequest):
    if len(req.smiles_list) < 2:
        raise HTTPException(400, "Need at least 2 SMILES")

    fps, valid_smiles = [], []
    for smi in req.smiles_list[:200]:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            fp = morgan_generator.GetFingerprint(mol)
            arr = np.zeros(FP_SIZE, dtype=np.float32)
            DataStructs.ConvertToNumpyArray(fp, arr)
            fps.append(arr)
            valid_smiles.append(smi)

    if len(fps) < 2:
        raise HTTPException(400, "Too few valid SMILES")

    X = np.array(fps)
    method = req.method.lower()
    if method == "tsne" and len(fps) >= 5:
        perp = min(5, len(fps) - 1)
        coords = TSNE(n_components=2, perplexity=perp, random_state=42).fit_transform(X)
        method_used = "t-SNE"
    else:
        coords = PCA(n_components=2, random_state=42).fit_transform(X)
        method_used = "PCA"

    points = [{"smiles": s, "x": round(float(c[0]), 4), "y": round(float(c[1]), 4)} for s, c in zip(valid_smiles, coords)]
    return {"method": method_used, "points": points, "count": len(points)}


@app.post("/drug_likeness")
def drug_likeness_endpoint(req: PredictRequest):
    mol = _mol_from_smiles(req.smiles)
    props = _mol_properties(mol)
    return {"properties": props, "drug_likeness": _drug_likeness(props), "admet": _admet_heuristics(props)}


@app.get("/top10/{target}")
def get_top10(target: str):
    target = _target_key(target)
    if target not in _supported_targets():
        raise HTTPException(400, "Invalid target")

    csv_path = _cleaned_data_path(target)
    if csv_path:
        df = pd.read_csv(csv_path)
        active_df = df[df["Activity"] == 1] if "Activity" in df.columns else df
        top = active_df.sort_values("IC50").head(10) if "IC50" in active_df.columns else active_df.head(10)
        return {"top10": [{"smiles": r["SMILES"], "ic50": r.get("IC50", "N/A"), "target": target} for _, r in top.iterrows()]}

    raise HTTPException(404, f"No cleaned data source found for {target}")


@app.get("/chembl")
def get_chembl(smiles: str):
    encoded = requests.utils.quote(smiles)
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule.json?molecule_structures__canonical_smiles__exact={encoded}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("molecules"):
            molecule = data["molecules"][0]
            cid = molecule["molecule_chembl_id"]
            return {"chembl_id": cid, "pref_name": molecule.get("pref_name", "Unknown"), "link": f"https://www.ebi.ac.uk/chembl/compound_report_card/{cid}/"}
        return {"error": "Not found in ChEMBL"}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/filter_batch")
def filter_batch(req: FilterRequest):
    passed, rejected = [], []
    invalid_smiles = 0

    for smi in req.smiles_list[:500]:
        smi = smi.strip()
        if not smi:
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            invalid_smiles += 1
            continue

        reasons = []
        props = _mol_properties(mol)
        mp = req.mol_properties
        if not (mp.mw_min <= props["mw"] <= mp.mw_max):
            reasons.append(f"MW {props['mw']} not in [{mp.mw_min}-{mp.mw_max}]")
        if not (mp.logp_min <= props["logp"] <= mp.logp_max):
            reasons.append(f"LogP {props['logp']} not in [{mp.logp_min}-{mp.logp_max}]")
        if not (mp.tpsa_min <= props["tpsa"] <= mp.tpsa_max):
            reasons.append(f"TPSA {props['tpsa']} not in [{mp.tpsa_min}-{mp.tpsa_max}]")
        if props["hbd"] > mp.hbd_max:
            reasons.append(f"HBD {props['hbd']} > max {mp.hbd_max}")
        if props["hba"] > mp.hba_max:
            reasons.append(f"HBA {props['hba']} > max {mp.hba_max}")
        if props["rotatable_bonds"] > mp.rotatable_max:
            reasons.append(f"RotBonds {props['rotatable_bonds']} > max {mp.rotatable_max}")
        if props["aromatic_rings"] < mp.aromatic_min:
            reasons.append(f"Aromatic rings {props['aromatic_rings']} < min {mp.aromatic_min}")
        if not (mp.heavy_min <= props["heavy_atom_count"] <= mp.heavy_max):
            reasons.append(f"Heavy atoms {props['heavy_atom_count']} not in [{mp.heavy_min}-{mp.heavy_max}]")

        hbd = hba = aromatic = hydrophobic = 0
        for atom in mol.GetAtoms():
            sym = atom.GetSymbol()
            if sym in ("N", "O") and atom.GetTotalNumHs() > 0:
                hbd += 1
            elif sym in ("N", "O", "F") and atom.GetTotalNumHs() == 0:
                hba += 1
            elif sym == "C" and not atom.GetIsAromatic():
                nb = [n.GetSymbol() for n in atom.GetNeighbors()]
                if all(s in ("C", "H") for s in nb):
                    hydrophobic += 1

        for ring in mol.GetRingInfo().AtomRings():
            if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring):
                aromatic += 1

        pf = req.pharmacophore
        if not (pf.hbd_min <= hbd <= pf.hbd_max):
            reasons.append(f"Pharmacophore HBD {hbd} not in [{pf.hbd_min}-{pf.hbd_max}]")
        if not (pf.hba_min <= hba <= pf.hba_max):
            reasons.append(f"Pharmacophore HBA {hba} not in [{pf.hba_min}-{pf.hba_max}]")
        if not (pf.aromatic_min <= aromatic <= pf.aromatic_max):
            reasons.append(f"Pharmacophore Aromatic {aromatic} not in [{pf.aromatic_min}-{pf.aromatic_max}]")
        if hydrophobic < pf.hydrophobic_min:
            reasons.append(f"Pharmacophore Hydrophobic {hydrophobic} < min {pf.hydrophobic_min}")

        dl = _drug_likeness(props)
        dlf = req.drug_likeness
        if dlf.lipinski and not dl["lipinski"]:
            reasons.append("Fails Lipinski Rule of Five")
        if dlf.veber and not dl["veber"]:
            reasons.append("Fails Veber Rule")
        if dlf.ghose and not dl["ghose"]:
            reasons.append("Fails Ghose Filter")
        if dlf.egan and not dl["egan"]:
            reasons.append("Fails Egan Rule")
        if dlf.muegge and not dl["muegge"]:
            reasons.append("Fails Muegge Rule")

        admet = _admet_heuristics(props)
        af = req.admet
        for field_name in ("absorption", "bbb", "herg", "hepatotoxicity", "toxicity", "cyp_inhibition"):
            wanted = getattr(af, field_name)
            if wanted and admet[field_name] != wanted:
                reasons.append(f"{field_name}: {admet[field_name]} (want {wanted})")

        entry = {
            "smiles": smi,
            "pharmacophore": {"hbd": hbd, "hba": hba, "aromatic": aromatic, "hydrophobic": hydrophobic},
            "properties": props,
            "drug_likeness": dl,
            "admet": admet,
        }
        if reasons:
            rejected.append({**entry, "reasons": reasons})
        else:
            passed.append(entry)

    return {
        "total_input": len(req.smiles_list),
        "invalid_smiles": invalid_smiles,
        "passed": len(passed),
        "rejected": len(rejected),
        "passed_molecules": passed[:100],
        "rejected_molecules": rejected[:50],
    }


@app.get("/pdb", response_class=PlainTextResponse)
def get_pdb(smiles: str):
    mol = _mol_from_smiles(smiles)
    mol3d = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol3d, AllChem.ETKDG())
    return Chem.MolToPDBBlock(mol3d)


# =============================================================================
# Molecular Docking Endpoints
# =============================================================================

def _get_docking_runner():
    """Lazy-import the docking module so the backend starts even if docking
    dependencies (rdkit, subprocess tools) have any issues."""
    try:
        import docking.vina_runner as vr
        return vr
    except ImportError as exc:
        logger.error("Failed to import docking module: %s", exc)
        raise HTTPException(500, f"Docking module not available: {exc}")


@app.get("/docking_targets")
def docking_targets():
    """Return all supported docking targets and their availability status."""
    vr = _get_docking_runner()
    targets = {}
    for name, cfg in vr.TARGET_CONFIG.items():
        targets[name] = {
            "pdb_id":    cfg["pdb_id"],
            "type":      cfg["type"],
            "cancer":    cfg["cancer"],
            "available": cfg["available"],
            "grid_center": cfg["center"],
            "grid_size":   cfg["size"],
        }
    available = [n for n, c in vr.TARGET_CONFIG.items() if c["available"]]
    return {
        "targets":         targets,
        "available_count": len(available),
        "available":       available,
    }


@app.get("/docking_status")
def docking_status():
    """Check whether AutoDock Vina and OpenBabel are installed and reachable."""
    vr = _get_docking_runner()
    return vr.check_tools()


@app.post("/dock")
def dock(req: DockingRequest):
    """Run the full molecular docking pipeline.

    Steps:
        1. Validate SMILES with RDKit
        2. Generate 3D ligand structure (MMFF optimized)
        3. Convert to AutoDock PDBQT via OpenBabel
        4. Run AutoDock Vina against the selected receptor
        5. Extract and return binding affinity scores

    Returns a JSON result with docking score (kcal/mol), all pose scores,
    binding quality label, and file paths.
    """
    vr = _get_docking_runner()

    # Basic SMILES validation before handing off to docking engine
    smiles = req.smiles.strip()
    if not smiles:
        raise HTTPException(400, "SMILES string cannot be empty")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise HTTPException(400, f"Invalid SMILES string: {smiles!r}")

    exhaustiveness = max(1, min(req.exhaustiveness, 32))  # clamp 1-32

    logger.info(
        "Docking request: target=%s smiles=%s exhaustiveness=%d",
        req.target, smiles[:40], exhaustiveness,
    )

    result = vr.run_docking_pipeline(
        smiles=smiles,
        target=req.target,
        exhaustiveness=exhaustiveness,
    )

    # Surface docking errors as HTTP errors so the frontend gets clean messages
    if result.get("status") == "error":
        raise HTTPException(422, result.get("error", "Docking failed"))
    if result.get("status") == "unavailable":
        raise HTTPException(503, result.get("error", "Target not available"))

    return result


if __name__ == "__main__":
    import sys
    import os
    import uvicorn

    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    uvicorn.run(app, host="0.0.0.0", port=8000)
