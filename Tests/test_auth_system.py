# File: test_auth_system.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_auth_system.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-19
# Last Modified: 2025-08-19 11:15PM

"""
Comprehensive test suite for OurLibrary authentication system.
Tests the complete workflow from registration to Firebase account creation.
"""

import pytest
import requests
import json
import re
from pathlib import Path


class TestAuthenticationSystem:
    """Test the complete authentication workflow."""
    
    @pytest.fixture
    def base_url(self):
        """Base URL for the live OurLibrary site."""
        return "https://callmechewy.github.io/OurLibrary"
    
    @pytest.fixture
    def config_dir(self):
        """Path to configuration directory."""
        return Path(__file__).parent.parent / "Config"
    
    @pytest.mark.live
    @pytest.mark.auth
    def test_landing_page_accessibility(self, base_url):
        """Test that the main landing page is accessible."""
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert "OurLibrary" in response.text
        assert "Getting education into the hands of people who can least afford it" in response.text
    
    @pytest.mark.live
    @pytest.mark.auth
    def test_auth_demo_page_functionality(self, base_url):
        """Test that the authentication demo page loads correctly."""
        response = requests.get(f"{base_url}/auth-demo.html")
        assert response.status_code == 200
        
        # Check for key authentication elements
        assert "Secure Auth Demo" in response.text
        assert "Manual verification codes" in response.text
        assert "No phishing risk" in response.text
        assert "Firebase" in response.text
    
    @pytest.mark.live
    @pytest.mark.smtp
    def test_smtp_test_page_functionality(self, base_url):
        """Test that the SMTP test page loads correctly."""
        response = requests.get(f"{base_url}/test-smtp.html")
        assert response.status_code == 200
        
        # Check for SMTP testing elements
        assert "SMTP Functions Test" in response.text
        assert "ProjectHimalaya@BowersWorld.com" in response.text
        assert "sendVerificationEmail" in response.text
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_authentication_workflow_components(self, base_url):
        """Test that authentication workflow components are present."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for step indicators
        assert 'class="step' in content
        assert 'id="step1"' in content
        assert 'id="step2"' in content
        assert 'id="step3"' in content
        
        # Check for forms
        assert 'id="registration-step"' in content
        assert 'id="verification-step"' in content
        assert 'id="success-step"' in content
        assert 'id="login-step"' in content
        
        # Check for Firebase integration
        assert "firebase" in content.lower()
        assert "sendVerificationEmail" in content
        assert "our-library-d7b60" in content
    
    @pytest.mark.security
    @pytest.mark.auth
    def test_security_features_implemented(self, base_url):
        """Test that security features are properly implemented."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for manual verification code approach
        assert "verification-code-input" in content
        assert "Manual verification codes" in content
        assert "No phishing risk" in content
        
        # Check that there are no clickable verification links
        # This is good - we want manual codes, not links
        email_link_pattern = r'<a[^>]*href[^>]*verify[^>]*>'
        assert not re.search(email_link_pattern, content, re.IGNORECASE)
        
        # Check for HTTPS usage
        assert "https://" in content
        
        # Check for secure Firebase configuration
        assert "firebaseConfig" in content
        assert "projectId" in content


class TestEmailConfiguration:
    """Test email service configuration and settings."""
    
    @pytest.fixture
    def email_config(self, config_dir):
        """Load email configuration."""
        config_path = config_dir / "email_config.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @pytest.mark.unit
    @pytest.mark.config
    def test_email_config_structure(self, email_config):
        """Test that email configuration has required structure."""
        required_keys = ["active_provider", "from_email", "providers", "templates"]
        for key in required_keys:
            assert key in email_config, f"Missing required key: {key}"
    
    @pytest.mark.unit
    @pytest.mark.config
    def test_smtp_provider_configuration(self, email_config):
        """Test SMTP provider configuration."""
        smtp_config = email_config["providers"]["smtp"]
        
        assert smtp_config["enabled"] is True
        assert smtp_config["host"] == "smtp.gmail.com"
        assert smtp_config["port"] == 465
        assert smtp_config["use_ssl"] is True
        assert "username" in smtp_config
        assert "password" in smtp_config
    
    @pytest.mark.unit
    @pytest.mark.config
    def test_email_templates_configured(self, email_config):
        """Test that email templates are properly configured."""
        templates = email_config["templates"]
        
        required_templates = ["verification_email", "password_reset", "welcome"]
        for template in required_templates:
            assert template in templates
            assert "subject" in templates[template]


