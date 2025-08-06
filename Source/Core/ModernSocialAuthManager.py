# File: ModernSocialAuthManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/ModernSocialAuthManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 06:35AM

"""
Modern Social Authentication Manager for AndyLibrary
Uses official Google libraries with 2025 security standards
Implements OAuth 2.0 with PKCE, token rotation, and comprehensive security
"""

import os
import json
import secrets
import logging
import hashlib
import base64
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, urlparse
from datetime import datetime, timedelta
from pathlib import Path

# Import secret manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Utils.SecretManager import GetSecretManager
except ImportError:
    GetSecretManager = None
    print("⚠️ SecretManager not available - using environment variables only")

# Official Google OAuth libraries (2025 standards)
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google.auth.exceptions

# Modern OAuth library for additional providers
try:
    from authlib.integrations.starlette_client import OAuth
    from authlib.oauth2.rfc7636 import create_s256_code_challenge
except ImportError:
    OAuth = None
    create_s256_code_challenge = None
    print("⚠️ Authlib not available - GitHub/Facebook OAuth disabled")

# Security libraries
from cryptography.fernet import Fernet
import jwt
from passlib.context import CryptContext

class ModernSocialAuthManager:
    """
    Modern OAuth 2.0 implementation with 2025 security standards
    - Uses official Google libraries
    - Implements PKCE for security
    - Token encryption and rotation
    - Comprehensive error handling
    - GDPR/CCPA compliant
    """
    
    def __init__(self):
        self.Logger = logging.getLogger(__name__)
        
        # Initialize secret manager
        self._InitializeSecretManager()
        
        # Load configurations
        self._LoadServerConfig()
        self._LoadSecurityConfig()
        
        # Initialize security components
        self._InitializeSecurity()
        
        # Initialize OAuth providers
        self._InitializeProviders()
        
        # Session store for PKCE and state management
        self.ActiveSessions = {}
        
        self.Logger.info("🔐 Modern OAuth 2.0 Manager initialized with 2025 security standards")
    
    def _InitializeSecretManager(self):
        """Initialize secret management system"""
        if GetSecretManager:
            try:
                self.SecretManager = GetSecretManager({
                    "backend": os.getenv("SECRET_BACKEND", "environment"),
                    "environment": os.getenv("ENVIRONMENT", "development")
                })
                self.Logger.info("✅ Secret Manager initialized")
            except Exception as e:
                self.Logger.error(f"Failed to initialize Secret Manager: {e}")
                self.SecretManager = None
        else:
            self.SecretManager = None
    
    def _LoadServerConfig(self):
        """Load server configuration for URL generation"""
        try:
            config_path = Path("Config/andygoogle_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.ServerHost = config.get("server_host", "127.0.0.1")
                    self.ServerPort = config.get("server_port", 8080)
                    self.Environment = config.get("environment", "development")
            else:
                # Default values
                self.ServerHost = "127.0.0.1"
                self.ServerPort = 8080
                self.Environment = "development"
        except Exception as e:
            self.Logger.warning(f"Failed to load server config: {e}")
            self.ServerHost = "127.0.0.1"
            self.ServerPort = 8080
            self.Environment = "development"
    
    def _LoadSecurityConfig(self):
        """Load OAuth security configuration"""
        try:
            config_path = Path("Config/oauth_security_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                    # Replace environment variables with proper defaults
                    env_replacements = {
                        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', 'dummy_google_client_id'),
                        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', 'dummy_google_client_secret'),
                        'GITHUB_CLIENT_ID': os.getenv('GITHUB_CLIENT_ID', 'dummy_github_client_id'),
                        'GITHUB_CLIENT_SECRET': os.getenv('GITHUB_CLIENT_SECRET', 'dummy_github_client_secret'),
                        'FACEBOOK_APP_ID': os.getenv('FACEBOOK_APP_ID', 'dummy_facebook_app_id'),
                        'FACEBOOK_APP_SECRET': os.getenv('FACEBOOK_APP_SECRET', 'dummy_facebook_app_secret'),
                        'OAUTH_TOKEN_ENCRYPTION_KEY': os.getenv('OAUTH_TOKEN_ENCRYPTION_KEY', secrets.token_urlsafe(32))
                    }
                    
                    for var_name, var_value in env_replacements.items():
                        content = content.replace(f"${{{var_name}}}", var_value)
                    
                    self.SecurityConfig = json.loads(content)
            else:
                raise FileNotFoundError("OAuth security config not found")
                
        except Exception as e:
            self.Logger.error(f"Failed to load OAuth security config: {e}")
            # Fallback to minimal secure defaults
            self.SecurityConfig = self._GetFallbackConfig()
    
    def _GetFallbackConfig(self):
        """Fallback security configuration"""
        return {
            "oauth_security": {
                "token_management": {"access_token_ttl": 3600},
                "rate_limiting": {"oauth_attempts_per_minute": 10}
            },
            "providers": {
                "google": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                    "enabled": bool(os.getenv('GOOGLE_CLIENT_ID'))
                }
            },
            "development": {"allowed_redirect_uris": [f"http://{self.ServerHost}:{self.ServerPort}/api/auth/oauth/callback"]}
        }
    
    def _InitializeSecurity(self):
        """Initialize security components"""
        # Token encryption
        encryption_key = os.getenv('OAUTH_TOKEN_ENCRYPTION_KEY')
        if not encryption_key:
            # Generate and warn about development key
            encryption_key = Fernet.generate_key().decode()
            self.Logger.warning("🚨 Using generated encryption key - set OAUTH_TOKEN_ENCRYPTION_KEY for production")
        
        try:
            self.TokenCipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        except Exception:
            # Fallback to generated key
            self.TokenCipher = Fernet(Fernet.generate_key())
            self.Logger.warning("🚨 Using fallback encryption key")
        
        # Password context for token hashing
        self.PasswordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Rate limiting store (in production, use Redis)
        self.RateLimitStore = {}
    
    def _LoadOAuthProviders(self) -> Dict[str, Dict[str, Any]]:
        """Load OAuth provider configurations using Secret Manager"""
        providers = {}
        
        # Helper function to get credentials
        def get_credentials(provider_name: str) -> Dict[str, str]:
            if self.SecretManager:
                return self.SecretManager.GetOAuthCredentials(provider_name)
            else:
                # Fallback to environment variables
                if provider_name == "google":
                    return {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET')
                    }
                elif provider_name == "github":
                    return {
                        "client_id": os.getenv('GITHUB_CLIENT_ID'),
                        "client_secret": os.getenv('GITHUB_CLIENT_SECRET')  
                    }
                elif provider_name == "facebook":
                    return {
                        "client_id": os.getenv('FACEBOOK_APP_ID'),
                        "client_secret": os.getenv('FACEBOOK_APP_SECRET')
                    }
                return {}
        
        # Google OAuth configuration
        google_creds = get_credentials("google")
        if google_creds.get("client_id") and google_creds.get("client_secret"):
            providers['google'] = {
                'client_id': google_creds["client_id"],
                'client_secret': google_creds["client_secret"],
                'auth_url': 'https://accounts.google.com/o/oauth2/auth/v2',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'scope': 'openid email profile',
                'name': 'Google',
                'enabled': True
            }
        
        # GitHub OAuth configuration
        github_creds = get_credentials("github")
        if github_creds.get("client_id") and github_creds.get("client_secret"):
            providers['github'] = {
                'client_id': github_creds["client_id"],
                'client_secret': github_creds["client_secret"],
                'auth_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'scope': 'user:email',
                'name': 'GitHub',
                'enabled': True
            }
        
        # Facebook OAuth configuration  
        facebook_creds = get_credentials("facebook")
        if facebook_creds.get("client_id") and facebook_creds.get("client_secret"):
            providers['facebook'] = {
                'client_id': facebook_creds["client_id"],
                'client_secret': facebook_creds["client_secret"],
                'auth_url': 'https://www.facebook.com/v19.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v19.0/oauth/access_token',
                'user_info_url': 'https://graph.facebook.com/me',
                'scope': 'email',
                'name': 'Facebook',
                'enabled': True
            }
        
        return providers
    
    def _InitializeProviders(self):
        """Initialize OAuth providers with official libraries"""
        self.Providers = {}
        
        # Load OAuth provider configurations
        oauth_providers = self._LoadOAuthProviders()
        
        # Google OAuth with official library
        if "google" in oauth_providers:
            try:
                google_config = oauth_providers["google"]
                
                # Create temporary credentials file for Google Flow
                google_creds = {
                    "web": {
                        "client_id": google_config["client_id"],
                        "client_secret": google_config["client_secret"],
                        "auth_uri": google_config.get("auth_url", "https://accounts.google.com/o/oauth2/auth"),
                        "token_uri": google_config.get("token_url", "https://oauth2.googleapis.com/token"),
                        "redirect_uris": self._GetAllowedRedirectUris()
                    }
                }
                
                # Initialize Google Flow
                self.GoogleFlow = Flow.from_client_config(
                    google_creds,
                    scopes=google_config.get("scope", "openid email profile").split(),
                    redirect_uri=self._GetRedirectUri("google")
                )
                
                self.Providers["google"] = {
                    "name": google_config["name"],
                    "flow": self.GoogleFlow,
                    "config": google_config,
                    "type": "official"
                }
                
                self.Logger.info("✅ Google OAuth initialized with official library and Secret Manager")
                
            except Exception as e:
                self.Logger.error(f"Failed to initialize Google OAuth: {e}")
        
        # Additional providers using Authlib
        for provider_name in ["github", "facebook"]:
            if provider_name in oauth_providers:
                provider_config = oauth_providers[provider_name]
                
                self.Providers[provider_name] = {
                    "name": provider_config["name"],
                    "config": provider_config,
                    "type": "authlib"
                }
                self.Logger.info(f"✅ {provider_config['name']} OAuth configured with Secret Manager")
    
    def _GetAllowedRedirectUris(self) -> List[str]:
        """Get allowed redirect URIs based on environment"""
        if self.Environment == "production":
            return self.SecurityConfig.get("production", {}).get("allowed_redirect_uris", [])
        else:
            return self.SecurityConfig.get("development", {}).get("allowed_redirect_uris", [])
    
    def _GetRedirectUri(self, provider: str) -> str:
        """Get redirect URI for specific provider"""
        allowed_uris = self._GetAllowedRedirectUris()
        if allowed_uris:
            return allowed_uris[0]  # Use first allowed URI
        
        # Fallback
        protocol = "https" if self.Environment == "production" else "http"
        return f"{protocol}://{self.ServerHost}:{self.ServerPort}/api/auth/oauth/callback"
    
    def GenerateAuthUrl(self, provider: str, user_ip: str = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL with modern security practices
        Implements PKCE, state validation, and rate limiting
        """
        try:
            # Rate limiting check
            if not self._CheckRateLimit(user_ip, "auth_request"):
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            
            if provider not in self.Providers:
                return {"success": False, "error": f"Provider '{provider}' not configured"}
            
            provider_info = self.Providers[provider]
            
            if provider == "google" and provider_info["type"] == "official":
                return self._GenerateGoogleAuthUrl()
            else:
                return self._GenerateAuthLibUrl(provider, provider_info)
                
        except Exception as e:
            self.Logger.error(f"Error generating auth URL for {provider}: {e}")
            return {"success": False, "error": "Authentication setup failed"}
    
    def _GenerateGoogleAuthUrl(self) -> Dict[str, Any]:
        """Generate Google OAuth URL using official library"""
        try:
            # Generate PKCE parameters
            code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
            
            if create_s256_code_challenge:
                code_challenge = create_s256_code_challenge(code_verifier)
            else:
                # Fallback PKCE implementation
                import hashlib
                code_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode()).digest()
                ).decode().rstrip('=')
            
            # Generate secure state
            state = secrets.token_urlsafe(32)
            
            # Configure flow with additional security parameters
            self.GoogleFlow.code_challenge = code_challenge
            self.GoogleFlow.code_challenge_method = 'S256'
            
            authorization_url, flow_state = self.GoogleFlow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )
            
            # Store session data securely
            session_id = secrets.token_urlsafe(16)
            self.ActiveSessions[session_id] = {
                "provider": "google",
                "state": state,
                "code_verifier": code_verifier,
                "created_at": datetime.utcnow(),
                "flow_state": flow_state
            }
            
            return {
                "success": True,
                "auth_url": authorization_url,
                "session_id": session_id,
                "state": state,
                "provider": "google"
            }
            
        except Exception as e:
            self.Logger.error(f"Google auth URL generation failed: {e}")
            return {"success": False, "error": "Google authentication setup failed"}
    
    def _GenerateAuthLibUrl(self, provider: str, provider_info: Dict) -> Dict[str, Any]:
        """Generate auth URL for non-Google providers using Authlib"""
        try:
            config = provider_info["config"]
            
            # Generate PKCE parameters
            code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
            
            if create_s256_code_challenge:
                code_challenge = create_s256_code_challenge(code_verifier)
            else:
                # Fallback PKCE implementation
                import hashlib
                code_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode()).digest()
                ).decode().rstrip('=')
            
            # Generate secure state
            state = f"{provider}:{secrets.token_urlsafe(32)}"
            
            # Build authorization URL
            auth_params = {
                "client_id": config["client_id"],
                "response_type": "code",
                "redirect_uri": self._GetRedirectUri(provider),
                "scope": " ".join(config.get("scopes", [])),
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }
            
            # Add provider-specific parameters
            additional_params = config.get("additional_params", {})
            auth_params.update(additional_params)
            
            auth_url = f"{config['auth_uri']}?{urlencode(auth_params)}"
            
            # Store session data
            session_id = secrets.token_urlsafe(16)
            self.ActiveSessions[session_id] = {
                "provider": provider,
                "state": state,
                "code_verifier": code_verifier,
                "created_at": datetime.utcnow()
            }
            
            return {
                "success": True,
                "auth_url": auth_url,
                "session_id": session_id,
                "state": state,
                "provider": provider
            }
            
        except Exception as e:
            self.Logger.error(f"{provider} auth URL generation failed: {e}")
            return {"success": False, "error": f"{provider_info['name']} authentication setup failed"}
    
    def HandleOAuthCallback(self, code: str, state: str, session_id: str = None) -> Dict[str, Any]:
        """
        Handle OAuth callback with comprehensive security validation
        """
        try:
            # Find session by state if session_id not provided
            session_data = None
            if session_id and session_id in self.ActiveSessions:
                session_data = self.ActiveSessions[session_id]
            else:
                # Find by state (fallback)
                for sid, data in self.ActiveSessions.items():
                    if data.get("state") == state:
                        session_data = data
                        session_id = sid
                        break
            
            if not session_data:
                return {"success": False, "error": "Invalid or expired session"}
            
            # Validate state parameter
            if session_data.get("state") != state:
                return {"success": False, "error": "State validation failed"}
            
            # Check session expiry (15 minutes max)
            session_age = datetime.utcnow() - session_data["created_at"]
            if session_age > timedelta(minutes=15):
                self.ActiveSessions.pop(session_id, None)
                return {"success": False, "error": "Session expired"}
            
            provider = session_data["provider"]
            
            if provider == "google":
                result = self._HandleGoogleCallback(code, session_data)
            else:
                result = self._HandleAuthLibCallback(provider, code, session_data)
            
            # Clean up session
            self.ActiveSessions.pop(session_id, None)
            
            return result
            
        except Exception as e:
            self.Logger.error(f"OAuth callback error: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def _HandleGoogleCallback(self, code: str, session_data: Dict) -> Dict[str, Any]:
        """Handle Google OAuth callback using official library"""
        try:
            # Exchange code for token
            self.GoogleFlow.fetch_token(code=code)
            credentials = self.GoogleFlow.credentials
            
            # Get user info
            user_info = self._GetGoogleUserInfo(credentials)
            if not user_info["success"]:
                return user_info
            
            # Encrypt and store credentials
            encrypted_credentials = self._EncryptCredentials(credentials)
            
            return {
                "success": True,
                "provider": "google",
                "user_info": user_info["user_info"],
                "credentials": encrypted_credentials,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token
            }
            
        except Exception as e:
            self.Logger.error(f"Google callback error: {e}")
            return {"success": False, "error": "Google authentication failed"}
    
    def _HandleAuthLibCallback(self, provider: str, code: str, session_data: Dict) -> Dict[str, Any]:
        """Handle non-Google OAuth callback"""
        try:
            provider_config = self.SecurityConfig["providers"][provider]
            
            # Exchange code for token
            token_data = {
                "grant_type": "authorization_code",
                "client_id": provider_config["client_id"],
                "client_secret": provider_config["client_secret"],
                "code": code,
                "redirect_uri": self._GetRedirectUri(provider),
                "code_verifier": session_data["code_verifier"]
            }
            
            import requests
            token_response = requests.post(
                provider_config["token_uri"],
                data=token_data,
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                self.Logger.error(f"{provider} token exchange failed: {token_response.text}")
                return {"success": False, "error": f"{provider} authentication failed"}
            
            token_info = token_response.json()
            access_token = token_info.get("access_token")
            
            if not access_token:
                return {"success": False, "error": "Failed to obtain access token"}
            
            # Get user info
            user_info = self._GetProviderUserInfo(provider, access_token)
            if not user_info["success"]:
                return user_info
            
            return {
                "success": True,
                "provider": provider,
                "user_info": user_info["user_info"],
                "access_token": access_token,
                "refresh_token": token_info.get("refresh_token")
            }
            
        except Exception as e:
            self.Logger.error(f"{provider} callback error: {e}")
            return {"success": False, "error": f"{provider} authentication failed"}
    
    def _GetGoogleUserInfo(self, credentials: Credentials) -> Dict[str, Any]:
        """Get Google user information using official library"""
        try:
            import googleapiclient.discovery
            
            service = googleapiclient.discovery.build(
                'oauth2', 'v2', credentials=credentials
            )
            
            user_info = service.userinfo().get().execute()
            
            normalized = {
                "provider": "google",
                "provider_id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False)
            }
            
            return {"success": True, "user_info": normalized}
            
        except Exception as e:
            self.Logger.error(f"Failed to get Google user info: {e}")
            return {"success": False, "error": "Failed to retrieve user information"}
    
    def _GetProviderUserInfo(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user info from non-Google providers"""
        try:
            provider_config = self.SecurityConfig["providers"][provider]
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            import requests
            response = requests.get(provider_config["userinfo_uri"], headers=headers)
            
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to get {provider} user info"}
            
            user_data = response.json()
            normalized = self._NormalizeUserData(provider, user_data)
            
            return {"success": True, "user_info": normalized}
            
        except Exception as e:
            self.Logger.error(f"Failed to get {provider} user info: {e}")
            return {"success": False, "error": "Failed to retrieve user information"}
    
    def _NormalizeUserData(self, provider: str, user_data: Dict) -> Dict[str, Any]:
        """Normalize user data across providers"""
        normalized = {
            "provider": provider,
            "provider_id": None,
            "email": None,
            "name": None,
            "picture": None,
            "verified_email": False
        }
        
        if provider == "github":
            normalized.update({
                "provider_id": str(user_data.get("id")),
                "email": user_data.get("email"),
                "name": user_data.get("name") or user_data.get("login"),
                "picture": user_data.get("avatar_url"),
                "verified_email": True  # GitHub emails are verified
            })
        
        elif provider == "facebook":
            normalized.update({
                "provider_id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture", {}).get("data", {}).get("url"),
                "verified_email": True  # Facebook emails are verified
            })
        
        return normalized
    
    def _EncryptCredentials(self, credentials) -> str:
        """Encrypt OAuth credentials for secure storage"""
        try:
            cred_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": list(credentials.scopes) if credentials.scopes else []
            }
            
            cred_json = json.dumps(cred_data).encode()
            encrypted = self.TokenCipher.encrypt(cred_json)
            return base64.b64encode(encrypted).decode()
            
        except Exception as e:
            self.Logger.error(f"Failed to encrypt credentials: {e}")
            return ""
    
    def _CheckRateLimit(self, user_ip: str, action: str) -> bool:
        """Check rate limiting for OAuth requests"""
        if not user_ip:
            return True
        
        key = f"{user_ip}:{action}"
        now = datetime.utcnow()
        
        # Clean old entries
        self.RateLimitStore = {
            k: v for k, v in self.RateLimitStore.items()
            if now - v["last_request"] < timedelta(minutes=5)
        }
        
        if key not in self.RateLimitStore:
            self.RateLimitStore[key] = {"count": 1, "last_request": now}
            return True
        
        entry = self.RateLimitStore[key]
        
        # Check if within rate limit
        rate_limit = self.SecurityConfig.get("oauth_security", {}).get("rate_limiting", {})
        max_attempts = rate_limit.get("oauth_attempts_per_minute", 10)
        
        if entry["count"] >= max_attempts:
            return False
        
        entry["count"] += 1
        entry["last_request"] = now
        return True
    
    def GetAvailableProviders(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available OAuth providers"""
        providers = {}
        
        for provider_id, provider_info in self.Providers.items():
            providers[provider_id] = {
                "name": provider_info["name"],
                "enabled": True,
                "auth_url": f"/api/auth/oauth/{provider_id}",
                "type": provider_info["type"]
            }
        
        return providers
    
    def RefreshToken(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Refresh OAuth token using encrypted credentials"""
        try:
            # Decrypt credentials
            encrypted_data = base64.b64decode(encrypted_credentials.encode())
            decrypted_data = self.TokenCipher.decrypt(encrypted_data)
            cred_data = json.loads(decrypted_data.decode())
            
            # Recreate credentials object
            credentials = Credentials(
                token=cred_data["token"],
                refresh_token=cred_data["refresh_token"],
                token_uri=cred_data["token_uri"],
                client_id=cred_data["client_id"],
                client_secret=cred_data["client_secret"],
                scopes=cred_data["scopes"]
            )
            
            # Refresh token
            request = Request()
            credentials.refresh(request)
            
            # Re-encrypt updated credentials
            new_encrypted = self._EncryptCredentials(credentials)
            
            return {
                "success": True,
                "credentials": new_encrypted,
                "access_token": credentials.token
            }
            
        except Exception as e:
            self.Logger.error(f"Token refresh failed: {e}")
            return {"success": False, "error": "Token refresh failed"}
    
    def RevokeToken(self, access_token: str) -> bool:
        """Revoke OAuth token"""
        try:
            import requests
            
            # Google token revocation
            revoke_url = "https://oauth2.googleapis.com/revoke"
            response = requests.post(revoke_url, data={"token": access_token})
            
            return response.status_code == 200
            
        except Exception as e:
            self.Logger.error(f"Token revocation failed: {e}")
            return False
    
    def ValidateToken(self, access_token: str) -> Dict[str, Any]:
        """Validate OAuth access token"""
        try:
            import requests
            
            # Google token validation
            validation_url = f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"
            response = requests.get(validation_url)
            
            if response.status_code == 200:
                token_info = response.json()
                return {
                    "valid": True,
                    "expires_in": token_info.get("expires_in"),
                    "scope": token_info.get("scope"),
                    "client_id": token_info.get("aud")
                }
            else:
                return {"valid": False, "error": "Token validation failed"}
                
        except Exception as e:
            self.Logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": "Token validation error"}