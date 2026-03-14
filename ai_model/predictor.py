import math
import re
from collections import defaultdict

# 📂 PURE PYTHON MULTINOMIAL NAIVE BAYES
# This implementation avoids C-dependency errors (like libgomp.so.1) on serverless platforms like Vercel.

class SimpleMultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha  # Laplace smoothing
        self.class_counts = defaultdict(int)
        self.class_word_counts = defaultdict(lambda: defaultdict(int))
        self.total_words_in_class = defaultdict(int)
        self.vocab = set()
        self.classes = []

    def _tokenize(self, text):
        return re.findall(r'\b\w\w+\b', text.lower())

    def fit(self, X, y):
        for text, label in zip(X, y):
            tokens = self._tokenize(text)
            self.class_counts[label] += 1
            for token in tokens:
                self.class_word_counts[label][token] += 1
                self.total_words_in_class[label] += 1
                self.vocab.add(token)
        self.classes = list(self.class_counts.keys())

    def predict(self, X):
        results = []
        for text in X:
            tokens = self._tokenize(text)
            best_class = None
            max_log_prob = -float('inf')

            total_docs = sum(self.class_counts.values())
            
            for cls in self.classes:
                # Log Prior: P(C)
                log_prob = math.log(self.class_counts[cls] / total_docs)
                
                # Log Likelihood: P(W|C) = (count(w,c) + alpha) / (total_words_in_c + alpha * vocab_size)
                denominator = self.total_words_in_class[cls] + self.alpha * len(self.vocab)
                
                for token in tokens:
                    if token in self.vocab:
                        count = self.class_word_counts[cls].get(token, 0)
                        log_prob += math.log((count + self.alpha) / denominator)
                
                if log_prob > max_log_prob:
                    max_log_prob = log_prob
                    best_class = cls
            
            results.append(best_class or "Others")
        return results

# 📊 Training Data
TRAIN_DATA = [
    ("rice grains wheat dal pulses grocery food meal", "Food"),
    ("cooked meal parcel box lunch dinner tiffin", "Food"),
    ("fruit apple banana orange grapes healthy bag", "Food"),
    ("vegetables potato onion tomato fresh green", "Food"),
    ("shirt pant tshirt jeans denim clothes wear apparel", "Clothes"),
    ("winter jacket sweater coat woollen scarf", "Clothes"),
    ("saree dress dupatta suit traditional ethnic", "Clothes"),
    ("kids baby clothes small size toys", "Clothes"),
    ("mobile phone smartphone laptop electronic gadget", "Electronics"),
    ("tablet ipad computer screen charger battery", "Electronics"),
    ("headphones speaker powerbank earbuds", "Electronics"),
    ("school books notebook textbook novel story", "Books"),
    ("engineering medical law exam guide study notes", "Books"),
    ("dictionary stationery pen pencil toolkit", "Books"),
    ("sofa chair table furniture desk stool", "Others"),
    ("first aid kit medicine mask bandage", "Others"),
]

# Initialize and Train
_texts, _labels = zip(*TRAIN_DATA)
_clf = SimpleMultinomialNB()
_clf.fit(_texts, _labels)

def predict_category(text):
    """Predicts category using Pure Python Naive Bayes."""
    if not text or len(text.strip()) < 2:
        return "Others"
    return _clf.predict([text])[0]

def predict_impact(text):
    """Analysis of condition and confidence."""
    category = predict_category(text)
    
    text_lower = text.lower()
    condition = "Good"
    if any(k in text_lower for k in ['old', 'used', 'worn', 'torn', 'repair', 'bad']):
        condition = "Used"
    elif any(k in text_lower for k in ['new', 'fresh', 'sealed', 'packed', 'brand new']):
        condition = "New"
        
    # Logic-based confidence
    tokens = re.findall(r'\b\w+\b', text_lower)
    known_tokens = [t for t in tokens if t in _clf.vocab]
    confidence = 0.5 + (len(known_tokens) / (len(tokens) + 1)) * 0.4
    
    return {
        "category": category,
        "condition": condition,
        "confidence": round(min(0.98, confidence), 2),
        "impact_score": 10
    }
