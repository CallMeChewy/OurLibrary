# File: test_database_functionality.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_database_functionality.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:26AM

"""
Test Suite for Database Functionality
Tests basic database operations and table initialization
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from Core.DatabaseManager import DatabaseManager

class TestDatabaseFunctionality(unittest.TestCase):
    """Test basic database functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.temp_db_path)
        
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.db_manager, 'Connection') and self.db_manager.Connection:
            self.db_manager.Connection.close()
        
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_database_connection(self):
        """Test that database connection is established"""
        self.assertIsNotNone(self.db_manager.Connection)
        self.assertTrue(self.db_manager.Connection)
    
    def test_user_tables_exist(self):
        """Test that user authentication tables are created"""
        required_tables = [
            'Users',
            'UserSessions', 
            'UserSubscriptions',
            'UserActivity',
            'UserPreferences',
            'PublicationRequests'
        ]
        
        cursor = self.db_manager.Connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            self.assertIn(table, existing_tables, f"Required table {table} not found")
    
    def test_user_creation_basic(self):
        """Test basic user creation functionality"""
        result = self.db_manager.CreateUser(
            Email="test@example.com",
            Password="testpassword123",
            Username="testuser",
            MissionAcknowledged=True
        )
        
        self.assertTrue(result["success"], f"User creation failed: {result.get('error')}")
        self.assertIn("user_id", result)
        self.assertIn("verification_token", result)
    
    def test_session_token_generation(self):
        """Test session token generation"""
        token1 = self.db_manager.GenerateSessionToken()
        token2 = self.db_manager.GenerateSessionToken()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        
        # Tokens should be reasonable length
        self.assertGreater(len(token1), 20)
        self.assertGreater(len(token2), 20)
    
    def test_email_verification_token_generation(self):
        """Test email verification token generation"""
        token1 = self.db_manager.GenerateEmailVerificationToken()
        token2 = self.db_manager.GenerateEmailVerificationToken()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        
        # Tokens should be reasonable length
        self.assertGreater(len(token1), 10)
        self.assertGreater(len(token2), 10)
    
    def test_database_directory_creation(self):
        """Test that database directory is created if it doesn't exist"""
        # This is more of a smoke test since the directory creation
        # happens during initialization
        self.assertTrue(os.path.exists(self.temp_db_path.rsplit('/', 1)[0]))
    
    def test_connection_resilience(self):
        """Test that database handles connection issues gracefully"""
        # Close the connection
        if self.db_manager.Connection:
            self.db_manager.Connection.close()
            self.db_manager.Connection = None
        
        # Try to create a user without connection
        result = self.db_manager.CreateUser(
            Email="test@example.com",
            Password="testpassword123",
            Username="testuser",
            MissionAcknowledged=True
        )
        
        # Should fail gracefully
        self.assertFalse(result["success"])
        self.assertIn("connection", result["error"].lower())

if __name__ == "__main__":
    unittest.main(verbosity=2)