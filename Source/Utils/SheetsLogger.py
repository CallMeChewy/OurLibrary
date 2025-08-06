# File: SheetsLogger.py
# Path: OurLibrary/Source/Utils/SheetsLogger.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-12  07:32PM
"""
Description: Google Sheets logging integration for OurLibrary usage analytics
Handles batch upload of user interactions and system events to Google Sheets
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsLogger:
    """Handle Google Sheets logging for OurLibrary usage analytics"""
    
    def __init__(self, credentials_path: str, token_path: str = None):
        self.credentials_path = credentials_path
        self.token_path = token_path or "OurLibrary/Config/google_token.json"
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.usage_sheet_id = None
        self.local_log_path = "OurLibrary/Data/Logs/usage_log.json"
        self.session_log_path = "OurLibrary/Data/Logs/session_log.json"
        
        # Ensure log directories exist
        os.makedirs(os.path.dirname(self.local_log_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.session_log_path), exist_ok=True)
    
    def Authenticate(self) -> bool:
        """Authenticate with Google Sheets API (reuse Drive credentials)"""
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
                
                # Run OAuth flow (this will share the token with GoogleDriveAPI)
                flow = Flow.from_client_secrets_file(self.credentials_path, self.scopes)
                flow.redirect_uri = 'http://localhost:8080/callback'
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"Please visit this URL to authorize the application: {auth_url}")
                
                auth_code = input("Enter the authorization code: ")
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
        
        # Save credentials
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
        with open(self.token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        
        # Build Sheets service
        self.service = build('sheets', 'v4', credentials=creds)
        return True
    
    def GetOrCreateUsageSheet(self) -> Optional[str]:
        """Get or create the OurLibrary Usage Log spreadsheet"""
        if self.usage_sheet_id:
            return self.usage_sheet_id
        
        if not self.service:
            if not self.Authenticate():
                return None
        
        try:
            # Create new spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': 'OurLibrary Usage Analytics',
                    'locale': 'en_US',
                    'timeZone': 'America/New_York'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Usage Log',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Session Log',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 8
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Error Log',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 6
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet_body).execute()
            self.usage_sheet_id = spreadsheet.get('spreadsheetId')
            
            print(f"Created usage analytics spreadsheet: {self.usage_sheet_id}")
            
            # Set up headers
            self.SetupSheetHeaders()
            
            return self.usage_sheet_id
            
        except HttpError as e:
            print(f"Error creating usage spreadsheet: {e}")
            return None
    
    def SetupSheetHeaders(self):
        """Set up column headers for all sheets"""
        if not self.service or not self.usage_sheet_id:
            return
        
        try:
            # Usage Log headers
            usage_headers = [
                ['Timestamp', 'SessionID', 'UserEmail', 'Action', 'BookID', 'BookTitle', 'ActionDetails', 'ClientIP', 'UserAgent', 'Duration']
            ]
            
            # Session Log headers
            session_headers = [
                ['SessionStart', 'SessionEnd', 'UserEmail', 'TotalActions', 'BooksViewed', 'SearchesPerformed', 'Duration', 'ClientInfo']
            ]
            
            # Error Log headers
            error_headers = [
                ['Timestamp', 'ErrorType', 'ErrorMessage', 'UserEmail', 'Context', 'Severity']
            ]
            
            # Batch update all headers
            requests = [
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 0,  # Usage Log sheet
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 10
                        },
                        'rows': [
                            {
                                'values': [
                                    {'userEnteredValue': {'stringValue': header}} for header in usage_headers[0]
                                ]
                            }
                        ],
                        'fields': 'userEnteredValue'
                    }
                },
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 1,  # Session Log sheet
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 8
                        },
                        'rows': [
                            {
                                'values': [
                                    {'userEnteredValue': {'stringValue': header}} for header in session_headers[0]
                                ]
                            }
                        ],
                        'fields': 'userEnteredValue'
                    }
                },
                {
                    'updateCells': {
                        'range': {
                            'sheetId': 2,  # Error Log sheet
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 6
                        },
                        'rows': [
                            {
                                'values': [
                                    {'userEnteredValue': {'stringValue': header}} for header in error_headers[0]
                                ]
                            }
                        ],
                        'fields': 'userEnteredValue'
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.usage_sheet_id,
                body={'requests': requests}
            ).execute()
            
            print("✅ Sheet headers configured successfully")
            
        except HttpError as e:
            print(f"Error setting up sheet headers: {e}")
    
    def LogUsage(self, action: str, book_id: int = None, book_title: str = None, 
                 action_details: str = None, user_email: str = None, 
                 session_id: str = None, client_ip: str = None, 
                 user_agent: str = None, duration: float = None):
        """Log a user action locally (for batch upload later)"""
        usage_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id or f"session_{int(time.time())}",
            'user_email': user_email or 'anonymous',
            'action': action,
            'book_id': book_id,
            'book_title': book_title or '',
            'action_details': action_details or '',
            'client_ip': client_ip or '',
            'user_agent': user_agent or '',
            'duration': duration or 0.0
        }
        
        # Append to local log file
        self.AppendToLocalLog(self.local_log_path, usage_entry)
        
        # Auto-upload if we have many pending entries
        pending_count = self.GetPendingLogCount()
        if pending_count >= 50:  # Batch upload every 50 entries
            self.BatchUploadLogs()
    
    def LogSession(self, session_start: datetime, session_end: datetime = None, 
                   user_email: str = None, total_actions: int = 0, 
                   books_viewed: int = 0, searches_performed: int = 0, 
                   client_info: str = None):
        """Log a user session locally"""
        if session_end is None:
            session_end = datetime.now()
        
        duration = (session_end - session_start).total_seconds()
        
        session_entry = {
            'session_start': session_start.isoformat(),
            'session_end': session_end.isoformat(),
            'user_email': user_email or 'anonymous',
            'total_actions': total_actions,
            'books_viewed': books_viewed,
            'searches_performed': searches_performed,
            'duration': duration,
            'client_info': client_info or ''
        }
        
        # Append to session log file
        self.AppendToLocalLog(self.session_log_path, session_entry)
    
    def LogError(self, error_type: str, error_message: str, user_email: str = None, 
                 context: str = None, severity: str = 'ERROR'):
        """Log an error event locally"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'user_email': user_email or 'system',
            'context': context or '',
            'severity': severity,
            'uploaded': False
        }
        
        # Store in a separate error log for immediate upload if severe
        error_log_path = "OurLibrary/Data/Logs/error_log.json"
        self.AppendToLocalLog(error_log_path, error_entry)
        
        # Upload immediately for critical errors
        if severity in ['CRITICAL', 'FATAL']:
            self.UploadErrorLogs()
    
    def AppendToLocalLog(self, log_path: str, entry: Dict[str, Any]):
        """Append an entry to a local JSON log file"""
        try:
            # Load existing log
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'entries': []}
            
            # Add new entry
            entry['uploaded'] = False
            log_data['entries'].append(entry)
            
            # Keep only last 1000 entries to prevent file bloat
            if len(log_data['entries']) > 1000:
                log_data['entries'] = log_data['entries'][-1000:]
            
            # Save back to file
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Error appending to local log {log_path}: {e}")
    
    def GetPendingLogCount(self) -> int:
        """Get count of pending (not uploaded) log entries"""
        try:
            if not os.path.exists(self.local_log_path):
                return 0
            
            with open(self.local_log_path, 'r') as f:
                log_data = json.load(f)
            
            pending_entries = [entry for entry in log_data.get('entries', []) if not entry.get('uploaded', False)]
            return len(pending_entries)
            
        except Exception as e:
            print(f"Error getting pending log count: {e}")
            return 0
    
    def BatchUploadLogs(self) -> bool:
        """Upload all pending log entries to Google Sheets"""
        if not self.service:
            if not self.Authenticate():
                return False
        
        sheet_id = self.GetOrCreateUsageSheet()
        if not sheet_id:
            return False
        
        try:
            # Upload usage logs
            success = self.UploadLogFile(self.local_log_path, 'Usage Log')
            if success:
                print("✅ Usage logs uploaded successfully")
            
            # Upload session logs
            success = self.UploadLogFile(self.session_log_path, 'Session Log')
            if success:
                print("✅ Session logs uploaded successfully")
            
            # Upload error logs
            success = self.UploadErrorLogs()
            if success:
                print("✅ Error logs uploaded successfully")
            
            return True
            
        except Exception as e:
            print(f"Error during batch upload: {e}")
            return False
    
    def UploadLogFile(self, log_path: str, sheet_name: str) -> bool:
        """Upload a specific log file to a sheet"""
        if not os.path.exists(log_path):
            return True  # No file to upload
        
        try:
            with open(log_path, 'r') as f:
                log_data = json.load(f)
            
            # Get pending entries
            pending_entries = [entry for entry in log_data.get('entries', []) if not entry.get('uploaded', False)]
            
            if not pending_entries:
                return True  # Nothing to upload
            
            # Convert entries to rows
            rows = []
            for entry in pending_entries:
                if sheet_name == 'Usage Log':
                    row = [
                        entry.get('timestamp', ''),
                        entry.get('session_id', ''),
                        entry.get('user_email', ''),
                        entry.get('action', ''),
                        str(entry.get('book_id', '')),
                        entry.get('book_title', ''),
                        entry.get('action_details', ''),
                        entry.get('client_ip', ''),
                        entry.get('user_agent', ''),
                        str(entry.get('duration', ''))
                    ]
                elif sheet_name == 'Session Log':
                    row = [
                        entry.get('session_start', ''),
                        entry.get('session_end', ''),
                        entry.get('user_email', ''),
                        str(entry.get('total_actions', '')),
                        str(entry.get('books_viewed', '')),
                        str(entry.get('searches_performed', '')),
                        str(entry.get('duration', '')),
                        entry.get('client_info', '')
                    ]
                else:
                    continue
                
                rows.append(row)
            
            if rows:
                # Append to sheet
                range_name = f"{sheet_name}!A:Z"
                body = {
                    'values': rows
                }
                
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.usage_sheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                # Mark entries as uploaded
                for entry in log_data.get('entries', []):
                    if not entry.get('uploaded', False):
                        entry['uploaded'] = True
                
                # Save updated log file
                with open(log_path, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                print(f"Uploaded {len(rows)} entries to {sheet_name}")
            
            return True
            
        except HttpError as e:
            print(f"Error uploading to {sheet_name}: {e}")
            return False
    
    def UploadErrorLogs(self) -> bool:
        """Upload error logs to Error Log sheet"""
        error_log_path = "OurLibrary/Data/Logs/error_log.json"
        return self.UploadLogFile(error_log_path, 'Error Log')
    
    def GetAnalyticsSummary(self, days: int = 7) -> Optional[Dict[str, Any]]:
        """Get usage analytics summary from local logs"""
        try:
            if not os.path.exists(self.local_log_path):
                return None
            
            with open(self.local_log_path, 'r') as f:
                log_data = json.load(f)
            
            # Filter entries from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_entries = []
            
            for entry in log_data.get('entries', []):
                try:
                    entry_date = datetime.fromisoformat(entry['timestamp'])
                    if entry_date >= cutoff_date:
                        recent_entries.append(entry)
                except (ValueError, KeyError):
                    continue
            
            # Calculate summary
            total_actions = len(recent_entries)
            unique_sessions = len(set(entry.get('session_id') for entry in recent_entries))
            unique_users = len(set(entry.get('user_email') for entry in recent_entries))
            books_accessed = len(set(entry.get('book_id') for entry in recent_entries if entry.get('book_id')))
            
            action_counts = {}
            for entry in recent_entries:
                action = entry.get('action', 'unknown')
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                'period_days': days,
                'total_actions': total_actions,
                'unique_sessions': unique_sessions,
                'unique_users': unique_users,
                'books_accessed': books_accessed,
                'action_breakdown': action_counts,
                'average_actions_per_session': total_actions / unique_sessions if unique_sessions > 0 else 0
            }
            
        except Exception as e:
            print(f"Error generating analytics summary: {e}")
            return None
    
    def LogVersionCheck(self, client_ip: str = None, user_agent: str = None, 
                       current_version: str = None, server_version: str = None,
                       update_available: bool = False):
        """Log database version check for analytics"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'version_check',
            'client_ip': client_ip or 'unknown',
            'user_agent': user_agent or 'unknown',
            'current_version': current_version or 'none',
            'server_version': server_version or 'unknown',
            'update_available': update_available,
            'action_details': f"Version check: {current_version} -> {server_version}"
        }
        
        self.AppendToLocalLog(self.local_log_path, entry)
    
    def LogDatabaseDownload(self, client_ip: str = None, user_agent: str = None,
                           version: str = None, size_mb: float = 0, 
                           duration_seconds: float = 0, success: bool = True):
        """Log database download for data usage analytics"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'database_download',
            'client_ip': client_ip or 'unknown',
            'user_agent': user_agent or 'unknown',
            'version': version or 'unknown',
            'size_mb': size_mb,
            'duration_seconds': duration_seconds,
            'success': success,
            'estimated_cost_usd': size_mb * 0.10,  # $0.10/MB estimate
            'action_details': f"Downloaded {size_mb}MB in {duration_seconds:.1f}s"
        }
        
        self.AppendToLocalLog(self.local_log_path, entry)
    
    def LogDataUsagePattern(self, client_ip: str = None, connection_type: str = None,
                           estimated_speed_mbps: float = 0, decision: str = None):
        """Log user data usage decisions for educational insights"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'data_usage_decision',
            'client_ip': client_ip or 'unknown',
            'connection_type': connection_type or 'unknown',
            'estimated_speed_mbps': estimated_speed_mbps,
            'user_decision': decision or 'unknown',  # 'download', 'skip', 'wifi_only'
            'action_details': f"User chose '{decision}' with {estimated_speed_mbps}Mbps {connection_type}"
        }
        
        self.AppendToLocalLog(self.local_log_path, entry)
    
    def LogEducationalAccess(self, client_ip: str = None, user_agent: str = None,
                            country: str = None, book_category: str = None,
                            session_duration: float = 0):
        """Log educational access patterns for mission analytics"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'educational_access',
            'client_ip': client_ip or 'unknown',
            'user_agent': user_agent or 'unknown',
            'country': country or 'unknown',
            'book_category': book_category or 'unknown',
            'session_duration': session_duration,
            'action_details': f"Educational access: {book_category} for {session_duration:.1f}s"
        }
        
        self.AppendToLocalLog(self.local_log_path, entry)
    
    def GetDataUsageAnalytics(self, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get data usage analytics for cost optimization"""
        try:
            if not os.path.exists(self.local_log_path):
                return None
            
            with open(self.local_log_path, 'r') as f:
                log_data = json.load(f)
            
            # Filter download entries from last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            download_entries = []
            version_checks = []
            
            for entry in log_data.get('entries', []):
                try:
                    entry_date = datetime.fromisoformat(entry['timestamp'])
                    if entry_date >= cutoff_date:
                        if entry.get('action') == 'database_download':
                            download_entries.append(entry)
                        elif entry.get('action') == 'version_check':
                            version_checks.append(entry)
                except (ValueError, KeyError):
                    continue
            
            # Calculate data usage metrics
            total_downloads = len(download_entries)
            total_mb_downloaded = sum(entry.get('size_mb', 0) for entry in download_entries)
            total_estimated_cost = sum(entry.get('estimated_cost_usd', 0) for entry in download_entries)
            total_version_checks = len(version_checks)
            
            # Calculate efficiency (version checks vs downloads)
            efficiency_ratio = total_version_checks / total_downloads if total_downloads > 0 else 0
            
            # Connection type breakdown
            connection_patterns = {}
            for entry in download_entries:
                user_agent = entry.get('user_agent', 'unknown')
                if 'Mobile' in user_agent:
                    conn_type = 'mobile'
                elif 'WiFi' in user_agent:
                    conn_type = 'wifi'
                else:
                    conn_type = 'unknown'
                connection_patterns[conn_type] = connection_patterns.get(conn_type, 0) + 1
            
            return {
                'period_days': days,
                'total_downloads': total_downloads,
                'total_mb_downloaded': round(total_mb_downloaded, 1),
                'total_estimated_cost_usd': round(total_estimated_cost, 2),
                'total_version_checks': total_version_checks,
                'efficiency_ratio': round(efficiency_ratio, 2),
                'average_download_size_mb': round(total_mb_downloaded / total_downloads, 1) if total_downloads > 0 else 0,
                'connection_patterns': connection_patterns,
                'data_savings_mb': total_version_checks * 0.0001,  # Each version check saves ~0.1KB
                'data_protection_enabled': efficiency_ratio > 5  # More checks than downloads = good protection
            }
            
        except Exception as e:
            print(f"Error generating data usage analytics: {e}")
            return None

def main():
    """Test Google Sheets logging functionality"""
    print("📊 Google Sheets Logger Test")
    print("=" * 40)
    
    credentials_path = "OurLibrary/Config/google_credentials.json"
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return
    
    logger = SheetsLogger(credentials_path)
    
    try:
        # Test authentication
        print("🔐 Testing authentication...")
        if logger.Authenticate():
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
        
        # Test sheet creation
        print("📋 Testing sheet creation...")
        sheet_id = logger.GetOrCreateUsageSheet()
        if sheet_id:
            print(f"✅ Usage sheet: {sheet_id}")
        else:
            print("❌ Failed to create usage sheet")
            return
        
        # Test local logging
        print("📝 Testing local logging...")
        logger.LogUsage(
            action='view_book',
            book_id=123,
            book_title='Test Book',
            user_email='test@example.com',
            session_id='test_session_123'
        )
        
        logger.LogSession(
            session_start=datetime.now() - timedelta(minutes=5),
            session_end=datetime.now(),
            user_email='test@example.com',
            total_actions=3,
            books_viewed=2
        )
        
        # Test analytics summary
        print("📈 Testing analytics summary...")
        summary = logger.GetAnalyticsSummary(days=7)
        if summary:
            print(f"✅ Analytics: {summary['total_actions']} actions, {summary['unique_sessions']} sessions")
        
        print("\n🎉 Google Sheets Logger test completed!")
        print(f"View your analytics: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()