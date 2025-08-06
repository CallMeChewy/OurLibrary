# File: test_user_environment_simple.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_user_environment_simple.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:25AM

"""
Simplified Test Suite for User Environment Isolation
Tests basic functionality that can be verified without complex mocking
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from Core.UserSetupManager import UserSetupManager

class TestUserEnvironmentSimple(unittest.TestCase):
    """Simplified tests for user environment isolation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_users = [
            {"id": 1, "username": "testuser1", "email": "test1@example.com"},
            {"id": 2, "username": "testuser2", "email": "test2@example.com"},
            {"id": 3, "username": "user_with_spaces", "email": "test3@example.com"}
        ]
    
    def test_user_specific_installation_paths(self):
        """Test that each user gets their own installation directory"""
        setup_managers = []
        
        for user in self.test_users:
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            setup_managers.append(setup_manager)
        
        # Verify each user has unique installation paths
        installation_paths = [str(sm.AndyLibraryDir) for sm in setup_managers]
        self.assertEqual(len(installation_paths), len(set(installation_paths)), 
                        "User installation paths are not unique")
        
        # Verify paths contain username
        for i, setup_manager in enumerate(setup_managers):
            username = self.test_users[i]["username"]
            self.assertIn(username.lower(), str(setup_manager.AndyLibraryDir).lower(),
                         f"Installation path should contain username: {username}")
    
    def test_platform_specific_paths(self):
        """Test that installation paths follow OS-specific conventions"""
        user = self.test_users[0]
        
        # Test different platforms
        test_platforms = ["windows", "darwin", "linux"]
        
        for platform in test_platforms:
            with patch('platform.system', return_value=platform):
                setup_manager = UserSetupManager(
                    user_id=user["id"],
                    username=user["username"]
                )
                
                if platform == "windows":
                    # Windows should use AndyLibrary\Users\{username}
                    self.assertIn("AndyLibrary", str(setup_manager.AndyLibraryDir))
                    self.assertIn("Users", str(setup_manager.AndyLibraryDir))
                elif platform == "darwin":
                    # macOS should use Library/Application Support/AndyLibrary/Users/{username}
                    self.assertIn("Library", str(setup_manager.AndyLibraryDir))
                    self.assertIn("Application Support", str(setup_manager.AndyLibraryDir))
                else:  # linux
                    # Linux should use .local/share/andylibrary/users/{username}
                    self.assertIn(".local", str(setup_manager.AndyLibraryDir))
                    self.assertIn("share", str(setup_manager.AndyLibraryDir))
                    self.assertIn("andylibrary", str(setup_manager.AndyLibraryDir))
                
                # All platforms should include username
                self.assertIn(user["username"], str(setup_manager.AndyLibraryDir))
    
    def test_user_directory_structure(self):
        """Test that user directory structure is properly defined"""
        user = self.test_users[0]
        
        setup_manager = UserSetupManager(
            user_id=user["id"],
            username=user["username"]
        )
        
        # Verify required directories are defined
        required_attrs = ['AndyLibraryDir', 'DatabaseDir', 'ConfigDir', 'LogsDir', 'AppDir']
        
        for attr in required_attrs:
            self.assertTrue(hasattr(setup_manager, attr), f"Missing required attribute: {attr}")
            path_value = getattr(setup_manager, attr)
            self.assertIsInstance(path_value, Path, f"{attr} should be a Path object")
            self.assertIn(user["username"], str(path_value), f"{attr} should include username")
    
    def test_multiple_users_no_path_conflicts(self):
        """Test that multiple users have non-conflicting paths"""
        setup_managers = []
        
        # Create setup managers for all test users
        for user in self.test_users:
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            setup_managers.append(setup_manager)
        
        # Collect all paths from all users
        all_paths = []
        for setup_manager in setup_managers:
            paths = [
                setup_manager.AndyLibraryDir,
                setup_manager.DatabaseDir,
                setup_manager.ConfigDir,
                setup_manager.LogsDir,
                setup_manager.AppDir
            ]
            all_paths.extend(paths)
        
        # Convert to strings for comparison
        all_path_strings = [str(p) for p in all_paths]
        unique_path_strings = set(all_path_strings)
        
        # Verify no path conflicts
        self.assertEqual(len(all_path_strings), len(unique_path_strings), 
                        "Found conflicting paths between users")
    
    def test_username_handling_edge_cases(self):
        """Test that usernames with special characters are handled properly"""
        edge_case_users = [
            {"id": 10, "username": "user.with.dots"},
            {"id": 11, "username": "user-with-dashes"},
            {"id": 12, "username": "user_with_underscores"},
            {"id": 13, "username": "UserWithCaps"}
        ]
        
        for user in edge_case_users:
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Verify path exists and contains some form of the username
            path_str = str(setup_manager.AndyLibraryDir)
            
            # Should contain the username in some form
            self.assertTrue(
                user["username"] in path_str or user["username"].lower() in path_str.lower(),
                f"Path {path_str} should contain username {user['username']}"
            )
    
    def test_user_id_fallback(self):
        """Test that when username is None, user_id is used as fallback"""
        setup_manager = UserSetupManager(user_id=999, username=None)
        
        # Should use user_999 as username fallback
        self.assertEqual(setup_manager.Username, "user_999")
        self.assertIn("user_999", str(setup_manager.AndyLibraryDir))
    
    def test_anonymous_user_handling(self):
        """Test handling of anonymous users (no user_id or username)"""
        setup_manager = UserSetupManager()
        
        # Should use "anonymous" as default
        self.assertEqual(setup_manager.Username, "anonymous")
        self.assertIn("anonymous", str(setup_manager.AndyLibraryDir))

if __name__ == "__main__":
    unittest.main(verbosity=2)