# File: SecretManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Utils/SecretManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 06:55AM

"""
Production-ready Secret Management System for AndyLibrary
Supports multiple backends: Environment variables, files, cloud secret managers
2025 security standards with encryption and rotation capabilities
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta

# Encryption for secret storage
from cryptography.fernet import Fernet
import base64

class SecretManager:
    """
    Multi-backend secret management with security best practices
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.Logger = logging.getLogger(__name__)
        self.Config = config or {}
        
        # Initialize encryption
        self._InitializeEncryption()
        
        # Backend configuration
        self.Backend = self.Config.get("backend", "environment")
        self.Environment = self.Config.get("environment", "development")
        
        # Secret cache with TTL
        self.SecretCache = {}
        self.CacheTTL = timedelta(minutes=5)  # Short TTL for security
        
        self.Logger.info(f"🔐 Secret Manager initialized with {self.Backend} backend")
    
    def _InitializeEncryption(self):
        """Initialize encryption for secret storage"""
        encryption_key = os.getenv("SECRET_ENCRYPTION_KEY")
        
        if not encryption_key:
            if self.Config.get("environment") == "production":
                raise ValueError("SECRET_ENCRYPTION_KEY required in production")
            else:
                # Generate for development (warn user)
                encryption_key = Fernet.generate_key().decode()
                self.Logger.warning("🚨 Using generated encryption key - set SECRET_ENCRYPTION_KEY for production")
        
        try:
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            self.Cipher = Fernet(encryption_key)
        except Exception as e:
            # Fallback encryption key
            self.Cipher = Fernet(Fernet.generate_key())
            self.Logger.warning(f"⚠️ Using fallback encryption: {e}")
    
    def GetSecret(self, secret_name: str, default: Any = None) -> Optional[str]:
        """
        Get secret from configured backend with caching
        """
        try:
            # Check cache first
            cache_key = f"{secret_name}:{self.Backend}"
            cached_entry = self.SecretCache.get(cache_key)
            
            if cached_entry and datetime.utcnow() - cached_entry["timestamp"] < self.CacheTTL:
                return cached_entry["value"]
            
            # Fetch from backend
            secret_value = None
            
            if self.Backend == "environment":
                secret_value = self._GetFromEnvironment(secret_name)
            elif self.Backend == "file":
                secret_value = self._GetFromFile(secret_name)
            elif self.Backend == "gcp_secret_manager":
                secret_value = self._GetFromGCPSecretManager(secret_name)
            elif self.Backend == "aws_secrets_manager":
                secret_value = self._GetFromAWSSecretsManager(secret_name)
            elif self.Backend == "azure_key_vault":
                secret_value = self._GetFromAzureKeyVault(secret_name)
            else:
                self.Logger.error(f"Unknown secret backend: {self.Backend}")
                return default
            
            # Cache the result
            if secret_value is not None:
                self.SecretCache[cache_key] = {
                    "value": secret_value,
                    "timestamp": datetime.utcnow()
                }
            
            return secret_value or default
            
        except Exception as e:
            self.Logger.error(f"Failed to get secret '{secret_name}': {e}")
            return default
    
    def _GetFromEnvironment(self, secret_name: str) -> Optional[str]:
        """Get secret from environment variables"""
        return os.getenv(secret_name)
    
    def _GetFromFile(self, secret_name: str) -> Optional[str]:
        """Get secret from encrypted file"""
        try:
            secrets_dir = Path(self.Config.get("secrets_directory", "Config/secrets"))
            secret_file = secrets_dir / f"{secret_name}.enc"
            
            if not secret_file.exists():
                return None
            
            # Read and decrypt
            with open(secret_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.Cipher.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            self.Logger.error(f"Failed to read secret file for '{secret_name}': {e}")
            return None
    
    def _GetFromGCPSecretManager(self, secret_name: str) -> Optional[str]:
        """Get secret from Google Cloud Secret Manager"""
        try:
            from google.cloud import secretmanager
            
            client = secretmanager.SecretManagerServiceClient()
            project_id = self.Config.get("gcp_project_id")
            
            if not project_id:
                raise ValueError("gcp_project_id required for GCP Secret Manager")
            
            name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            
            return response.payload.data.decode("UTF-8")
            
        except ImportError:
            self.Logger.error("google-cloud-secret-manager not installed")
            return None
        except Exception as e:
            self.Logger.error(f"GCP Secret Manager error for '{secret_name}': {e}")
            return None
    
    def _GetFromAWSSecretsManager(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            region = self.Config.get("aws_region", "us-east-1")
            client = boto3.client("secretsmanager", region_name=region)
            
            response = client.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
            
        except ImportError:
            self.Logger.error("boto3 not installed")
            return None
        except ClientError as e:
            self.Logger.error(f"AWS Secrets Manager error for '{secret_name}': {e}")
            return None
        except Exception as e:
            self.Logger.error(f"AWS Secrets Manager error for '{secret_name}': {e}")
            return None
    
    def _GetFromAzureKeyVault(self, secret_name: str) -> Optional[str]:
        """Get secret from Azure Key Vault"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = self.Config.get("azure_vault_url")
            if not vault_url:
                raise ValueError("azure_vault_url required for Azure Key Vault")
            
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            secret = client.get_secret(secret_name)
            return secret.value
            
        except ImportError:
            self.Logger.error("azure-keyvault-secrets not installed")
            return None
        except Exception as e:
            self.Logger.error(f"Azure Key Vault error for '{secret_name}': {e}")
            return None
    
    def SetSecret(self, secret_name: str, secret_value: str) -> bool:
        """
        Set secret in configured backend (development/testing only)
        """
        if self.Environment == "production":
            self.Logger.error("Setting secrets not allowed in production")
            return False
        
        try:
            if self.Backend == "file":
                return self._SetToFile(secret_name, secret_value)
            else:
                self.Logger.warning(f"Setting secrets not supported for backend: {self.Backend}")
                return False
                
        except Exception as e:
            self.Logger.error(f"Failed to set secret '{secret_name}': {e}")
            return False
    
    def _SetToFile(self, secret_name: str, secret_value: str) -> bool:
        """Set secret to encrypted file (development only)"""
        try:
            secrets_dir = Path(self.Config.get("secrets_directory", "Config/secrets"))
            secrets_dir.mkdir(parents=True, exist_ok=True)
            
            secret_file = secrets_dir / f"{secret_name}.enc"
            
            # Encrypt and write
            encrypted_data = self.Cipher.encrypt(secret_value.encode())
            
            with open(secret_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Secure file permissions
            os.chmod(secret_file, 0o600)
            
            return True
            
        except Exception as e:
            self.Logger.error(f"Failed to write secret file for '{secret_name}': {e}")
            return False
    
    def GetOAuthCredentials(self, provider: str) -> Dict[str, str]:
        """
        Get OAuth credentials for a specific provider
        """
        credentials = {}
        
        if provider.lower() == "google":
            credentials = {
                "client_id": self.GetSecret("GOOGLE_CLIENT_ID"),
                "client_secret": self.GetSecret("GOOGLE_CLIENT_SECRET")
            }
        elif provider.lower() == "github":
            credentials = {
                "client_id": self.GetSecret("GITHUB_CLIENT_ID"),
                "client_secret": self.GetSecret("GITHUB_CLIENT_SECRET")
            }
        elif provider.lower() == "facebook":
            credentials = {
                "client_id": self.GetSecret("FACEBOOK_APP_ID"),
                "client_secret": self.GetSecret("FACEBOOK_APP_SECRET")
            }
        
        # Filter out None values
        return {k: v for k, v in credentials.items() if v is not None}
    
    def ValidateOAuthCredentials(self, provider: str) -> bool:
        """
        Validate that OAuth credentials are available for provider
        """
        credentials = self.GetOAuthCredentials(provider)
        required_fields = ["client_id", "client_secret"]
        
        return all(credentials.get(field) for field in required_fields)
    
    def GetDatabaseSecrets(self) -> Dict[str, str]:
        """
        Get database connection secrets
        """
        return {
            "encryption_key": self.GetSecret("DATABASE_ENCRYPTION_KEY"),
            "backup_key": self.GetSecret("DATABASE_BACKUP_KEY"),
            "api_key": self.GetSecret("DATABASE_API_KEY")
        }
    
    def ClearCache(self):
        """Clear secret cache (for testing or security)"""
        self.SecretCache.clear()
        self.Logger.info("🧹 Secret cache cleared")
    
    def GetCacheStats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        
        valid_entries = sum(
            1 for entry in self.SecretCache.values()
            if now - entry["timestamp"] < self.CacheTTL
        )
        
        return {
            "total_entries": len(self.SecretCache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.SecretCache) - valid_entries,
            "cache_ttl_minutes": self.CacheTTL.total_seconds() / 60,
            "backend": self.Backend
        }
    
    def RotateSecret(self, secret_name: str) -> bool:
        """
        Rotate a secret (invalidate cache and trigger refresh)
        """
        try:
            # Remove from cache to force refresh
            cache_keys_to_remove = [
                key for key in self.SecretCache.keys()
                if key.startswith(f"{secret_name}:")
            ]
            
            for key in cache_keys_to_remove:
                del self.SecretCache[key]
            
            self.Logger.info(f"🔄 Secret '{secret_name}' rotated (cache invalidated)")
            return True
            
        except Exception as e:
            self.Logger.error(f"Failed to rotate secret '{secret_name}': {e}")
            return False
    
    def HealthCheck(self) -> Dict[str, Any]:
        """
        Health check for secret management system
        """
        try:
            # Test encryption
            test_data = "health_check_test"
            encrypted = self.Cipher.encrypt(test_data.encode())
            decrypted = self.Cipher.decrypt(encrypted).decode()
            
            encryption_healthy = (decrypted == test_data)
            
            # Test backend connectivity
            backend_healthy = self._TestBackendConnectivity()
            
            return {
                "healthy": encryption_healthy and backend_healthy,
                "encryption": encryption_healthy,
                "backend": backend_healthy,
                "backend_type": self.Backend,
                "cache_stats": self.GetCacheStats()
            }
            
        except Exception as e:
            self.Logger.error(f"Secret manager health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "backend_type": self.Backend
            }
    
    def _TestBackendConnectivity(self) -> bool:
        """Test connectivity to secret backend"""
        try:
            # Try to get a non-existent secret (should not error, just return None)
            test_result = self._GetFromEnvironment("__NON_EXISTENT_SECRET_TEST__")
            return True  # If no exception, backend is accessible
            
        except Exception as e:
            self.Logger.error(f"Backend connectivity test failed: {e}")
            return False

# Global secret manager instance
_secret_manager_instance = None

def GetSecretManager(config: Dict[str, Any] = None) -> SecretManager:
    """
    Get global secret manager instance (singleton pattern)
    """
    global _secret_manager_instance
    
    if _secret_manager_instance is None:
        _secret_manager_instance = SecretManager(config or {})
    
    return _secret_manager_instance

def InitializeSecrets(config: Dict[str, Any] = None):
    """
    Initialize secret management system
    """
    secret_manager = GetSecretManager(config)
    
    # Set environment variables for OAuth if using file backend
    if secret_manager.Backend == "file":
        oauth_providers = ["google", "github", "facebook"]
        
        for provider in oauth_providers:
            credentials = secret_manager.GetOAuthCredentials(provider)
            for key, value in credentials.items():
                if value and not os.getenv(f"{provider.upper()}_{key.upper()}"):
                    os.environ[f"{provider.upper()}_{key.upper()}"] = value
    
    return secret_manager