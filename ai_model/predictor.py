import math
import re
from collections import defaultdict

# 📂 PRO-GRADE PURE PYTHON AI ENGINE (v2.1)
# 🚀 Fixed: Stationery vs Books precision & Short-word recognition.

class SmartPredictor:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.class_counts = defaultdict(int)
        self.class_word_counts = defaultdict(lambda: defaultdict(float))
        self.total_weights_in_class = defaultdict(float)
        self.vocab = set()
        self.classes = []
        # Optimized Stop Words
        self.stop_words = {'a', 'an', 'the', 'is', 'at', 'on', 'and', 'for', 'with', 'to', 'in', 'of', 'by', 'it', 'from', 'my'}

    def _preprocess(self, text):
        # Basic cleaning
        text = re.sub(r'[^a-z\s]', ' ', text.lower())
        tokens = []
        for word in text.split():
            if word in self.stop_words:
                continue
            # Keep short critical words like 'pen', 'box', 'kit', 'bag'
            stem = re.sub(r'(s|es|ing|ed)$', '', word)
            tokens.append(stem if len(stem) > 2 else word)
        
        # Bigrams for compound context (e.g., "pen set", "pencil box")
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
        if not tokens: return "Others"
        
        best_class = None
        max_log_prob = -float('inf')
        total_docs = sum(self.class_counts.values())
        
        for cls in self.classes:
            # Prior P(C)
            log_prob = math.log(self.class_counts[cls] / total_docs)
            
            # Likelihood P(W|C)
            denominator = self.total_weights_in_class[cls] + self.alpha * len(self.vocab)
            for token in tokens:
                if token in self.vocab:
                    count = self.class_word_counts[cls].get(token, 0)
                    log_prob += math.log((count + self.alpha) / denominator)
            
            if log_prob > max_log_prob:
                max_log_prob = log_prob
                best_class = cls
        
        return best_class or "Others"

# 📊 THE "PRECISION" DATASET (Entry, Category, ConfidenceWeight)
DATASET = [
    # FOOD
    ("rice dal grains wheat pulses flour sugar salt kitchen pantry", "Food", 2.0),
    ("cooked meal dinner lunch box tiffin home style food snacks package", "Food", 2.0),
    ("fresh fruit apple banana orange grapes mango vegetable potato tomato", "Food", 2.0),
    ("milk powder baby food biscuits cookies snacks nutrition", "Food", 1.5),
    
    # CLOTHES
    ("shirt tshirt pant jeans denim trousers clothes wear garment apparel sweater", "Clothes", 3.0),
    ("jacket winter woollen coat scarf glove sock cap thermal", "Clothes", 2.0),
    ("saree dress salwar suit dupatta traditional ethnic silk cotton", "Clothes", 2.0),
    ("kids baby clothes toddler small size onesie", "Clothes", 1.5),
    
    # FOOTWEAR
    ("shoes sneaker boots sandal heels slipper footwear floaters sports jogging", "Footwear", 5.0),
    ("leather shoes formal shoes office wear walking running", "Footwear", 4.0),
    ("pump flats flipflop sliders wedges stilettos", "Footwear", 4.0),
    
    # ELECTRONICS
    ("smartphone cell mobile phone android iphone accessories charger cable wire", "Electronics", 3.0),
    ("laptop computer macbook dell pc keyboard mouse monitor tablet ipad", "Electronics", 3.0),
    ("headphones earphone bluetooth speaker powerbank bulb lamp battery electric", "Electronics", 2.0),
    
    # STATIONERY (New Dedicated Category for High-Precision)
    ("pen pencil rubber eraser sharpener ruler scale compass geometry box", "Stationery", 8.0), # Extra high weight for 'pen'
    ("marker ink highlighter sketch pen glitter pen inkwell refill", "Stationery", 6.0),
    ("stationery kit drawing set painting colors brush palette canvas paper", "Stationery", 5.0),
    ("stapler pins clips calculator punch folder file holder diary", "Stationery", 4.0),

    # BOOKS
    ("school book textbook notebook engineering medical study notes guide manual", "Books", 4.0),
    ("novel fiction story literature comic manga magazine library atlas encyclopedia", "Books", 3.0),
    ("dictionary biography poem reading material", "Books", 2.0),
    
    # OTHERS
    ("sofa bed chair table furniture desk cupboard wooden metal", "Others", 1.0),
    ("toys doll car action figure sports bat ball racket gym kit board games", "Others", 1.0),
    ("utensils pan cooker plate glass bowl kitchenware home decor tools", "Others", 1.0),
]

# Initialization
_engine = SmartPredictor()
_engine.fit(DATASET)

def predict_category(text):
    """Categorization with specific Stationery handling."""
    if not text or len(text.strip()) < 2: return "Others"
    return _engine.predict(text)

def predict_impact(text):
    """Deep analysis of condition and credibility."""
    res = _engine.predict(text)
    lower = text.lower()
    
    # Precise Condition Detection
    condition = "Good"
    bad_tags = ['old', 'used', 'worn', 'torn', 'damaged', 'broken', 'repair', 'dirty', 'leak']
    good_tags = ['new', 'fresh', 'sealed', 'tag', 'brand new', 'original', 'unused', 'working']
    
    if any(k in lower for k in bad_tags): condition = "Used"
    elif any(k in lower for k in good_tags): condition = "New"
        
    # Confidence Score Logic
    tokens = re.findall(r'\b\w+\b', lower)
    useful_tokens = [t for t in tokens if t in _engine.vocab]
    confidence = 0.55 + (len(useful_tokens) / (len(tokens) + 1)) * 0.45
    
    return {
        "category": res,
        "condition": condition,
        "confidence": round(min(0.99, confidence), 2),
        "impact_score": 10 if condition == "New" else 7
    }
