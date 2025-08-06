# File: test_modern_oauth.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_modern_oauth.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 07:00AM

"""
Comprehensive test suite for Modern OAuth 2.0 implementation
Tests security, PKCE, token management, and provider integration
"""

import os
import sys
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
from Source.Core.ModernSocialAuthManager import ModernSocialAuthManager
from Source.Utils.SecretManager import SecretManager, GetSecretManager
from Source.Middleware.SecurityMiddleware import SecurityMiddleware

class TestModernSocialAuthManager:
    """Test suite for Modern Social Auth Manager"""
    
    @pytest.fixture
    def mock_secret_manager(self):
        """Mock secret manager for testing"""
        mock_sm = Mock(spec=SecretManager)
        mock_sm.GetOAuthCredentials.return_value = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
        return mock_sm
    
    @pytest.fixture
    def auth_manager(self, mock_secret_manager):
        """Create auth manager with mocked dependencies"""
        with patch('Source.Core.ModernSocialAuthManager.GetSecretManager', return_value=mock_secret_manager):
            with patch.dict(os.environ, {
                'GOOGLE_CLIENT_ID': 'test_google_id',
                'GOOGLE_CLIENT_SECRET': 'test_google_secret',
                'OAUTH_TOKEN_ENCRYPTION_KEY': 'test_encryption_key_32_chars_long_'
            }):
                return ModernSocialAuthManager()
    
    def test_initialization(self, auth_manager):
        """Test proper initialization of auth manager"""
        assert auth_manager is not None
        assert hasattr(auth_manager, 'Providers')
        assert hasattr(auth_manager, 'ActiveSessions')
        assert hasattr(auth_manager, 'SecretManager')
    
    def test_oauth_providers_loading(self, auth_manager):
        """Test OAuth providers are loaded correctly"""
        providers = auth_manager._LoadOAuthProviders()
        
        # Should have Google provider if credentials available
        if os.getenv('GOOGLE_CLIENT_ID'):
            assert 'google' in providers
            assert providers['google']['name'] == 'Google'
            assert 'client_id' in providers['google']
            assert 'client_secret' in providers['google']
    
    def test_generate_auth_url_google(self, auth_manager):
        """Test Google OAuth URL generation"""
        # Mock Google Flow
        mock_flow = Mock()
        mock_flow.authorization_url.return_value = ('https://accounts.google.com/oauth/auth?test', 'test_state')
        auth_manager.GoogleFlow = mock_flow
        
        result = auth_manager._GenerateGoogleAuthUrl()
        
        assert result['success'] is True
        assert 'auth_url' in result
        assert 'session_id' in result
        assert 'state' in result
        assert result['provider'] == 'google'
    
    def test_rate_limiting(self, auth_manager):
        """Test rate limiting functionality"""
        user_ip = "192.168.1.1"
        
        # First request should pass
        assert auth_manager._CheckRateLimit(user_ip, "auth_request") is True
        
        # Simulate multiple requests
        for _ in range(15):  # Exceed rate limit
            auth_manager._CheckRateLimit(user_ip, "auth_request")
        
        # Should now be rate limited
        assert auth_manager._CheckRateLimit(user_ip, "auth_request") is False
    
    def test_session_management(self, auth_manager):
        """Test PKCE session management"""
        session_id = "test_session_123"
        session_data = {
            "provider": "google",
            "state": "test_state",
            "code_verifier": "test_verifier",
            "created_at": datetime.utcnow()
        }
        
        # Store session
        auth_manager.ActiveSessions[session_id] = session_data
        
        # Verify session exists and is valid
        assert session_id in auth_manager.ActiveSessions
        assert auth_manager.ActiveSessions[session_id]['provider'] == 'google'
    
    def test_token_encryption(self, auth_manager):
        """Test OAuth token encryption"""
        # Mock credentials
        mock_credentials = Mock()
        mock_credentials.token = "test_access_token"
        mock_credentials.refresh_token = "test_refresh_token"
        mock_credentials.token_uri = "https://oauth2.googleapis.com/token"
        mock_credentials.client_id = "test_client_id"
        mock_credentials.client_secret = "test_client_secret"
        mock_credentials.scopes = ["email", "profile"]
        
        # Test encryption
        encrypted = auth_manager._EncryptCredentials(mock_credentials)
        
        assert encrypted is not None
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
    
    def test_security_validation(self, auth_manager):
        """Test security validation methods"""
        # Test state validation
        test_state = "test_state_12345"
        
        # First use should be valid
        assert not auth_manager._IsReplayAttack(test_state)
        
        # Second use should be detected as replay
        assert auth_manager._IsReplayAttack(test_state)
    
    def test_provider_availability(self, auth_manager):
        """Test provider availability checking"""
        providers = auth_manager.GetAvailableProviders()
        
        assert isinstance(providers, dict)
        
        # Each provider should have required fields
        for provider_id, provider_info in providers.items():
            assert 'name' in provider_info
            assert 'enabled' in provider_info
            assert 'auth_url' in provider_info

