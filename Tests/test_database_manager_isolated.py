# File: test_database_manager_isolated.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_database_manager_isolated.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:27AM

"""
Isolated Test Suite for DatabaseManager
Tests database functionality with proper table initialization
"""

import os
import sys
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from Core.DatabaseManager import DatabaseManager

class TestDatabaseManagerIsolated(unittest.TestCase):
    """Test DatabaseManager with isolated test setup"""
    
    def setUp(self):
        """Set up test environment with proper database initialization"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create a minimal database with required tables for testing
        self.initialize_test_database()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.temp_db_path)
        
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.db_manager, 'Connection') and self.db_manager.Connection:
            self.db_manager.Connection.close()
        
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def initialize_test_database(self):
        """Initialize test database with minimal required tables"""
        conn = sqlite3.connect(self.temp_db_path)
        
        # Create minimal books table that DatabaseManager expects
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT
            )
        """)
        
        # Insert a test book so the connection test passes
        conn.execute("INSERT INTO books (title, author) VALUES (?, ?)", 
                    ("Test Book", "Test Author"))
        
        conn.commit()
        conn.close()
    
    def test_database_connection_with_existing_books_table(self):
        """Test that DatabaseManager connects when books table exists"""
        self.assertIsNotNone(self.db_manager.Connection)
        self.assertTrue(self.db_manager.Connection)
    
    def test_user_tables_created_during_initialization(self):
        """Test that user authentication tables are created during initialization"""
        required_tables = [
            'Users',
            'UserSessions', 
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
    
    def test_user_creation_with_proper_database(self):
        """Test user creation with properly initialized database"""
        result = self.db_manager.CreateUser(
            Email="test@example.com",
            Password="testpassword123",
            Username="testuser",
            MissionAcknowledged=True
        )
        
        self.assertTrue(result["success"], f"User creation failed: {result.get('error')}")
        self.assertIn("user_id", result)
        self.assertTrue(result.get("verification_required", False))
        self.assertFalse(result["email_verified"])
        self.assertEqual(result["access_level"], "pending")
    
    def test_email_verification_with_proper_database(self):
        """Test email verification with properly initialized database"""
        # Create user first
        create_result = self.db_manager.CreateUser(
            Email="verify@example.com",
            Password="testpassword123",
            Username="verifyuser",
            MissionAcknowledged=True
        )
        
        self.assertTrue(create_result["success"])
        user_id = create_result["user_id"]
        
        # Get verification token from database
        cursor = self.db_manager.Connection.execute(
            "SELECT EmailVerificationToken FROM Users WHERE Id = ?", (user_id,)
        )
        verification_token = cursor.fetchone()[0]
        
        # Verify email
        verify_result = self.db_manager.VerifyUserEmail(verification_token)
        
        self.assertTrue(verify_result["success"], f"Email verification failed: {verify_result.get('error')}")
        self.assertIn("user_id", verify_result)
        self.assertIn("email", verify_result)
    
    def test_user_authentication_workflow(self):
        """Test complete user authentication workflow"""
        # Create user
        create_result = self.db_manager.CreateUser(
            Email="auth@example.com",
            Password="testpassword123",
            Username="authuser",
            MissionAcknowledged=True
        )
        
        self.assertTrue(create_result["success"])
        user_id = create_result["user_id"]
        
        # Get verification token from database
        cursor = self.db_manager.Connection.execute(
            "SELECT EmailVerificationToken FROM Users WHERE Id = ?", (user_id,)
        )
        verification_token = cursor.fetchone()[0]
        
        # Verify email
        verify_result = self.db_manager.VerifyUserEmail(verification_token)
        self.assertTrue(verify_result["success"])
        
        # Authenticate user
        auth_result = self.db_manager.AuthenticateUser(
            "auth@example.com",
            "testpassword123"
        )
        
        self.assertTrue(auth_result["success"], f"Authentication failed: {auth_result.get('error')}")
        self.assertEqual(auth_result["user"]["email"], "auth@example.com")
        self.assertEqual(auth_result["user"]["username"], "authuser")
    
    def test_session_management(self):
        """Test session creation and validation"""
        # Create and verify user
        create_result = self.db_manager.CreateUser(
            Email="session@example.com",
            Password="testpassword123",
            Username="sessionuser",
            MissionAcknowledged=True
        )
        
        user_id = create_result["user_id"]
        
        # Get verification token from database
        cursor = self.db_manager.Connection.execute(
            "SELECT EmailVerificationToken FROM Users WHERE Id = ?", (user_id,)
        )
        verification_token = cursor.fetchone()[0]
        
        self.db_manager.VerifyUserEmail(verification_token)
        
        # Create session
        session_result = self.db_manager.CreateUserSession(user_id, "127.0.0.1", "Test Agent")
        
        self.assertTrue(session_result["success"], f"Session creation failed: {session_result.get('error')}")
        self.assertIn("session_token", session_result)
        
        # Validate session
        session_token = session_result["session_token"]
        validation_result = self.db_manager.ValidateSession(session_token)
        
        self.assertTrue(validation_result["success"], f"Session validation failed: {validation_result.get('error')}")
        self.assertEqual(validation_result["user"]["id"], user_id)
    
    def test_duplicate_email_prevention(self):
        """Test that duplicate email registration is properly prevented"""
        user_data = {
            "Email": "duplicate@example.com",
            "Password": "testpassword123",
            "Username": "user1",
            "MissionAcknowledged": True
        }
        
        # Create first user
        result1 = self.db_manager.CreateUser(**user_data)
        self.assertTrue(result1["success"])
        
        # Try to create user with same email
        user_data["Username"] = "user2"  # Different username, same email
        result2 = self.db_manager.CreateUser(**user_data)
        
        self.assertFalse(result2["success"])
        self.assertIn("already registered", result2["error"])

class TestDatabaseManagerDirectConnection(unittest.TestCase):
    """Test DatabaseManager direct database operations"""
    
    def setUp(self):
        """Set up test with direct database connection"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create connection directly
        self.connection = sqlite3.connect(self.temp_db_path)
        self.connection.row_factory = sqlite3.Row
        
        # Create minimal books table
        self.connection.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT
            )
        """)
        self.connection.execute("INSERT INTO books (title, author) VALUES (?, ?)", 
                              ("Test Book", "Test Author"))
        self.connection.commit()
        
    def tearDown(self):
        """Clean up test environment"""
        if self.connection:
            self.connection.close()
        
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_direct_user_table_creation(self):
        """Test creating user tables directly"""
        db_manager = DatabaseManager(self.temp_db_path)
        
        # Check that user tables were created
        cursor = db_manager.Connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'User%'"
        )
        user_tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['Users', 'UserSessions', 'UserActivity', 'UserPreferences']
        for table in expected_tables:
            self.assertIn(table, user_tables, f"User table {table} not created")
        
        db_manager.Connection.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)