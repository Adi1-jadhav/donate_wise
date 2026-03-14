import math
import re
from collections import defaultdict

# 📂 PRO-GRADE PURE PYTHON AI ENGINE (v3.0 - "Global & Local" Edition)
# 🚀 Robust handling for Unknown words and High-Precision Categorization.

class SmartPredictor:
    def __init__(self, alpha=0.1):
        self.alpha = alpha # Lower alpha for sharper predictions
        self.class_counts = defaultdict(int)
        self.class_word_counts = defaultdict(lambda: defaultdict(float))
        self.total_weights_in_class = defaultdict(float)
        self.vocab = set()
        self.classes = []
        self.stop_words = {'a', 'an', 'the', 'is', 'at', 'on', 'and', 'for', 'with', 'to', 'in', 'of', 'by', 'it', 'from', 'my', 'is'}

    def _preprocess(self, text):
        text = str(text).lower()
        # Clean special chars but keep space
        text = re.sub(r'[^a-z\s]', ' ', text)
        tokens = []
        for word in text.split():
            if word in self.stop_words:
                continue
            # Stemming: keep short words like 'pen', 'box', 'toy'
            stem = re.sub(r'(s|es|ing|ed)$', '', word)
            tokens.append(stem if len(stem) > 2 else word)
        
        # Bigrams for phrases like "ready meal", "school bag"
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
        return tokens + bigrams

    def fit(self, data):
        for text, label, weight in data:
            tokens = self._preprocess(text)
            self.class_counts[label] += 1 * weight
            for token in tokens:
                self.class_word_counts[label][token] += 1.0 * weight
                self.total_weights_in_class[label] += 1.0 * weight
                self.vocab.add(token)
        self.classes = list(self.class_counts.keys())

    def predict(self, text):
        tokens = self._preprocess(text)
        
        # 🛡️ CRITICAL FIX: Handle words not in Vocabulary (like "samosa" if not trained)
        # Instead of picking the smallest class by math, we use Keyword Fallback + Others
        useful_tokens = [t for t in tokens if t in self.vocab]
        
        if not useful_tokens:
            # Smart Regex Fallback for common patterns
            text_low = text.lower()
            if any(k in text_low for k in ['food', 'meal', 'eat', 'dinner', 'lunch', 'breakfast', 'samosa', 'snack', 'bread', 'roti', 'sabzi', 'rice']):
                return "Food"
            if any(k in text_low for k in ['clothe', 'wear', 'shirt', 'pant', 'dress', 'saree']):
                return "Clothes"
            if any(k in text_low for k in ['pen', 'pencil', 'write', 'draw', 'stationery']):
                return "Stationery"
            return "Others"
        
        best_class = None
        max_log_prob = -float('inf')
        total_docs = sum(self.class_counts.values())
        
        for cls in self.classes:
            # Prior Log P(C)
            log_prob = math.log(self.class_counts[cls] / total_docs)
            
            # Likelihood Log P(W|C)
            denominator = self.total_weights_in_class[cls] + self.alpha * len(self.vocab)
            for token in useful_tokens:
                count = self.class_word_counts[cls].get(token, 0)
                log_prob += math.log((count + self.alpha) / denominator)
            
            if log_prob > max_log_prob:
                max_log_prob = log_prob
                best_class = cls
        
        return best_class or "Others"

# 📊 THE "POWERFUL" DATASET (Comprehensive entries)
DATASET = [
    # FOOD (Massive expansion)
    ("rice dal grains wheat pulses flour sugar salt groceries oil spices", "Food", 2.0),
    ("cooked meal dinner lunch box tiffin package breakfast khichdi thali", "Food", 2.0),
    ("fresh fruit apple banana orange grapes mango vegetable potato tomato onion", "Food", 2.0),
    ("biscuit cookies cake bread bun sandwich snack samosa kachori pakoda street food", "Food", 5.0), # Added samosa specifically
    ("milk powder baby food cerelac canned food juice water drink bottle", "Food", 1.5),
    
    # CLOTHES
    ("shirt tshirt pant jeans denim trousers clothes wear garment apparel sweater jacket", "Clothes", 3.0),
    ("winter woollen coat scarf glove sock cap thermal shawl", "Clothes", 2.0),
    ("saree dress salwar suit dupatta traditional ethnic silk cotton kurta pajama", "Clothes", 3.0),
    ("kids baby clothes toddler small size onesie bib", "Clothes", 2.0),
    
    # FOOTWEAR
    ("shoes sneaker boots sandal heels slipper footwear floaters sports jogging running", "Footwear", 5.0),
    ("leather formal shoes office wear walking pump flat flipflop slider", "Footwear", 4.0),
    
    # ELECTRONICS
    ("smartphone cell mobile phone android iphone accessories charger cable wire plug", "Electronics", 3.0),
    ("laptop computer macbook dell pc keyboard mouse monitor tablet ipad ebook", "Electronics", 3.0),
    ("headphones earphone bluetooth speaker powerbank bulb lamp battery electric gadget", "Electronics", 2.0),
    
    # STATIONERY
    ("pen pencil rubber eraser sharpener ruler scale compass geometry box geometry set", "Stationery", 8.0),
    ("marker ink highlighter sketch pen glitter pen inkwell refill", "Stationery", 6.0),
    ("drawing set painting colors brush palette canvas paper glue tape", "Stationery", 5.0),
    ("stapler pins clips calculator punch folder file holder diary journal notebook", "Stationery", 5.0),

    # BOOKS
    ("school book textbook notebook engineering medical study notes guide manual reference", "Books", 4.0),
    ("novel fiction story literature comic manga magazine library atlas encyclopedia", "Books", 3.0),
    ("dictionary biography poem reading material", "Books", 2.0),
    
    # OTHERS
    ("sofa bed chair table furniture desk cupboard wooden metal furniture plastic", "Others", 1.0),
    ("toys doll car action figure sports bat ball racket gym kit board games cycle", "Others", 1.0),
    ("utensils pan cooker plate glass bowl kitchenware home decor tools first aid kit", "Others", 1.0),
]

# Initialization
_engine = SmartPredictor()
_engine.fit(DATASET)

def predict_category(text):
    """Categorization with specific Food and unknown-word protection."""
    if not text or len(str(text).strip()) < 2: return "Others"
    return _engine.predict(text)

def predict_impact(text):
    """Deep analysis for NGO decision making."""
    res = predict_category(text)
    lower = str(text).lower()
    
    condition = "Good"
    bad_tags = ['old', 'used', 'worn', 'torn', 'damaged', 'broken', 'repair', 'dirty', 'expired', 'stale']
    good_tags = ['new', 'fresh', 'sealed', 'tag', 'brand new', 'original', 'unused', 'working', 'clean']
    
    if any(k in lower for k in bad_tags): condition = "Used"
    elif any(k in lower for k in good_tags): condition = "New"
        
    tokens = re.findall(r'\b\w+\b', lower)
    useful_tokens = [t for t in tokens if t in _engine.vocab]
    confidence = 0.5 + (len(useful_tokens) / (len(tokens) + 1)) * 0.49
    
    return {
        "category": res,
        "condition": condition,
        "confidence": round(min(0.99, confidence), 2),
        "impact_score": 10 if (condition == "New" or res == "Food") else 7
    }
