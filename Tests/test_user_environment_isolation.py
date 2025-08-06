# File: test_user_environment_isolation.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_user_environment_isolation.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:21AM

"""
Test Suite for User Environment Isolation
Validates that user installations are properly isolated from development environment
and multiple users can coexist on the same system without conflicts
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add source directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from Core.UserSetupManager import UserSetupManager

class TestUserEnvironmentIsolation(unittest.TestCase):
    """Test user environment isolation and multi-user support"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_users = [
            {"id": 1, "username": "testuser1", "email": "test1@example.com"},
            {"id": 2, "username": "testuser2", "email": "test2@example.com"},
            {"id": 3, "username": "user_with_spaces", "email": "test3@example.com"}
        ]
        
        # Create temporary development directory
        self.temp_dev_dir = tempfile.mkdtemp(prefix="andylibrary_dev_")
        self.temp_dev_path = Path(self.temp_dev_dir)
        
        # Create mock development structure
        self.CreateMockDevelopmentEnvironment()
        
        # Store original working directory
        self.original_cwd = os.getcwd()
        
    def tearDown(self):
        """Clean up test environment"""
        # Restore original working directory
        os.chdir(self.original_cwd)
        
        # Clean up temporary directories
        if self.temp_dev_path.exists():
            shutil.rmtree(self.temp_dev_path)
        
        # Clean up any user installations created during tests
        for user in self.test_users:
            try:
                setup_manager = UserSetupManager(
                    user_id=user["id"], 
                    username=user["username"]
                )
                if setup_manager.AndyLibraryDir.exists():
                    shutil.rmtree(setup_manager.AndyLibraryDir)
            except:
                pass  # Ignore cleanup errors
    
    def CreateMockDevelopmentEnvironment(self):
        """Create a mock development environment for testing"""
        # Create development directory structure
        dev_dirs = [
            "Source/Core",
            "Source/API", 
            "WebPages",
            "Config",
            "Data/Local",
            "Tests"
        ]
        
        for dir_path in dev_dirs:
            (self.temp_dev_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create mock files
        mock_files = {
            "StartOurLibrary.py": "# Mock startup script\nprint('Starting AndyLibrary')",
            "requirements.txt": "fastapi\nuvicorn\nsqlite3",
            "Config/andygoogle_config.json": json.dumps({
                "database_path": "Data/Local/MyLibrary.db",
                "server_port": 8000
            }),
            "Data/Local/MyLibrary.db": b"MOCK_DATABASE_CONTENT",
            "Source/Core/__init__.py": "",
            "WebPages/index.html": "<html><body>Mock Library</body></html>"
        }
        
        for file_path, content in mock_files.items():
            full_path = self.temp_dev_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                with open(full_path, 'w') as f:
                    f.write(content)
            else:
                with open(full_path, 'wb') as f:
                    f.write(content)
    
    def test_user_specific_installation_paths(self):
        """Test that each user gets their own installation directory"""
        setup_managers = []
        
        for user in self.test_users:
            with patch.object(UserSetupManager, '__init__', wraps=UserSetupManager.__init__) as mock_init:
                setup_manager = UserSetupManager(
                    user_id=user["id"],
                    username=user["username"]
                )
                setup_managers.append(setup_manager)
        
        # Verify each user has unique installation paths
        installation_paths = [sm.AndyLibraryDir for sm in setup_managers]
        self.assertEqual(len(installation_paths), len(set(installation_paths)), 
                        "User installation paths are not unique")
        
        # Verify paths contain username
        for i, setup_manager in enumerate(setup_managers):
            username = self.test_users[i]["username"]
            self.assertIn(username.lower(), str(setup_manager.AndyLibraryDir).lower(),
                         f"Installation path should contain username: {username}")
    
    def test_development_environment_isolation(self):
        """Test that user installations don't interfere with development environment"""
        user = self.test_users[0]
        
        with patch.object(Path, '__new__') as mock_path:
            # Mock the DevSourceDir property to return our temp path
            def side_effect(cls, *args):
                if len(args) > 0 and str(args[0]).endswith('UserSetupManager.py'):
                    # Return path that makes DevSourceDir point to our temp directory
                    mock_file_path = Path(self.temp_dev_path / 'Source' / 'Core' / 'UserSetupManager.py')
                    return mock_file_path
                return Path(*args)
            
            mock_path.side_effect = side_effect
            
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Verify user directories are separate from development
            self.assertNotEqual(setup_manager.AndyLibraryDir, self.temp_dev_path)
            self.assertFalse(str(setup_manager.AndyLibraryDir).startswith(str(self.temp_dev_path)))
    
    def test_user_directory_creation(self):
        """Test that user directories are created properly"""
        user = self.test_users[0]
        
        with patch.object(UserSetupManager, 'DevSourceDir', self.temp_dev_path):
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Test directory creation
            result = setup_manager.CreateUserDirectories()
            
            self.assertTrue(result["success"], f"Directory creation failed: {result.get('error')}")
            
            # Verify all required directories exist
            required_dirs = [
                setup_manager.AndyLibraryDir,
                setup_manager.DatabaseDir,
                setup_manager.ConfigDir,
                setup_manager.LogsDir
            ]
            
            for directory in required_dirs:
                self.assertTrue(directory.exists(), f"Required directory not created: {directory}")
    
    def test_database_isolation(self):
        """Test that each user gets their own database copy"""
        user = self.test_users[0]
        
        with patch.object(UserSetupManager, 'DevSourceDir', self.temp_dev_path):
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Test database download/copy
            result = setup_manager.DownloadDatabase(user["id"], "mock_token")
            
            self.assertTrue(result["success"], f"Database download failed: {result.get('error')}")
            
            # Verify user database exists and is separate from development
            user_db_path = setup_manager.DatabaseDir / "MyLibrary.db"
            dev_db_path = self.temp_dev_path / "Data" / "Local" / "MyLibrary.db"
            
            self.assertTrue(user_db_path.exists(), "User database not created")
            self.assertNotEqual(user_db_path, dev_db_path, "User database path same as development")
    
    def test_file_copying_with_artifact_filtering(self):
        """Test that application files are copied without development artifacts"""
        user = self.test_users[0]
        
        # Add development artifacts to test filtering
        dev_artifacts = [
            "__pycache__/test.pyc",
            ".git/config",
            ".venv/bin/python",
            "Tests/test_file.py",
            ".pytest_cache/README.md",
            "node_modules/package/index.js"
        ]
        
        for artifact in dev_artifacts:
            artifact_path = self.temp_dev_path / artifact
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("development artifact")
        
        with patch.object(UserSetupManager, 'DevSourceDir', self.temp_dev_path):
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Create directories first
            setup_manager.CreateUserDirectories()
            
            # Test file copying
            result = setup_manager.CopyApplicationFiles()
            
            self.assertTrue(result["success"], f"File copying failed: {result.get('error')}")
            
            # Verify development artifacts were not copied
            for artifact in dev_artifacts:
                user_artifact_path = setup_manager.AndyLibraryDir / artifact
                self.assertFalse(user_artifact_path.exists(), 
                               f"Development artifact was copied: {artifact}")
    
    def test_user_configuration_isolation(self):
        """Test that user configurations are properly isolated"""
        user = self.test_users[0]
        
        with patch.object(UserSetupManager, 'DevSourceDir', self.temp_dev_path):
            setup_manager = UserSetupManager(
                user_id=user["id"],
                username=user["username"]
            )
            
            # Create directories first
            setup_manager.CreateUserDirectories()
            
            # Test configuration creation
            result = setup_manager.CreateUserConfiguration(user)
            
            self.assertTrue(result["success"], f"Configuration creation failed: {result.get('error')}")
            
            # Verify configuration content
            config = result["config"]
            self.assertEqual(config["environment"]["type"], "USER_INSTALLATION")
            self.assertTrue(config["environment"]["isolated_from_dev"])
            self.assertEqual(config["user"]["username"], user["username"])
            
            # Verify different port range than development
            user_ports = config["server"]["port_range"]
            dev_ports = [8000, 8010, 8080, 8090, 3000, 5000, 9000]
            self.assertNotEqual(user_ports, dev_ports, "User should have different port range than development")
    
    def test_multiple_users_no_conflicts(self):
        """Test that multiple users can be set up without conflicts"""
        setup_managers = []
        
        with patch.object(UserSetupManager, 'DevSourceDir', self.temp_dev_path):
            # Set up multiple users
            for user in self.test_users:
                setup_manager = UserSetupManager(
                    user_id=user["id"],
                    username=user["username"]
                )
                
                # Create directories
                dir_result = setup_manager.CreateUserDirectories()
                self.assertTrue(dir_result["success"], f"Directory creation failed for {user['username']}")
                
                # Create configuration
                config_result = setup_manager.CreateUserConfiguration(user)
                self.assertTrue(config_result["success"], f"Configuration creation failed for {user['username']}")
                
                setup_managers.append(setup_manager)
            
            # Verify no path conflicts
            all_paths = [sm.AndyLibraryDir for sm in setup_managers]
            unique_paths = set(all_paths)
            self.assertEqual(len(all_paths), len(unique_paths), "User installation paths conflict")
            
            # Verify all installations exist simultaneously
            for setup_manager in setup_managers:
                self.assertTrue(setup_manager.AndyLibraryDir.exists())
                self.assertTrue(setup_manager.ConfigDir.exists())
                self.assertTrue(setup_manager.DatabaseDir.exists())
    
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
                    # Windows should use %LOCALAPPDATA%\AndyLibrary\Users\{username}
                    self.assertIn("AndyLibrary", str(setup_manager.AndyLibraryDir))
                    self.assertIn("Users", str(setup_manager.AndyLibraryDir))
                elif platform == "darwin":
                    # macOS should use ~/Library/Application Support/AndyLibrary/Users/{username}
                    self.assertIn("Library", str(setup_manager.AndyLibraryDir))
                    self.assertIn("Application Support", str(setup_manager.AndyLibraryDir))
                else:  # linux
                    # Linux should use ~/.local/share/andylibrary/users/{username}
                    self.assertIn(".local", str(setup_manager.AndyLibraryDir))
                    self.assertIn("share", str(setup_manager.AndyLibraryDir))
                    self.assertIn("andylibrary", str(setup_manager.AndyLibraryDir))
                
                # All platforms should include username
                self.assertIn(user["username"], str(setup_manager.AndyLibraryDir))

if __name__ == "__main__":
    unittest.main(verbosity=2)