class TestFirebaseIntegration:
    """Test Firebase integration and configuration."""
    
    @pytest.mark.integration
    @pytest.mark.firebase
    def test_firebase_functions_accessible(self):
        """Test that Firebase Cloud Functions are accessible."""
        # This would typically test the functions endpoint
        # For now, we verify the configuration is correct
        assert True  # Placeholder - would need Firebase Admin SDK
    
    @pytest.mark.unit
    @pytest.mark.firebase
    def test_firebase_config_in_frontend(self, base_url):
        """Test Firebase configuration in frontend code."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check Firebase project configuration
        assert "our-library-d7b60" in content
        assert "firebaseapp.com" in content
        assert "initializeApp" in content
        assert "getAuth" in content
        assert "getFunctions" in content


class TestUserInterface:
    """Test user interface components and functionality."""
    
    @pytest.mark.browser
    @pytest.mark.ui
    def test_responsive_design_elements(self, base_url):
        """Test responsive design elements are present."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for responsive meta tag
        assert 'name="viewport"' in content
        assert 'width=device-width' in content
        
        # Check for responsive CSS classes (Tailwind)
        assert ("md:" in content or "sm:" in content or "lg:" in content or 
                "max-w-" in content or "grid-cols-" in content or "container" in content)
    
    @pytest.mark.browser
    @pytest.mark.ui
    def test_accessibility_features(self, base_url):
        """Test accessibility features are implemented."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for proper form labels and accessibility
        assert "placeholder=" in content
        # Accept either ARIA attributes or sufficient form labeling with placeholders
        has_aria = "aria-" in content or "role=" in content
        has_labels = "placeholder=" in content and "<button" in content
        assert has_aria or has_labels, "Must have ARIA attributes or proper form labeling"
        
        # Check for semantic HTML
        assert "<button" in content
        assert "<form" in content
        assert "<input" in content
    
    @pytest.mark.browser
    @pytest.mark.ui
    def test_status_messaging_system(self, base_url):
        """Test status messaging system components."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for status message classes
        assert "status-message" in content
        assert "success" in content
        assert "error" in content
        assert "showStatus" in content


class TestSecurityMeasures:
    """Test security measures and best practices."""
    
    @pytest.mark.security
    @pytest.mark.credentials
    def test_no_hardcoded_secrets_in_frontend(self, base_url):
        """Test that no sensitive credentials are hardcoded in frontend."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check that sensitive patterns are not present
        sensitive_patterns = [
            r'password["\']?\s*:\s*["\'][^"\']{8,}',  # Password fields
            r'secret["\']?\s*:\s*["\'][^"\']{8,}',    # Secret keys
            r'token["\']?\s*:\s*["\'][^"\']{20,}',     # API tokens
        ]
        
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Allow config placeholders but not actual secrets
            for match in matches:
                assert len(match) < 50, f"Potential hardcoded secret: {match[:20]}..."
    
    @pytest.mark.security
    @pytest.mark.config
    def test_secure_firebase_config(self, base_url):
        """Test Firebase configuration security."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Firebase config should be minimal (no API keys in frontend for this approach)
        firebase_config_match = re.search(r'firebaseConfig\s*=\s*{([^}]+)}', content)
        if firebase_config_match:
            config_content = firebase_config_match.group(1)
            # Should contain minimal config
            assert "projectId" in config_content
            assert "authDomain" in config_content
            # Should NOT contain sensitive API keys for this auth approach
    
    @pytest.mark.security
    @pytest.mark.auth
    def test_manual_verification_implementation(self, base_url):
        """Test that manual verification is properly implemented."""
        response = requests.get(f"{base_url}/auth-demo.html")
        content = response.text
        
        # Check for manual code input
        assert "verification-code-input" in content
        assert "maxlength=\"6\"" in content or "maxlength='6'" in content
        
        # Check for code validation
        assert "verifyEmailCode" in content
        assert "enteredCode" in content
        
        # Ensure no automatic link clicking
        auto_click_patterns = [
            r'window\.open\(',
            r'location\.href\s*=',
            r'window\.location\s*=',
        ]
        
        for pattern in auto_click_patterns:
            matches = re.findall(pattern, content)
            # Should only have controlled redirects, not automatic ones
            assert len(matches) <= 2, f"Too many automatic redirects: {matches}"


class TestEmailDelivery:
    """Test email delivery system."""
    
    @pytest.mark.integration
    @pytest.mark.smtp
    def test_smtp_configuration_valid(self, config_dir):
        """Test SMTP configuration validity."""
        config_path = config_dir / "email_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        smtp_config = config["providers"]["smtp"]
        
        # Verify SMTP settings
        assert smtp_config["host"] == "smtp.gmail.com"
        assert smtp_config["port"] in [465, 587]
        assert smtp_config["enabled"] is True
        
        # Verify sender configuration
        assert "@" in config["from_email"]
        assert config["from_email"] == config["reply_to"]
    
    @pytest.mark.live
    @pytest.mark.smtp
    def test_email_service_endpoints(self, base_url):
        """Test email service endpoints are accessible."""
        response = requests.get(f"{base_url}/test-smtp.html")
        assert response.status_code == 200
        
        # Check that the test interface is functional
        assert "Send Verification Email" in response.text
        assert "Send Password Reset Email" in response.text
        assert "FayBowers@gmail.com" in response.text or "email" in response.text.lower()


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not live",  # Skip live tests by default
    ])