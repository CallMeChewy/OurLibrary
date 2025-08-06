# File: test_startup.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_startup.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 09:38AM

import pytest
import socket
import json
from unittest.mock import patch, MagicMock
from StartOurLibrary import OurLibraryStarter

class TestOurLibraryStarter:
    """Test suite for OurLibrary startup functionality"""
    
    @pytest.fixture
    def starter(self):
        """Create a starter instance for testing"""
        return OurLibraryStarter()
    
    def test_init_creates_instance(self, starter):
        """Test that OurLibraryStarter initializes correctly"""
        assert starter is not None
        assert hasattr(starter, 'script_dir')
        assert hasattr(starter, 'config_path')
        assert hasattr(starter, 'config')
    
    def test_load_config_with_missing_file(self, starter):
        """Test config loading when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            config = starter.load_config()
            assert config == {}
    
    def test_load_config_with_valid_file(self, starter):
        """Test config loading with valid JSON file"""
        test_config = {"test_key": "test_value", "server_port": 8000}
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(test_config)
            
            config = starter.load_config()
            assert config == test_config
    
    def test_check_environment_python_version(self, starter):
        """Test environment check validates Python version"""
        issues = starter.check_environment()
        # Should not have Python version issues in current environment
        python_issues = [issue for issue in issues if "Python" in issue]
        assert len(python_issues) == 0
    
    def test_find_available_port_success(self, starter):
        """Test finding an available port"""
        port = starter.find_available_port(9000, max_attempts=5)
        assert port is not None
        assert isinstance(port, int)
        assert 9000 <= port < 9005
    
    def test_find_available_port_with_busy_port(self, starter):
        """Test port detection when preferred port is busy"""
        # Create a socket to occupy a port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('127.0.0.1', 9001))
            sock.listen(1)
            
            # Should find an alternative port
            port = starter.find_available_port(9001, max_attempts=5)
            assert port is not None
            assert port != 9001
            
        finally:
            sock.close()
    
    def test_find_available_port_no_ports_available(self, starter):
        """Test when no ports are available in range"""
        # Mock socket to always raise OSError
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.bind.side_effect = OSError("Port busy")
            
            port = starter.find_available_port(9010, max_attempts=3)
            assert port is None
    
    @pytest.mark.unit
    def test_identify_port_user_handles_missing_tools(self, starter):
        """Test port identification gracefully handles missing system tools"""
        # Should not raise exceptions even if netstat/lsof are missing
        try:
            starter.identify_port_user(8000)
        except Exception as e:
            pytest.fail(f"identify_port_user raised an exception: {e}")
    
    def test_config_path_construction(self, starter):
        """Test that config path is constructed correctly"""
        assert starter.config_path.endswith("Config/andygoogle_config.json")
        assert "andygoogle_config.json" in starter.config_path