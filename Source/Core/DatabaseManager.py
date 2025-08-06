# File: DatabaseManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 07:27AM

"""
Enhanced Database Manager for AndyLibrary
Extends existing library database with user authentication and educational mission features
Supports both library operations and user management
"""

import sqlite3
import logging
import os
import hashlib
import secrets
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
import json
import bcrypt

class DatabaseManager:
    """
    Enhanced Database Manager for AndyLibrary
    Supports library operations and user authentication with educational mission focus
    """
    
    def __init__(self, DatabasePath: str = "Data/Databases/MyLibrary.db"):
        """
        Initialize database manager with authentication support
        
        Args:
            DatabasePath: Path to SQLite database file
        """
        self.DatabasePath = DatabasePath
        self.Connection: Optional[sqlite3.Connection] = None
        self.Logger = logging.getLogger(self.__class__.__name__)
        
        # Load server configuration for URL generation
        self._LoadServerConfig()
        
        # Initialize EmailManager for production email services
        try:
            from .EmailManager import EmailManager
            self.EmailManager = EmailManager()
        except ImportError:
            self.EmailManager = None
            self.Logger.warning("EmailManager not available - using mock email")
        
        # Ensure database directory exists
        self.EnsureDatabaseDirectory()
    
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
        
        # Connect and initialize
        if self.Connect():
            self.InitializeUserTables()
        
        self.Logger.debug(f"DatabaseManager v2.1 initialized for: {self.DatabasePath}")

    def EnsureDatabaseDirectory(self):
        """Ensure the database directory exists"""
        DatabaseDir = Path(self.DatabasePath).parent
        DatabaseDir.mkdir(parents=True, exist_ok=True)

    def Connect(self) -> bool:
        """
        Establish database connection with optimization for web applications
        """
        try:
            if not os.path.exists(self.DatabasePath):
                self.Logger.error(f"Database file not found: {self.DatabasePath}")
                return False
            
            # Create connection with performance optimizations
            self.Connection = sqlite3.connect(
                self.DatabasePath, 
                timeout=30.0,
                check_same_thread=False,
                isolation_level=None
            )
            
            # Configure for better web performance
            self.Connection.row_factory = sqlite3.Row
            self.Connection.execute("PRAGMA journal_mode=WAL")
            self.Connection.execute("PRAGMA synchronous=NORMAL")
            self.Connection.execute("PRAGMA cache_size=10000")
            self.Connection.execute("PRAGMA temp_store=MEMORY")
            self.Connection.execute("PRAGMA mmap_size=268435456")
            
            # Test connection with existing books table
            TestResult = self.Connection.execute("SELECT COUNT(*) FROM books").fetchone()
            BookCount = TestResult[0] if TestResult else 0
            
            self.Logger.debug(f"✅ Database connected successfully - {BookCount} books available")
            return True
            
        except sqlite3.Error as Error:
            self.Logger.error(f"Database connection failed: {Error}")
            return False
        except Exception as Error:
            self.Logger.error(f"Unexpected error connecting to database: {Error}")
            return False

    def Disconnect(self) -> None:
        """Close database connection gracefully"""
        if self.Connection:
            try:
                self.Connection.close()
                self.Connection = None
                self.Logger.debug("Database disconnected successfully")
            except Exception as Error:
                self.Logger.error(f"Error disconnecting from database: {Error}")

    def InitializeUserTables(self) -> bool:
        """
        Initialize user authentication tables for enhanced registration system
        """
        try:
            if not self.Connection:
                self.Logger.error("No database connection available")
                return False

            # Users table with subscription tiers and email validation
            UsersTableQuery = """
            CREATE TABLE IF NOT EXISTS Users (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Email TEXT UNIQUE NOT NULL,
                Username TEXT UNIQUE,
                PasswordHash TEXT NOT NULL,
                EmailVerified BOOLEAN DEFAULT FALSE,
                EmailVerificationToken TEXT UNIQUE,
                EmailVerificationExpiry DATETIME,
                SubscriptionTier TEXT DEFAULT 'guest' CHECK(SubscriptionTier IN ('guest', 'free', 'scholar', 'researcher', 'institution')),
                AccessLevel TEXT DEFAULT 'pending' CHECK(AccessLevel IN ('pending', 'basic', 'verified', 'elevated', 'admin')),
                MissionAcknowledged BOOLEAN DEFAULT FALSE,
                IsActive BOOLEAN DEFAULT FALSE,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                LastLoginAt DATETIME,
                LoginAttempts INTEGER DEFAULT 0,
                LockoutUntil DATETIME,
                ModifiedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """

            # User sessions for authentication
            UserSessionsTableQuery = """
            CREATE TABLE IF NOT EXISTS UserSessions (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId INTEGER NOT NULL,
                SessionToken TEXT UNIQUE NOT NULL,
                RefreshToken TEXT UNIQUE,
                ExpiresAt DATETIME NOT NULL,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                IsActive BOOLEAN DEFAULT TRUE,
                IPAddress TEXT,
                UserAgent TEXT,
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE CASCADE
            )
            """

            # User preferences for educational mission analytics
            UserPreferencesTableQuery = """
            CREATE TABLE IF NOT EXISTS UserPreferences (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId INTEGER UNIQUE NOT NULL,
                DataSharingConsent BOOLEAN DEFAULT FALSE,
                AnonymousUsageConsent BOOLEAN DEFAULT FALSE,
                PreferredSubjects TEXT,
                AcademicLevel TEXT,
                InstitutionType TEXT,
                GeographicRegion TEXT,
                LanguagePreferences TEXT,
                AccessibilityNeeds TEXT,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                ModifiedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE CASCADE
            )
            """

            # Publication requests for community-driven collection development
            PublicationRequestsTableQuery = """
            CREATE TABLE IF NOT EXISTS PublicationRequests (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId INTEGER NOT NULL,
                RequestType TEXT NOT NULL CHECK(RequestType IN ('subject_area', 'specific_title', 'author', 'level')),
                ContentDescription TEXT NOT NULL,
                SubjectArea TEXT,
                Reason TEXT,
                Status TEXT DEFAULT 'pending' CHECK(Status IN ('pending', 'reviewing', 'approved', 'fulfilled', 'declined')),
                Priority INTEGER DEFAULT 0,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                ModifiedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE CASCADE
            )
            """

            # User activity tracking for usage analytics
            UserActivityTableQuery = """
            CREATE TABLE IF NOT EXISTS UserActivity (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId INTEGER,
                ActivityType TEXT NOT NULL,
                ResourceId INTEGER,
                ActivityData TEXT,
                IPAddress TEXT,
                UserAgent TEXT,
                CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(UserId) REFERENCES Users(Id) ON DELETE SET NULL
            )
            """

            # Execute table creation queries
            Tables = [
                ("Users", UsersTableQuery),
                ("UserSessions", UserSessionsTableQuery), 
                ("UserPreferences", UserPreferencesTableQuery),
                ("PublicationRequests", PublicationRequestsTableQuery),
                ("UserActivity", UserActivityTableQuery)
            ]

            for TableName, Query in Tables:
                self.Connection.execute(Query)
                self.Logger.debug(f"✅ Table {TableName} initialized")

            # Create indexes for better performance
            Indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON Users(Email)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON Users(Username)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_token ON UserSessions(SessionToken)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_user ON UserSessions(UserId)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_active ON UserSessions(IsActive, ExpiresAt)",
                "CREATE INDEX IF NOT EXISTS idx_preferences_user ON UserPreferences(UserId)",
                "CREATE INDEX IF NOT EXISTS idx_requests_user ON PublicationRequests(UserId)",
                "CREATE INDEX IF NOT EXISTS idx_requests_status ON PublicationRequests(Status)",
                "CREATE INDEX IF NOT EXISTS idx_activity_user ON UserActivity(UserId)",
                "CREATE INDEX IF NOT EXISTS idx_activity_type ON UserActivity(ActivityType)"
            ]

            for IndexQuery in Indexes:
                self.Connection.execute(IndexQuery)

            self.Connection.commit()
            self.Logger.info("✅ User authentication tables initialized successfully")
            return True

        except sqlite3.Error as Error:
            self.Logger.error(f"Failed to initialize user tables: {Error}")
            return False
        except Exception as Error:
            self.Logger.error(f"Unexpected error initializing user tables: {Error}")
            return False

    def HashPassword(self, Password: str) -> str:
        """Hash password using bcrypt"""
        Salt = bcrypt.gensalt()
        return bcrypt.hashpw(Password.encode('utf-8'), Salt).decode('utf-8')

    def VerifyPassword(self, Password: str, HashedPassword: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(Password.encode('utf-8'), HashedPassword.encode('utf-8'))

    def GenerateSessionToken(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def GenerateEmailVerificationToken(self) -> str:
        """Generate secure email verification token"""
        return secrets.token_urlsafe(32)
    
    def SendVerificationEmail(self, Email: str, VerificationToken: str, Username: str = None) -> bool:
        """
        Send email verification using production EmailManager or fallback to mock
        """
        try:
            if self.EmailManager:
                # Production email service
                Result = self.EmailManager.SendVerificationEmail(Email, VerificationToken, Username)
                if Result["success"]:
                    self.Logger.info(f"📧 Verification email sent successfully to {Email}")
                    return True
                else:
                    self.Logger.error(f"Failed to send verification email: {Result.get('error')}")
                    # Fall through to mock email for development
            
            # Mock email for development/testing
            VerificationUrl = f"http://{self.ServerHost}:{self.ServerPort}/api/auth/verify-email?token={VerificationToken}"
            
            self.Logger.info(f"📧 Email Verification Required (MOCK)")
            self.Logger.info(f"   User: {Email}")
            self.Logger.info(f"   Verification URL: {VerificationUrl}")
            print(f"\n📧 EMAIL VERIFICATION REQUIRED")
            print(f"   📬 User: {Email}")
            print(f"   🔗 Verification URL: {VerificationUrl}")
            print(f"   ⏰ Token expires in 24 hours")
            if not self.EmailManager:
                print(f"   🔧 Using mock email - configure EmailManager for production")
            print()
            
            return True
            
        except Exception as e:
            self.Logger.error(f"Failed to send verification email: {e}")
            return False
    
    def VerifyUserEmail(self, VerificationToken: str) -> Dict[str, Any]:
        """
        Verify user email with token and activate account
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}
            
            # Find user with valid verification token
            User = self.Connection.execute("""
                SELECT Id, Email, EmailVerificationExpiry 
                FROM Users 
                WHERE EmailVerificationToken = ? AND EmailVerified = FALSE
            """, (VerificationToken,)).fetchone()
            
            if not User:
                return {"success": False, "error": "Invalid or expired verification token"}
            
            # Check if token is expired
            ExpiryTime = datetime.fromisoformat(User["EmailVerificationExpiry"])
            if datetime.now() > ExpiryTime:
                return {"success": False, "error": "Verification token has expired"}
            
            # Activate user account
            self.Connection.execute("""
                UPDATE Users 
                SET EmailVerified = TRUE, 
                    IsActive = TRUE, 
                    AccessLevel = 'basic',
                    EmailVerificationToken = NULL, 
                    EmailVerificationExpiry = NULL,
                    ModifiedAt = CURRENT_TIMESTAMP
                WHERE Id = ?
            """, (User["Id"],))
            
            self.Connection.commit()
            
            self.Logger.info(f"✅ Email verified for user: {User['Email']}")
            return {
                "success": True, 
                "message": "Email verified successfully. Account activated.",
                "user_id": User["Id"],
                "email": User["Email"]
            }
            
        except Exception as e:
            self.Logger.error(f"Email verification failed: {e}")
            return {"success": False, "error": f"Verification failed: {str(e)}"}

    def CreateUser(self, Email: str, Password: str, Username: str = None, 
                   SubscriptionTier: str = 'guest', MissionAcknowledged: bool = False) -> Dict[str, Any]:
        """
        Create new user account with email verification and lowest access level
        User starts as inactive/pending until email is verified
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Mission acknowledgment is required
            if not MissionAcknowledged:
                return {"success": False, "error": "Mission acknowledgment is required"}

            # Check if email already exists
            ExistingUser = self.Connection.execute(
                "SELECT Id FROM Users WHERE Email = ?", (Email,)
            ).fetchone()

            if ExistingUser:
                return {"success": False, "error": "Email already registered"}

            # Check if username already exists (if provided)
            if Username:
                ExistingUsername = self.Connection.execute(
                    "SELECT Id FROM Users WHERE Username = ?", (Username,)
                ).fetchone()
                
                if ExistingUsername:
                    return {"success": False, "error": "Username already taken"}

            # Generate email verification token
            VerificationToken = self.GenerateEmailVerificationToken()
            VerificationExpiry = (datetime.now() + timedelta(hours=24)).isoformat()

            # Hash password
            PasswordHash = self.HashPassword(Password)

            # Insert user with email verification required and lowest access level
            Cursor = self.Connection.execute("""
                INSERT INTO Users (
                    Email, Username, PasswordHash, 
                    EmailVerificationToken, EmailVerificationExpiry,
                    SubscriptionTier, AccessLevel, MissionAcknowledged,
                    EmailVerified, IsActive
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE, FALSE)
            """, (Email, Username, PasswordHash, VerificationToken, VerificationExpiry,
                  SubscriptionTier, 'pending', MissionAcknowledged))

            UserId = Cursor.lastrowid
            self.Connection.commit()

            # Send verification email
            EmailSent = self.SendVerificationEmail(Email, VerificationToken, Username)

            self.Logger.info(f"✅ User created successfully: {Email} (ID: {UserId}) - Email verification required")
            return {
                "success": True,
                "user_id": UserId,
                "email": Email,
                "username": Username,
                "subscription_tier": SubscriptionTier,
                "access_level": "pending",
                "email_verified": False,
                "verification_required": True,
                "message": f"Account created successfully. Please check your email ({Email}) for verification instructions."
            }

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error creating user: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error creating user: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def AuthenticateUser(self, Email: str, Password: str) -> Dict[str, Any]:
        """
        Authenticate user credentials
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Get user by email
            User = self.Connection.execute("""
                SELECT Id, Email, Username, PasswordHash, SubscriptionTier, AccessLevel,
                       IsActive, EmailVerified, LoginAttempts, LockoutUntil
                FROM Users WHERE Email = ?
            """, (Email,)).fetchone()

            if not User:
                return {"success": False, "error": "Invalid credentials"}

            # Check if account is locked
            if User['LockoutUntil'] and datetime.fromisoformat(User['LockoutUntil']) > datetime.now():
                return {"success": False, "error": "Account temporarily locked due to failed login attempts"}

            # Check if email is verified first (more specific than general account status)
            if not User['EmailVerified']:
                return {
                    "success": False, 
                    "error": "Email verification required", 
                    "verification_required": True,
                    "message": f"Please check your email ({Email}) and click the verification link to activate your account."
                }

            # Check if account is active
            if not User['IsActive']:
                return {"success": False, "error": "Account is deactivated"}

            # Verify password
            if not self.VerifyPassword(Password, User['PasswordHash']):
                # Increment login attempts
                NewAttempts = User['LoginAttempts'] + 1
                LockoutUntil = None
                
                if NewAttempts >= 5:
                    LockoutUntil = (datetime.now() + timedelta(minutes=15)).isoformat()

                self.Connection.execute("""
                    UPDATE Users SET LoginAttempts = ?, LockoutUntil = ?
                    WHERE Id = ?
                """, (NewAttempts, LockoutUntil, User['Id']))
                self.Connection.commit()

                return {"success": False, "error": "Invalid credentials"}

            # Reset login attempts on successful login
            self.Connection.execute("""
                UPDATE Users SET LoginAttempts = 0, LockoutUntil = NULL, LastLoginAt = CURRENT_TIMESTAMP
                WHERE Id = ?
            """, (User['Id'],))
            self.Connection.commit()

            self.Logger.info(f"✅ User authenticated successfully: {Email}")
            return {
                "success": True,
                "user": {
                    "id": User['Id'],
                    "email": User['Email'],
                    "username": User['Username'],
                    "subscription_tier": User['SubscriptionTier'],
                    "access_level": User['AccessLevel'],
                    "email_verified": User['EmailVerified']
                }
            }

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error authenticating user: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error authenticating user: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def CreateUserSession(self, UserId: int, IPAddress: str = None, UserAgent: str = None) -> Dict[str, Any]:
        """
        Create new user session
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Generate tokens
            SessionToken = self.GenerateSessionToken()
            RefreshToken = self.GenerateSessionToken()

            # Session expires in 24 hours
            ExpiresAt = (datetime.now() + timedelta(hours=24)).isoformat()

            # Insert session
            self.Connection.execute("""
                INSERT INTO UserSessions (UserId, SessionToken, RefreshToken, ExpiresAt, IPAddress, UserAgent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (UserId, SessionToken, RefreshToken, ExpiresAt, IPAddress, UserAgent))

            self.Connection.commit()

            self.Logger.info(f"✅ Session created for user ID: {UserId}")
            return {
                "success": True,
                "session_token": SessionToken,
                "refresh_token": RefreshToken,
                "expires_at": ExpiresAt
            }

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error creating session: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error creating session: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def ValidateSession(self, SessionToken: str) -> Dict[str, Any]:
        """
        Validate user session token
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Get session with user info
            Session = self.Connection.execute("""
                SELECT s.UserId, s.ExpiresAt, s.IsActive,
                       u.Email, u.Username, u.SubscriptionTier, u.IsActive as UserActive
                FROM UserSessions s
                JOIN Users u ON s.UserId = u.Id
                WHERE s.SessionToken = ?
            """, (SessionToken,)).fetchone()

            if not Session:
                return {"success": False, "error": "Invalid session token"}

            # Check if session is active
            if not Session['IsActive']:
                return {"success": False, "error": "Session is inactive"}

            # Check if session is expired
            if datetime.fromisoformat(Session['ExpiresAt']) < datetime.now():
                return {"success": False, "error": "Session expired"}

            # Check if user is active
            if not Session['UserActive']:
                return {"success": False, "error": "User account is inactive"}

            return {
                "success": True,
                "user": {
                    "id": Session['UserId'],
                    "email": Session['Email'],
                    "username": Session['Username'],
                    "subscription_tier": Session['SubscriptionTier']
                }
            }

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error validating session: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error validating session: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def CreateUserPreferences(self, UserId: int, Preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user preferences for educational mission analytics
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Convert subjects list to JSON string
            PreferredSubjects = json.dumps(Preferences.get('preferred_subjects', []))

            # Insert or replace preferences
            self.Connection.execute("""
                INSERT OR REPLACE INTO UserPreferences 
                (UserId, DataSharingConsent, AnonymousUsageConsent, PreferredSubjects,
                 AcademicLevel, InstitutionType, GeographicRegion, ModifiedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                UserId,
                Preferences.get('data_sharing_consent', False),
                Preferences.get('anonymous_usage_consent', False),
                PreferredSubjects,
                Preferences.get('academic_level'),
                Preferences.get('institution_type'),
                Preferences.get('geographic_region')
            ))

            self.Connection.commit()

            self.Logger.info(f"✅ User preferences saved for user ID: {UserId}")
            return {"success": True, "message": "Preferences saved successfully"}

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error saving preferences: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error saving preferences: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def CreatePublicationRequest(self, UserId: int, Request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create publication request for community-driven collection development
        """
        try:
            if not self.Connection:
                return {"success": False, "error": "No database connection"}

            # Insert publication request
            Cursor = self.Connection.execute("""
                INSERT INTO PublicationRequests 
                (UserId, RequestType, ContentDescription, SubjectArea, Reason)
                VALUES (?, ?, ?, ?, ?)
            """, (
                UserId,
                Request.get('request_type'),
                Request.get('content_description'),
                Request.get('subject_area'),
                Request.get('reason')
            ))

            RequestId = Cursor.lastrowid
            self.Connection.commit()

            self.Logger.info(f"✅ Publication request created: ID {RequestId} for user {UserId}")
            return {"success": True, "request_id": RequestId}

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error creating publication request: {Error}")
            return {"success": False, "error": f"Database error: {Error}"}
        except Exception as Error:
            self.Logger.error(f"Unexpected error creating publication request: {Error}")
            return {"success": False, "error": f"Unexpected error: {Error}"}

    def GetBooks(self, CategoryId: int = None, SubjectId: int = None, SearchTerm: str = None, 
                 Limit: int = 50, Offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get books from library with filtering and pagination
        """
        try:
            if not self.Connection:
                return []

            Query = """
                SELECT b.id, b.title, b.author, b.FilePath, b.ThumbnailImage,
                       c.category, s.subject, b.Rating, b.FileSize, b.PageCount
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                WHERE 1=1
            """
            
            Params = []

            if CategoryId:
                Query += " AND b.category_id = ?"
                Params.append(CategoryId)

            if SubjectId:
                Query += " AND b.subject_id = ?"
                Params.append(SubjectId)

            if SearchTerm:
                Query += " AND (b.title LIKE ? OR b.author LIKE ?)"
                SearchPattern = f"%{SearchTerm}%"
                Params.extend([SearchPattern, SearchPattern])

            Query += " ORDER BY b.title LIMIT ? OFFSET ?"
            Params.extend([Limit, Offset])

            Results = self.Connection.execute(Query, Params).fetchall()

            Books = []
            for Row in Results:
                Books.append({
                    'id': Row['id'],
                    'title': Row['title'],
                    'author': Row['author'],
                    'category': Row['category'],
                    'subject': Row['subject'],
                    'file_path': Row['FilePath'],
                    'rating': Row['Rating'],
                    'file_size': Row['FileSize'],
                    'page_count': Row['PageCount'],
                    'has_thumbnail': Row['ThumbnailImage'] is not None
                })

            return Books

        except sqlite3.Error as Error:
            self.Logger.error(f"Database error getting books: {Error}")
            return []
        except Exception as Error:
            self.Logger.error(f"Unexpected error getting books: {Error}")
            return []

    def GetCategories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        try:
            if not self.Connection:
                return []

            Results = self.Connection.execute(
                "SELECT id, category FROM categories ORDER BY category"
            ).fetchall()

            return [{'id': row['id'], 'name': row['category']} for row in Results]

        except Exception as Error:
            self.Logger.error(f"Error getting categories: {Error}")
            return []

    def GetSubjects(self, CategoryId: int = None) -> List[Dict[str, Any]]:
        """Get subjects, optionally filtered by category"""
        try:
            if not self.Connection:
                return []

            if CategoryId:
                Results = self.Connection.execute(
                    "SELECT id, subject FROM subjects WHERE category_id = ? ORDER BY subject",
                    (CategoryId,)
                ).fetchall()
            else:
                Results = self.Connection.execute(
                    "SELECT id, subject FROM subjects ORDER BY subject"
                ).fetchall()

            return [{'id': row['id'], 'name': row['subject']} for row in Results]

        except Exception as Error:
            self.Logger.error(f"Error getting subjects: {Error}")
            return []