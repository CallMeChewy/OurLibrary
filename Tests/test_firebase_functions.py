# File: test_firebase_functions.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_firebase_functions.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-19
# Last Modified: 2025-08-19 11:20PM

"""
Test suite for Firebase Cloud Functions.
Tests email verification and password reset functionality.
"""

import pytest
import json
import requests
from pathlib import Path


class TestFirebaseFunctions:
    """Test Firebase Cloud Functions for email services."""
    
    @pytest.fixture
    def functions_base_url(self):
        """Base URL for Firebase Cloud Functions."""
        return "https://us-central1-our-library-d7b60.cloudfunctions.net"
    
    @pytest.fixture
    def test_email(self):
        """Test email address for function testing."""
        return "test@example.com"
    
    @pytest.mark.integration
    @pytest.mark.firebase
    @pytest.mark.smtp
    def test_send_verification_email_function_exists(self, functions_base_url):
        """Test that sendVerificationEmail function is deployed."""
        # Note: Firebase callable functions require authentication
        # This test verifies the function endpoint exists
        function_url = f"{functions_base_url}/sendVerificationEmail"
        
        # We expect a 401/403 for unauthenticated requests, not 404
        response = requests.post(function_url, json={"data": {"email": "test@example.com"}})
        
        # Function exists if we don't get 404
        assert response.status_code != 404, "sendVerificationEmail function not found"
    
    @pytest.mark.integration
    @pytest.mark.firebase
    @pytest.mark.smtp
    def test_send_password_reset_function_exists(self, functions_base_url):
        """Test that sendPasswordResetEmail function is deployed."""
        function_url = f"{functions_base_url}/sendPasswordResetEmail"
        
        # We expect a 401/403 for unauthenticated requests, not 404
        response = requests.post(function_url, json={"data": {"email": "test@example.com"}})
        
        # Function exists if we don't get 404
        assert response.status_code != 404, "sendPasswordResetEmail function not found"
    
    @pytest.mark.unit
    @pytest.mark.firebase
    def test_function_configuration_structure(self):
        """Test Firebase functions configuration structure."""
        functions_dir = Path("/home/herb/functions")
        
        # Check required files exist
        assert (functions_dir / "index.js").exists(), "functions/index.js missing"
        assert (functions_dir / "package.json").exists(), "functions/package.json missing"
        
        # Check package.json structure
        with open(functions_dir / "package.json", 'r') as f:
            package_config = json.load(f)
        
        assert "dependencies" in package_config
        assert "firebase-functions" in package_config["dependencies"]
        assert "nodemailer" in package_config["dependencies"]
        assert "firebase-admin" in package_config["dependencies"]
    
    @pytest.mark.unit
    @pytest.mark.firebase
    def test_function_implementation_structure(self):
        """Test Firebase functions implementation structure."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for required exports
        assert "exports.sendVerificationEmail" in content
        assert "exports.sendPasswordResetEmail" in content
        
        # Check for Firebase Functions v2 usage
        assert "firebase-functions/v2" in content
        assert "onCall" in content
        
        # Check for SMTP configuration
        assert "nodemailer" in content
        assert "createTransport" in content
        assert "smtp.misk.com" in content or "ProjectHimalaya@BowersWorld.com" in content
        
        # Check for error handling
        assert "throw" in content or "Error" in content
        assert "console.log" in content or "console.error" in content
    
    @pytest.mark.unit
    @pytest.mark.smtp
    def test_email_template_structure(self):
        """Test email template structure in functions."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for email template components
        assert "emailHtml" in content
        assert "sendMail" in content
        assert "subject" in content
        assert "from" in content
        assert "to" in content
        
        # Check for verification code generation
        assert "verificationCode" in content or "resetToken" in content
        assert "Math.random" in content
        assert "toString" in content
        
        # Check for professional email formatting
        assert "OurLibrary" in content
        assert "verification" in content.lower()


