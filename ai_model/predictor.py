import joblib
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

# Dynamically get full path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dummy model used when a real model cannot be loaded
class DummyModel:
    def predict(self, X):
        return ["Others"]  # generic class
    def predict_proba(self, X):
        # return a uniform low‑confidence distribution for two classes
        return np.array([[0.5, 0.5]])

# ---- Load category model -------------------------------------------------
try:
    cat_model = joblib.load(os.path.join(BASE_DIR, "cat_model.pkl"))
except Exception as e:
    print(f"⚠️ Could not load cat_model.pkl: {e}. Using dummy model.")
    cat_model = DummyModel()

# ---- Load category vectorizer --------------------------------------------
try:
    cat_vec = joblib.load(os.path.join(BASE_DIR, "cat_vec.pkl"))
except Exception as e:
    print(f"⚠️ Could not load cat_vec.pkl: {e}. Using simple CountVectorizer.")
    cat_vec = CountVectorizer()

# ---- Load condition model ------------------------------------------------
try:
    cond_model = joblib.load(os.path.join(BASE_DIR, "cond_model.pkl"))
except Exception as e:
    print(f"⚠️ Could not load cond_model.pkl: {e}. Using dummy model.")
    cond_model = DummyModel()

# ---- Load condition vectorizer -------------------------------------------
try:
    cond_vec = joblib.load(os.path.join(BASE_DIR, "cond_vec.pkl"))
except Exception as e:
    print(f"⚠️ Could not load cond_vec.pkl: {e}. Using simple CountVectorizer.")
    cond_vec = CountVectorizer()

def predict_impact(text):
    """Predicts both Category and Condition for a donation."""
    if not text.strip():
        return {"category": "Others", "condition": "Unknown", "confidence": 0}
    try:
        # Category Prediction
        cat_X = cat_vec.transform([text.lower()])
        cat_pred = cat_model.predict(cat_X)[0]
        cat_probs = cat_model.predict_proba(cat_X)
        cat_conf = float(max(cat_probs[0]))
        # Condition Prediction
        cond_X = cond_vec.transform([text.lower()])
        cond_pred = cond_model.predict(cond_X)[0]
        return {
            "category": cat_pred,
            "condition": cond_pred,
            "confidence": round(cat_conf * 100, 1)
        }
    except Exception as e:
        print("❌ Prediction error:", e)
        return {"category": "Others", "condition": "Unknown", "confidence": 0}

# Legacy wrapper used by existing routes
def predict_category(title, description):
    res = predict_impact(f"{title} {description}")
    return res["category"]
