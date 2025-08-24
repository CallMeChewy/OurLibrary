# File: DriveManager.py
# Path: AndyGoogle/Source/Core/DriveManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-12  07:35PM
"""
Description: Central manager for Google Drive database synchronization in AndyGoogle
Orchestrates database downloads, updates, version checking, and offline mode handling
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import time

# Import AndyGoogle modules
from API.GoogleDriveAPI import GoogleDriveAPI
from Utils.SheetsLogger import SheetsLogger

class DriveManager:
    """Manage database synchronization with Google Drive"""
    
    def __init__(self, config_path: str = "AndyGoogle/Config/andygoogle_config.json"):
        self.config_path = config_path
        self.config = self.LoadConfig()
        
        # Initialize API components
        credentials_path = self.config.get('google_credentials_path', 'AndyGoogle/Config/google_credentials.json')
        self.drive_api = GoogleDriveAPI(credentials_path)
        self.sheets_logger = SheetsLogger(credentials_path)
        
        # Local paths
        self.local_db_path = self.config.get('local_database_path', 'AndyGoogle/Data/Local/cached_library.db')
        self.backup_db_path = self.config.get('backup_database_path', 'AndyGoogle/Data/Local/backup_library.db')
        self.version_info_path = "AndyGoogle/Data/Local/version_info.json"
        
        # Sync settings
        self.auto_sync_enabled = self.config.get('auto_sync_enabled', True)
        self.sync_interval_hours = self.config.get('sync_interval_hours', 24)
        self.offline_mode = False
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.version_info_path), exist_ok=True)
    
    def LoadConfig(self) -> Dict[str, Any]:
        """Load AndyGoogle configuration"""
        default_config = {
            'google_credentials_path': 'AndyGoogle/Config/google_credentials.json',
            'local_database_path': 'AndyGoogle/Data/Local/cached_library.db',
            'backup_database_path': 'AndyGoogle/Data/Local/backup_library.db',
            'auto_sync_enabled': True,
            'sync_interval_hours': 24,
            'offline_grace_period_days': 7,
            'version_check_interval_hours': 6,
            'max_backup_versions': 5,
            'required_free_space_mb': 100
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            else:
                # Create default config file
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Error loading config, using defaults: {e}")
        
        return default_config
    
    def SaveConfig(self):
        """Save current configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def GetLocalVersionInfo(self) -> Dict[str, Any]:
        """Get local database version information"""
        default_info = {
            'version': '0.0.0',
            'file_id': None,
            'last_sync': None,
            'file_hash': None,
            'record_count': 0,
            'sync_status': 'never_synced'
        }
        
        try:
            if os.path.exists(self.version_info_path):
                with open(self.version_info_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading version info: {e}")
        
        return default_info
    
    def SaveLocalVersionInfo(self, version_info: Dict[str, Any]):
        """Save local database version information"""
        try:
            os.makedirs(os.path.dirname(self.version_info_path), exist_ok=True)
            with open(self.version_info_path, 'w') as f:
                json.dump(version_info, f, indent=2)
        except Exception as e:
            print(f"Error saving version info: {e}")
    
    def CheckForUpdates(self) -> Dict[str, Any]:
        """Check if database updates are available on Google Drive"""
        update_info = {
            'update_available': False,
            'local_version': '0.0.0',
            'remote_version': '0.0.0',
            'update_type': 'none',  # 'optional', 'recommended', 'required'
            'download_size': 0,
            'change_description': '',
            'last_check': datetime.now().isoformat(),
            'offline_mode': self.offline_mode
        }
        
        try:
            # Get local version
            local_info = self.GetLocalVersionInfo()
            update_info['local_version'] = local_info.get('version', '0.0.0')
            
            # Try to get remote version
            if not self.offline_mode:
                remote_info = self.drive_api.GetLatestDatabaseVersion()
                
                if remote_info:
                    update_info['remote_version'] = remote_info['version']
                    update_info['download_size'] = remote_info['size_bytes']
                    update_info['change_description'] = remote_info.get('description', '')
                    
                    # Compare versions
                    if self.CompareVersions(remote_info['version'], local_info['version']) > 0:
                        update_info['update_available'] = True
                        
                        # Determine update urgency (you can expand this logic)
                        version_diff = self.GetVersionDifference(local_info['version'], remote_info['version'])
                        if version_diff['major'] > 0:
                            update_info['update_type'] = 'required'
                        elif version_diff['minor'] > 0:
                            update_info['update_type'] = 'recommended'
                        else:
                            update_info['update_type'] = 'optional'
                else:
                    print("Could not reach Google Drive - entering offline mode")
                    self.offline_mode = True
                    update_info['offline_mode'] = True
            
            # Log the update check
            self.sheets_logger.LogUsage(
                action='update_check',
                action_details=f"Local: {update_info['local_version']}, Remote: {update_info['remote_version']}, Available: {update_info['update_available']}"
            )
            
            return update_info
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            self.sheets_logger.LogError('update_check_failed', str(e))
            update_info['offline_mode'] = True
            self.offline_mode = True
            return update_info
    
    def SyncDatabaseFromDrive(self, force_download: bool = False) -> bool:
        """Sync database from Google Drive"""
        print("🔄 Starting database sync from Google Drive...")
        
        try:
            # Check if sync is needed
            if not force_download:
                local_info = self.GetLocalVersionInfo()
                last_sync = local_info.get('last_sync')
                
                if last_sync:
                    last_sync_time = datetime.fromisoformat(last_sync)
                    if datetime.now() - last_sync_time < timedelta(hours=self.sync_interval_hours):
                        print(f"✅ Database is recent (last sync: {last_sync})")
                        return True
            
            # Get latest version from Drive
            remote_info = self.drive_api.GetLatestDatabaseVersion()
            if not remote_info:
                print("❌ Could not get database version from Google Drive")
                return False
            
            # Create backup of current database
            if os.path.exists(self.local_db_path):
                self.CreateBackup()
            
            # Download new database
            print(f"📥 Downloading database v{remote_info['version']} ({remote_info['size_bytes']} bytes)...")
            
            temp_path = self.local_db_path + ".tmp"
            success = self.drive_api.DownloadDatabase(remote_info['file_id'], temp_path)
            
            if not success:
                print("❌ Failed to download database")
                return False
            
            # Validate downloaded database
            if not self.drive_api.ValidateDatabaseIntegrity(temp_path):
                print("❌ Downloaded database failed integrity check")
                os.remove(temp_path)
                return False
            
            # Move temp file to final location
            shutil.move(temp_path, self.local_db_path)
            
            # Update version info
            new_version_info = {
                'version': remote_info['version'],
                'file_id': remote_info['file_id'],
                'last_sync': datetime.now().isoformat(),
                'file_hash': self.drive_api.CalculateFileHash(self.local_db_path),
                'record_count': self.GetDatabaseRecordCount(),
                'sync_status': 'synced'
            }
            
            self.SaveLocalVersionInfo(new_version_info)
            
            print(f"✅ Database sync completed successfully (v{remote_info['version']})")
            
            # Log successful sync
            self.sheets_logger.LogUsage(
                action='database_sync',
                action_details=f"Downloaded v{remote_info['version']}, {new_version_info['record_count']} records"
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Database sync failed: {e}")
            self.sheets_logger.LogError('database_sync_failed', str(e))
            return False
    
    def CreateBackup(self) -> bool:
        """Create backup of current database"""
        try:
            if not os.path.exists(self.local_db_path):
                return True
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.dirname(self.backup_db_path)
            backup_filename = f"library_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copy2(self.local_db_path, backup_path)
            
            # Clean up old backups
            self.CleanupOldBackups(backup_dir)
            
            print(f"✅ Created database backup: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def CleanupOldBackups(self, backup_dir: str):
        """Remove old backup files beyond the configured limit"""
        try:
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('library_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            max_backups = self.config.get('max_backup_versions', 5)
            for filepath, _ in backup_files[max_backups:]:
                os.remove(filepath)
                print(f"🗑️ Removed old backup: {os.path.basename(filepath)}")
                
        except Exception as e:
            print(f"Warning: Error cleaning up backups: {e}")
    
    def GetDatabaseRecordCount(self) -> int:
        """Get total record count from local database"""
        try:
            if not os.path.exists(self.local_db_path):
                return 0
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books WHERE 1=1")  # Assuming books is main table
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error counting database records: {e}")
            return 0
    
    def CompareVersions(self, version1: str, version2: str) -> int:
        """Compare two version strings (returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal)"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
            
        except Exception:
            # If version comparison fails, treat as equal
            return 0
    
    def GetVersionDifference(self, old_version: str, new_version: str) -> Dict[str, int]:
        """Get the difference between two versions"""
        try:
            old_parts = [int(x) for x in old_version.split('.')]
            new_parts = [int(x) for x in new_version.split('.')]
            
            # Ensure both have same length
            max_len = max(len(old_parts), len(new_parts))
            old_parts.extend([0] * (max_len - len(old_parts)))
            new_parts.extend([0] * (max_len - len(new_parts)))
            
            return {
                'major': new_parts[0] - old_parts[0] if len(new_parts) > 0 else 0,
                'minor': new_parts[1] - old_parts[1] if len(new_parts) > 1 else 0,
                'patch': new_parts[2] - old_parts[2] if len(new_parts) > 2 else 0
            }
            
        except Exception:
            return {'major': 0, 'minor': 0, 'patch': 0}
    
    def HandleDatabaseUpdate(self, update_info: Dict[str, Any]) -> bool:
        """Handle database update based on update info"""
        if not update_info.get('update_available', False):
            return True
        
        update_type = update_info.get('update_type', 'optional')
        
        print(f"📢 Database update available: v{update_info['local_version']} → v{update_info['remote_version']}")
        print(f"Update type: {update_type}")
        print(f"Download size: {update_info['download_size']} bytes")
        print(f"Changes: {update_info['change_description']}")
        
        # Auto-update logic
        auto_update = False
        
        if update_type == 'required':
            print("🚨 Required update - downloading automatically...")
            auto_update = True
        elif update_type == 'recommended' and self.config.get('auto_update_recommended', True):
            print("💡 Recommended update - downloading automatically...")
            auto_update = True
        elif update_type == 'optional' and self.config.get('auto_update_optional', False):
            print("ℹ️ Optional update - downloading automatically...")
            auto_update = True
        else:
            print(f"ℹ️ {update_type.title()} update available - skipping automatic download")
            return False
        
        # Perform update
        return self.SyncDatabaseFromDrive(force_download=True)
    
    def GetSyncStatus(self) -> Dict[str, Any]:
        """Get comprehensive sync status information"""
        local_info = self.GetLocalVersionInfo()
        
        status = {
            'local_database_exists': os.path.exists(self.local_db_path),
            'local_version': local_info.get('version', '0.0.0'),
            'last_sync': local_info.get('last_sync'),
            'record_count': local_info.get('record_count', 0),
            'sync_status': local_info.get('sync_status', 'unknown'),
            'offline_mode': self.offline_mode,
            'auto_sync_enabled': self.auto_sync_enabled,
            'next_check_due': None,
            'database_size_mb': 0
        }
        
        # Calculate database size
        if status['local_database_exists']:
            try:
                status['database_size_mb'] = round(os.path.getsize(self.local_db_path) / 1024 / 1024, 2)
            except:
                pass
        
        # Calculate next check time
        if local_info.get('last_sync'):
            try:
                last_sync = datetime.fromisoformat(local_info['last_sync'])
                next_check = last_sync + timedelta(hours=self.sync_interval_hours)
                status['next_check_due'] = next_check.isoformat()
            except:
                pass
        
        return status
    
    def InitializeDatabase(self) -> bool:
        """Initialize database on first run"""
        print("🚀 Initializing AndyGoogle database...")
        
        # Check if local database already exists
        if os.path.exists(self.local_db_path):
            local_info = self.GetLocalVersionInfo()
            if local_info.get('sync_status') == 'synced':
                print("✅ Database already initialized")
                return True
        
        # Try to sync from Google Drive
        if self.SyncDatabaseFromDrive(force_download=True):
            print("✅ Database initialized from Google Drive")
            return True
        else:
            print("⚠️ Could not sync from Google Drive - running in offline mode")
            self.offline_mode = True
            
            # Check if we have any local database
            if os.path.exists(self.local_db_path):
                print("ℹ️ Using existing local database")
                return True
            else:
                print("❌ No database available - AndyGoogle cannot start")
                return False

def main():
    """Test DriveManager functionality"""
    print("🔄 DriveManager Test")
    print("=" * 40)
    
    try:
        manager = DriveManager()
        
        # Test initialization
        print("🚀 Testing initialization...")
        if manager.InitializeDatabase():
            print("✅ Database initialization successful")
        else:
            print("❌ Database initialization failed")
            return
        
        # Test update checking
        print("🔍 Testing update checking...")
        update_info = manager.CheckForUpdates()
        print(f"✅ Update check: {update_info['update_available']}")
        print(f"   Local: v{update_info['local_version']}")
        print(f"   Remote: v{update_info['remote_version']}")
        
        # Test sync status
        print("📊 Testing sync status...")
        status = manager.GetSyncStatus()
        print(f"✅ Sync status: {status['sync_status']}")
        print(f"   Database: {status['database_size_mb']} MB, {status['record_count']} records")
        print(f"   Offline mode: {status['offline_mode']}")
        
        print("\n🎉 DriveManager test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()