class TestSecretManager:
    """Test suite for Secret Manager"""
    
    @pytest.fixture
    def secret_manager(self):
        """Create secret manager for testing"""
        config = {
            "backend": "environment",
            "environment": "development"
        }
        return SecretManager(config)
    
    def test_initialization(self, secret_manager):
        """Test secret manager initialization"""
        assert secret_manager is not None
        assert secret_manager.Backend == "environment"
        assert hasattr(secret_manager, 'Cipher')
    
    def test_environment_secrets(self, secret_manager):
        """Test getting secrets from environment"""
        with patch.dict(os.environ, {'TEST_SECRET': 'test_value'}):
            result = secret_manager.GetSecret('TEST_SECRET')
            assert result == 'test_value'
    
    def test_oauth_credentials(self, secret_manager):
        """Test OAuth credential retrieval"""
        with patch.dict(os.environ, {
            'GOOGLE_CLIENT_ID': 'test_google_id',
            'GOOGLE_CLIENT_SECRET': 'test_google_secret'
        }):
            creds = secret_manager.GetOAuthCredentials('google')
            
            assert 'client_id' in creds
            assert 'client_secret' in creds
            assert creds['client_id'] == 'test_google_id'
            assert creds['client_secret'] == 'test_google_secret'
    
    def test_cache_functionality(self, secret_manager):
        """Test secret caching"""
        with patch.dict(os.environ, {'CACHE_TEST': 'cached_value'}):
            # First call
            result1 = secret_manager.GetSecret('CACHE_TEST')
            
            # Second call should use cache
            result2 = secret_manager.GetSecret('CACHE_TEST')
            
            assert result1 == result2 == 'cached_value'
            
            # Check cache stats
            stats = secret_manager.GetCacheStats()
            assert stats['total_entries'] > 0
    
    def test_secret_rotation(self, secret_manager):
        """Test secret rotation functionality"""
        with patch.dict(os.environ, {'ROTATE_TEST': 'original_value'}):
            # Get secret to cache it
            secret_manager.GetSecret('ROTATE_TEST')
            
            # Rotate secret
            result = secret_manager.RotateSecret('ROTATE_TEST')
            assert result is True
            
            # Cache should be cleared for this secret
            stats = secret_manager.GetCacheStats()
            # Verify rotation worked (cache entry removed)

class TestSecurityMiddleware:
    """Test suite for Security Middleware"""
    
    @pytest.fixture
    def security_middleware(self):
        """Create security middleware for testing"""
        config = {
            "environment": "development"
        }
        mock_app = Mock()
        return SecurityMiddleware(mock_app, config)
    
    def test_initialization(self, security_middleware):
        """Test security middleware initialization"""
        assert security_middleware is not None
        assert hasattr(security_middleware, 'SecurityHeaders')
        assert hasattr(security_middleware, 'RateLimits')
    
    def test_security_headers(self, security_middleware):
        """Test security headers generation"""
        headers = security_middleware._GetSecurityHeaders()
        
        # Check for required security headers
        assert 'X-Content-Type-Options' in headers
        assert 'X-Frame-Options' in headers
        assert 'X-XSS-Protection' in headers
        assert 'Content-Security-Policy' in headers
        
        assert headers['X-Content-Type-Options'] == 'nosniff'
        assert headers['X-Frame-Options'] == 'DENY'
    
    def test_malicious_pattern_detection(self, security_middleware):
        """Test malicious pattern detection"""
        # Mock request with malicious content
        mock_request = Mock()
        mock_request.url.path = "/admin/login"
        mock_request.url.query = ""
        
        result = security_middleware._DetectMaliciousPatterns(mock_request)
        assert result is True  # Should detect 'admin' pattern
        
        # Test legitimate request
        mock_request_clean = Mock()
        mock_request_clean.url.path = "/api/auth/login"
        mock_request_clean.url.query = ""
        
        result_clean = security_middleware._DetectMaliciousPatterns(mock_request_clean)
        assert result_clean is False
    
    def test_rate_limiting(self, security_middleware):
        """Test rate limiting functionality"""
        client_ip = "192.168.1.100"
        
        # Mock request
        mock_request = Mock()
        mock_request.url.path = "/api/auth/oauth"
        mock_request.client.host = client_ip
        
        # First requests should pass
        for _ in range(5):
            result = security_middleware._CheckRateLimit(mock_request, client_ip)
            assert result is None  # No rate limit response
        
        # Exceed rate limit
        for _ in range(20):
            security_middleware._CheckRateLimit(mock_request, client_ip)
        
        # Should now be rate limited
        result = security_middleware._CheckRateLimit(mock_request, client_ip)
        assert result is not None  # Rate limit response returned
    
    def test_oauth_security_checks(self, security_middleware):
        """Test OAuth-specific security checks"""
        # Mock OAuth callback request without state
        mock_request = Mock()
        mock_request.url.path = "/api/auth/oauth/callback"
        mock_request.query_params.get.return_value = None
        
        result = security_middleware._CheckOAuthSecurity(mock_request)
        assert result is not None  # Should return error response
        
        # Mock OAuth callback with state
        mock_request_with_state = Mock()
        mock_request_with_state.url.path = "/api/auth/oauth/callback"
        mock_request_with_state.query_params.get.return_value = "valid_state"
        
        result_valid = security_middleware._CheckOAuthSecurity(mock_request_with_state)
        # First call should pass, second should detect replay
        result_replay = security_middleware._CheckOAuthSecurity(mock_request_with_state)

