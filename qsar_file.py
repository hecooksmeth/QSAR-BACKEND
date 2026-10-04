import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import accuracy_score
import torch
import torch.nn as nn
import joblib

# =========================
# 1. LOAD DATA
# =========================
df = pd.concat([
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_egfr.csv"),
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_BRAF.csv"),
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_CDK.csv"),
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_HER2.csv"),
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_VEGFR2.csv"),
    pd.read_csv("C:/Users/sudharsan/OneDrive/Desktop/qsar/data/clean_FLT3.csv")
], ignore_index=True)


print("Total samples:", len(df))

# =========================
# 2. BALANCE DATA
# =========================

active = df[df["Activity"] == 1]
inactive = df[df["Activity"] == 0]

n = min(len(active), len(inactive), 5000)

df = pd.concat([
    active.sample(n, random_state=42),
    inactive.sample(n, random_state=42)
])

print("Balanced samples:", len(df))

# =========================
# 3. FEATURE EXTRACTION
# =========================

descriptor_names = [desc[0] for desc in Descriptors._descList]
calc = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)

def featurize(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        return calc.CalcDescriptors(mol)
    return None

df["features"] = df["SMILES"].apply(featurize)
df = df.dropna()

# =========================
# 4. ENCODE TARGET
# =========================

target_map = {
    "EGFR":0,
    "BRAF":1,
    "CDK2":2,
    "HER2":3,
    "VEGFR2":4,
    "FLT3":5
}

df["target_encoded"] = df["Target"].map(target_map)

# =========================
# 5. PREPARE DATA
# =========================

X = np.array(df["features"].tolist())
y = df["Activity"].values
target_vals = df["target_encoded"].values.reshape(-1,1)

# =========================
# 6. CLEAN + STABILIZE DATA (FINAL FIX)
# =========================

# Replace inf with NaN
X[np.isinf(X)] = np.nan

# Remove rows with NaN
mask = ~np.isnan(X).any(axis=1)
X = X[mask]
y = y[mask]
target_vals = target_vals[mask]

# Clip extreme values
X = np.clip(X, -1e6, 1e6)

# Log transform (key step)
X = np.sign(X) * np.log1p(np.abs(X))

# Add target AFTER cleaning
X = np.hstack((X, target_vals))

# Remove constant features
selector = VarianceThreshold()
X = selector.fit_transform(X)

print("Final feature count:", X.shape[1])

# =========================
# 7. SCALE FEATURES
# =========================

scaler = StandardScaler()
X = scaler.fit_transform(X)

# Safety check
print("NaN in X:", np.isnan(X).any())
print("Inf in X:", np.isinf(X).any())

# =========================
# 8. TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).view(-1,1)

X_test = torch.tensor(X_test, dtype=torch.float32)

# =========================
# 9. MODEL
# =========================

model = nn.Sequential(
    nn.Linear(X.shape[1], 256),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 1)
)

loss_fn = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)

# =========================
# 10. TRAINING
# =========================

for epoch in range(100):
    preds = model(X_train)
    loss = loss_fn(preds, y_train)

    if torch.isnan(loss):
        print("NaN detected! Stopping training.")
        break

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch} Loss {loss.item():.4f}")

# =========================
# 11. EVALUATION
# =========================

preds = torch.sigmoid(model(X_test)).detach().numpy()
preds = (preds > 0.5).astype(int)

print("Accuracy:", accuracy_score(y_test, preds))

# =========================
# 12. PREDICTION FUNCTION
# =========================

def predict(smiles, target):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Invalid SMILES"

    desc = calc.CalcDescriptors(mol)
    desc = np.array(desc).reshape(1, -1)

    # Handle bad values
    desc[np.isinf(desc)] = np.nan
    if np.isnan(desc).any():
        return "Invalid molecule"

    # Same transformations
    desc = np.clip(desc, -1e6, 1e6)
    desc = np.sign(desc) * np.log1p(np.abs(desc))

    target_val = target_map[target]
    x = np.hstack((desc, [[target_val]]))

    x = selector.transform(x)
    x = scaler.transform(x)

    x = torch.tensor(x, dtype=torch.float32)

    pred = torch.sigmoid(model(x)).item()

    return "Active" if pred > 0.5 else "Inactive"

# =========================
# 13. TEST
# =========================

print(predict("CCO", "EGFR"))

# =========================
# 14. SAVE ARTIFACTS
# =========================
import os
save_dir = "C:/Users/sudharsan/OneDrive/Desktop/molecular_modelling"
os.makedirs(save_dir, exist_ok=True)

torch.save(model.state_dict(), os.path.join(save_dir, "model.pth"))
joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))
joblib.dump(selector, os.path.join(save_dir, "selector.pkl"))
print("Saved model.pth, scaler.pkl, and selector.pkl successfully.")