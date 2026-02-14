import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

# Get current directory (m1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Correct CSV path
csv_path = os.path.join(BASE_DIR, "bug_dataset.csv")

# Load dataset
data = pd.read_csv(csv_path)

X = data["description"]
y_type = data["type"]
y_priority = data["priority"]

# Model pipelines
type_model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=1000))
])

priority_model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=1000))
])

# Train models
type_model.fit(X, y_type)
priority_model.fit(X, y_priority)

# Save models
joblib.dump(type_model, os.path.join(BASE_DIR, "type_model.pkl"))
joblib.dump(priority_model, os.path.join(BASE_DIR, "priority_model.pkl"))

print("✅ Models trained and saved successfully")
