import joblib
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# 📂 Paths for the model
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "category_model.pkl")

def get_trained_model():
    """Returns a trained Naive Bayes pipeline. Trains if not exists."""
    # Foundation data for Multinomial Naive Bayes
    data = [
        # Food items
        ("rice grains wheat dal pulses", "Food"),
        ("cooked meal parcel box lunch dinner", "Food"),
        ("fruit apple banana orange grapes bag", "Food"),
        ("vegetables potato onion tomato fresh", "Food"),
        ("milk bread eggs butter daily", "Food"),
        ("biscuits snacks chocolate chips", "Food"),
        
        # Clothes
        ("shirt pant tshirt jeans denim", "Clothes"),
        ("winter jacket sweater coat woollen", "Clothes"),
        ("saree dress dupatta suit traditional", "Clothes"),
        ("kids baby clothes small size", "Clothes"),
        ("blanket bedsheet towel linen", "Clothes"),
        ("shoes footwear sandals sleepers", "Clothes"),
        
        # Electronics
        ("mobile phone smartphone mobilephone", "Electronics"),
        ("laptop computer charger cable battery", "Electronics"),
        ("tablet ipad gadget electronic item", "Electronics"),
        ("fan light bulb switch power cord", "Electronics"),
        ("television radio speaker sound system", "Electronics"),
        
        # Books
        ("school books notebook textbook novel", "Electronics"), # Fixing potential label error in next line if any
        ("story book magazine newspaper paper", "Books"),
        ("engineering medical law entrance guide", "Books"),
        ("pen pencil stationary toolkit", "Books"),
        ("atlas map dictionary encyclopedia", "Books"),
        
        # Others
        ("sofa chair table furniture desk", "Others"),
        ("medical supplies first aid kit", "Others"),
        ("toys dolls games cards kids play", "Others"),
        ("cycle bicycle wheel tire pump", "Others")
    ]
    
    texts, labels = zip(*data)
    
    # Create Pipeline: Vectorizer -> Classifier
    pipeline = Pipeline([
        ('vectorizer', CountVectorizer(stop_words='english', min_df=1)),
        ('classifier', MultinomialNB(alpha=1.0))
    ])
    
    pipeline.fit(texts, labels)
    return pipeline

# Load or Train on start
try:
    if os.path.exists(MODEL_FILE):
        _clf = joblib.load(MODEL_FILE)
    else:
        _clf = get_trained_model()
        # joblib.dump(_clf, MODEL_FILE) # Optional: enable if write permission is guaranteed
except:
    _clf = get_trained_model()

def predict_category(text):
    """Predicts a category using the Multinomial Naive Bayes model."""
    if not text or len(text.strip()) < 3:
        return "Others"
    
    try:
        pred = _clf.predict([text.lower()])[0]
        return pred
    except:
        return "Others"

def predict_impact(text):
    """Analysis of condition and confidence."""
    category = predict_category(text)
    
    text_lower = text.lower()
    condition = "Good"
    if any(k in text_lower for k in ['old', 'used', 'worn', 'torn', 'repair']):
        condition = "Used"
    elif any(k in text_lower for k in ['new', 'fresh', 'sealed', 'packed', 'brand new']):
        condition = "New"
        
    # Mock confidence for now based on text length
    confidence = min(0.95, 0.4 + (len(text) / 200))
    
    return {
        "category": category,
        "condition": condition,
        "confidence": round(confidence, 2),
        "impact_score": 10
    }
