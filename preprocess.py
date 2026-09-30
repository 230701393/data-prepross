import pandas as pd
import numpy as np
from typing import Tuple, Optional


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load dataset from a CSV file.
    
    Parameters:
    -----------
    filepath : str
        Path to the CSV file to load
        
    Returns:
    --------
    pd.DataFrame
        Loaded dataset
        
    Raises:
    -------
    FileNotFoundError
        If the file does not exist
    pd.errors.ParserError
        If the file cannot be parsed as CSV
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Dataset loaded successfully from {filepath}")
        print(f"Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        raise
    except pd.errors.ParserError as e:
        print(f"Error: Could not parse CSV file. {e}")
        raise


def handle_missing_values(df: pd.DataFrame, strategy: str = 'mean', 
                         threshold: float = 0.5) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with potential missing values
    strategy : str, default='mean'
        Strategy for handling missing values:
        - 'mean': Fill with column mean (numeric columns only)
        - 'median': Fill with column median (numeric columns only)
        - 'drop': Drop rows with any missing values
        - 'forward_fill': Forward fill missing values
        - 'backward_fill': Backward fill missing values
    threshold : float, default=0.5
        If a column has more than threshold% missing values, drop the column
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with missing values handled
    """
    df_copy = df.copy()
    
    # Calculate missing value percentages
    missing_percent = (df_copy.isnull().sum() / len(df_copy)) * 100
    
    # Drop columns exceeding threshold
    cols_to_drop = missing_percent[missing_percent > threshold * 100].index
    df_copy = df_copy.drop(columns=cols_to_drop)
    
    if len(cols_to_drop) > 0:
        print(f"Dropped columns with >{threshold*100}% missing values: {list(cols_to_drop)}")
    
    # Handle remaining missing values
    if strategy == 'mean':
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].mean())
        print(f"Filled missing values using mean strategy for {len(numeric_cols)} numeric columns")
        
    elif strategy == 'median':
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
        df_copy[numeric_cols] = df_copy[numeric_cols].fillna(df_copy[numeric_cols].median())
        print(f"Filled missing values using median strategy for {len(numeric_cols)} numeric columns")
        
    elif strategy == 'drop':
        df_copy = df_copy.dropna()
        print(f"Dropped rows with missing values. New shape: {df_copy.shape}")
        
    elif strategy == 'forward_fill':
        df_copy = df_copy.fillna(method='ffill')
        print("Filled missing values using forward fill strategy")
        
    elif strategy == 'backward_fill':
        df_copy = df_copy.fillna(method='bfill')
        print("Filled missing values using backward fill strategy")
    
    return df_copy


def perform_basic_preprocessing(df: pd.DataFrame, 
                               remove_duplicates: bool = True,
                               normalize_columns: bool = False) -> pd.DataFrame:
    """
    Perform basic preprocessing on the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    remove_duplicates : bool, default=True
        Whether to remove duplicate rows
    normalize_columns : bool, default=False
        Whether to normalize column names (lowercase, strip whitespace)
        
    Returns:
    --------
    pd.DataFrame
        Preprocessed dataframe
    """
    df_copy = df.copy()
    
    # Remove duplicates
    if remove_duplicates:
        initial_shape = df_copy.shape[0]
        df_copy = df_copy.drop_duplicates()
        duplicates_removed = initial_shape - df_copy.shape[0]
        if duplicates_removed > 0:
            print(f"Removed {duplicates_removed} duplicate rows")
    
    # Normalize column names
    if normalize_columns:
        df_copy.columns = df_copy.columns.str.lower().str.strip()
        print("Normalized column names (lowercase, whitespace stripped)")
    
    print(f"Preprocessing complete. Final shape: {df_copy.shape}")
    
    return df_copy


def preprocess_pipeline(filepath: str, 
                       handle_missing: bool = True,
                       missing_strategy: str = 'mean',
                       remove_duplicates: bool = True,
                       normalize_columns: bool = True) -> pd.DataFrame:
    """
    Complete preprocessing pipeline combining all operations.
    
    Parameters:
    -----------
    filepath : str
        Path to the input CSV file
    handle_missing : bool, default=True
        Whether to handle missing values
    missing_strategy : str, default='mean'
        Strategy for handling missing values
    remove_duplicates : bool, default=True
        Whether to remove duplicate rows
    normalize_columns : bool, default=True
        Whether to normalize column names
        
    Returns:
    --------
    pd.DataFrame
        Fully preprocessed dataset
    """
    print("Starting preprocessing pipeline...")
    
    # Load dataset
    df = load_dataset(filepath)
    
    # Handle missing values
    if handle_missing:
        df = handle_missing_values(df, strategy=missing_strategy)
    
    # Perform basic preprocessing
    df = perform_basic_preprocessing(df, 
                                    remove_duplicates=remove_duplicates,
                                    normalize_columns=normalize_columns)
    
    print("Pipeline complete!")
    
    return df


if __name__ == "__main__":
    # Example usage
    print("Data Preprocessing Module")
    print("=" * 50)
    print("This module provides functions for data preprocessing.")
    print("Use the functions defined here to clean and prepare your data.")
