import sys
import os

sys.path.append(os.path.abspath("."))

try:
    import qsar_api
    print("Imported qsar_api successfully!")
    bundle = qsar_api._load_target_bundle("EGFR")
    print("Loaded EGFR target bundle:", bundle)
except Exception as e:
    print("Failed to load target bundle:", e)
    import traceback
    traceback.print_exc()
