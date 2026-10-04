# =====================================================
# DEEP LEARNING–DRIVEN QSAR (ANN) – TRAINING SCRIPT
# =====================================================

import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import tensorflow as tf
import pickle
import os
import warnings
warnings.filterwarnings("ignore")

# -----------------------------------------------------
# 1. LOAD ChEMBL DATA
# -----------------------------------------------------
# Using relative path or absolute path as provided
DATA_PATH = r"C:\Users\sudharsan\OneDrive\Desktop\molecular_modelling\CHEMBL_DATASET.csv"
if not os.path.exists(DATA_PATH):
    print(f"Error: Dataset not found at {DATA_PATH}")
    exit(1)

df = pd.read_csv(
    DATA_PATH,
    sep=";",
    engine="python",
    on_bad_lines="skip"
)

df.columns = df.columns.str.strip().str.replace('"', '')

print("Raw shape:", df.shape)

# -----------------------------------------------------
# 2. KEEP REQUIRED COLUMNS
# -----------------------------------------------------
df = df[
    [
        "Smiles",
        "Standard Value",
        "pChEMBL Value",
        "Assay Variant Mutation"
    ]
]

df = df[df["Smiles"].notna()]
df["Standard Value"] = pd.to_numeric(df["Standard Value"], errors="coerce")
df = df[df["Standard Value"].notna()]

# -----------------------------------------------------
# 3. IC50 → pIC50
# -----------------------------------------------------
df["pIC50"] = pd.to_numeric(df["pChEMBL Value"], errors="coerce")

mask = df["pIC50"].isna()
df.loc[mask, "pIC50"] = 9 - np.log10(df.loc[mask, "Standard Value"])

# -----------------------------------------------------
# 4. WT-ONLY + POTENCY FILTER
# -----------------------------------------------------
df = df[df["Assay Variant Mutation"].isna()]
df = df[(df["pIC50"] >= 4.5) & (df["pIC50"] <= 9.0)]

# -----------------------------------------------------
# 5. REMOVE DUPLICATES
# -----------------------------------------------------
df = df.groupby("Smiles")["pIC50"].mean().reset_index()

print("Final compound count:", df.shape[0])

# -----------------------------------------------------
# 6. SMILES → MORGAN FINGERPRINTS
# -----------------------------------------------------
morgan_gen = GetMorganGenerator(radius=2, fpSize=2048)

def smiles_to_fp(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return np.array(morgan_gen.GetFingerprint(mol), dtype=np.float32)

X, y = [], []

for _, row in df.iterrows():
    fp = smiles_to_fp(row["Smiles"])
    if fp is not None:
        X.append(fp)
        y.append(row["pIC50"])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

print("ML-ready dataset:", X.shape)

# -----------------------------------------------------
# 7. TRAIN / TEST SPLIT
# -----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# -----------------------------------------------------
# 8. FEATURE SCALING
# -----------------------------------------------------
scaler = StandardScaler(with_mean=False)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print("Scaler saved to scaler.pkl")

# -----------------------------------------------------
# 9. BUILD ANN MODEL
# -----------------------------------------------------
model = Sequential([
    Dense(1024, activation="relu", input_shape=(2048,)),
    BatchNormalization(),
    Dropout(0.4),

    Dense(512, activation="relu"),
    BatchNormalization(),
    Dropout(0.3),

    Dense(256, activation="relu"),
    BatchNormalization(),
    Dropout(0.2),

    Dense(1)
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="mse"
)

# -----------------------------------------------------
# 10. CALLBACKS
# -----------------------------------------------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)

lr_reduce = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=5,
    min_lr=1e-5
)

# -----------------------------------------------------
# 11. TRAIN MODEL
# -----------------------------------------------------
print("Starting training...")
model.fit(
    X_train,
    y_train,
    validation_split=0.1,
    epochs=100,
    batch_size=128,
    callbacks=[early_stop, lr_reduce],
    verbose=1
)

# -----------------------------------------------------
# 12. EVALUATION
# -----------------------------------------------------
y_pred = model.predict(X_test).flatten()

print("\nANN MODEL PERFORMANCE")
print("R²   :", round(r2_score(y_test, y_pred), 3))
print("RMSE :", round(np.sqrt(mean_squared_error(y_test, y_pred)), 3))

# -----------------------------------------------------
# 13. SAVE MODEL
# -----------------------------------------------------
model.save("qsar_model.h5")
print("Model saved to qsar_model.h5")
