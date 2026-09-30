"""
Pytest configuration and fixtures for data preprocessing tests.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame with various data types and missing values."""
    np.random.seed(42)
    return pd.DataFrame({
        'id': range(1, 101),
        'name': ['Person_' + str(i) for i in range(100)],
        'age': np.random.randint(18, 80, 100),
        'salary': np.random.uniform(30000, 150000, 100),
        'score': np.random.uniform(0, 100, 100),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 100),
    })


@pytest.fixture
def dataframe_with_missing():
    """Create a DataFrame with missing values."""
    np.random.seed(42)
    df = pd.DataFrame({
        'id': range(1, 51),
        'value1': np.random.uniform(0, 100, 50),
        'value2': np.random.uniform(0, 100, 50),
        'category': np.random.choice(['A', 'B', 'C'], 50),
    })
    
    # Introduce missing values
    df.loc[5:10, 'value1'] = np.nan
    df.loc[15:20, 'value2'] = np.nan
    df.loc[25:45, 'value2'] = np.nan  # More than 50% missing
    
    return df


@pytest.fixture
def dataframe_with_duplicates():
    """Create a DataFrame with duplicate rows."""
    df = pd.DataFrame({
        'id': [1, 2, 2, 3, 3, 3, 4, 5],
        'name': ['A', 'B', 'B', 'C', 'C', 'C', 'D', 'E'],
        'value': [10, 20, 20, 30, 30, 30, 40, 50]
    })
    return df


@pytest.fixture
def csv_file_path(sample_dataframe, tmp_path):
    """Create a temporary CSV file with sample data."""
    filepath = tmp_path / "test_data.csv"
    sample_dataframe.to_csv(filepath, index=False)
    return str(filepath)


@pytest.fixture
def csv_with_missing_path(dataframe_with_missing, tmp_path):
    """Create a temporary CSV file with missing values."""
    filepath = tmp_path / "test_missing.csv"
    dataframe_with_missing.to_csv(filepath, index=False)
    return str(filepath)


@pytest.fixture
def csv_with_duplicates_path(dataframe_with_duplicates, tmp_path):
    """Create a temporary CSV file with duplicates."""
    filepath = tmp_path / "test_duplicates.csv"
    dataframe_with_duplicates.to_csv(filepath, index=False)
    return str(filepath)


@pytest.fixture
def invalid_csv_path(tmp_path):
    """Create an invalid CSV file."""
    filepath = tmp_path / "invalid.csv"
    with open(filepath, 'w') as f:
        f.write("This is not a valid CSV")
    return str(filepath)


@pytest.fixture
def flask_client():
    """Create a Flask test client."""
    import app
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
