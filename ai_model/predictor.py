import math
import re
from collections import defaultdict

# 📂 PRO-GRADE PURE PYTHON AI ENGINE (v3.2 - "Precision Context")
# 🚀 Fixed: "Bottle" ambiguity & improved "Others" vs "Food" differentiation.

class SmartPredictor:
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self.class_counts = defaultdict(int)
        self.class_word_counts = defaultdict(lambda: defaultdict(float))
        self.total_weights_in_class = defaultdict(float)
        self.vocab = set()
        self.classes = []
        self.stop_words = {'a', 'an', 'the', 'is', 'at', 'on', 'and', 'for', 'with', 'to', 'in', 'of', 'by', 'it', 'from', 'my'}

    def _preprocess(self, text):
        text = str(text).lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        tokens = []
        for word in text.split():
            if word in self.stop_words:
                continue
            stem = re.sub(r'(s|es|ing|ed)$', '', word)
            tokens.append(stem if len(stem) > 2 else word)
        
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
        useful_tokens = [t for t in tokens if t in self.vocab]
        
        if not useful_tokens:
            text_low = text.lower()
            # 🛡️ Fallback Logic
            if any(k in text_low for k in ['rice', 'dal', 'samosa', 'meal', 'food', 'snack', 'bread', 'thali', 'khichdi', 'fruits', 'veg']):
                return "Food"
            if any(k in text_low for k in ['clothe', 'shirt', 'pant', 'jean', 'saree', 'suit']):
                return "Clothes"
            if any(k in text_low for k in ['pen', 'pencil', 'stationery', 'marker', 'eraser']):
                return "Stationery"
            if any(k in text_low for k in ['bottle', 'flask', 'spoon', 'plate', 'utensil', 'bucket']):
                return "Others"
            return "Others"
        
        best_class = None
        max_log_prob = -float('inf')
        total_docs = sum(self.class_counts.values())
        
        for cls in self.classes:
            log_prob = math.log(self.class_counts[cls] / total_docs)
            denominator = self.total_weights_in_class[cls] + self.alpha * len(self.vocab)
            for token in useful_tokens:
                count = self.class_word_counts[cls].get(token, 0)
                log_prob += math.log((count + self.alpha) / denominator)
            
            if log_prob > max_log_prob:
                max_log_prob = log_prob
                best_class = cls
        
        return best_class or "Others"

# 📊 THE "PRECISION" DATASET
DATASET = [
    # FOOD
    ("rice dal grains wheat pulses flour sugar salt groceries oil spices", "Food", 2.0),
    ("cooked meal dinner lunch box tiffin package breakfast khichdi thali sabzi roti", "Food", 3.0),
    ("fresh fruit apple banana orange grapes mango vegetable potato tomato onion", "Food", 2.0),
    ("biscuit cookies cake bread bun sandwich snack samosa kachori pakoda snacks", "Food", 5.0),
    ("milk powder baby food cerelac canned juice beverages drinks water pouch", "Food", 1.5),
    
    # CLOTHES
    ("shirt tshirt pant jeans denim trousers clothes wear garment apparel sweater jacket winter woollen", "Clothes", 3.0),
    ("coat scarf glove sock cap thermal shawl saree dress salwar suit dupatta traditional ethnic silk cotton kurta pajama kids baby", "Clothes", 2.0),
    
    # FOOTWEAR
    ("shoes sneaker boots sandal heels slipper footwear floaters sports jogging running loafers flipflop slider", "Footwear", 5.0),
    ("leather formal shoes office wear walking pump flat wedges stilettos", "Footwear", 4.0),
    
    # ELECTRONICS
    ("smartphone cell mobile phone android iphone accessories charger cable wire plug laptop computer macbook dell pc keyboard mouse monitor tablet ipad ebook headphones earphone bluetooth speaker powerbank bulb lamp battery electric gadget", "Electronics", 3.0),
    
    # STATIONERY
    ("pen pencil rubber eraser sharpener ruler scale compass geometry box geometry set marker ink highlighter sketch pen glitter pen inkwell refill stationery kit drawing set painting colors brush palette canvas paper glue tape stapler pins clips calculator punch folder file holder diary journal notebook", "Stationery", 8.0),

    # BOOKS
    ("school book textbook notebook engineering medical study notes guide manual reference novel fiction story literature comic manga magazine library atlas encyclopedia dictionary biography poem reading material", "Books", 4.0),
    
    # OTHERS (Includes Houseware & Containers)
    ("bottle water bottle thermos flask copper bottle sipper steel bottle flask bottle", "Others", 10.0), # Maximum priority for 'bottle'
    ("utensils pan cooker plate glass bowl kitchenware home decor tools first aid kit toys doll car action figure sports bat ball racket gym cycle bucket umbrella backpack luggage", "Others", 2.0),
]

# Initialization
_engine = SmartPredictor()
_engine.fit(DATASET)

def predict_category(text):
    if not text or len(str(text).strip()) < 2: return "Others"
    return _engine.predict(text)

def predict_impact(text):
    res = predict_category(text)
    lower = str(text).lower()
    
    condition = "Good"
    bad_tags = ['old', 'used', 'worn', 'torn', 'damaged', 'broken', 'repair', 'dirty', 'expired', 'stale']
    good_tags = ['new', 'fresh', 'sealed', 'tag', 'brand new', 'original', 'unused', 'working', 'clean']
    
    if any(k in lower for k in bad_tags): condition = "Used"
    elif any(k in lower for k in good_tags): condition = "New"
        
    tokens = re.findall(r'\b\w+\b', lower)
    useful_tokens = [t for t in tokens if t in _engine.vocab]
    confidence = 0.55 + (len(useful_tokens) / (len(tokens) + 1)) * 0.44
    
    return {
        "category": res,
        "condition": condition,
        "confidence": round(min(0.99, confidence), 2),
        "impact_score": 10 if (condition == "New" or res == "Food") else 7
    }
