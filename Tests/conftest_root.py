# File: conftest.py
# Path: /home/herb/Desktop/AndyLibrary/conftest.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 09:37AM

import sys
import os
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "test_db_path": "Data/Local/test_library.db",
        "test_port": 8999,
        "test_host": "127.0.0.1"
    }

@pytest.fixture
def clean_test_db(test_config):
    """Ensure clean test database for each test"""
    db_path = test_config["test_db_path"]
    if os.path.exists(db_path):
        os.remove(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)