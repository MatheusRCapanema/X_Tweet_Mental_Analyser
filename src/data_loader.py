
import pandas as pd
import os

def load_data(filepath="data/Combined Data.csv"):
    """
    Loads the dataset from the CSV file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Read CSV, handling potential irregularities
    df = pd.read_csv(filepath)
    
    # Ensure columns exist (handling the unnamed index column if present)
    # Based on inspection, columns are [index, statement, status] or similar
    # We rename to standard 'text' and 'label' for internal use
    
    # Verify expected columns
    if 'statement' not in df.columns or 'status' not in df.columns:
        # Fallback check if it has different headers or no headers
        # But based on user file view, it has headers.
        raise ValueError(f"CSV must contain 'statement' and 'status' columns. Found: {df.columns.tolist()}")

    df = df.rename(columns={'statement': 'text', 'status': 'label'})
    
    # Drop rows with missing text or labels
    df = df.dropna(subset=['text', 'label'])
    
    return df
