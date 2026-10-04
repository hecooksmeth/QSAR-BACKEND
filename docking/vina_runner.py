"""
vina_runner.py — Modular AutoDock Vina docking engine
======================================================
Supports: AKT1, ALK, BRAF, CDK2, EGFR, FLT3, HER2, PARP1, PI3K, VEGFR2

Usage (imported by FastAPI backend):
    from docking.vina_runner import run_docking_pipeline
    result = run_docking_pipeline(smiles="CCO", target="CDK2")
"""

import os
import re
import subprocess
import tempfile
import logging
from typing import Dict, Any, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem

logger = logging.getLogger("docking")

# ─────────────────────────────────────────────────────────────────────────────
# Tool paths
# On Linux (Docker / Cloud Run): vina and obabel are installed via apt and
# available on PATH — use plain binary names.
# On Windows (local dev): override via VINA_PATH / OBABEL_PATH env vars.
# ─────────────────────────────────────────────────────────────────────────────
VINA_PATH   = os.environ.get("VINA_PATH",   "vina")
OBABEL_PATH = os.environ.get("OBABEL_PATH", "obabel")

# In Docker the layout is:
#   /app/docking/vina_runner.py   ← this file
#   /app/proteins/<TARGET>.pdbqt  ← receptor files
#   /app/ligands/                 ← generated ligand files (temp)
#   /app/results/                 ← docking output (temp)
#
# _BACKEND_DIR = /app   (parent of docking/)
_BACKEND_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTEINS_DIR  = os.path.join(_BACKEND_DIR, "proteins")
LIGANDS_DIR   = os.path.join(_BACKEND_DIR, "ligands")
RESULTS_DIR   = os.path.join(_BACKEND_DIR, "results")

# Legacy fallback — not used in Docker but kept for local dev
_LEGACY_PROTEINS_DIR = os.path.join(_BACKEND_DIR, "docking_test", "proteins")

