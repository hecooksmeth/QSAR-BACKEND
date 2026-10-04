import os
import warnings

import joblib
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


warnings.filterwarnings("ignore")

TARGET = "FLT3"
SOURCE_CSV = (
    r"C:\Users\sudharsan\Downloads\DOWNLOAD-RiO5rjsPnqiie6qkHNRzX1OR89vUU3cZeiDIsqsTO1U_eq_"
    r"\DOWNLOAD-RiO5rjsPnqiie6qkHNRzX1OR89vUU3cZeiDIsqsTO1U_eq_.csv"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models", TARGET)
FP_SIZE = 2048
ACTIVE_PIC50_THRESHOLD = 6.0


def load_source(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Source CSV not found: {path}")

    df = pd.read_csv(path, sep=";", engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip().str.replace('"', "", regex=False)
    return df


def clean_flt3(df: pd.DataFrame) -> pd.DataFrame:
    required = ["Smiles", "Standard Value", "Standard Units", "pChEMBL Value", "Assay Variant Mutation"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df[required].copy()
    cleaned = cleaned[cleaned["Smiles"].notna()]
    cleaned = cleaned[cleaned["Standard Units"].astype(str).str.lower().eq("nm")]

    cleaned["IC50"] = pd.to_numeric(cleaned["Standard Value"], errors="coerce")
    cleaned["pIC50"] = pd.to_numeric(cleaned["pChEMBL Value"], errors="coerce")
    missing_pic50 = cleaned["pIC50"].isna()
    cleaned.loc[missing_pic50, "pIC50"] = 9 - np.log10(cleaned.loc[missing_pic50, "IC50"])

    mutation = cleaned["Assay Variant Mutation"]
    cleaned = cleaned[mutation.isna() | mutation.astype(str).str.strip().isin(["", "None"])]
    cleaned = cleaned[cleaned["IC50"].notna() & cleaned["pIC50"].notna()]
    cleaned = cleaned[cleaned["IC50"] > 0]
    cleaned = cleaned[cleaned["pIC50"].between(4.5, 9.0)]

    rows = []
    for _, row in cleaned.iterrows():
        smiles = str(row["Smiles"]).strip()
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            continue
        rows.append(
            {
                "SMILES": Chem.MolToSmiles(mol),
                "IC50": float(row["IC50"]),
                "pIC50": float(row["pIC50"]),
                "Activity": int(row["pIC50"] >= ACTIVE_PIC50_THRESHOLD),
                "MolWt": round(float(Descriptors.MolWt(mol)), 3),
            }
        )

    out = pd.DataFrame(rows)
    out = (
        out.groupby("SMILES", as_index=False)
        .agg({"IC50": "median", "pIC50": "mean", "Activity": "max", "MolWt": "first"})
        .sort_values(["Activity", "pIC50"], ascending=[False, False])
    )
    out["Activity"] = (out["pIC50"] >= ACTIVE_PIC50_THRESHOLD).astype(int)
    return out


def feature_matrix(smiles: pd.Series) -> np.ndarray:
    descriptor_names = [desc[0] for desc in Descriptors._descList]
    descriptor_calculator = MoleculeDescriptors.MolecularDescriptorCalculator(descriptor_names)
    morgan_generator = GetMorganGenerator(radius=2, fpSize=FP_SIZE)

    features = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            features.append(None)
            continue

        desc = np.array(descriptor_calculator.CalcDescriptors(mol), dtype=np.float64)
        desc = np.nan_to_num(desc, nan=0.0, posinf=1e6, neginf=-1e6)
        desc = np.clip(desc, -1e6, 1e6)

        fp = morgan_generator.GetFingerprint(mol)
        fp_arr = np.zeros((FP_SIZE,), dtype=np.float32)
        DataStructs.ConvertToNumpyArray(fp, fp_arr)
        features.append(np.hstack([desc.astype(np.float32), fp_arr]))

    mask = [row is not None for row in features]
    return np.array([row for row in features if row is not None], dtype=np.float32), np.array(mask)


def train_model(cleaned: pd.DataFrame) -> dict:
    X, valid_mask = feature_matrix(cleaned["SMILES"])
    y = cleaned.loc[valid_mask, "Activity"].astype(int).to_numpy()

    if len(np.unique(y)) < 2:
        raise ValueError("FLT3 cleaned data has only one activity class; cannot train classifier.")

    stratify = y if min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    selector = VarianceThreshold()
    X_train = selector.fit_transform(X_train)
    X_test = selector.transform(X_test)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    neg = max(1, int((y_train == 0).sum()))
    pos = max(1, int((y_train == 1).sum()))
    model = XGBClassifier(
        n_estimators=350,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
        scale_pos_weight=neg / pos,
    )
    model.fit(X_train, y_train)

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    metrics = {
        "samples": int(len(y)),
        "active": int((y == 1).sum()),
        "inactive": int((y == 0).sum()),
        "features": int(X_train.shape[1]),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
    }
    if len(np.unique(y_test)) > 1:
        metrics["auc"] = round(float(roc_auc_score(y_test, probabilities)), 4)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    joblib.dump(selector, os.path.join(MODEL_DIR, "selector.pkl"))
    return metrics


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    source = load_source(SOURCE_CSV)
    cleaned = clean_flt3(source)
    cleaned_path = os.path.join(DATA_DIR, f"{TARGET}_cleaned.csv")
    cleaned.to_csv(cleaned_path, index=False)

    metrics = train_model(cleaned)
    print(f"Saved cleaned data: {cleaned_path}")
    print(f"Saved model artifacts: {MODEL_DIR}")
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
