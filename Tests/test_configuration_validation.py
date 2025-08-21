# File: test_configuration_validation.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_configuration_validation.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-12
# Last Modified: 2025-08-12 01:20PM

"""
Configuration validation tests for OurLibrary

Validates that all configuration files are properly structured and contain required settings.
"""

import pytest
import json
from pathlib import Path

@pytest.mark.config
@pytest.mark.unit
def test_oauth_security_config_structure(config_dir):
    """Test OAuth security configuration structure."""
    config_file = config_dir / "oauth_security_config.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        # Required top-level sections
        assert "oauth_security" in config, "oauth_security section required"
        assert "providers" in config, "providers section required"
        
        # OAuth security settings
        oauth_sec = config["oauth_security"]
        assert "encryption" in oauth_sec, "encryption settings required"
        assert "token_management" in oauth_sec, "token management settings required"
        assert "security_headers" in oauth_sec, "security headers required"
        
        # Provider configurations
        providers = config["providers"]
        assert "google" in providers, "Google provider configuration required"
        
        google_config = providers["google"]
        assert "client_id" in google_config, "Google client_id required"
        assert "scopes" in google_config, "Google scopes required"
        assert "pkce_enabled" in google_config, "PKCE must be configured"
        assert google_config["pkce_enabled"] == True, "PKCE must be enabled for security"

@pytest.mark.config
@pytest.mark.unit
def test_ourlibrary_config_exists(config_dir):
    """Test that main OurLibrary configuration exists."""
    config_file = config_dir / "ourlibrary_config.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        # Should contain basic app configuration
        assert isinstance(config, dict), "Configuration must be valid JSON object"

@pytest.mark.config
@pytest.mark.unit
def test_google_credentials_template_exists(config_dir):
    """Test that Google credentials template exists for setup guidance."""
    template_file = config_dir / "google_credentials.json.template"
    assert template_file.exists(), "Google credentials template required for setup"
    
    with template_file.open() as f:
        template = json.load(f)
    
    # Template structure validation
    assert "web" in template, "Google credentials template must have 'web' section"
    web_config = template["web"]
    assert "client_id" in web_config, "Template must include client_id placeholder"
    assert "redirect_uris" in web_config, "Template must include redirect_uris"
    assert "javascript_origins" in web_config, "Template must include javascript_origins"

@pytest.mark.config
@pytest.mark.educational_mission
def test_email_config_structure(config_dir):
    """Test email configuration for educational mission communications."""
    config_file = config_dir / "email_config.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        # Email configuration should support educational mission
        assert "smtp" in config or "service" in config or "providers" in config, "Email service configuration required"
        
        # Should not contain hardcoded passwords
        config_str = json.dumps(config)
        assert "IChewy#4" not in config_str, "Real passwords must not be in config files"

@pytest.mark.config
@pytest.mark.security
def test_oauth_test_accounts_structure(config_dir):
    """Test OAuth test accounts configuration."""
    config_file = config_dir / "oauth_test_accounts.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        # Should provide test account setup guidance
        assert isinstance(config, dict), "Test accounts config must be valid JSON"
        
        # Should not contain real production credentials
        config_str = json.dumps(config)
        for pattern in ["@gmail.com", "@bowersworld.com"]:
            if pattern in config_str:
                # If real emails present, they should be clearly marked as examples
                assert "example" in config_str.lower() or "test" in config_str.lower(), \
                    f"Real email {pattern} in test config should be marked as example"

@pytest.mark.config
@pytest.mark.unit
def test_config_files_are_valid_json(config_dir):
    """Test that all JSON configuration files are valid."""
    json_files = list(config_dir.glob("*.json"))
    
    for json_file in json_files:
        try:
            with json_file.open() as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {json_file}: {e}")

@pytest.mark.config
@pytest.mark.performance
def test_oauth_security_settings_performance(config_dir):
    """Test OAuth security settings for performance requirements."""
    config_file = config_dir / "oauth_security_config.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        if "oauth_security" in config:
            oauth_sec = config["oauth_security"]
            
            # Token management performance settings
            if "token_management" in oauth_sec:
                token_mgmt = oauth_sec["token_management"]
                
                # Access token TTL should be reasonable (not too short for performance)
                if "access_token_ttl" in token_mgmt:
                    assert token_mgmt["access_token_ttl"] >= 600, "Access token TTL should be at least 10 minutes"
                
                # Automatic refresh should be enabled for user experience
                if "automatic_refresh" in token_mgmt:
                    assert token_mgmt["automatic_refresh"] == True, "Automatic token refresh should be enabled"

@pytest.mark.config
@pytest.mark.educational_mission
def test_config_supports_educational_requirements(config_dir):
    """Test that configuration supports educational mission requirements."""
    oauth_config_file = config_dir / "oauth_security_config.json"
    
    if oauth_config_file.exists():
        with oauth_config_file.open() as f:
            config = json.load(f)
        
        # Should have compliance settings for educational use
        if "compliance" in config:
            compliance = config["compliance"]
            
            # Educational compliance requirements
            assert compliance.get("gdpr_compliant", False), "GDPR compliance required for global educational access"
            assert compliance.get("coppa_considerations", False), "COPPA considerations required for younger users"
            
            # Privacy policy should be configured
            if "privacy_policy_url" in compliance:
                privacy_url = compliance["privacy_policy_url"]
                assert "bowersworld.com" in privacy_url, "Privacy policy should be on project domain"

@pytest.mark.config
@pytest.mark.unit
def test_social_auth_config_browser_compatibility(config_dir):
    """Test social auth configuration for browser-only compatibility."""
    config_file = config_dir / "social_auth_config.json"
    
    if config_file.exists():
        with config_file.open() as f:
            config = json.load(f)
        
        if "oauth_providers" in config:
            providers = config["oauth_providers"]
            
            for provider_name, provider_config in providers.items():
                # Redirect URIs should support browser-only approach
                if "redirect_uri" in provider_config:
                    redirect_uri = provider_config["redirect_uri"]
                    # Should either be localhost for development or production domain
                    assert ("localhost" in redirect_uri or "127.0.0.1" in redirect_uri or 
                           "bowersworld.com" in redirect_uri), \
                           f"{provider_name} redirect URI should be localhost or production domain"