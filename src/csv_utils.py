import pandas as pd
import hashlib

def row_hash(row):
    """Generate a consistent hash for a DataFrame row."""
    return hashlib.md5(str(row.values).encode()).hexdigest()

def add_hash_column(df):
    """Add a 'hash' column to the DataFrame."""
    df['hash'] = df.apply(row_hash, axis=1)
    return df

def detect_changes(current_df, previous_df):
    """Return rows from current_df that are new or have changed."""
    current_df = add_hash_column(current_df.copy())
    previous_df = add_hash_column(previous_df.copy())
    return current_df[~current_df['hash'].isin(previous_df['hash'])]
