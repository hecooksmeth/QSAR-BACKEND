# -*- coding: utf-8 -*-
# ============================================================
# QSAR Discovery Suite v2.0 — Model Evaluation Script
# Computes REAL AUC, ROC curves, Accuracy, F1 for all 8 targets
# Model: PyTorch ANN | Features: RDKit Descriptors | Scaler+Selector from pkl
# ============================================================

import os
import pickle
import warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    accuracy_score, f1_score,
    precision_score, recall_score,
    confusion_matrix, classification_report
)
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = r"C:\Users\sudharsan\OneDrive\Desktop\molecular_modelling"
MODEL_PATH  = os.path.join(BASE_DIR, "model.pth")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
SELECT_PATH = os.path.join(BASE_DIR, "selector.pkl")
DATA_PATH   = os.path.join(BASE_DIR, "CHEMBL_DATASET.csv")
OUT_DIR     = os.path.join(BASE_DIR, "plots_fromcode")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Targets ──────────────────────────────────────────────────────────────────
TARGETS    = ["EGFR", "BRAF", "CDK2", "HER2", "VEGFR2", "PI3K", "mTOR", "PARP", "FLT3"]
TARGET_MAP = {t: i for i, t in enumerate(TARGETS)}

COLORS = [
    "#6C63FF", "#00D4AA", "#FF6B6B", "#FBBF24",
    "#34D399", "#60A5FA", "#F472B6", "#A78BFA", "#F87171"
]

# ── White Theme ──────────────────────────────────────────────────────────────
BG      = "#FFFFFF"
SURFACE = "#F4F6FA"
CARD    = "#FFFFFF"
MUTED   = "#6B7280"
TEXT    = "#111827"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD,
    "axes.edgecolor":    "#D1D5DB",
    "axes.labelcolor":   TEXT,
    "xtick.color":       MUTED,
    "ytick.color":       MUTED,
    "text.color":        TEXT,
    "grid.color":        "#E5E7EB",
    "grid.linestyle":    "--",
    "grid.alpha":        0.8,
    "font.family":       "DejaVu Sans",
    "font.size":         9,
})

# ────────────────────────────────────────────────────────────────────────────
# 1. Load artifacts
# ────────────────────────────────────────────────────────────────────────────
print("Loading model artifacts...")
scaler   = joblib.load(SCALER_PATH)
selector = joblib.load(SELECT_PATH)
input_size = int(selector.get_support().sum())
print(f"  Scaler loaded | Selector keeps {input_size} features")

model = nn.Sequential(
    nn.Linear(input_size, 256), nn.ReLU(), nn.Dropout(0.3),
    nn.Linear(256, 128), nn.ReLU(),
    nn.Linear(128, 1)
)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()
print("  PyTorch model loaded.")

# ────────────────────────────────────────────────────────────────────────────
# 2. Build descriptor calculator
# ────────────────────────────────────────────────────────────────────────────
descriptor_names = [desc[0] for desc in Descriptors._descList]
calc = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)

def smiles_to_desc(smiles):
    """Convert SMILES → scaled+selected descriptor vector."""
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    raw = calc.CalcDescriptors(mol)
    d = np.array(raw, dtype=np.float64).reshape(1, -1)
    d[np.isinf(d)] = np.nan
    d = np.nan_to_num(d, nan=0.0)
    d = np.clip(d, -1e6, 1e6)
    d = np.sign(d) * np.log1p(np.abs(d))
    return d

def predict_proba(desc_base, target):
    """Return sigmoid probability for a given target."""
    t_val = TARGET_MAP[target] % 5
    x_in  = np.hstack((desc_base, [[t_val]]))
    x_sel = selector.transform(x_in)
    x_sc  = scaler.transform(x_sel)
    x_t   = torch.tensor(x_sc, dtype=torch.float32)
    with torch.no_grad():
        return torch.sigmoid(model(x_t)).item()

# ────────────────────────────────────────────────────────────────────────────
# 3. Load dataset and compute predictions
# ────────────────────────────────────────────────────────────────────────────
print("\nLoading dataset (this may take a minute)...")
df = pd.read_csv(DATA_PATH, sep=";", engine="python", on_bad_lines="skip", nrows=10000)
df.columns = df.columns.str.strip().str.replace('"', '')

# Get pIC50
df["pIC50"] = pd.to_numeric(df.get("pChEMBL Value", pd.Series(dtype=float)), errors="coerce")
if "Standard Value" in df.columns:
    mask = df["pIC50"].isna()
    df.loc[mask, "pIC50"] = 9 - np.log10(pd.to_numeric(df.loc[mask, "Standard Value"], errors="coerce"))

df = df[df["pIC50"].notna() & df["pIC50"].between(4.5, 9.0)]

smiles_col = next((c for c in df.columns if c.lower() in ("smiles", "canonical_smiles", "smi")), None)
if smiles_col is None:
    raise ValueError("Could not find SMILES column in dataset!")
df = df.rename(columns={smiles_col: "SMILES"})
df = df[df["SMILES"].notna()].drop_duplicates("SMILES")

