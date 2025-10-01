import pytest
import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def sample_raw_file(test_data_dir):
    """Return path to sample raw file"""
    return os.path.join(test_data_dir, 'raw', 'AC P1 E3.raw') 