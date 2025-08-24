# File: GoogleDriveAPI.py
# Path: AndyGoogle/Source/API/GoogleDriveAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-12  07:30PM
"""
Description: Google Drive API integration for AndyGoogle library management
Handles SQLite database download, upload, and version management with Google Drive
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io

class GoogleDriveAPI:
    """Handle Google Drive operations for AndyGoogle library management"""
    
    def __init__(self, credentials_path: str, token_path: str = None):
        self.credentials_path = credentials_path
        self.token_path = token_path or "AndyGoogle/Config/google_token.json"
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        self.andylibrary_folder_id = None
        
    def Authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            except Exception as e:
                print(f"Error loading existing credentials: {e}")
        
        # If no valid credentials, request authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                
                # Run OAuth flow
                flow = Flow.from_client_secrets_file(self.credentials_path, self.scopes)
                flow.redirect_uri = 'http://localhost:8080/callback'
                
                # Get authorization URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"Please visit this URL to authorize the application: {auth_url}")
                
                # Get authorization code from user
                auth_code = input("Enter the authorization code: ")
                
                # Exchange code for credentials
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
        
        # Save credentials for future use
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
        with open(self.token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        
        # Build Drive service
        self.service = build('drive', 'v3', credentials=creds)
        return True
    
    def GetOrCreateAndyLibraryFolder(self) -> str:
        """Get or create the AndyLibrary folder on Google Drive"""
        if self.andylibrary_folder_id:
            return self.andylibrary_folder_id
        
        try:
            # Search for existing AndyLibrary folder
            query = "name='AndyLibrary' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            folders = results.get('files', [])
            
            if folders:
                self.andylibrary_folder_id = folders[0]['id']
                print(f"Found existing AndyLibrary folder: {self.andylibrary_folder_id}")
            else:
                # Create new folder
                folder_metadata = {
                    'name': 'AndyLibrary',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=folder_metadata, fields='id').execute()
                self.andylibrary_folder_id = folder.get('id')
                print(f"Created AndyLibrary folder: {self.andylibrary_folder_id}")
            
            return self.andylibrary_folder_id
            
        except HttpError as e:
            print(f"Error managing AndyLibrary folder: {e}")
            return None
    
    def UploadDatabase(self, local_db_path: str, version_info: Dict[str, Any]) -> Optional[str]:
        """Upload SQLite database to Google Drive"""
        if not self.service:
            if not self.Authenticate():
                return None
        
        folder_id = self.GetOrCreateAndyLibraryFolder()
        if not folder_id:
            return None
        
        try:
            # Generate filename with version
            version = version_info.get('version', '1.0.0')
            filename = f"AndersonLibrary_v{version.replace('.', '_')}.db"
            
            # Check if file already exists
            query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            existing_files = results.get('files', [])
            
            if existing_files:
                # Update existing file
                file_id = existing_files[0]['id']
                media = MediaFileUpload(local_db_path, mimetype='application/x-sqlite3')
                updated_file = self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    fields='id,name,size,modifiedTime'
                ).execute()
                print(f"Updated database: {updated_file.get('name')}")
                return file_id
            else:
                # Create new file
                file_metadata = {
                    'name': filename,
                    'parents': [folder_id],
                    'description': f"AndyGoogle SQLite Database v{version} - {version_info.get('description', '')}"
                }
                
                media = MediaFileUpload(local_db_path, mimetype='application/x-sqlite3')
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,modifiedTime'
                ).execute()
                
                print(f"Uploaded database: {file.get('name')} ({file.get('size')} bytes)")
                return file.get('id')
                
        except HttpError as e:
            print(f"Error uploading database: {e}")
            return None
    
    def DownloadDatabase(self, file_id: str, local_path: str) -> bool:
        """Download SQLite database from Google Drive"""
        if not self.service:
            if not self.Authenticate():
                return False
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id, fields='name,size').execute()
            print(f"Downloading: {file_metadata.get('name')} ({file_metadata.get('size')} bytes)")
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download progress: {int(status.progress() * 100)}%")
            
            # Write to local file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            
            print(f"Database downloaded successfully: {local_path}")
            return True
            
        except HttpError as e:
            print(f"Error downloading database: {e}")
            return False
    
    def GetLatestDatabaseVersion(self) -> Optional[Dict[str, Any]]:
        """Get information about the latest database version"""
        if not self.service:
            if not self.Authenticate():
                return None
        
        folder_id = self.GetOrCreateAndyLibraryFolder()
        if not folder_id:
            return None
        
        try:
            # Search for database files in AndyLibrary folder
            query = f"'{folder_id}' in parents and name contains 'AndersonLibrary_v' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id,name,size,modifiedTime,description)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            latest_file = files[0]
            
            # Extract version from filename
            filename = latest_file['name']
            try:
                version_part = filename.split('_v')[1].split('.db')[0]
                version = version_part.replace('_', '.')
            except (IndexError, ValueError):
                version = "unknown"
            
            return {
                'file_id': latest_file['id'],
                'filename': filename,
                'version': version,
                'size_bytes': int(latest_file.get('size', 0)),
                'modified_time': latest_file['modifiedTime'],
                'description': latest_file.get('description', ''),
                'download_url': f"https://drive.google.com/file/d/{latest_file['id']}/view"
            }
            
        except HttpError as e:
            print(f"Error getting latest database version: {e}")
            return None
    
    def ListDatabaseVersions(self) -> List[Dict[str, Any]]:
        """List all database versions available on Google Drive"""
        if not self.service:
            if not self.Authenticate():
                return []
        
        folder_id = self.GetOrCreateAndyLibraryFolder()
        if not folder_id:
            return []
        
        try:
            # Search for all database files
            query = f"'{folder_id}' in parents and name contains 'AndersonLibrary_v' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id,name,size,modifiedTime,description)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            versions = []
            
            for file in files:
                filename = file['name']
                try:
                    version_part = filename.split('_v')[1].split('.db')[0]
                    version = version_part.replace('_', '.')
                except (IndexError, ValueError):
                    version = "unknown"
                
                versions.append({
                    'file_id': file['id'],
                    'filename': filename,
                    'version': version,
                    'size_bytes': int(file.get('size', 0)),
                    'modified_time': file['modifiedTime'],
                    'description': file.get('description', ''),
                    'download_url': f"https://drive.google.com/file/d/{file['id']}/view"
                })
            
            return versions
            
        except HttpError as e:
            print(f"Error listing database versions: {e}")
            return []
    
    def CalculateFileHash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file for integrity checking"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return ""
    
    def ValidateDatabaseIntegrity(self, local_path: str) -> bool:
        """Validate downloaded SQLite database integrity"""
        if not os.path.exists(local_path):
            return False
        
        try:
            import sqlite3
            # Try to open and query the database
            conn = sqlite3.connect(local_path)
            cursor = conn.cursor()
            
            # Basic integrity checks
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] == 'ok':
                # Check for required tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['books', 'categories', 'subjects']
                missing_tables = [table for table in required_tables if table not in tables]
                
                conn.close()
                
                if missing_tables:
                    print(f"Database missing required tables: {missing_tables}")
                    return False
                
                return True
            else:
                conn.close()
                print(f"Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            print(f"Error validating database: {e}")
            return False
    
    def GetDriveUsageInfo(self) -> Optional[Dict[str, Any]]:
        """Get Google Drive storage usage information"""
        if not self.service:
            if not self.Authenticate():
                return None
        
        try:
            about = self.service.about().get(fields='storageQuota,user').execute()
            quota = about.get('storageQuota', {})
            user = about.get('user', {})
            
            return {
                'user_email': user.get('emailAddress'),
                'user_name': user.get('displayName'),
                'total_bytes': int(quota.get('limit', 0)),
                'used_bytes': int(quota.get('usage', 0)),
                'available_bytes': int(quota.get('limit', 0)) - int(quota.get('usage', 0)),
                'usage_percentage': (int(quota.get('usage', 0)) / int(quota.get('limit', 1))) * 100
            }
            
        except HttpError as e:
            print(f"Error getting drive usage info: {e}")
            return None

def main():
    """Test Google Drive API functionality"""
    print("🚀 Google Drive API Test")
    print("=" * 40)
    
    # Test with your existing credentials
    credentials_path = "AndyGoogle/Config/google_credentials.json"
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please download your Google API credentials and save them to this path.")
        return
    
    api = GoogleDriveAPI(credentials_path)
    
    try:
        # Test authentication
        print("🔐 Testing authentication...")
        if api.Authenticate():
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
        
        # Test folder creation/access
        print("📁 Testing folder access...")
        folder_id = api.GetOrCreateAndyLibraryFolder()
        if folder_id:
            print(f"✅ AndyLibrary folder: {folder_id}")
        else:
            print("❌ Failed to access AndyLibrary folder")
            return
        
        # Test getting latest version
        print("📋 Testing version listing...")
        latest = api.GetLatestDatabaseVersion()
        if latest:
            print(f"✅ Latest version: {latest['version']} ({latest['size_bytes']} bytes)")
        else:
            print("ℹ️ No database versions found (this is normal for first run)")
        
        # Test drive usage
        print("💾 Testing drive usage info...")
        usage = api.GetDriveUsageInfo()
        if usage:
            print(f"✅ Drive usage: {usage['usage_percentage']:.1f}% ({usage['user_email']})")
        else:
            print("❌ Failed to get drive usage info")
        
        print("\n🎉 Google Drive API test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()