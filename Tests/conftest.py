# File: conftest.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/conftest.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 10:56PM

"""
Pytest configuration and shared fixtures for AndyLibrary tests
Provides common test setup, fixtures, and utilities
"""

import pytest
import os
import sys
import tempfile
import sqlite3
import json
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def project_root_path():
    """Get the project root directory"""
    return project_root

@pytest.fixture(scope="session")
def test_database_schema():
    """SQL schema for test databases"""
    return '''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE subjects (
            id INTEGER PRIMARY KEY,
            category_id INTEGER,
            subject TEXT NOT NULL,
            UNIQUE(category_id, subject),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );
        
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            category TEXT,
            subject TEXT,
            file_path TEXT,
            file_size INTEGER,
            page_count INTEGER,
            rating INTEGER,
            last_opened TEXT
        );
        
        CREATE INDEX idx_books_category ON books (category);
        CREATE INDEX idx_books_subject ON books (subject);
        CREATE INDEX idx_books_title ON books (title);
        CREATE INDEX idx_subjects_category_subject ON subjects (category_id, subject);
    '''

@pytest.fixture(scope="session")
def test_data():
    """Sample test data for database"""
    return {
        'categories': [
            (1, 'Programming'),
            (2, 'Science'),
            (3, 'Mathematics'),
            (4, 'Medicine'),
            (5, 'Engineering')
        ],
        'subjects': [
            (1, 1, 'Python'),
            (2, 1, 'JavaScript'),
            (3, 1, 'Java'),
            (4, 2, 'Biology'),
            (5, 2, 'Chemistry'),
            (6, 3, 'Calculus'),
            (7, 3, 'Statistics'),
            (8, 4, 'Anatomy'),
            (9, 4, 'Dentistry'),
            (10, 5, 'Mechanical')
        ],
        'books': [
            (1, 'Python Programming Guide', 'John Doe', 'Programming', 'Python', '/test/python.pdf', 1024000, 200, 5, '2025-01-01'),
            (2, 'JavaScript Essentials', 'Jane Smith', 'Programming', 'JavaScript', '/test/js.pdf', 2048000, 300, 4, '2025-01-02'),
            (3, 'Java Fundamentals', 'Bob Johnson', 'Programming', 'Java', '/test/java.pdf', 1536000, 250, 4, '2025-01-03'),
            (4, 'Biology Textbook', 'Dr. Science', 'Science', 'Biology', '/test/bio.pdf', 3072000, 400, 5, '2025-01-04'),
            (5, 'Chemistry Lab Manual', 'Prof. Chem', 'Science', 'Chemistry', '/test/chem.pdf', 2560000, 350, 4, '2025-01-05'),
            (6, 'Calculus Made Easy', 'Math Expert', 'Mathematics', 'Calculus', '/test/calc.pdf', 2048000, 300, 5, '2025-01-06'),
            (7, 'Statistics for Beginners', 'Data Analyst', 'Mathematics', 'Statistics', '/test/stats.pdf', 1792000, 280, 4, '2025-01-07'),
            (8, 'Human Anatomy Atlas', 'Dr. Medical', 'Medicine', 'Anatomy', '/test/anatomy.pdf', 4096000, 500, 5, '2025-01-08'),
            (9, 'Dental Procedures Guide', 'Dr. Teeth', 'Medicine', 'Dentistry', '/test/dental.pdf', 1280000, 180, 4, '2025-01-09'),
            (10, 'Mechanical Engineering Handbook', 'Engineer Pro', 'Engineering', 'Mechanical', '/test/mech.pdf', 3584000, 450, 5, '2025-01-10')
        ]
    }