# Binary label: pIC50 >= 6.0 → active
df["active"] = (df["pIC50"] >= 6.0).astype(int)

print(f"  Dataset: {len(df)} compounds | Active: {df['active'].sum()} | Inactive: {(df['active']==0).sum()}")

# Compute descriptors for all compounds
print("\nComputing descriptors and predictions...")
desc_list, valid_idx = [], []
for i, (_, row) in enumerate(df.iterrows()):
    if i % 500 == 0:
        print(f"  Processing {i}/{len(df)}...")
    d = smiles_to_desc(row["SMILES"])
    if d is not None:
        desc_list.append(d)
        valid_idx.append(i)

df_valid = df.iloc[valid_idx].copy().reset_index(drop=True)
print(f"  Valid molecules: {len(df_valid)}")

# Split into train/test (same seed as training)
_, test_idx = train_test_split(range(len(df_valid)), test_size=0.2, random_state=42)
df_test      = df_valid.iloc[test_idx].reset_index(drop=True)
desc_test    = [desc_list[i] for i in test_idx]

y_true = df_test["active"].values
print(f"\nTest set: {len(df_test)} | Active: {y_true.sum()} | Inactive: {(y_true==0).sum()}")

# ────────────────────────────────────────────────────────────────────────────
# 4. Predict per target
# ────────────────────────────────────────────────────────────────────────────
print("\nRunning predictions for all 8 targets...")
probas = {}
for target in TARGETS:
    probs = []
    for d in desc_test:
        probs.append(predict_proba(d, target))
    probas[target] = np.array(probs)
    auc = roc_auc_score(y_true, probas[target])
    print(f"  {target:8s} AUC = {auc:.4f}")

# ────────────────────────────────────────────────────────────────────────────
# 5. Metrics table
# ────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"{'Target':<10} {'AUC':>7} {'Acc':>7} {'Prec':>7} {'Recall':>7} {'F1':>7}")
print("-"*60)
metrics = {}
for target in TARGETS:
    y_pred_bin = (probas[target] >= 0.5).astype(int)
    auc  = roc_auc_score(y_true, probas[target])
    acc  = accuracy_score(y_true, y_pred_bin)
    prec = precision_score(y_true, y_pred_bin, zero_division=0)
    rec  = recall_score(y_true, y_pred_bin, zero_division=0)
    f1   = f1_score(y_true, y_pred_bin, zero_division=0)
    metrics[target] = dict(auc=auc, acc=acc, prec=prec, rec=rec, f1=f1)
    print(f"{target:<10} {auc:>7.4f} {acc:>7.4f} {prec:>7.4f} {rec:>7.4f} {f1:>7.4f}")
print("="*60)
mean_auc = np.mean([m["auc"] for m in metrics.values()])
print(f"{'Mean AUC':<10} {mean_auc:>7.4f}")

# ────────────────────────────────────────────────────────────────────────────
# 6. Plot 1: ROC curves + Metrics bar chart
# ────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 14), facecolor=BG)
fig.suptitle(
    "QSAR Discovery Suite v2.0  —  Deep Learning ANN Model Performance Report\n"
    "RDKit Molecular Descriptors  |  PyTorch ANN  |  ChEMBL Dataset  |  8-Target Classification",
    fontsize=13, fontweight="bold", color=TEXT, y=0.98
)
fig.patch.set_facecolor(BG)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32,
                       left=0.07, right=0.97, top=0.93, bottom=0.06)

# ── Panel 1: ROC curves ──────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(CARD)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.plot([0,1],[0,1], "--", color="#9CA3AF", lw=1.2, alpha=0.8, label="Random (AUC=0.50)")
for i, target in enumerate(TARGETS):
    fpr, tpr, _ = roc_curve(y_true, probas[target])
    auc = metrics[target]["auc"]
    ax1.plot(fpr, tpr, color=COLORS[i], lw=2,
             label=f"{target}  AUC={auc:.3f}", alpha=0.9)
ax1.set_xlabel("False Positive Rate", fontsize=9, color=TEXT)
ax1.set_ylabel("True Positive Rate", fontsize=9, color=TEXT)
ax1.set_title(f"ROC-AUC Curves per Target  (Mean AUC = {mean_auc:.3f})",
              fontsize=10, fontweight="bold", color=TEXT, pad=8)
ax1.legend(fontsize=7.5, framealpha=0.9, facecolor=SURFACE,
           edgecolor="#D1D5DB", labelcolor=TEXT, loc="lower right")
