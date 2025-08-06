# File: StudentGoogleDriveAPI.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/StudentGoogleDriveAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 01:24PM

"""
Student-Focused Google Drive API
Handles book downloads with chunking, cost protection, and student-friendly experience
"""

import os
import sys
import io
import json
import time
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Google Drive imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")

# Import our student systems
from Core.ChunkedDownloader import ChunkedDownloader, DownloadProgress, NetworkCondition
from Core.StudentBookDownloader import StudentBookDownloader

@dataclass
class GoogleDriveBookInfo:
    """Information about a book stored in Google Drive"""
    file_id: str
    name: str
    size_bytes: int
    mime_type: str
    download_url: str
    parent_folders: List[str]

class StudentGoogleDriveAPI:
    """Student-focused Google Drive API with cost protection and chunked downloads"""
    
    def __init__(self, credentials_path: str = "Config/google_credentials.json"):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries not installed")
        
        self.credentials_path = credentials_path
        self.token_path = "Config/google_token.json"
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        
        # Initialize student-focused components
        self.cost_calculator = StudentBookDownloader()
        self.chunked_downloader = ChunkedDownloader()
        
        # Book library folder - configure this for your Google Drive
        self.library_folder_name = "AndyLibrary"  # Adjust as needed
        self.library_folder_id = None
        
        # Cache for file metadata
        self.file_cache = {}
    
    def Authenticate(self) -> bool:
        """Authenticate with Google Drive using student-friendly flow"""
        print("🔐 Authenticating with Google Drive...")
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                print("✅ Found existing credentials")
            except Exception as e:
                print(f"⚠️ Error loading existing credentials: {e}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 Refreshing expired credentials...")
                    creds.refresh(Request())
                    print("✅ Credentials refreshed successfully")
                except Exception as e:
                    print(f"❌ Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                print("🌐 Starting OAuth flow for new authentication...")
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Credentials file not found: {self.credentials_path}")
                    print("   Please download credentials from Google Cloud Console")
                    return False
                
                try:
                    # Run OAuth flow
                    flow = Flow.from_client_secrets_file(self.credentials_path, self.scopes)
                    flow.redirect_uri = 'http://localhost:8080'
                    
                    # Get authorization URL
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"\n📱 Please visit this URL to authorize the application:")
                    print(f"   {auth_url}")
                    print("\n   1. Open the URL in your browser")
                    print("   2. Sign in to your Google account")
                    print("   3. Grant permission to access Google Drive")
                    print("   4. Copy the authorization code\n")
                    
                    # Get authorization code from user
                    auth_code = input("Enter the authorization code: ").strip()
                    
                    if not auth_code:
                        print("❌ No authorization code provided")
                        return False
                    
                    # Exchange code for credentials
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    print("✅ Authorization successful!")
                    
                except Exception as e:
                    print(f"❌ OAuth flow error: {e}")
                    return False
        
        # Save credentials for future use
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token_file:
                token_file.write(creds.to_json())
            print("✅ Credentials saved for future use")
        except Exception as e:
            print(f"⚠️ Warning: Could not save credentials: {e}")
        
        # Build the service
        try:
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive service initialized")
            return True
        except Exception as e:
            print(f"❌ Error building Drive service: {e}")
            return False
    
    def FindLibraryFolder(self) -> Optional[str]:
        """Find the AndyLibrary folder in Google Drive"""
        if not self.service:
            print("❌ Not authenticated with Google Drive")
            return None
        
        try:
            print(f"🔍 Searching for '{self.library_folder_name}' folder...")
            
            # Search for the library folder
            query = f"name='{self.library_folder_name}' and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query, spaces='drive').execute()
            
            folders = results.get('files', [])
            
            if not folders:
                print(f"❌ Library folder '{self.library_folder_name}' not found")
                print("   Please create this folder in your Google Drive and upload books to it")
                return None
            
            self.library_folder_id = folders[0]['id']
            print(f"✅ Found library folder: {self.library_folder_id}")
            return self.library_folder_id
            
        except Exception as e:
            print(f"❌ Error finding library folder: {e}")
            return None
    
    def GetBookFileInfo(self, book_title: str) -> Optional[GoogleDriveBookInfo]:
        """Get file information for a book from Google Drive"""
        if not self.service:
            return None
        
        if not self.library_folder_id:
            if not self.FindLibraryFolder():
                return None
        
        try:
            # Search for the book file in the library folder
            # Try multiple extensions
            extensions = ['.pdf', '.epub', '.mobi', '.txt', '.doc', '.docx']
            
            for ext in extensions:
                search_name = f"{book_title}{ext}"
                query = f"name='{search_name}' and parents in '{self.library_folder_id}'"
                
                results = self.service.files().list(
                    q=query, 
                    fields='files(id,name,size,mimeType,parents)',
                    spaces='drive'
                ).execute()
                
                files = results.get('files', [])
                if files:
                    file_info = files[0]
                    
                    # Get download URL (this is simplified - real implementation needs proper handling)
                    download_url = f"https://drive.google.com/uc?id={file_info['id']}&export=download"
                    
                    return GoogleDriveBookInfo(
                        file_id=file_info['id'],
                        name=file_info['name'],
                        size_bytes=int(file_info.get('size', 0)),
                        mime_type=file_info.get('mimeType', ''),
                        download_url=download_url,
                        parent_folders=file_info.get('parents', [])
                    )
            
            print(f"⚠️ Book file not found in Google Drive: {book_title}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting book file info: {e}")
            return None
    
    def DownloadBookWithStudentProtection(
        self,
        book_id: int,
        book_title: str,
        progress_callback: Callable[[DownloadProgress], None] = None,
        region: str = "developing"
    ) -> Dict[str, Any]:
        """Download a book with full student cost protection and chunked download"""
        
        print(f"📚 Starting protected download for: {book_title}")
        
        # Step 1: Get file info from Google Drive
        file_info = self.GetBookFileInfo(book_title)
        if not file_info:
            return {
                'success': False,
                'error': f'Book file not found in Google Drive: {book_title}',
                'recommendation': 'Check that the book exists in your Google Drive library folder'
            }
        
        print(f"✅ Found book file: {file_info.name} ({file_info.size_bytes / (1024*1024):.1f}MB)")
        
        # Step 2: Get cost estimate and student guidance
        cost_info = self.cost_calculator.GetBookCostEstimate(book_id)
        if cost_info:
            # Update with real file size from Google Drive
            real_size_mb = file_info.size_bytes / (1024 * 1024)
            real_cost = real_size_mb * 0.10  # $0.10/MB for developing region
            
            print(f"💰 Real cost estimate: ${real_cost:.2f} for {real_size_mb:.1f}MB")
            
            if real_cost > 3.0:  # High cost warning
                return {
                    'success': False,
                    'cost_warning': True,
                    'estimated_cost': real_cost,
                    'file_size_mb': real_size_mb,
                    'warning_level': 'extreme',
                    'recommendation': 'This book is very expensive for mobile download. Consider waiting for WiFi.',
                    'alternatives': [
                        'Wait for WiFi connection (Free)',
                        'Download a smaller book instead',
                        'Read book description only'
                    ]
                }
        
        # Step 3: Start chunked download
        try:
            # Detect optimal network condition
            network_condition = self._DetectNetworkCondition()
            
            # Start the download
            download_result = self.chunked_downloader.StartChunkedDownload(
                book_id=book_id,
                title=book_title,
                file_size_bytes=file_info.size_bytes,
                download_url=file_info.download_url,
                progress_callback=progress_callback,
                network_condition=network_condition
            )
            
            return {
                'success': True,
                'message': download_result,
                'file_size_mb': file_info.size_bytes / (1024 * 1024),
                'estimated_cost': real_cost if 'real_cost' in locals() else 0.0,
                'network_condition': network_condition.value,
                'download_id': book_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed: {str(e)}',
                'recommendation': 'Check your internet connection and try again'
            }
    
    def _DetectNetworkCondition(self) -> NetworkCondition:
        """Detect current network condition for optimal chunking"""
        # Simple detection - in real implementation, test actual speed
        # For now, assume slow connection for student protection
        return NetworkCondition.SLOW_3G
    
    def GetLibraryStats(self) -> Dict[str, Any]:
        """Get statistics about the Google Drive library"""
        if not self.service or not self.library_folder_id:
            return {'error': 'Not connected to Google Drive'}
        
        try:
            # Get all files in library folder
            query = f"parents in '{self.library_folder_id}'"
            results = self.service.files().list(
                q=query,
                fields='files(id,name,size,mimeType)',
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            
            total_files = len(files)
            total_size_bytes = sum(int(f.get('size', 0)) for f in files if f.get('size'))
            total_size_mb = total_size_bytes / (1024 * 1024)
            
            # Count by file type
            file_types = {}
            for file in files:
                mime_type = file.get('mimeType', 'unknown')
                file_types[mime_type] = file_types.get(mime_type, 0) + 1
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size_mb, 1),
                'total_size_gb': round(total_size_mb / 1024, 2),
                'file_types': file_types,
                'average_file_size_mb': round(total_size_mb / total_files, 1) if total_files > 0 else 0,
                'library_folder_id': self.library_folder_id
            }
            
        except Exception as e:
            return {'error': f'Failed to get library stats: {str(e)}'}

# Test the Google Drive integration
if __name__ == "__main__":
    print("🧪 Testing Student Google Drive API")
    
    # Initialize the API
    student_gdrive = StudentGoogleDriveAPI()
    
    # Test authentication
    if student_gdrive.Authenticate():
        print("✅ Authentication successful")
        
        # Find library folder
        if student_gdrive.FindLibraryFolder():
            print("✅ Library folder found")
            
            # Get library stats
            stats = student_gdrive.GetLibraryStats()
            if 'error' not in stats:
                print(f"📊 Library Stats:")
                print(f"   Total files: {stats['total_files']}")
                print(f"   Total size: {stats['total_size_mb']:.1f}MB ({stats['total_size_gb']:.2f}GB)")
                print(f"   Average file size: {stats['average_file_size_mb']:.1f}MB")
            else:
                print(f"❌ Stats error: {stats['error']}")
        else:
            print("❌ Library folder not found")
    else:
        print("❌ Authentication failed")