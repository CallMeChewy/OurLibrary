# File: test_api_core.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_api_core.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 12:24PM

"""
Core API Tests - Focused on Working Functionality
Tests the essential API endpoints that support the educational mission
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.mark.api
class TestCoreAPI:
    """Test core API functionality that works"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        try:
            from Source.API.MainAPI import app
            return TestClient(app)
        except ImportError:
            pytest.skip("MainAPI not available")
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]
    
    def test_mode_endpoint(self, client):
        """Test mode endpoint"""
        response = client.get("/api/mode")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["local", "gdrive"]
    
    def test_categories_endpoint(self, client):
        """Test categories endpoint"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have categories from real database
        if len(data) > 0:
            assert "id" in data[0]
            assert "category" in data[0]
    
    def test_subjects_endpoint_all(self, client):
        """Test getting all subjects"""
        response = client.get("/api/subjects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "subject" in data[0]
    
    def test_stats_endpoint(self, client):
        """Test library statistics endpoint"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Should have basic stats
        expected_keys = ["total_books", "total_categories", "total_subjects"]
        for key in expected_keys:
            assert key in data
            assert isinstance(data[key], int)
            assert data[key] >= 0

@pytest.mark.database
class TestDatabaseCore:
    """Test core database functionality"""
    
    def test_database_connection(self):
        """Test database can be connected to"""
        import sqlite3
        
        db_path = "Data/Databases/MyLibrary.db"
        if not os.path.exists(db_path):
            pytest.skip("Database not found")
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            assert result[0] == 1
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    def test_database_has_expected_tables(self):
        """Test database has core tables"""
        import sqlite3
        
        db_path = "Data/Databases/MyLibrary.db"
        if not os.path.exists(db_path):
            pytest.skip("Database not found")
            
        conn = sqlite3.connect(db_path)
        try:
            # Check for essential tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            cursor = conn.execute(tables_query)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ["books", "categories", "subjects"]
            for table in expected_tables:
                assert table in tables, f"Missing essential table: {table}"
        finally:
            conn.close()
    
    def test_database_has_data(self):
        """Test database contains actual data"""
        import sqlite3
        
        db_path = "Data/Databases/MyLibrary.db"
        if not os.path.exists(db_path):
            pytest.skip("Database not found")
            
        conn = sqlite3.connect(db_path)
        try:
            # Check books table has data
            cursor = conn.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            assert book_count > 0, "Database should have books"
            
            # Check categories table has data
            cursor = conn.execute("SELECT COUNT(*) FROM categories")
            category_count = cursor.fetchone()[0]
            assert category_count > 0, "Database should have categories"
            
        finally:
            conn.close()

@pytest.mark.fast
class TestPerformance:
    """Test performance requirements for educational mission"""
    
    def test_quick_health_check(self, client=None):
        """Test health check is fast (for version control)"""
        import time
        
        if client is None:
            try:
                from Source.API.MainAPI import app
                client = TestClient(app)
            except ImportError:
                pytest.skip("MainAPI not available")
        
        start_time = time.time()
        response = client.get("/api/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0, f"Health check too slow: {response_time:.3f}s"
        assert response.status_code == 200
    
    def test_stats_query_speed(self, client=None):
        """Test stats query is fast (Python dict caching)"""
        import time
        
        if client is None:
            try:
                from Source.API.MainAPI import app
                client = TestClient(app)
            except ImportError:
                pytest.skip("MainAPI not available")
        
        start_time = time.time()
        response = client.get("/api/stats")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 0.1, f"Stats query too slow: {response_time:.3f}s"
        assert response.status_code == 200