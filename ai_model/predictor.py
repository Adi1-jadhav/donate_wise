import joblib
import os

# Dynamically get full path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models and vectorizers
cat_model = joblib.load(os.path.join(BASE_DIR, 'cat_model.pkl'))
cat_vec = joblib.load(os.path.join(BASE_DIR, 'cat_vec.pkl'))
cond_model = joblib.load(os.path.join(BASE_DIR, 'cond_model.pkl'))
cond_vec = joblib.load(os.path.join(BASE_DIR, 'cond_vec.pkl'))

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

# Maintain legacy support for existing routes
def predict_category(title, description):
    res = predict_impact(f"{title} {description}")
    return res['category']
