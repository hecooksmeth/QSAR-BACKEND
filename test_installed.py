import joblib
import os
import traceback

model_path = r"C:\Program Files\QSAR Discovery Suite\resources\backend\_internal\models\EGFR\model.pkl"
scaler_path = r"C:\Program Files\QSAR Discovery Suite\resources\backend\_internal\models\EGFR\scaler.pkl"
selector_path = r"C:\Program Files\QSAR Discovery Suite\resources\backend\_internal\models\EGFR\selector.pkl"

print("Checking EGFR files:")
print("Model exists:", os.path.exists(model_path))
print("Scaler exists:", os.path.exists(scaler_path))
print("Selector exists:", os.path.exists(selector_path))

try:
    print("Loading scaler...")
    scaler = joblib.load(scaler_path)
    print("Scaler loaded successfully:", type(scaler))
except Exception as e:
    print("Failed to load scaler:")
    traceback.print_exc()

try:
    print("Loading selector...")
    selector = joblib.load(selector_path)
    print("Selector loaded successfully:", type(selector))
except Exception as e:
    print("Failed to load selector:")
    traceback.print_exc()

try:
    print("Loading model...")
    model = joblib.load(model_path)
    print("Model loaded successfully:", type(model))
except Exception as e:
    print("Failed to load model:")
    traceback.print_exc()
