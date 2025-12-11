
import pandas as pd
import joblib
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from src.data_loader import load_data

MODEL_PATH = "models/mental_health_model.pkl"

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Remove URLs
    text = re.sub(r'@\w+', '', text) # Remove Mentions
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove strict special chars (keep only letters)
    return text

def train_model():
    print("Loading data...")
    try:
        df = load_data("data/Combined Data.csv")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Data loaded. Shape: {df.shape}")
    
    # 1. Clean Data
    print("Cleaning texts...")
    df['clean_text'] = df['text'].apply(clean_text)
    
    # Drop empty after cleaning
    df = df[df['clean_text'].str.strip().astype(bool)]

    print(f"Data after cleaning. Shape: {df.shape}")
    print("Labels distribution:")
    print(df['label'].value_counts())

    X = df['clean_text']
    y = df['label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create Pipeline: Vectorizer + Classifier
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words='english', 
            max_features=10000, # Increased features
            ngram_range=(1, 2), # Use bigrams to capture "not happy", "wanna die"
            min_df=5 # Ignore incredibly rare words (like "opera" if it only appears once)
        )), 
        ('clf', LogisticRegression(
            solver='liblinear', 
            multi_class='auto',
            class_weight='balanced', # Fix imbalance
            max_iter=1000
        ))
    ])

    print("Training model (this might take a bit longer)...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred))

    # Save model
    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(pipeline, MODEL_PATH)
    print("Done.")

if __name__ == "__main__":
    train_model()