@pytest.fixture
def temp_database(test_database_schema, test_data):
    """Create a temporary database with test data"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Create schema
        conn.executescript(test_database_schema)
        
        # Insert test data
        conn.executemany('INSERT INTO categories VALUES (?, ?)', test_data['categories'])
        conn.executemany('INSERT INTO subjects VALUES (?, ?, ?)', test_data['subjects'])
        conn.executemany('INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', test_data['books'])
        
        conn.commit()
        conn.close()
        
        yield db_path
        
    finally:
        os.close(db_fd)
        if os.path.exists(db_path):
            os.unlink(db_path)

@pytest.fixture
def mock_config():
    """Mock application configuration"""
    return {
        "server_host": "127.0.0.1",
        "server_port": 8080,
        "server_port_range": [8080, 8081, 8082, 3000, 8000, 8010, 8090, 5000, 9000],
        "database": {
            "local_path": "Data/Local/cached_library.db",
            "backup_path": "Data/Backups/",
            "connection_timeout": 30
        },
        "google_drive": {
            "credentials_file": "Config/google_credentials.json",
            "database_file_id": "test_file_id_123",
            "sync_interval": 3600,
            "enable_sync": True
        },
        "logging": {
            "level": "INFO",
            "file": "Data/Logs/andygoogle.log"
        }
    }

@pytest.fixture
def mock_google_credentials():
    """Mock Google OAuth credentials"""
    return {
        "web": {
            "client_id": "test_client_id_123.apps.googleusercontent.com",
            "project_id": "andygoogle-test-project",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "test_client_secret_456",
            "redirect_uris": ["http://127.0.0.1:8080/auth/callback"]
        }
    }

@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing"""
    return {
        'ANDYGOOGLE_MODE': 'local',
        'ANDYGOOGLE_DEBUG': 'true',
        'ANDYGOOGLE_CONFIG_PATH': 'Config/andygoogle_config.json'
    }

@pytest.fixture
def api_client():
    """Create a test client for API testing"""
    from fastapi.testclient import TestClient
    
    try:
        from Source.API.MainAPI import app
        return TestClient(app)
    except ImportError:
        pytest.skip("MainAPI not available")

@pytest.fixture
def mock_drive_manager():
    """Mock DriveManager for testing"""
    mock_manager = Mock()
    
    # Mock common methods
    mock_manager.local_db_path = "Data/Local/cached_library.db"
    mock_manager.GetSyncStatus.return_value = {
        'local_version': '1.0.0',
        'remote_version': '1.0.0',
        'last_sync': '2025-07-23T10:00:00',
        'sync_status': 'up_to_date',
        'offline_mode': False
    }
    mock_manager.SyncDatabaseFromDrive.return_value = True
    mock_manager.CheckForUpdates.return_value = {
        'updates_available': False,
        'current_version': '1.0.0',
        'latest_version': '1.0.0'
    }
    
    return mock_manager

@pytest.fixture
def mock_sheets_logger():
    """Mock SheetsLogger for testing"""
    mock_logger = Mock()
    
    # Mock logging methods
    mock_logger.log_api_usage.return_value = True
    mock_logger.log_error.return_value = True
    mock_logger.log_sync_event.return_value = True
    
    return mock_logger

# Test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as a database test"
    )
    config.addinivalue_line(
        "markers", "google_drive: mark test as a Google Drive test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "fast: mark test as fast running"
    )

# Test utilities
class TestHelpers:
    """Utility functions for tests"""
    
    @staticmethod
    def create_test_database(path, schema, data):
        """Create a test database with given schema and data"""
        conn = sqlite3.connect(path)
        conn.executescript(schema)
        
        if 'categories' in data:
            conn.executemany('INSERT INTO categories VALUES (?, ?)', data['categories'])
        if 'subjects' in data:
            conn.executemany('INSERT INTO subjects VALUES (?, ?, ?)', data['subjects'])
        if 'books' in data:
            conn.executemany('INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data['books'])
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def verify_database_integrity(db_path):
        """Verify database integrity"""
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            return result[0] == "ok"
        finally:
            conn.close()
    
    @staticmethod
    def count_table_rows(db_path, table_name):
        """Count rows in a table"""
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        finally:
            conn.close()

@pytest.fixture
def test_helpers():
    """Provide test helper utilities"""
    return TestHelpers()

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test"""
    # Setup
    test_files = []
    
    yield test_files
    
    # Cleanup
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass  # File might already be deleted

# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

# Database connection testing
@pytest.fixture
def database_connection_test():
    """Test database connections"""
    def _test_connection(db_path):
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] == 1
        except Exception:
            return False
    
    return _test_connection