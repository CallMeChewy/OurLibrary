# File: EnvironmentConfig.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Utils/EnvironmentConfig.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 08:38PM

"""
Environment Configuration Manager for PROJECT HIMALAYA
Handles secure credential loading from environment variables with fallbacks
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

class EnvironmentConfig:
    """Secure environment configuration management"""
    
    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize environment config with optional .env file"""
        self.env_file_path = env_file_path or ".env"
        self.config = {}
        self.LoadEnvironmentVariables()
    
    def LoadEnvironmentVariables(self):
        """Load environment variables from .env file if it exists"""
        try:
            # Try to load python-dotenv if available
            try:
                from dotenv import load_dotenv
                if os.path.exists(self.env_file_path):
                    load_dotenv(self.env_file_path)
                    print(f"✅ Loaded environment from {self.env_file_path}")
                else:
                    print(f"⚠️ No .env file found at {self.env_file_path} - using system environment")
            except ImportError:
                # Manual .env parsing if python-dotenv not available
                if os.path.exists(self.env_file_path):
                    self.ParseDotEnvFile()
                    print(f"✅ Loaded environment from {self.env_file_path} (manual parsing)")
        except Exception as e:
            print(f"⚠️ Error loading environment variables: {e}")
    
    def ParseDotEnvFile(self):
        """Manually parse .env file (fallback when python-dotenv not available)"""
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        os.environ[key.strip()] = value
        except Exception as e:
            print(f"⚠️ Error parsing .env file: {e}")
    
    def GetGoogleCredentials(self) -> Dict[str, str]:
        """Get Google OAuth credentials from environment"""
        credentials = {
            'client_id': self.Get('GOOGLE_CLIENT_ID'),
            'client_secret': self.Get('GOOGLE_CLIENT_SECRET'),
            'api_key': self.Get('GOOGLE_API_KEY'),
            'project_id': self.Get('GOOGLE_PROJECT_ID', 'andygoogle-project'),
        }
        
        # Validate required credentials
        missing = [k for k, v in credentials.items() if not v or v.startswith('YOUR_')]
        if missing:
            print(f"⚠️ Missing Google credentials: {missing}")
            print("   Please set environment variables or update .env file")
        
        return credentials
    
    def GetStudentProtectionConfig(self) -> Dict[str, Any]:
        """Get student protection settings"""
        return {
            'default_region': self.Get('DEFAULT_STUDENT_REGION', 'developing'),
            'monthly_budget': float(self.Get('MONTHLY_BUDGET_USD', '5.00')),
            'cost_per_mb': {
                'developing': float(self.Get('COST_PER_MB_DEVELOPING', '0.10')),
                'emerging': float(self.Get('COST_PER_MB_EMERGING', '0.05')),
                'developed': float(self.Get('COST_PER_MB_DEVELOPED', '0.02'))
            }
        }
    
    def GetServerConfig(self) -> Dict[str, Any]:
        """Get server configuration"""
        return {
            'host': self.Get('DEFAULT_HOST', '127.0.0.1'),
            'port': int(self.Get('DEFAULT_PORT', '8081')),
            'debug': self.Get('DEBUG', 'false').lower() == 'true',
            'environment': self.Get('ENVIRONMENT', 'development'),
            'secret_key': self.Get('APP_SECRET_KEY', 'dev-secret-key-change-in-production')
        }
    
    def GetDatabaseConfig(self) -> Dict[str, str]:
        """Get database configuration"""
        return {
            'url': self.Get('DATABASE_URL', 'sqlite:///Data/Databases/MyLibrary.db'),
            'backup_enabled': self.Get('DATABASE_BACKUP_ENABLED', 'true').lower() == 'true'
        }
    
    def GetSecurityConfig(self) -> Dict[str, Any]:
        """Get security settings"""
        cors_origins = self.Get('CORS_ORIGINS', 'http://localhost:8081,http://127.0.0.1:8081')
        allowed_hosts = self.Get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
        
        return {
            'cors_origins': [origin.strip() for origin in cors_origins.split(',')],
            'allowed_hosts': [host.strip() for host in allowed_hosts.split(',')],
            'rate_limit_per_minute': int(self.Get('RATE_LIMIT_PER_MINUTE', '60'))
        }
    
    def GetGoogleDriveConfig(self) -> Dict[str, Any]:
        """Get Google Drive specific settings"""
        scopes = self.Get('GOOGLE_SCOPES', 
                         'https://www.googleapis.com/auth/drive.readonly,'
                         'https://www.googleapis.com/auth/drive.metadata.readonly')
        
        return {
            'library_folder_name': self.Get('LIBRARY_FOLDER_NAME', 'AndyLibrary'),
            'scopes': [scope.strip() for scope in scopes.split(',')],
            'credentials_path': 'Config/google_credentials.json',
            'token_path': 'Config/google_token.json'
        }
    
    def Get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default"""
        value = os.environ.get(key, default)
        
        # Don't return placeholder values
        if value and value.startswith('YOUR_'):
            return default
        
        return value
    
    def IsProduction(self) -> bool:
        """Check if running in production environment"""
        return self.Get('ENVIRONMENT', 'development').lower() == 'production'
    
    def IsDebugMode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.Get('DEBUG', 'false').lower() == 'true'
    
    def ValidateConfiguration(self) -> Dict[str, Any]:
        """Validate current configuration and return status"""
        validation = {
            'google_credentials': False,
            'server_config': True,
            'database_config': True,
            'student_protection': True,
            'warnings': [],
            'errors': []
        }
        
        # Validate Google credentials
        creds = self.GetGoogleCredentials()
        if all(v and not v.startswith('YOUR_') for v in creds.values()):
            validation['google_credentials'] = True
        else:
            validation['warnings'].append('Google credentials not fully configured')
        
        # Validate production settings
        if self.IsProduction():
            secret_key = self.Get('APP_SECRET_KEY')
            if not secret_key or secret_key == 'dev-secret-key-change-in-production':
                validation['errors'].append('Production requires secure APP_SECRET_KEY')
        
        # Validate database path
        db_config = self.GetDatabaseConfig()
        if 'sqlite:///' in db_config['url']:
            db_path = db_config['url'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                validation['warnings'].append(f'Database file not found: {db_path}')
        
        return validation

# Global instance for easy access
config = EnvironmentConfig()

# Convenience functions
def GetGoogleCredentials() -> Dict[str, str]:
    """Get Google credentials from environment"""
    return config.GetGoogleCredentials()

def GetStudentProtectionConfig() -> Dict[str, Any]:
    """Get student protection configuration"""
    return config.GetStudentProtectionConfig()

def GetServerConfig() -> Dict[str, Any]:
    """Get server configuration"""
    return config.GetServerConfig()

def IsProduction() -> bool:
    """Check if running in production"""
    return config.IsProduction()

def ValidateConfiguration() -> Dict[str, Any]:
    """Validate current configuration"""
    return config.ValidateConfiguration()