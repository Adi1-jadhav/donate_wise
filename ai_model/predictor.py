# Mock Predictor to replace missing ai_model module

def predict_category(text):
    text = text.lower()
    if any(k in text for k in ['food', 'meal', 'fruit', 'veg']):
        return "Food"
    if any(k in text for k in ['shirt', 'pant', 'cloth', 'wear']):
        return "Clothes"
    if any(k in text for k in ['mobile', 'phone', 'laptop', 'electronics']):
        return "Electronics"
    if any(k in text for k in ['book', 'study', 'note']):
        return "Books"
    return "Others"

def predict_impact(text):
    # This mock returns a dictionary similar to what the app expects
    category = predict_category(text)
    
    # Simple heuristic for condition
    condition = "Good"
    if any(k in text.lower() for k in ['old', 'used', 'worn']):
        condition = "Used"
    elif any(k in text.lower() for k in ['new', 'fresh', 'sealed']):
        condition = "New"
        
    return {
        "category": category,
        "condition": condition,
        "confidence": 0.85,
        "impact_score": 10  # Optional, but keep it for consistency
    }
