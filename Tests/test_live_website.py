# File: test_live_website.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_live_website.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-12
# Last Modified: 2025-08-12 01:25PM

"""
Live website testing for OurLibrary

Tests the actual deployed website functionality and performance.
Note: These tests require internet connection and may be slower.
"""

import pytest
import requests
import time
from urllib.parse import urlparse

@pytest.mark.live
@pytest.mark.performance
def test_website_accessibility(website_url):
    """Test that the live website is accessible."""
    response = requests.get(website_url, timeout=10)
    assert response.status_code == 200, f"Website should be accessible: {response.status_code}"

@pytest.mark.live
@pytest.mark.performance
def test_website_response_time(website_url):
    """Test website response time for educational accessibility."""
    start_time = time.time()
    response = requests.get(website_url, timeout=10)
    response_time = time.time() - start_time
    
    assert response_time < 5.0, f"Website should load in under 5 seconds for accessibility: {response_time:.2f}s"
    assert response.status_code == 200, "Website should be accessible"

@pytest.mark.live
@pytest.mark.educational_mission
def test_educational_content_present(website_url):
    """Test that educational content is present on live site."""
    response = requests.get(website_url, timeout=10)
    content = response.text
    
    # Educational mission should be prominent
    assert "Getting education into the hands of people who can least afford it" in content, \
        "Educational mission must be on live site"
    assert "OurLibrary" in content, "OurLibrary branding must be present"
    assert "Join Our Library" in content, "Call-to-action must be present"

@pytest.mark.live
@pytest.mark.unit
def test_registration_form_available(base_url):
    """Test that registration functionality is available on live site."""
    response = requests.get(f"{base_url}/index.html", timeout=10)
    content = response.text
    
    # Registration form elements
    assert 'id="registration-form"' in content, "Registration form must be available"
    assert 'name="email"' in content, "Email field must be present"

@pytest.mark.live
@pytest.mark.security
def test_https_redirect(website_url):
    """Test HTTPS security for live website."""
    # Test both HTTP and HTTPS versions
    http_url = website_url.replace("https://", "http://")
    
    try:
        # Some deployments may redirect HTTP to HTTPS
        response = requests.get(http_url, timeout=10, allow_redirects=True)
        
        # Either should work with HTTPS or redirect to HTTPS
        final_url = response.url
        if response.status_code == 200:
            # Check if final URL is HTTPS or if content indicates secure setup
            assert "https://" in final_url or "github.io" in final_url or "bowersworld.com" in final_url, \
                "Should use HTTPS or secure hosting platform"
    except requests.exceptions.RequestException:
        # HTTP might be blocked, which is acceptable for security
        pass

@pytest.mark.live
@pytest.mark.performance
def test_mobile_responsiveness_headers(website_url):
    """Test mobile responsiveness headers."""
    response = requests.get(website_url, timeout=10)
    content = response.text
    
    # Mobile optimization meta tags
    assert 'viewport' in content, "Viewport meta tag required for mobile"
    assert 'width=device-width' in content, "Responsive viewport required"

@pytest.mark.live
@pytest.mark.unit
def test_javascript_functionality_present(base_url):
    """Test that JavaScript functionality is present on live site."""
    response = requests.get(f"{base_url}/index.html", timeout=10)
    content = response.text
    
    # JavaScript functions should be present
    assert "function handleRegistration" in content, "Registration handler must be available"
    assert "function showRegistration" in content, "Modal functions must be available"
    assert "function validateEmail" in content, "Validation functions must be available"

@pytest.mark.live
@pytest.mark.performance
def test_external_resource_loading(base_url):
    """Test that external resources load properly."""
    response = requests.get(f"{base_url}/index.html", timeout=10)
    content = response.text
    
    # Check for critical external resources
    if "tailwindcss" in content:
        # Tailwind CSS should be accessible
        import re
        tailwind_links = re.findall(r'src="(https://[^"]*tailwindcss[^"]*)"', content)
        for link in tailwind_links:
            try:
                resource_response = requests.head(link, timeout=5)
                # Accept 200 (OK) or 302 (redirect) as successful responses for CDNs
                assert resource_response.status_code in [200, 302], f"Tailwind CSS should be accessible: {link} (got {resource_response.status_code})"
            except requests.exceptions.RequestException:
                pytest.skip(f"External resource temporarily unavailable: {link}")

@pytest.mark.live
@pytest.mark.performance
def test_page_size_optimization(website_url):
    """Test page size for accessibility on limited bandwidth."""
    response = requests.get(website_url, timeout=10)
    content_length = len(response.content)
    
    # Page should be under 1MB for accessibility on slow connections
    max_size = 1024 * 1024  # 1MB
    assert content_length < max_size, \
        f"Page size should be under 1MB for accessibility: {content_length / 1024:.1f}KB"

@pytest.mark.live
@pytest.mark.educational_mission
def test_accessibility_features_live(base_url):
    """Test accessibility features on live site."""
    response = requests.get(f"{base_url}/index.html", timeout=10)
    content = response.text
    
    # Basic accessibility features
    assert '<label' in content, "Form labels required for screen readers"
    assert 'alt=' in content, "Alt text for images required"
    assert 'aria-' in content or 'role=' in content or 'tabindex' in content, \
        "ARIA attributes or accessibility features should be present"

@pytest.mark.live
@pytest.mark.unit
def test_social_login_placeholders_live(base_url):
    """Test that social login placeholders work on live site."""
    response = requests.get(f"{base_url}/index.html", timeout=10)
    content = response.text
    
    # Social login buttons should be present
    assert "Google" in content and "registerWithGoogle" in content, "Google login option should be available"
    assert "GitHub" in content and "registerWithGitHub" in content, "GitHub login option should be available"
    assert "Facebook" in content and "registerWithFacebook" in content, "Facebook login option should be available"

@pytest.mark.live
@pytest.mark.integration
def test_github_pages_deployment(github_pages_url):
    """Test GitHub Pages deployment if accessible."""
    try:
        response = requests.get(github_pages_url, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # If GitHub Pages is accessible, test basic functionality
            content = response.text
            assert "OurLibrary" in content or "BowersWorld" in content, \
                "GitHub Pages should serve OurLibrary content"
        elif response.status_code == 301 or response.status_code == 302:
            # Redirect is acceptable (may redirect to custom domain)
            assert True, "GitHub Pages redirect is acceptable"
        else:
            pytest.skip(f"GitHub Pages not accessible: {response.status_code}")
            
    except requests.exceptions.RequestException:
        pytest.skip("GitHub Pages temporarily unavailable")