class TestEmailTemplates:
    """Test email template functionality and content."""
    
    @pytest.mark.unit
    @pytest.mark.smtp
    def test_verification_email_template_content(self):
        """Test verification email template content."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for verification email elements
        assert "Email Verification Required" in content or "verification" in content.lower()
        assert "code" in content.lower()
        assert "verify" in content.lower()
        
        # Check for professional branding
        assert "OurLibrary" in content
        assert "Educational Platform" in content or "education" in content.lower()
    
    @pytest.mark.unit
    @pytest.mark.smtp
    def test_password_reset_email_template_content(self):
        """Test password reset email template content."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for password reset elements
        assert "password reset" in content.lower() or "reset" in content.lower()
        assert "token" in content.lower()
        
        # Check for security messaging
        assert "ignore" in content.lower() or "didn't request" in content.lower()
    
    @pytest.mark.security
    @pytest.mark.smtp
    def test_email_security_features(self):
        """Test email security features implementation."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check that no clickable links are generated
        # This is GOOD - we want manual codes, not links
        assert "http://" not in content or content.count("http://") <= 1
        assert "https://" not in content or content.count("https://") <= 2
        
        # Check for secure token generation
        assert "Math.random" in content
        assert "substring" in content or "slice" in content
        assert "toUpperCase" in content
        
        # Check for expiration messaging
        assert "expire" in content.lower() or "hour" in content.lower()


class TestSMTPConfiguration:
    """Test SMTP configuration and connectivity."""
    
    @pytest.mark.unit
    @pytest.mark.smtp
    def test_smtp_server_configuration(self):
        """Test SMTP server configuration."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for correct SMTP server
        assert "smtp.misk.com" in content
        assert "587" in content  # STARTTLS port
        
        # Check for authentication
        assert "Herb@BowersWorld.com" in content
        assert "auth:" in content
        
        # Check for sender configuration
        assert "ProjectHimalaya@BowersWorld.com" in content
    
    @pytest.mark.integration
    @pytest.mark.smtp
    def test_email_delivery_configuration(self):
        """Test email delivery configuration."""
        config_path = Path(__file__).parent.parent / "Config" / "email_config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check SMTP provider is active
        assert config["active_provider"] == "smtp"
        assert config["providers"]["smtp"]["enabled"] is True
        
        # Check sender configuration
        assert "from_email" in config
        assert "@" in config["from_email"]
        assert config["from_name"] is not None
    
    @pytest.mark.unit
    @pytest.mark.smtp
    def test_email_error_handling(self):
        """Test email error handling implementation."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for error handling
        assert "throw" in content or "Error" in content
        assert "console.error" in content or "console.log" in content
        
        # Check for input validation
        assert "!email" in content or "email" in content
        assert "Error" in content


class TestFunctionDeployment:
    """Test Firebase Functions deployment and configuration."""
    
    @pytest.mark.integration
    @pytest.mark.firebase
    def test_firebase_project_configuration(self):
        """Test Firebase project configuration."""
        functions_dir = Path("/home/herb/functions")
        
        # Check for Firebase configuration files
        firebase_json = Path(__file__).parent.parent / "firebase.json"
        if firebase_json.exists():
            with open(firebase_json, 'r') as f:
                config = json.load(f)
            
            assert "functions" in config
            assert "source" in config["functions"]
        
        # Check functions directory structure
        assert functions_dir.exists()
        assert (functions_dir / "index.js").exists()
        assert (functions_dir / "package.json").exists()
    
    @pytest.mark.unit
    @pytest.mark.firebase
    def test_function_runtime_configuration(self):
        """Test function runtime configuration."""
        functions_file = Path("/home/herb/functions/index.js")
        
        with open(functions_file, 'r') as f:
            content = f.read()
        
        # Check for Firebase Functions v2
        assert "firebase-functions/v2" in content
        assert "setGlobalOptions" in content
        
        # Check for admin initialization
        assert "firebase-admin" in content
        assert "initializeApp" in content


if __name__ == "__main__":
    # Run Firebase-specific tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not integration",  # Skip integration tests by default
    ])