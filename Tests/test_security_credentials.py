# File: test_security_credentials.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_security_credentials.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-12
# Last Modified: 2025-08-12 01:15PM

"""
Security and credential protection tests for OurLibrary

Ensures that sensitive information is properly protected and not exposed in public files.
"""

import pytest
import re
import os
from pathlib import Path

@pytest.mark.security
@pytest.mark.unit
def test_sensitive_credentials_file_exists(project_root):
    """Test that sensitive credentials file exists but is gitignored."""
    sensitive_file = project_root / "SENSITIVE_CREDENTIALS.md"
    assert sensitive_file.exists(), "SENSITIVE_CREDENTIALS.md must exist for security"
    
    gitignore_file = project_root / ".gitignore"
    assert gitignore_file.exists(), ".gitignore must exist"
    
    gitignore_content = gitignore_file.read_text()
    assert "SENSITIVE_CREDENTIALS.md" in gitignore_content, "Sensitive file must be gitignored"

@pytest.mark.security
@pytest.mark.unit
def test_no_passwords_in_public_files(project_root):
    """Test that no passwords are exposed in public files."""
    # Files that should never contain passwords
    public_files = [
        project_root / "Library.txt",
        project_root / "README.md", 
        project_root / "PROJECT_PLAN.md",
        project_root / "BowersWorld.com" / "index.html"
    ]
    
    password_patterns = [
        r"IChewy#4",  # Specific password from docs
        r"password\s*[:=]\s*['\"][^'\"]+['\"]",  # password: "value" (hardcoded passwords)
        r"pwd\s*[:=]\s*['\"][^'\"]+['\"]",       # pwd: "value" (hardcoded passwords)
        r"secret\s*[:=]\s*['\"][^'\"]+['\"]"     # secret: "value" (hardcoded secrets)
    ]
    
    for file_path in public_files:
        if file_path.exists():
            content = file_path.read_text()
            for pattern in password_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert not matches, f"Password found in public file {file_path}: {matches}"

@pytest.mark.security
@pytest.mark.unit
def test_gitignore_comprehensive_protection(project_root):
    """Test that .gitignore provides comprehensive credential protection."""
    gitignore_file = project_root / ".gitignore"
    gitignore_content = gitignore_file.read_text()
    
    required_patterns = [
        "SENSITIVE_",
        "*.credentials",
        "*.secret", 
        "*.token",
        "google_credentials.json",
        "oauth_security_config.json",
        "email_config.json"
    ]
    
    for pattern in required_patterns:
        assert pattern in gitignore_content, f"Pattern '{pattern}' must be in .gitignore"

@pytest.mark.security
@pytest.mark.config
def test_config_files_use_environment_variables(config_dir):
    """Test that config files use environment variables instead of hardcoded secrets."""
    config_files = [
        config_dir / "oauth_security_config.json",
        config_dir / "social_auth_config.json"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            content = config_file.read_text()
            
            # Should use environment variable placeholders
            assert "${" in content, f"Config file {config_file} should use environment variables"
            assert "GOOGLE_CLIENT_ID" in content or "dummy" in content, "Should use env vars or dummy values"
            
            # Should not contain real secrets
            assert not re.search(r'"[A-Za-z0-9]{20,}"', content), f"Real secrets found in {config_file}"

@pytest.mark.security
@pytest.mark.unit
def test_no_hardcoded_emails_in_browser_code(bowersworld_dir):
    """Test that no hardcoded emails are in browser-accessible code."""
    index_file = bowersworld_dir / "index.html"
    content = index_file.read_text()
    
    # Should not contain actual project emails in JavaScript
    sensitive_emails = [
        "Herb@BowersWorld.com",
        "ProjectHimalaya@BowersWorld.com",
        "HimalayaProject1@gmail.com"
    ]
    
    for email in sensitive_emails:
        assert email not in content, f"Sensitive email {email} found in browser code"

@pytest.mark.security
@pytest.mark.unit
def test_oauth_client_secrets_protection(config_dir):
    """Test that OAuth client secrets are properly protected."""
    oauth_files = [
        config_dir / "google_credentials.json",
        config_dir / "google_token.json"
    ]
    
    for oauth_file in oauth_files:
        if oauth_file.exists():
            content = oauth_file.read_text()
            
            # Check if using dummy values (acceptable) or real values (must be gitignored)
            if "dummy" not in content.lower():
                # Real credentials - verify file is gitignored
                gitignore_file = config_dir.parent / ".gitignore"
                gitignore_content = gitignore_file.read_text()
                assert oauth_file.name in gitignore_content, f"{oauth_file.name} with real credentials must be gitignored"

@pytest.mark.security
@pytest.mark.performance
def test_https_enforcement_in_production_config(config_dir):
    """Test that production configurations enforce HTTPS."""
    oauth_config = config_dir / "oauth_security_config.json"
    
    if oauth_config.exists():
        import json
        with oauth_config.open() as f:
            config = json.load(f)
        
        # Production settings should enforce HTTPS
        if "production" in config:
            prod_config = config["production"]
            assert prod_config.get("skip_https_check", True) == False, "Production must enforce HTTPS"
            
            # Redirect URIs should be HTTPS in production
            redirect_uris = prod_config.get("allowed_redirect_uris", [])
            for uri in redirect_uris:
                assert uri.startswith("https://"), f"Production redirect URI must use HTTPS: {uri}"

@pytest.mark.security
@pytest.mark.unit
def test_no_debug_information_in_browser_code(bowersworld_dir):
    """Test that no debug information is exposed in browser code."""
    index_file = bowersworld_dir / "index.html"
    content = index_file.read_text()
    
    debug_patterns = [
        r"console\.log\(",  # Console logging
        r"debugger;",       # Debugger statements
        r"alert\([^)]*debug", # Debug alerts
        r"TODO:",           # TODO comments
        r"FIXME:",          # FIXME comments
    ]
    
    for pattern in debug_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # Allow specific educational alerts but not debug info
        if pattern == r"alert\(" and all("registration" in m.lower() or "sign" in m.lower() or "terms" in m.lower() for m in matches):
            continue
        assert not matches, f"Debug information found in browser code: {matches}"

@pytest.mark.security
@pytest.mark.unit
def test_file_permissions_security(project_root):
    """Test that sensitive files have appropriate permissions."""
    sensitive_file = project_root / "SENSITIVE_CREDENTIALS.md"
    
    if sensitive_file.exists():
        # File should not be world-readable
        stat_info = sensitive_file.stat()
        permissions = oct(stat_info.st_mode)[-3:]
        
        # Should not be world-readable (last digit should not be 4, 5, 6, or 7)
        world_permissions = int(permissions[-1])
        assert world_permissions < 4, f"Sensitive file should not be world-readable: {permissions}"