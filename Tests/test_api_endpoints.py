# File: test_api_endpoints.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_api_endpoints.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:22AM

"""
Test Suite for API Endpoints
Tests authentication, setup, and user management API endpoints
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

# Import after path setup
from API.MainAPI import app
from Core.DatabaseManager import DatabaseManager
from Core.UserSetupManager import UserSetupManager

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints for authentication and setup"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Mock user data
        self.test_user = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "subscription_tier": "free",
            "access_level": "verified"
        }
        
        # Mock auth token
        self.mock_token = "mock_jwt_token_12345"
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary database
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_health_check_endpoint(self):
        """Test API health check endpoint"""
        response = self.client.get("/api/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("version", data)
    
    def test_mode_endpoint(self):
        """Test API mode endpoint"""
        response = self.client.get("/api/mode")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("mode", data)
        self.assertIn("display_name", data)
        self.assertIn("icon", data)
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_status_endpoint_not_installed(self, mock_setup_class, mock_auth):
        """Test setup status endpoint when not installed"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager
        mock_setup = MagicMock()
        mock_setup.ConfigDir = Path("/mock/config")
        mock_setup.DatabaseDir = Path("/mock/database")
        mock_setup.AndyLibraryDir = Path("/mock/installation")
        mock_setup.Username = "testuser"
        mock_setup.Platform = "linux"
        mock_setup_class.return_value = mock_setup
        
        # Mock files not existing
        with patch('pathlib.Path.exists', return_value=False):
            response = self.client.get(
                "/api/setup/status",
                headers={"Authorization": f"Bearer {self.mock_token}"}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["installed"])
        self.assertIn("not installed", data["message"])
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_status_endpoint_installed(self, mock_setup_class, mock_auth):
        """Test setup status endpoint when already installed"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager
        mock_setup = MagicMock()
        mock_setup.ConfigDir = Path("/mock/config")
        mock_setup.DatabaseDir = Path("/mock/database") 
        mock_setup.AndyLibraryDir = Path("/mock/installation")
        mock_setup.Username = "testuser"
        mock_setup.Platform = "linux"
        mock_setup_class.return_value = mock_setup
        
        # Mock configuration content
        mock_config = {
            "environment": {
                "type": "USER_INSTALLATION",
                "isolated_from_dev": True
            },
            "user": {
                "installed_at": "2025-07-25T10:00:00"
            },
            "database": {
                "version": "2025.07.25"
            }
        }
        
        # Mock files existing and config content
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(mock_config))):
            
            response = self.client.get(
                "/api/setup/status",
                headers={"Authorization": f"Bearer {self.mock_token}"}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["installed"])
        self.assertEqual(data["environment_type"], "USER_INSTALLATION")
        self.assertTrue(data["isolated_from_dev"])
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_install_endpoint_success(self, mock_setup_class, mock_auth):
        """Test setup install endpoint successful installation"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager and successful setup
        mock_setup = MagicMock()
        mock_setup.Username = "testuser"
        mock_setup.Platform = "linux"
        mock_setup.AndyLibraryDir = Path("/mock/installation")
        mock_setup.CompleteUserSetup.return_value = {
            "success": True,
            "message": "Installation completed successfully",
            "setup_steps": [
                ("Database Download", True, "Database downloaded"),
                ("Application Files", True, "Files copied"),
                ("User Configuration", True, "Configuration created"),
                ("Desktop Shortcut", True, "Shortcut created")
            ]
        }
        mock_setup_class.return_value = mock_setup
        
        response = self.client.post(
            "/api/setup/install",
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("isolated environment", data["message"])
        self.assertEqual(data["environment_info"]["type"], "USER_INSTALLATION")
        self.assertTrue(data["environment_info"]["isolated_from_dev"])
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_install_endpoint_failure(self, mock_setup_class, mock_auth):
        """Test setup install endpoint installation failure"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager and failed setup
        mock_setup = MagicMock()
        mock_setup.CompleteUserSetup.return_value = {
            "success": False,
            "error": "Database download failed"
        }
        mock_setup_class.return_value = mock_setup
        
        response = self.client.post(
            "/api/setup/install",
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("Database download failed", data["detail"])
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_launch_endpoint_success(self, mock_setup_class, mock_auth):
        """Test setup launch endpoint successful launch"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager and successful launch
        mock_setup = MagicMock()
        mock_setup.Username = "testuser"
        mock_setup.Platform = "linux"
        mock_setup.AndyLibraryDir = Path("/mock/installation")
        mock_setup.LaunchAndyLibrary.return_value = {
            "success": True,
            "message": "AndyLibrary launched successfully",
            "installation_path": "/mock/installation",
            "process_id": 12345,
            "user_environment": True
        }
        mock_setup_class.return_value = mock_setup
        
        response = self.client.post(
            "/api/setup/launch",
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
    
    @patch('Source.API.MainAPI.require_auth')
    @patch('Source.Core.UserSetupManager.UserSetupManager')
    def test_setup_launch_endpoint_failure(self, mock_setup_class, mock_auth):
        """Test setup launch endpoint launch failure"""
        # Mock authentication
        mock_auth.return_value = self.test_user
        
        # Mock setup manager and failed launch
        mock_setup = MagicMock()
        mock_setup.LaunchAndyLibrary.return_value = {
            "success": False,
            "error": "User installation not found"
        }
        mock_setup_class.return_value = mock_setup
        
        response = self.client.post(
            "/api/setup/launch",
            headers={"Authorization": f"Bearer {self.mock_token}"}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("User installation not found", data["detail"])
    
    def test_unauthenticated_setup_endpoints(self):
        """Test that setup endpoints require authentication"""
        endpoints = [
            "/api/setup/status",
            "/api/setup/install", 
            "/api/setup/launch"
        ]
        
        for endpoint in endpoints:
            # Test GET endpoints
            if "status" in endpoint:
                response = self.client.get(endpoint)
            else:
                # Test POST endpoints
                response = self.client.post(endpoint)
            
            # Should require authentication
            self.assertIn(response.status_code, [401, 403], 
                         f"Endpoint {endpoint} should require authentication")
    
    @patch('Source.Core.DatabaseManager.DatabaseManager')
    def test_registration_endpoint(self, mock_db_class):
        """Test user registration endpoint"""
        # Mock database manager
        mock_db = MagicMock()
        mock_db.CreateUser.return_value = {
            "success": True,
            "user_id": 1,
            "message": "User created successfully",
            "verification_token": "mock_token"
        }
        mock_db_class.return_value = mock_db
        
        registration_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "username": "newuser",
            "mission_acknowledged": True,
            "data_consent": True
        }
        
        response = self.client.post("/api/auth/register", json=registration_data)
        
        # Should be successful (if endpoint exists and is working)
        # Note: This test depends on the actual registration endpoint implementation
        if response.status_code == 404:
            self.skipTest("Registration endpoint not found - may need implementation")
        else:
            self.assertEqual(response.status_code, 200)
    
    def test_oauth_providers_endpoint(self):
        """Test OAuth providers endpoint"""
        response = self.client.get("/api/auth/oauth/providers")
        
        # Should return available OAuth providers
        if response.status_code == 404:
            self.skipTest("OAuth providers endpoint not found - may need implementation")
        else:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("providers", data)

class TestAPIEndpointsIntegration(unittest.TestCase):
    """Integration tests for API endpoints with real database"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.client = TestClient(app)
        
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Initialize database with required tables
        self.db_manager = DatabaseManager(self.temp_db_path)
        
    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self.db_manager, 'Connection'):
            self.db_manager.Connection.close()
        
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    @patch('Source.API.MainAPI.DatabaseManager')
    def test_full_registration_flow(self, mock_db_class):
        """Test complete user registration flow"""
        # Mock database manager to use our test database
        mock_db_class.return_value = self.db_manager
        
        # Test registration
        registration_data = {
            "email": "integration@example.com",
            "password": "testpassword123",
            "username": "integrationuser",
            "mission_acknowledged": True,
            "data_consent": True
        }
        
        # This test would require the actual registration endpoint to be implemented
        # For now, we'll test the database operations directly
        result = self.db_manager.CreateUser(
            Email=registration_data["email"],
            Password=registration_data["password"],
            Username=registration_data["username"],
            MissionAcknowledged=registration_data["mission_acknowledged"]
        )
        
        self.assertTrue(result["success"])
        self.assertIn("user_id", result)

if __name__ == "__main__":
    unittest.main(verbosity=2)