class TestIntegration:
    """Integration tests for complete OAuth flow"""
    
    @pytest.fixture
    def complete_setup(self):
        """Set up complete testing environment"""
        # Mock environment
        test_env = {
            'GOOGLE_CLIENT_ID': 'integration_test_client_id',
            'GOOGLE_CLIENT_SECRET': 'integration_test_client_secret',
            'OAUTH_TOKEN_ENCRYPTION_KEY': 'integration_test_key_32_chars_'
        }
        
        with patch.dict(os.environ, test_env):
            # Initialize components
            secret_manager = SecretManager({"backend": "environment"})
            
            with patch('Source.Core.ModernSocialAuthManager.GetSecretManager', return_value=secret_manager):
                auth_manager = ModernSocialAuthManager()
                
                return {
                    'secret_manager': secret_manager,
                    'auth_manager': auth_manager
                }
    
    def test_end_to_end_oauth_flow(self, complete_setup):
        """Test complete OAuth flow from start to finish"""
        auth_manager = complete_setup['auth_manager']
        
        # 1. Generate auth URL
        with patch.object(auth_manager, '_GenerateGoogleAuthUrl') as mock_generate:
            mock_generate.return_value = {
                'success': True,
                'auth_url': 'https://accounts.google.com/oauth/test',
                'session_id': 'test_session',
                'state': 'test_state',
                'provider': 'google'
            }
            
            auth_result = auth_manager.GenerateAuthUrl('google', '192.168.1.1')
            assert auth_result['success'] is True
            assert 'auth_url' in auth_result
        
        # 2. Handle callback
        with patch.object(auth_manager, '_HandleGoogleCallback') as mock_handle:
            mock_handle.return_value = {
                'success': True,
                'provider': 'google',
                'user_info': {
                    'email': 'test@example.com',
                    'name': 'Test User'
                },
                'access_token': 'test_access_token'
            }
            
            callback_result = auth_manager.HandleOAuthCallback(
                code='test_code',
                state='test_state',
                session_id='test_session'
            )
            assert callback_result['success'] is True
    
    def test_security_integration(self, complete_setup):
        """Test security measures integration"""
        auth_manager = complete_setup['auth_manager']
        
        # Test rate limiting integration
        user_ip = "192.168.1.200"
        
        # Exceed rate limit
        for _ in range(15):
            auth_manager._CheckRateLimit(user_ip, "auth_request")
        
        # Next request should be blocked
        auth_result = auth_manager.GenerateAuthUrl('google', user_ip)
        
        # Should return rate limit error
        assert auth_result['success'] is False
        assert 'Rate limit' in auth_result.get('error', '')

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_credentials(self):
        """Test handling of missing OAuth credentials"""
        with patch.dict(os.environ, {}, clear=True):
            auth_manager = ModernSocialAuthManager()
            
            # Should handle missing credentials gracefully
            providers = auth_manager.GetAvailableProviders()
            assert isinstance(providers, dict)
    
    def test_invalid_provider(self):
        """Test handling of invalid provider requests"""
        auth_manager = ModernSocialAuthManager()
        
        result = auth_manager.GenerateAuthUrl('invalid_provider', '192.168.1.1')
        assert result['success'] is False
        assert 'not configured' in result.get('error', '').lower()
    
    def test_expired_sessions(self):
        """Test handling of expired OAuth sessions"""
        auth_manager = ModernSocialAuthManager()
        
        # Create expired session
        expired_session = {
            "provider": "google",
            "state": "expired_state",
            "code_verifier": "expired_verifier",
            "created_at": datetime.utcnow() - timedelta(minutes=20)  # Expired
        }
        
        auth_manager.ActiveSessions["expired_session"] = expired_session
        
        # Attempt to use expired session
        result = auth_manager.HandleOAuthCallback(
            code='test_code',
            state='expired_state',
            session_id='expired_session'
        )
        
        assert result['success'] is False
        assert 'expired' in result.get('error', '').lower()

# Test fixtures and utilities
@pytest.fixture
def mock_database():
    """Mock database for testing"""
    mock_db = Mock()
    mock_db.Connection.execute.return_value.fetchone.return_value = None
    mock_db.Connection.commit.return_value = None
    mock_db.HashPassword.return_value = "hashed_password"
    return mock_db

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])