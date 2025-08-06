# File: WindowsDatabaseInit.py
# Path: Source/Utils/WindowsDatabaseInit.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-30
# Last Modified: 2025-07-30 21:45PM
"""
Windows-specific database initialization utilities.
Handles database setup and Google Drive sync for Windows executables.
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

class WindowsDatabaseInitializer:
    """Handle database initialization for Windows executables"""
    
    def __init__(self, app_directory: Optional[Path] = None):
        self.app_dir = app_directory or Path(sys.executable).parent
        self.data_dir = self.app_dir / "Data"
        self.config_dir = self.app_dir / "Config"
        
    def InitializeDatabase(self) -> bool:
        """Initialize database with fallback options"""
        print("🔄 Windows Database Initialization")
        
        # Step 1: Try Google Drive sync
        if self.TryGoogleDriveSync():
            return True
        
        # Step 2: Check for bundled database
        if self.CheckBundledDatabase():
            return True
        
        # Step 3: Create minimal database
        if self.CreateMinimalDatabase():
            return True
        
        print("❌ All database initialization methods failed")
        return False
    
    def TryGoogleDriveSync(self) -> bool:
        """Attempt to sync database from Google Drive"""
        try:
            sys.path.insert(0, str(self.app_dir / "Source"))
            from Core.DriveManager import DriveManager
            
            config_path = self.config_dir / "andygoogle_config.json"
            if not config_path.exists():
                print("⚠️ Configuration file not found - skipping Google Drive sync")
                return False
            
            drive_manager = DriveManager(str(config_path))
            
            if drive_manager.InitializeDatabase():
                print("✅ Database synced from Google Drive")
                return True
            else:
                print("⚠️ Google Drive sync failed")
                return False
                
        except Exception as e:
            print(f"⚠️ Google Drive sync error: {e}")
            return False
    
    def CheckBundledDatabase(self) -> bool:
        """Check for bundled database files"""
        possible_paths = [
            self.data_dir / "Databases" / "MyLibrary.db",
            self.data_dir / "Local" / "cached_library.db",
            self.app_dir / "MyLibrary.db"
        ]
        
        for db_path in possible_paths:
            if db_path.exists() and self.ValidateDatabase(db_path):
                print(f"✅ Using bundled database: {db_path}")
                return True
        
        print("⚠️ No valid bundled database found")
        return False
    
    def CreateMinimalDatabase(self) -> bool:
        """Create minimal functional database"""
        try:
            db_path = self.data_dir / "Databases" / "MyLibrary.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create basic tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    category_id INTEGER,
                    subject_id INTEGER,
                    FilePath TEXT,
                    ThumbnailImage BLOB,
                    last_opened TEXT,
                    LastOpened TEXT,
                    Rating INTEGER,
                    Notes TEXT,
                    Keywords TEXT,
                    FileSize INTEGER,
                    FileHash TEXT,
                    AddedDate TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            # Insert sample data
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES ('General')")
            cursor.execute("INSERT OR IGNORE INTO subjects (name) VALUES ('Uncategorized')")
            
            cursor.execute("""
                INSERT OR IGNORE INTO books (title, author, category_id, subject_id) 
                VALUES ('Welcome to AndyLibrary', 'System', 1, 1)
            """)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created minimal database: {db_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create minimal database: {e}")
            return False
    
    def ValidateDatabase(self, db_path: Path) -> bool:
        """Validate database integrity and structure"""
        try:
            if db_path.stat().st_size < 8192:  # Less than 8KB is suspicious
                return False
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result[0] != 'ok':
                conn.close()
                return False
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['books', 'categories', 'subjects']
            
            conn.close()
            
            return all(table in tables for table in required_tables)
            
        except Exception:
            return False

def InitializeWindowsDatabase(app_directory: Optional[Path] = None) -> bool:
    """Main function to initialize Windows database"""
    initializer = WindowsDatabaseInitializer(app_directory)
    return initializer.InitializeDatabase()