# ─────────────────────────────────────────────────────────────────────────────
# Protein target configuration
# Each target has:
#   pdb_id  : RCSB PDB accession
#   type    : protein family
#   cancer  : relevant cancer type
#   center  : (x, y, z) grid box center at the binding site
#   size    : (sx, sy, sz) grid box dimensions in Angstroms
#   available: True when .pdbqt file is confirmed present
# ─────────────────────────────────────────────────────────────────────────────
TARGET_CONFIG: Dict[str, Dict[str, Any]] = {
    # ── Originally supported targets ────────────────────────────────────────
    "CDK2": {
        "pdb_id":    "4EK3",
        "type":      "Cyclin-Dependent Kinase",
        "cancer":    "Cell Cycle Regulation / Breast Cancer",
        "center":    (24.0, 5.0, 17.0),
        "size":      (20.0, 20.0, 20.0),
        "available": True,
    },
    "PARP1": {
        "pdb_id":    "4UND",
        "type":      "DNA Repair Enzyme",
        "cancer":    "Ovarian / Breast Cancer",
        "center":    (28.0, -6.0, 18.0),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "HER2": {
        "pdb_id":    "3PP0",
        "type":      "Growth Factor Receptor",
        "cancer":    "Breast Cancer",
        "center":    (6.0, 17.0, 29.0),
        "size":      (20.0, 20.0, 20.0),
        "available": True,
    },
    "ALK": {
        "pdb_id":    "2XP2",
        "type":      "Receptor Tyrosine Kinase",
        "cancer":    "Lung Cancer",
        "center":    (30.0, 2.0, 14.0),
        "size":      (20.0, 20.0, 20.0),
        "available": True,
    },

    # ── Newly added targets (.pdbqt files present in docking_test/proteins/) ─
    "EGFR": {
        "pdb_id":    "1M17",
        "type":      "Receptor Tyrosine Kinase",
        "cancer":    "Lung / Breast Cancer",
        # ATP-binding cleft — centered on erlotinib co-crystal (1M17)
        "center":    (22.5, 4.5, 51.0),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "BRAF": {
        "pdb_id":    "4RZV",
        "type":      "Serine/Threonine Kinase",
        "cancer":    "Melanoma / Colorectal Cancer",
        # DFG-in ATP pocket — centered on vemurafenib binding site (4RZV)
        "center":    (-10.0, 4.0, 49.0),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "AKT1": {
        "pdb_id":    "4EKL",
        "type":      "Serine/Threonine Kinase",
        "cancer":    "Breast / Prostate Cancer",
        # ATP-binding cleft of AKT1 kinase domain (4EKL)
        "center":    (1.5, 17.0, 10.0),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "VEGFR2": {
        "pdb_id":    "3VHE",
        "type":      "Angiogenesis Receptor",
        "cancer":    "Tumor Vascularization",
        # ATP-binding site — centered on axitinib co-crystal (3VHE)
        "center":    (-1.5, 9.5, -4.5),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "FLT3": {
        "pdb_id":    "6JQR",
        "type":      "Receptor Tyrosine Kinase",
        "cancer":    "Acute Myeloid Leukemia",
        # Catalytic site — centered on gilteritinib binding region (6JQR)
        "center":    (8.5, -1.0, 18.5),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
    "PI3K": {
        "pdb_id":    "2RD0",
        "type":      "Lipid Kinase",
        "cancer":    "Cancer Survival / Proliferation",
        # ATP-binding pocket of PI3Kα (2RD0)
        "center":    (9.0, 5.0, -1.0),
        "size":      (22.0, 22.0, 22.0),
        "available": True,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_dirs() -> None:
    """Create output directories if they don't exist."""
    for d in (LIGANDS_DIR, RESULTS_DIR):
        os.makedirs(d, exist_ok=True)


def _find_receptor(target: str) -> Optional[str]:
    """Locate the .pdbqt receptor file for a given target.

    Searches in:
      1. project-root/proteins/<TARGET>.pdbqt
      2. project-root/docking_test/proteins/<TARGET>.pdbqt   (legacy location)
    """
    filename = f"{target}.pdbqt"
    candidates = [
        os.path.join(PROTEINS_DIR, filename),
        os.path.join(_LEGACY_PROTEINS_DIR, filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _which(cmd: str) -> bool:
    """Return True if `cmd` is executable (found on PATH or as a file)."""
    import shutil
    return bool(shutil.which(cmd)) or os.path.isfile(cmd)


def check_tools() -> Dict[str, Any]:
    """Check whether Vina and OpenBabel executables are reachable."""
    vina_ok   = _which(VINA_PATH)
    obabel_ok = _which(OBABEL_PATH)

    vina_version = obabel_version = "not found"
    if vina_ok:
        try:
            out = subprocess.run([VINA_PATH, "--version"],
                                 capture_output=True, text=True, timeout=10)
            vina_version = (out.stdout or out.stderr).strip().split("\n")[0]
        except Exception:
            vina_version = "error reading version"

    if obabel_ok:
        try:
            out = subprocess.run([OBABEL_PATH, "--version"],
                                 capture_output=True, text=True, timeout=10)
            obabel_version = (out.stdout or out.stderr).strip().split("\n")[0]
        except Exception:
            obabel_version = "error reading version"

    return {
        "vina_available":   vina_ok,
        "vina_path":        VINA_PATH,
        "vina_version":     vina_version,
        "obabel_available": obabel_ok,
        "obabel_path":      OBABEL_PATH,
        "obabel_version":   obabel_version,
        "ready":            vina_ok and obabel_ok,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Generate 3D ligand .mol from SMILES using RDKit
# ─────────────────────────────────────────────────────────────────────────────

def generate_ligand_mol(smiles: str, output_path: str) -> str:
    """Convert a SMILES string to a 3D-optimized .mol file.

    Args:
        smiles: Input SMILES string.
        output_path: Path to write the .mol file.

    Returns:
        The output_path on success.

    Raises:
        ValueError: If SMILES is invalid or 3D embedding fails.
    """
    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles!r}")

    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol, params)
    if result == -1:
        # Fallback: random coordinates
        result = AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    if result == -1:
        raise ValueError("3D embedding failed — molecule may be too complex or invalid.")

    # MMFF94 geometry optimization
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)
    except Exception as exc:
        logger.warning("MMFF optimization failed (non-fatal): %s", exc)

    Chem.MolToMolFile(mol, output_path)
    logger.info("Ligand .mol written: %s", output_path)
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Convert .mol → .pdbqt using OpenBabel
# ─────────────────────────────────────────────────────────────────────────────

def convert_mol_to_pdbqt(mol_path: str, pdbqt_path: str) -> str:
    """Convert a .mol file to AutoDock .pdbqt format using OpenBabel.

    Args:
        mol_path:   Path to input .mol file.
        pdbqt_path: Path to write output .pdbqt file.

    Returns:
        The pdbqt_path on success.

    Raises:
        RuntimeError: If OpenBabel fails or the output file is not created.
    """
    cmd = [OBABEL_PATH, mol_path, "-O", pdbqt_path, "--gen3d", "-h"]
    logger.info("Running OpenBabel: %s", " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    logger.debug("OpenBabel stdout: %s", result.stdout)
    logger.debug("OpenBabel stderr: %s", result.stderr)

    if result.returncode != 0 and not os.path.isfile(pdbqt_path):
        raise RuntimeError(
            f"OpenBabel conversion failed (exit {result.returncode}):\n{result.stderr}"
        )

    if not os.path.isfile(pdbqt_path):
        raise RuntimeError("OpenBabel ran but .pdbqt output file was not created.")

    logger.info("Ligand .pdbqt written: %s", pdbqt_path)
    return pdbqt_path


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Run AutoDock Vina
# ─────────────────────────────────────────────────────────────────────────────

def run_vina(
    receptor: str,
    ligand: str,
    center: Tuple[float, float, float],
    size: Tuple[float, float, float],
    output: str,
    exhaustiveness: int = 8,
) -> subprocess.CompletedProcess:
    """Execute AutoDock Vina and return the completed process.

    Args:
        receptor:       Path to receptor .pdbqt file.
        ligand:         Path to ligand .pdbqt file.
        center:         (cx, cy, cz) grid box center coordinates.
        size:           (sx, sy, sz) grid box dimensions in Angstroms.
        output:         Path to write docked poses .pdbqt.
        exhaustiveness: Search thoroughness (8 = default, higher = slower/better).

    Returns:
        subprocess.CompletedProcess with stdout/stderr.

    Raises:
        RuntimeError: If Vina exits with a non-zero return code.
    """
    cx, cy, cz = center
    sx, sy, sz = size

    cmd = [
        VINA_PATH,
        "--receptor",      receptor,
        "--ligand",        ligand,
        "--center_x",      str(cx),
        "--center_y",      str(cy),
        "--center_z",      str(cz),
        "--size_x",        str(sx),
        "--size_y",        str(sy),
        "--size_z",        str(sz),
        "--out",           output,
        "--exhaustiveness", str(exhaustiveness),
    ]

    logger.info("Running Vina: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    logger.debug("Vina stdout:\n%s", result.stdout)

    if result.returncode != 0:
        raise RuntimeError(
            f"AutoDock Vina failed (exit {result.returncode}):\n{result.stderr}"
        )

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Extract docking scores from Vina output
# ─────────────────────────────────────────────────────────────────────────────

def extract_scores(vina_stdout: str) -> List[float]:
    """Parse all binding affinities from Vina stdout.

    Vina output table looks like:
       mode |   affinity | dist from best mode
            | (kcal/mol) | rmsd l.b.| rmsd u.b.
    --------+------------+----------+----------
          1       -8.700      0.000      0.000
          2       -7.900      1.234      2.100
    ...

    Args:
        vina_stdout: Raw stdout string from Vina.

    Returns:
        List of binding affinity floats, best pose first. Empty list if none found.
    """
    pattern = re.compile(r"^\s+\d+\s+(-?\d+\.\d+)", re.MULTILINE)
    matches = pattern.findall(vina_stdout)
    scores = [float(s) for s in matches]
    logger.info("Extracted docking scores: %s", scores)
    return scores


def score_label(score: float) -> str:
    """Return a human-readable binding quality label."""
    if score <= -9.0:
        return "Excellent"
    elif score <= -7.0:
        return "Good"
    elif score <= -5.0:
        return "Moderate"
    else:
        return "Weak"


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline — called by the FastAPI endpoint
# ─────────────────────────────────────────────────────────────────────────────

def run_docking_pipeline(
    smiles: str,
    target: str,
    exhaustiveness: int = 8,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the full docking pipeline for a SMILES string against a target protein.

    Pipeline:
        SMILES → RDKit 3D mol → OpenBabel PDBQT → Vina → score extraction

    Args:
        smiles:          Ligand SMILES string.
        target:          Target name (e.g. "CDK2"). Must be in TARGET_CONFIG.
        exhaustiveness:  Vina search thoroughness (default 8).
        job_id:          Optional unique job identifier for file naming.

    Returns:
        Dict with keys:
            target, pdb_id, smiles, score, all_poses, score_label,
            pose_file, status, error (if any)
    """
    target = target.upper().strip()

    # ── Validate target ──────────────────────────────────────────────────────
    if target not in TARGET_CONFIG:
        return {
            "target": target,
            "status": "error",
            "error": f"Unknown target '{target}'. Available: {list(TARGET_CONFIG.keys())}",
        }

    cfg = TARGET_CONFIG[target]

    if not cfg["available"]:
        return {
            "target":  target,
            "pdb_id":  cfg["pdb_id"],
            "status":  "unavailable",
            "error":   (
                f"Receptor file for {target} ({cfg['pdb_id']}) is not yet available. "
                f"Please download from RCSB PDB, prepare with AutoDockTools, "
                f"and place the .pdbqt file at: proteins/{target}.pdbqt"
            ),
        }

    # ── Validate tools ───────────────────────────────────────────────────────
    if not _which(VINA_PATH):
        return {
            "target": target,
            "status": "error",
            "error":  f"AutoDock Vina not found: '{VINA_PATH}'. Install vina or set VINA_PATH env var.",
        }
    if not _which(OBABEL_PATH):
        return {
            "target": target,
            "status": "error",
            "error":  f"OpenBabel not found: '{OBABEL_PATH}'. Install openbabel or set OBABEL_PATH env var.",
        }

    # ── Locate receptor ──────────────────────────────────────────────────────
    receptor_path = _find_receptor(target)
    if receptor_path is None:
        return {
            "target":  target,
            "pdb_id":  cfg["pdb_id"],
            "status":  "error",
            "error":   (
                f"Receptor file not found for {target}. "
                f"Expected: proteins/{target}.pdbqt or docking_test/proteins/{target}.pdbqt"
            ),
        }

    # ── Set up file paths ────────────────────────────────────────────────────
    _ensure_dirs()
    suffix = job_id or target.lower()
    mol_path    = os.path.join(LIGANDS_DIR, f"ligand_{suffix}.mol")
    pdbqt_path  = os.path.join(LIGANDS_DIR, f"ligand_{suffix}.pdbqt")
    output_path = os.path.join(RESULTS_DIR, f"{target}_output_{suffix}.pdbqt")

    try:
        # Step 1: Generate 3D ligand
        logger.info("[%s] Step 1: Generating 3D ligand from SMILES...", target)
        generate_ligand_mol(smiles, mol_path)

        # Step 2: Convert to PDBQT
        logger.info("[%s] Step 2: Converting .mol → .pdbqt...", target)
        convert_mol_to_pdbqt(mol_path, pdbqt_path)

        # Step 3: Run Vina
        logger.info("[%s] Step 3: Running AutoDock Vina (exhaustiveness=%d)...",
                    target, exhaustiveness)
        vina_result = run_vina(
            receptor=receptor_path,
            ligand=pdbqt_path,
            center=cfg["center"],
            size=cfg["size"],
            output=output_path,
            exhaustiveness=exhaustiveness,
        )

        # Step 4: Extract scores
        logger.info("[%s] Step 4: Extracting docking scores...", target)
        scores = extract_scores(vina_result.stdout)

        if not scores:
            return {
                "target":   target,
                "pdb_id":   cfg["pdb_id"],
                "smiles":   smiles,
                "status":   "error",
                "error":    "Vina ran successfully but no docking scores were found in output.",
                "raw_output": vina_result.stdout[:500],
            }

        best_score = scores[0]

        return {
            "target":         target,
            "pdb_id":         cfg["pdb_id"],
            "type":           cfg["type"],
            "cancer":         cfg["cancer"],
            "smiles":         smiles,
            "score":          best_score,
            "score_unit":     "kcal/mol",
            "score_label":    score_label(best_score),
            "all_poses":      scores,
            "pose_count":     len(scores),
            "pose_file":      output_path,
            "receptor_file":  receptor_path,
            "status":         "success",
        }

    except ValueError as exc:
        logger.error("[%s] Ligand preparation error: %s", target, exc)
        return {
            "target": target,
            "pdb_id": cfg["pdb_id"],
            "smiles": smiles,
            "status": "error",
            "error":  f"Ligand preparation failed: {exc}",
        }
    except RuntimeError as exc:
        logger.error("[%s] Docking runtime error: %s", target, exc)
        return {
            "target": target,
            "pdb_id": cfg["pdb_id"],
            "smiles": smiles,
            "status": "error",
            "error":  str(exc),
        }
    except subprocess.TimeoutExpired:
        logger.error("[%s] Docking timed out", target)
        return {
            "target": target,
            "pdb_id": cfg["pdb_id"],
            "smiles": smiles,
            "status": "error",
            "error":  "Docking timed out (>5 minutes). Try reducing exhaustiveness.",
        }
    except Exception as exc:
        logger.exception("[%s] Unexpected docking error: %s", target, exc)
        return {
            "target": target,
            "pdb_id": cfg.get("pdb_id", "?"),
            "smiles": smiles,
            "status": "error",
            "error":  f"Unexpected error: {exc}",
        }
