# File: conftest.py
# Path: /home/herb/Desktop/OurLibrary/Tests/conftest.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-12
# Last Modified: 2025-08-19 11:30PM

"""
Pytest configuration and fixtures for OurLibrary testing

Provides common fixtures and configuration for all test modules.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path

# Test markers for categorizing tests
pytest_markers = [
    "browser: Browser-only functionality tests",
    "security: Security and credential protection tests", 
    "config: Configuration file validation tests",
    "live: Live website testing",
    "integration: Integration tests for future features",
    "performance: Performance and accessibility tests",
    "unit: Unit tests for individual components",
    "educational_mission: Mission-critical educational features"
]

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def config_dir(project_root):
    """Return the Config directory path."""
    return project_root / "Config"

@pytest.fixture(scope="session")
def bowersworld_dir(project_root):
    """Return the BowersWorld.com directory path."""
    return project_root / "BowersWorld.com"

@pytest.fixture(scope="session")
def website_url():
    """Return the live website URL."""
    return "https://callmechewy.github.io/BowersWorld-com/"

@pytest.fixture(scope="session")
def github_pages_url():
    """Return the GitHub Pages URL."""
    return "https://callmechewy.github.io/BowersWorld-com/"

@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for OurLibrary live site."""
    return "https://callmechewy.github.io/OurLibrary"

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_user_data():
    """Provide mock user registration data for testing."""
    return {
        "username": "testuser123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "zipCode": "12345",
        "agreeTerms": True,
        "registrationDate": "2025-08-12T13:00:00.000Z",
        "method": "email",
        "verified": False,
        "id": "1691841600000"
    }

@pytest.fixture(scope="session")
def educational_mission():
    """Return the project's educational mission statement."""
    return "Getting education into the hands of people who can least afford it"

def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)