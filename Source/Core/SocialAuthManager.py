# File: SocialAuthManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/SocialAuthManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-28 12:42AM

"""
Social Authentication Manager for AndyLibrary
Handles OAuth login with Google, GitHub, and Facebook as optional convenience features
Maintains mission focus: email registration works everywhere, social login is just easier
"""

import os
import json
import secrets
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta
from pathlib import Path

class SocialAuthManager:
    """
    Manage OAuth social authentication for educational accessibility
    """
    
    def __init__(self):
        self.Logger = logging.getLogger(__name__)
        
        # Load server configuration for URL generation
        self._LoadServerConfig()
        
        # OAuth Provider Configurations
        self.OAuthProviders = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile',
                'name': 'Google'
            },
            'github': {
                'client_id': os.getenv('GITHUB_CLIENT_ID'),
                'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
                'auth_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'scope': 'user:email',
                'name': 'GitHub'
            },
            'facebook': {
                'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
                'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'user_info_url': 'https://graph.facebook.com/me',
                'scope': 'email',
                'name': 'Facebook'
            }
        }
        
        # Base redirect URI using server configuration (matches Google Cloud Console)
        self.BaseRedirectUri = f"http://{self.ServerHost}:{self.ServerPort}"
    
    def _LoadServerConfig(self):
        """Load server configuration for URL generation"""
        try:
            config_path = Path("Config/andygoogle_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.ServerHost = config.get("server_host", "127.0.0.1")
                    self.ServerPort = config.get("server_port", 8080)
            else:
                # Default values if config not found
                self.ServerHost = "127.0.0.1"
                self.ServerPort = 8080
        except Exception as e:
            self.Logger.warning(f"Failed to load server config: {e}")
            self.ServerHost = "127.0.0.1"
            self.ServerPort = 8080
    
    def GetAvailableProviders(self) -> Dict[str, Dict[str, Any]]:
        """
        Get list of configured OAuth providers
        Only returns providers with valid client credentials
        """
        available_providers = {}
        
        for provider_id, config in self.OAuthProviders.items():
            if config['client_id'] and config['client_secret']:
                available_providers[provider_id] = {
                    'name': config['name'],
                    'login_url': f"/api/auth/oauth/{provider_id}",
                    'configured': True
                }
            else:
                available_providers[provider_id] = {
                    'name': config['name'],
                    'login_url': None,
                    'configured': False
                }
        
        return available_providers
    
    def GenerateAuthUrl(self, provider: str, redirect_uri: str = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for social login
        """
        try:
            if provider not in self.OAuthProviders:
                return {"success": False, "error": f"Unsupported provider: {provider}"}
            
            config = self.OAuthProviders[provider]
            
            if not config['client_id'] or not config['client_secret']:
                return {
                    "success": False, 
                    "error": f"{config['name']} OAuth not configured. Please use email registration instead."
                }
            
            # Generate state parameter for security
            state = secrets.token_urlsafe(32)
            
            # Use provided redirect URI or default
            redirect_uri = redirect_uri or self.BaseRedirectUri
            
            # Build authorization URL
            auth_params = {
                'client_id': config['client_id'],
                'redirect_uri': redirect_uri,
                'scope': config['scope'],
                'response_type': 'code',
                'state': f"{provider}:{state}"  # Encode provider in state for callback identification
            }
            
            auth_url = f"{config['auth_url']}?{urlencode(auth_params)}"
            
            self.Logger.info(f"Generated {config['name']} OAuth URL")
            
            return {
                "success": True,
                "auth_url": auth_url,
                "state": state,
                "provider": provider,
                "provider_name": config['name']
            }
            
        except Exception as e:
            self.Logger.error(f"Error generating {provider} auth URL: {e}")
            return {"success": False, "error": f"OAuth setup failed: {str(e)}"}
    
    def HandleOAuthCallback(self, provider: str, code: str, state: str, redirect_uri: str = None) -> Dict[str, Any]:
        """
        Handle OAuth callback and get user information
        """
        try:
            if provider not in self.OAuthProviders:
                return {"success": False, "error": f"Unsupported provider: {provider}"}
            
            config = self.OAuthProviders[provider]
            redirect_uri = redirect_uri or self.BaseRedirectUri
            
            # Exchange code for access token
            token_data = {
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'redirect_uri': redirect_uri
            }
            
            if provider == 'google':
                token_data['grant_type'] = 'authorization_code'
            
            # Get access token
            headers = {'Accept': 'application/json'}
            token_response = requests.post(config['token_url'], data=token_data, headers=headers)
            
            if token_response.status_code != 200:
                self.Logger.error(f"{config['name']} token exchange failed: {token_response.text}")
                return {"success": False, "error": f"{config['name']} authentication failed"}
            
            token_info = token_response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                return {"success": False, "error": "Failed to obtain access token"}
            
            # Get user information
            user_info = self.GetUserInfo(provider, access_token)
            
            if not user_info["success"]:
                return user_info
            
            return {
                "success": True,
                "user_info": user_info["user_info"],
                "provider": provider,
                "provider_name": config['name'],
                "access_token": access_token
            }
            
        except Exception as e:
            self.Logger.error(f"OAuth callback error for {provider}: {e}")
            return {"success": False, "error": f"OAuth authentication failed: {str(e)}"}
    
    def GetUserInfo(self, provider: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information from OAuth provider
        """
        try:
            config = self.OAuthProviders[provider]
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Special handling for different providers
            if provider == 'facebook':
                # Facebook requires specific fields
                user_url = f"{config['user_info_url']}?fields=id,name,email"
            else:
                user_url = config['user_info_url']
            
            response = requests.get(user_url, headers=headers)
            
            if response.status_code != 200:
                self.Logger.error(f"Failed to get {config['name']} user info: {response.text}")
                return {"success": False, "error": f"Failed to get user information from {config['name']}"}
            
            user_data = response.json()
            
            # Normalize user data across providers
            normalized_user = self.NormalizeUserData(provider, user_data)
            
            return {
                "success": True,
                "user_info": normalized_user,
                "raw_data": user_data
            }
            
        except Exception as e:
            self.Logger.error(f"Error getting user info from {provider}: {e}")
            return {"success": False, "error": f"Failed to retrieve user information: {str(e)}"}
    
    def NormalizeUserData(self, provider: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user data from different OAuth providers into consistent format
        """
        normalized = {
            'provider': provider,
            'provider_id': None,
            'email': None,
            'name': None,
            'username': None,
            'avatar_url': None
        }
        
        if provider == 'google':
            normalized.update({
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'username': user_data.get('email', '').split('@')[0] if user_data.get('email') else None,
                'avatar_url': user_data.get('picture')
            })
        
        elif provider == 'github':
            normalized.update({
                'provider_id': str(user_data.get('id')),
                'email': user_data.get('email'),
                'name': user_data.get('name') or user_data.get('login'),
                'username': user_data.get('login'),
                'avatar_url': user_data.get('avatar_url')
            })
        
        elif provider == 'facebook':
            normalized.update({
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'username': user_data.get('name', '').replace(' ', '').lower() if user_data.get('name') else None,
                'avatar_url': f"https://graph.facebook.com/{user_data.get('id')}/picture?type=large" if user_data.get('id') else None
            })
        
        return normalized
    
    def CreateOrUpdateSocialUser(self, user_info: Dict[str, Any], database_manager) -> Dict[str, Any]:
        """
        Create or update user account from social login
        Integrates with existing DatabaseManager for consistency
        """
        try:
            if not user_info.get('email'):
                return {
                    "success": False, 
                    "error": f"Email address required. Please ensure your {user_info.get('provider', 'social')} account has a public email address."
                }
            
            # Check if user already exists
            existing_user_query = """
                SELECT Id, Email, Username, SubscriptionTier, AccessLevel, EmailVerified, IsActive
                FROM Users WHERE Email = ?
            """
            
            existing_user = database_manager.Connection.execute(
                existing_user_query, (user_info['email'],)
            ).fetchone()
            
            if existing_user:
                # Update existing user with social login info if not already verified
                if not existing_user['EmailVerified']:
                    database_manager.Connection.execute("""
                        UPDATE Users 
                        SET EmailVerified = TRUE, 
                            IsActive = TRUE, 
                            AccessLevel = 'basic',
                            ModifiedAt = CURRENT_TIMESTAMP
                        WHERE Email = ?
                    """, (user_info['email'],))
                    database_manager.Connection.commit()
                    
                    self.Logger.info(f"✅ Social login activated existing account: {user_info['email']}")
                
                return {
                    "success": True,
                    "user_id": existing_user['Id'],
                    "email": existing_user['Email'],
                    "existing_user": True,
                    "message": f"Logged in successfully with {user_info.get('provider', 'social')} account"
                }
            
            else:
                # Create new user from social login
                # Social login users are automatically verified (email confirmed by provider)
                username = user_info.get('username') or user_info.get('name', '').replace(' ', '').lower()
                
                # Ensure unique username
                base_username = username[:20] if username else 'user'
                unique_username = base_username
                counter = 1
                while database_manager.Connection.execute(
                    "SELECT Id FROM Users WHERE Username = ?", (unique_username,)
                ).fetchone():
                    unique_username = f"{base_username}{counter}"
                    counter += 1
                
                # Create user (no password needed for social login)
                social_password = secrets.token_urlsafe(32)  # Generate secure random password
                password_hash = database_manager.HashPassword(social_password)
                
                cursor = database_manager.Connection.execute("""
                    INSERT INTO Users (
                        Email, Username, PasswordHash, 
                        SubscriptionTier, AccessLevel,
                        EmailVerified, IsActive, MissionAcknowledged
                    ) VALUES (?, ?, ?, 'guest', 'basic', TRUE, TRUE, TRUE)
                """, (user_info['email'], unique_username, password_hash))
                
                user_id = cursor.lastrowid
                database_manager.Connection.commit()
                
                self.Logger.info(f"✅ Created new social user: {user_info['email']} via {user_info.get('provider')}")
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "email": user_info['email'],
                    "username": unique_username,
                    "existing_user": False,
                    "message": f"Account created successfully with {user_info.get('provider', 'social')} login"
                }
                
        except Exception as e:
            self.Logger.error(f"Error creating/updating social user: {e}")
            return {"success": False, "error": f"Account creation failed: {str(e)}"}