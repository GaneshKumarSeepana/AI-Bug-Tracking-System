import joblib
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

type_model = joblib.load(os.path.join(BASE_DIR, "type_model.pkl"))
priority_model = joblib.load(os.path.join(BASE_DIR, "priority_model.pkl"))

def predict_bug(text):
    # Type prediction
    type_probs = type_model.predict_proba([text])[0]
    type_index = type_probs.argmax()
    bug_type = type_model.classes_[type_index]
    type_confidence = round(type_probs[type_index] * 100, 2)

    # Priority prediction
    priority_probs = priority_model.predict_proba([text])[0]
    priority_index = priority_probs.argmax()
    priority = priority_model.classes_[priority_index]
    priority_confidence = round(priority_probs[priority_index] * 100, 2)

    return {
        "type": bug_type,
        "type_confidence": type_confidence,
        "priority": priority,
        "priority_confidence": priority_confidence
    }
