
from deep_translator import GoogleTranslator
import pandas as pd
import re

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Remove URLs
    text = re.sub(r'@\w+', '', text) # Remove Mentions
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove strict special chars
    return text

def translate_text(text, target='en'):
    """
    Translates text to target language (default English) using deep_translator.
    """
    try:
        # Simple caching or batching could be added here for performance
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text # Fallback to original text

def analyze_profile(df, model):
    """
    Analyzes a DataFrame of tweets (with 'text' column) using the provided model.
    Adds 'translation', 'prediction', and 'probability' columns.
    """
    if model is None:
        print("Error: Model is None in analyze_profile")
        return pd.DataFrame()

    results = []
    
    # Analyze each tweet
    for index, row in df.iterrows():
        original_text = row['text']
        
        # 0. Clean (Crucial for model calibration)
        cleaned_text = clean_text(original_text)
        
        # Skip if empty after cleaning
        if not cleaned_text.strip():
            continue

        # 1. Translate
        translated_text = translate_text(cleaned_text)
        
        # 2. Predict
        try:
            pred_class = model.predict([translated_text])[0]
            pred_prob = model.predict_proba([translated_text])[0].max()
            
            results.append({
                'original_text': original_text,
                'cleaned_text': cleaned_text,
                'translated_text': translated_text,
                'prediction': pred_class,
                'probability': pred_prob,
                'date': row.get('date', '')
            })
        except Exception as e:
            print(f"Prediction error for tweet: {e}")
            
    return pd.DataFrame(results)