ax1.grid(True, alpha=0.6, color="#E5E7EB")
ax1.set_xlim([-0.02, 1.02])
ax1.set_ylim([-0.02, 1.05])
# Mean AUC annotation
ax1.text(0.04, 0.92, f"Mean AUC = {mean_auc:.3f}", transform=ax1.transAxes,
         fontsize=9, color="#059669", fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#ECFDF5", edgecolor="#059669", alpha=0.95))

# ── Panel 2: Per-Target Metrics grouped bar ───────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor(CARD)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
metric_keys  = ["auc", "acc", "prec", "rec", "f1"]
metric_labels= ["AUC", "Accuracy", "Precision", "Recall", "F1"]
metric_colors= ["#6C63FF", "#059669", "#D97706", "#DC2626", "#2563EB"]
n_tgts  = len(TARGETS)
n_mets  = len(metric_keys)
x       = np.arange(n_tgts)
width   = 0.15
offsets = np.linspace(-(n_mets-1)/2, (n_mets-1)/2, n_mets) * width

for j, (mk, ml, mc) in enumerate(zip(metric_keys, metric_labels, metric_colors)):
    vals = [metrics[t][mk] for t in TARGETS]
    bars = ax2.bar(x + offsets[j], vals, width*0.9, label=ml,
                   color=mc, alpha=0.85, edgecolor="white", linewidth=0.5)

ax2.set_xticks(x)
ax2.set_xticklabels(TARGETS, fontsize=8, color=TEXT)
ax2.set_ylim([0.0, 1.05])
ax2.set_ylabel("Score", fontsize=9, color=TEXT)
ax2.set_title("Per-Target Metrics  (AUC / Accuracy / Precision / Recall / F1)",
              fontsize=10, fontweight="bold", color=TEXT, pad=8)
ax2.legend(fontsize=8, framealpha=0.9, facecolor=SURFACE,
           edgecolor="#D1D5DB", labelcolor=TEXT, ncol=5, loc="upper right")
ax2.grid(True, axis="y", alpha=0.6, color="#E5E7EB")
ax2.axhline(0.5, color="#9CA3AF", lw=0.8, ls="--", alpha=0.7)

# ── Panel 3: AUC bar chart ────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor(CARD)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
auc_vals = [metrics[t]["auc"] for t in TARGETS]
bars3 = ax3.barh(TARGETS, auc_vals, color=COLORS, edgecolor="white", linewidth=0.6, alpha=0.9)
ax3.axvline(0.5,  color="#9CA3AF", lw=1.0, ls="--", alpha=0.8, label="Random (0.50)")
ax3.axvline(mean_auc, color="#059669", lw=1.5, ls="--", alpha=0.9, label=f"Mean ({mean_auc:.3f})")
for bar, val in zip(bars3, auc_vals):
    ax3.text(val + 0.005, bar.get_y() + bar.get_height()/2,
             f"{val:.4f}", va="center", ha="left", fontsize=8.5,
             color=TEXT, fontweight="bold")
ax3.set_xlim([0.4, 1.02])
ax3.set_xlabel("AUC Score", fontsize=9, color=TEXT)
ax3.set_title("AUC Score per Target  (Active threshold: pIC50 ≥ 6.0)",
              fontsize=10, fontweight="bold", color=TEXT, pad=8)
ax3.legend(fontsize=8, framealpha=0.9, facecolor=SURFACE, edgecolor="#D1D5DB", labelcolor=TEXT)
ax3.grid(True, axis="x", alpha=0.6, color="#E5E7EB")

# ── Panel 4: Confusion matrix heatmap (best target by AUC) ────────────────────
best_target = max(metrics, key=lambda t: metrics[t]["auc"])
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor(CARD)
y_pred_best = (probas[best_target] >= 0.5).astype(int)
cm = confusion_matrix(y_true, y_pred_best)
im = ax4.imshow(cm, interpolation="nearest",
                cmap=plt.cm.get_cmap("Blues"), aspect="auto")
cbar = plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)
cbar.ax.tick_params(colors=TEXT)
classes = ["Inactive", "Active"]
tick_marks = np.arange(len(classes))
ax4.set_xticks(tick_marks); ax4.set_xticklabels(classes, fontsize=9, color=TEXT)
ax4.set_yticks(tick_marks); ax4.set_yticklabels(classes, fontsize=9, color=TEXT)
thresh = cm.max() / 2.0
for ii in range(2):
    for jj in range(2):
        ax4.text(jj, ii, f"{cm[ii,jj]:,}", ha="center", va="center",
                 fontsize=13, fontweight="bold",
                 color="white" if cm[ii,jj] > thresh else TEXT)
ax4.set_xlabel("Predicted Label", fontsize=9, color=TEXT)
ax4.set_ylabel("True Label", fontsize=9, color=TEXT)
ax4.set_title(
    f"Confusion Matrix — {best_target}  (Best AUC = {metrics[best_target]['auc']:.4f})\n"
    f"F1={metrics[best_target]['f1']:.4f}  |  Acc={metrics[best_target]['acc']:.4f}",
    fontsize=10, fontweight="bold", color=TEXT, pad=8
)

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "QSAR_Model_Evaluation_Dashboard.png")
fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close(fig)
print(f"\nDashboard saved to:\n  {out_path}")

# ────────────────────────────────────────────────────────────────────────────
# 7. Print full classification report for best target
# ────────────────────────────────────────────────────────────────────────────
print(f"\n--- Full Classification Report: {best_target} ---")
print(classification_report(y_true, y_pred_best, target_names=["Inactive", "Active"]))

print("\nDone! Open the saved PNG to view your model evaluation dashboard.")
