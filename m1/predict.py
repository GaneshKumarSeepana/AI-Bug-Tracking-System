import joblib
import os
import re
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIORITY_MODEL_PATH = os.path.join(BASE_DIR, "priority_model.pkl")
TYPE_MODEL_PATH = os.path.join(BASE_DIR, "type_model.pkl")

priority_model = None
type_model = None

def load_models():
    global priority_model, type_model
    try:
        if os.path.exists(PRIORITY_MODEL_PATH):
            priority_model = joblib.load(PRIORITY_MODEL_PATH)
        
        if os.path.exists(TYPE_MODEL_PATH):
            type_model = joblib.load(TYPE_MODEL_PATH)
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def predict_priority_and_type(title, description):
    """
    Predicts priority and bug type based on title and description.
    Returns (priority, bug_type) tuple.
    """
    text = clean_text(title + " " + description)
    
    priority = "Medium"
    bug_type = "Bug"
    
    if priority_model:
        try:
            priority = priority_model.predict([text])[0]
        except:
            pass
            
    if type_model:
        try:
            bug_type = type_model.predict([text])[0]
        except:
            pass
            
    # Simple rule-based fallback if models fail or aren't confident
    if "crash" in text or "critical" in text or "security" in text:
        priority = "High"
    elif "typo" in text or "color" in text:
        priority = "Low"
        
    if "add" in text or "new" in text or "request" in text:
        bug_type = "Feature Request"
        
    return priority, bug_type
