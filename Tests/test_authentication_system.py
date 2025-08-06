# File: test_authentication_system.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_authentication_system.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:23AM

"""
Test Suite for Authentication System
Tests user registration, email verification, login, and session management
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from Core.DatabaseManager import DatabaseManager

class TestAuthenticationSystem(unittest.TestCase):
    """Test authentication system components"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.temp_db_path)
        
        # Test user data
        self.test_user_data = {
            "Email": "test@example.com",
            "Password": "securepassword123",
            "Username": "testuser",
            "MissionAcknowledged": True
        }
        
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self.db_manager, 'Connection'):
            self.db_manager.Connection.close()
        
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_user_creation_with_email_verification(self):
        """Test user creation includes email verification token"""
        result = self.db_manager.CreateUser(**self.test_user_data)
        
        self.assertTrue(result["success"], f"User creation failed: {result.get('error')}")
        self.assertIn("user_id", result)
        self.assertIn("verification_token", result)
        self.assertFalse(result["email_verified"])
        self.assertFalse(result["is_active"])
        self.assertEqual(result["access_level"], "pending")
    
    def test_duplicate_email_registration(self):
        """Test that duplicate email registration is prevented"""
        # Create first user
        result1 = self.db_manager.CreateUser(**self.test_user_data)
        self.assertTrue(result1["success"])
        
        # Try to create user with same email
        result2 = self.db_manager.CreateUser(**self.test_user_data)
        self.assertFalse(result2["success"])
        self.assertIn("already exists", result2["error"])
    
    def test_email_verification_process(self):
        """Test email verification token validation"""
        # Create user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        self.assertTrue(create_result["success"])
        
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        
        # Verify email with correct token
        verify_result = self.db_manager.VerifyUserEmail(user_id, verification_token)
        self.assertTrue(verify_result["success"])
        self.assertTrue(verify_result["email_verified"])
        
        # Try to verify again with same token (should fail)
        verify_again = self.db_manager.VerifyUserEmail(user_id, verification_token)
        self.assertFalse(verify_again["success"])
    
    def test_email_verification_token_expiry(self):
        """Test that expired verification tokens are rejected"""
        # Create user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        
        # Manually expire the token by updating database
        expired_time = (datetime.now() - timedelta(hours=25)).isoformat()
        self.db_manager.Connection.execute(
            "UPDATE Users SET EmailVerificationExpiry = ? WHERE UserID = ?",
            (expired_time, user_id)
        )
        self.db_manager.Connection.commit()
        
        # Try to verify with expired token
        verify_result = self.db_manager.VerifyUserEmail(user_id, verification_token)
        self.assertFalse(verify_result["success"])
        self.assertIn("expired", verify_result["error"])
    
    def test_invalid_verification_token(self):
        """Test that invalid verification tokens are rejected"""
        # Create user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        
        # Try to verify with wrong token
        verify_result = self.db_manager.VerifyUserEmail(user_id, "invalid_token_12345")
        self.assertFalse(verify_result["success"])
        self.assertIn("Invalid", verify_result["error"])
    
    def test_user_authentication_unverified_email(self):
        """Test that users with unverified email cannot authenticate"""
        # Create user (email not verified)
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        self.assertTrue(create_result["success"])
        
        # Try to authenticate
        auth_result = self.db_manager.AuthenticateUser(
            self.test_user_data["Email"],
            self.test_user_data["Password"]
        )
        
        self.assertFalse(auth_result["success"])
        self.assertIn("email verification", auth_result["error"])
    
    def test_user_authentication_verified_email(self):
        """Test that users with verified email can authenticate"""
        # Create and verify user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        
        # Verify email
        verify_result = self.db_manager.VerifyUserEmail(user_id, verification_token)
        self.assertTrue(verify_result["success"])
        
        # Now try to authenticate
        auth_result = self.db_manager.AuthenticateUser(
            self.test_user_data["Email"],
            self.test_user_data["Password"]
        )
        
        self.assertTrue(auth_result["success"])
        self.assertEqual(auth_result["user"]["email"], self.test_user_data["Email"])
        self.assertEqual(auth_result["user"]["username"], self.test_user_data["Username"])
    
    def test_wrong_password_authentication(self):
        """Test that wrong password authentication fails"""
        # Create and verify user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        # Try to authenticate with wrong password
        auth_result = self.db_manager.AuthenticateUser(
            self.test_user_data["Email"],
            "wrongpassword"
        )
        
        self.assertFalse(auth_result["success"])
        self.assertIn("Invalid", auth_result["error"])
    
    def test_nonexistent_user_authentication(self):
        """Test authentication with non-existent email"""
        auth_result = self.db_manager.AuthenticateUser(
            "nonexistent@example.com",
            "anypassword"
        )
        
        self.assertFalse(auth_result["success"])
        self.assertIn("not found", auth_result["error"])
    
    def test_session_creation(self):
        """Test user session creation"""
        # Create and verify user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        # Create session
        session_result = self.db_manager.CreateUserSession(user_id, "127.0.0.1", "Test User Agent")
        
        self.assertTrue(session_result["success"])
        self.assertIn("session_token", session_result)
        self.assertIn("expires_at", session_result)
    
    def test_session_validation(self):
        """Test session token validation"""
        # Create user, verify, and create session
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        session_result = self.db_manager.CreateUserSession(user_id, "127.0.0.1", "Test User Agent")
        session_token = session_result["session_token"]
        
        # Validate session
        validation_result = self.db_manager.ValidateSession(session_token)
        
        self.assertTrue(validation_result["success"])
        self.assertEqual(validation_result["user"]["id"], user_id)
        self.assertEqual(validation_result["user"]["email"], self.test_user_data["email"])
    
    def test_invalid_session_validation(self):
        """Test validation of invalid session token"""
        validation_result = self.db_manager.ValidateSession("invalid_session_token")
        
        self.assertFalse(validation_result["success"])
        self.assertIn("Invalid", validation_result["error"])
    
    def test_expired_session_validation(self):
        """Test validation of expired session token"""
        # Create user, verify, and create session
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        session_result = self.db_manager.CreateUserSession(user_id, "127.0.0.1", "Test User Agent")
        session_token = session_result["session_token"]
        
        # Manually expire the session
        expired_time = (datetime.now() - timedelta(hours=1)).isoformat()
        self.db_manager.Connection.execute(
            "UPDATE UserSessions SET ExpiresAt = ? WHERE SessionToken = ?",
            (expired_time, session_token)
        )
        self.db_manager.Connection.commit()
        
        # Try to validate expired session
        validation_result = self.db_manager.ValidateSession(session_token)
        
        self.assertFalse(validation_result["success"])
        self.assertIn("expired", validation_result["error"])
    
    def test_user_access_levels(self):
        """Test user access level progression"""
        # Create user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        
        # Check initial access level
        self.assertEqual(create_result["access_level"], "pending")
        
        # Verify email - should upgrade access level
        verification_token = create_result["verification_token"]
        verify_result = self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        # After email verification, access level should be upgraded
        # This would need to be implemented in the VerifyUserEmail method
        cursor = self.db_manager.Connection.execute(
            "SELECT AccessLevel FROM Users WHERE UserID = ?", (user_id,)
        )
        current_access_level = cursor.fetchone()[0]
        
        # Should be upgraded from 'pending' after email verification
        self.assertNotEqual(current_access_level, "pending")
    
    def test_password_hashing_security(self):
        """Test that passwords are properly hashed and not stored in plaintext"""
        # Create user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        
        # Check that password is hashed in database
        cursor = self.db_manager.Connection.execute(
            "SELECT PasswordHash FROM Users WHERE UserID = ?", (user_id,)
        )
        stored_hash = cursor.fetchone()[0]
        
        # Hash should not equal original password
        self.assertNotEqual(stored_hash, self.test_user_data["Password"])
        
        # Hash should be bcrypt format (starts with $2b$)
        self.assertTrue(stored_hash.startswith("$2b$"))
    
    def test_rate_limiting_simulation(self):
        """Test rate limiting for authentication attempts"""
        # This would test the rate limiting functionality if implemented
        # For now, we'll just verify the basic structure exists
        
        # Create and verify user
        create_result = self.db_manager.CreateUser(**self.test_user_data)
        user_id = create_result["user_id"]
        verification_token = create_result["verification_token"]
        self.db_manager.VerifyUserEmail(user_id, verification_token)
        
        # Multiple failed authentication attempts
        failed_attempts = 0
        for i in range(10):  # Try 10 failed attempts
            auth_result = self.db_manager.AuthenticateUser(
                self.test_user_data["Email"],
                "wrongpassword"
            )
            if not auth_result["success"]:
                failed_attempts += 1
        
        # All should fail due to wrong password
        self.assertEqual(failed_attempts, 10)
        
        # Rate limiting would need to be implemented in the AuthenticateUser method
        # to prevent brute force attacks

if __name__ == "__main__":
    unittest.main(verbosity=2)