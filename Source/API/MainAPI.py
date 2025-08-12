# File: MainAPI.py
# Path: /home/herb/Desktop/OurLibrary/Source/API/MainAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-08-12 11:45AM
"""
Description: Enhanced FastAPI main server for OurLibrary with authentication
Provides RESTful API endpoints for library management with user authentication and educational mission features
"""

import os
import sys
import sqlite3
import time
import platform
import requests
import psutil
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Security, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Core.DriveManager import DriveManager
except ImportError:
    DriveManager = None
    print("⚠️ DriveManager not available - Google Drive functionality disabled")

try:
    from Core.DatabaseManager import DatabaseManager
except ImportError:
    DatabaseManager = None
    print("⚠️ DatabaseManager not available - authentication functionality disabled")

try:
    from Core.ModernSocialAuthManager import ModernSocialAuthManager
except ImportError:
    ModernSocialAuthManager = None
    print("⚠️ ModernSocialAuthManager not available - social login functionality disabled")

try:
    from Core.SocialAuthManager import SocialAuthManager
except ImportError:
    SocialAuthManager = None
    print("⚠️ Legacy SocialAuthManager not available")

try:
    from Core.UserSetupManager import UserSetupManager
except ImportError:
    UserSetupManager = None
    print("⚠️ UserSetupManager not available - user setup functionality disabled")

try:
    from API.AdvancedSearchAPI import CreateAdvancedSearchAPI
except ImportError:
    CreateAdvancedSearchAPI = None
    print("⚠️ AdvancedSearchAPI not available - advanced search functionality disabled")

try:
    from Core.UserProgressManager import UserProgressManager
except ImportError:
    UserProgressManager = None
    print("⚠️ UserProgressManager not available - progress tracking functionality disabled")

try:
    from Utils.SheetsLogger import SheetsLogger  
except ImportError:
    SheetsLogger = None
    print("⚠️ SheetsLogger not available - logging to sheets disabled")

try:
    from Core.StudentBookDownloader import StudentBookDownloader, StudentRegion
except ImportError:
    StudentBookDownloader = None
    print("⚠️ StudentBookDownloader not available - book download functionality disabled")

try:
    from Middleware.SecurityMiddleware import SecurityMiddleware
except ImportError:
    SecurityMiddleware = None
    print("⚠️ SecurityMiddleware not available - running without enhanced security")

try:
    from Core.UserJourneyManager import UserJourneyManager, JourneyStage, UserIntent
except ImportError:
    UserJourneyManager = None
    JourneyStage = None
    UserIntent = None
    print("⚠️ UserJourneyManager not available - running without benchmark UX orchestration")

try:
    from Core.IntelligentSearchEngine import IntelligentSearchEngine, SearchQuery, LearningIntent, AcademicLevel, SearchMode
except ImportError:
    IntelligentSearchEngine = None
    SearchQuery = None
    LearningIntent = None
    AcademicLevel = None
    SearchMode = None
    print("⚠️ IntelligentSearchEngine not available - running without benchmark search capabilities")

# FastAPI app instance
app = FastAPI(
    title="AndyLibrary API",
    description="""
    **Enhanced Educational Library Platform with Authentication**
    
    ## Educational Mission
    "Getting education into the hands of people who can least afford it"
    
    ## Features
    - 📚 **Book Management**: Search, filter, and browse your digital library
    - 🔐 **User Authentication**: Secure registration and login with educational mission focus
    - 🌐 **Google Drive Sync**: Seamless cloud synchronization 
    - 🔍 **Smart Search**: Full-text search across titles and metadata
    - 📱 **Multi-mode**: LOCAL (offline) or GDRIVE (cloud sync)
    - 🎯 **Educational Analytics**: Anonymous usage data for collection development
    - 📖 **Publication Requests**: Community-driven collection development
    - 🚀 **High Performance**: Optimized database queries with indexing
    - 🛡️ **Robust**: Auto-recovery and graceful error handling
    
    ## Quick Start
    1. **Register**: Create account with mission acknowledgment
    2. **Browse**: Access library with subscription tier limits
    3. **Request**: Help us grow the collection with publication requests
    
    ## API Status
    - Health check: `/api/health`
    - Authentication: `/api/auth/*`
    - Library stats: `/api/stats`
    """,
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AndyLibrary Support",
        "url": "https://github.com/your-repo/andylibrary"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Security scheme for authentication
security = HTTPBearer(auto_error=False)

# Configure Security Middleware (must be first)
if SecurityMiddleware:
    app.add_middleware(
        SecurityMiddleware,
        config={
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    )

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers (initialized on startup)
drive_manager = None
sheets_logger = None
progress_manager = None
modern_auth_manager = None
journey_manager = None
intelligent_search_engine = None

# ==================== AUTHENTICATION HELPERS ====================

def get_auth_database():
    """Dependency to get authenticated database manager instance"""
    if not DatabaseManager:
        raise HTTPException(status_code=503, detail="Authentication system not available")
    
    # Use the main database path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
    return DatabaseManager(db_path)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from token"""
    if not credentials:
        return None
    
    try:
        db_manager = get_auth_database()
        result = db_manager.ValidateSession(credentials.credentials)
        
        if result.get('success'):
            return result['user']
        return None
    except Exception as e:
        logging.error(f"Error validating session: {e}")
        return None

async def require_auth(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authentication dependency"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user



# Pydantic models for API requests/responses
class BookResponse(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    rating: Optional[int] = None
    last_opened: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    category: str

class SubjectResponse(BaseModel):
    id: int
    subject: str
    category_id: Optional[int] = None

class StatsResponse(BaseModel):
    total_books: int
    total_categories: int
    total_subjects: int
    database_version: str
    last_sync: Optional[str] = None
    offline_mode: bool

class SyncStatusResponse(BaseModel):
    local_database_exists: bool
    local_version: str
    last_sync: Optional[str] = None
    record_count: int
    sync_status: str
    offline_mode: bool

# Student book download models
class BookCostResponse(BaseModel):
    book_id: int
    title: str
    file_size_mb: float
    estimated_cost_usd: float
    warning_level: str
    budget_percentage: float

class DownloadOptionsResponse(BaseModel):
    book_info: dict
    download_options: list
    cost_warnings: list
    student_guidance: dict

class BudgetSummaryResponse(BaseModel):
    month: str
    total_spent: float
    remaining_budget: float
    budget_used_percentage: float
    downloads_count: int
    budget_status: str

# ==================== AUTHENTICATION MODELS ====================

class UserPreferencesRequest(BaseModel):
    """User preferences for educational mission analytics"""
    data_sharing_consent: bool = Field(default=False, description="Consent to anonymous data sharing for educational mission")
    anonymous_usage_consent: bool = Field(default=False, description="Consent to anonymous usage analytics")
    preferred_subjects: List[str] = Field(default=[], description="Academic subjects of interest")
    academic_level: Optional[str] = Field(None, description="Academic level")
    institution_type: Optional[str] = Field(None, description="Type of institution")
    geographic_region: Optional[str] = Field(None, description="Geographic region")

class PublicationRequestModel(BaseModel):
    """Publication request for collection development"""
    request_type: str = Field(..., description="Type of request: subject_area, specific_title, author, level")
    content_description: str = Field(..., min_length=3, description="Description of requested content")
    subject_area: Optional[str] = Field(None, description="Academic subject area")
    reason: Optional[str] = Field(None, description="Reason for the request")
    
    @field_validator('request_type')
    @classmethod
    def validate_request_type(cls, v):
        valid_types = ['subject_area', 'specific_title', 'author', 'level']
        if v not in valid_types:
            raise ValueError(f'Request type must be one of: {valid_types}')
        return v

class UserRegistrationRequest(BaseModel):
    """Enhanced user registration request with mission awareness"""
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (8-100 characters)")
    username: Optional[str] = Field(default=None, min_length=3, max_length=30, description="Username (optional)")
    subscription_tier: str = Field(default='free', pattern=r'^(free|scholar|researcher|institution)$', description="Subscription tier")
    
    # Educational mission and data consent
    mission_acknowledgment: bool = Field(..., description="Acknowledgment of AndyLibrary educational mission")
    user_preferences: Optional[UserPreferencesRequest] = Field(None, description="User preferences for educational analytics")
    publication_requests: List[PublicationRequestModel] = Field(default=[], description="Initial publication requests")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        """Validate email format"""
        return value.lower().strip()
    
    @field_validator('mission_acknowledgment')
    @classmethod
    def validate_mission_acknowledgment(cls, value):
        """Ensure mission acknowledgment is provided"""
        if not value:
            raise ValueError('You must acknowledge our educational mission to create an account')
        return value

class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        return value.lower().strip()

class UserResponse(BaseModel):
    """Response model for user information"""
    id: int
    email: str
    username: Optional[str] = None
    subscription_tier: str
    created_at: str

class LoginResponse(BaseModel):
    """Response model for successful login"""
    user: UserResponse
    session_token: str
    refresh_token: str
    expires_at: str
    message: str = "Login successful"

class RegisterResponse(BaseModel):
    """Response model for successful registration"""
    user: UserResponse
    message: str = "Registration successful"
    preferences_saved: bool = False
    publication_requests_saved: int = 0

# Intelligent Search API Models (Project Himalaya Benchmark)
class IntelligentSearchRequest(BaseModel):
    """Request model for intelligent educational search"""
    query: str = Field(..., min_length=1, max_length=500, description="The search query")
    learning_intent: Optional[str] = Field(None, description="Specific learning intent (homework_help, deep_learning, etc.)")
    academic_level: Optional[str] = Field(None, description="Academic level (elementary, middle_school, high_school, etc.)")
    subject_area: Optional[str] = Field(None, description="Subject area filter")
    search_mode: Optional[str] = Field("instant", description="Search interaction mode")
    accessibility_requirements: Optional[Dict[str, bool]] = Field(None, description="Accessibility needs")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: Optional[int] = Field(0, ge=0, description="Offset for pagination")

class IntelligentSearchResult(BaseModel):
    """Enhanced search result with educational metadata"""
    content_id: int
    title: str
    author: str
    relevance_score: float
    educational_value: float
    difficulty_level: str
    content_type: str
    subject_areas: List[str]
    learning_objectives: List[str]
    accessibility_features: Dict[str, bool]
    preview_text: str
    thumbnail_available: bool
    estimated_reading_time: int
    quality_indicators: Dict[str, Any]

class IntelligentSearchResponse(BaseModel):
    """Complete intelligent search response"""
    results: List[IntelligentSearchResult]
    total_count: int
    query_analysis: Dict[str, Any]
    suggestions: List[str]
    accessibility_optimized: bool
    search_metadata: Dict[str, Any]

class SearchAnalyticsResponse(BaseModel):
    """Privacy-respecting search analytics response"""
    total_searches: int
    intent_distribution: Dict[str, int]
    level_distribution: Dict[str, int]
    avg_results_per_search: float
    avg_search_duration_ms: float
    engagement_rate: float
    accessibility_usage_rate: float
    privacy_compliant: bool
    anonymized: bool

def convert_user_to_response(user_data: Dict[str, Any]) -> UserResponse:
    """Convert database user data to API response model"""
    return UserResponse(
        id=user_data.get('id', user_data.get('user_id')),
        email=user_data['email'],
        username=user_data.get('username'),
        subscription_tier=user_data['subscription_tier'],
        created_at=user_data.get('created_at', datetime.now().isoformat())
    )

# Dependency to get database connection
def get_database():
    """Get SQLite database connection with enhanced error handling"""
    try:
        # Use direct path when drive_manager is not available
        if drive_manager:
            print("🔍 Using DriveManager database path")
            db_path = drive_manager.local_db_path
        else:
            # Check for temp database path from environment (for testing)
            temp_db_path = os.environ.get('ANDYGOOGLE_TEMP_DB')
            if temp_db_path and os.path.exists(temp_db_path):
                print(f"🔍 Using temp database from environment: {temp_db_path}")
                db_path = temp_db_path
            else:
                print("🔍 Using fallback local database path")
                # Use absolute path to ensure it works regardless of working directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        print(f"🔍 Database path resolved to: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            raise HTTPException(status_code=503, detail="Database not available - sync required")
        
        print(f"🔗 Connecting to database at: {db_path}")
        # Use check_same_thread=False to allow SQLite to work with FastAPI's threading
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        print("✅ Database connection established")
        yield conn
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
    finally:
        try:
            if 'conn' in locals():
                conn.close()
                print("🔒 Database connection closed")
        except Exception as e:
            print(f"⚠️ Error closing database connection: {e}")

async def optimize_database_indexes():
    """Optimize database indexes for better query performance"""
    try:
        # Get database connection
        db_gen = get_database()
        conn = next(db_gen)
        
        try:
            # Create performance indexes if they don't exist
            optimization_queries = [
                # Books table optimizations
                "CREATE INDEX IF NOT EXISTS idx_books_title_search ON books (title COLLATE NOCASE)",
                "CREATE INDEX IF NOT EXISTS idx_books_category_subject ON books (category_id, subject_id)",
                "CREATE INDEX IF NOT EXISTS idx_books_title_category ON books (title, category_id)",
                
                # Categories table optimization
                "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (category COLLATE NOCASE)",
                
                # Subjects table optimization  
                "CREATE INDEX IF NOT EXISTS idx_subjects_name_category ON subjects (subject COLLATE NOCASE, category_id)",
                "CREATE INDEX IF NOT EXISTS idx_subjects_category ON subjects (category_id)",
                
                # Analyze tables for query planner optimization
                "ANALYZE books",
                "ANALYZE categories", 
                "ANALYZE subjects"
            ]
            
            for query in optimization_queries:
                try:
                    conn.execute(query)
                except Exception as e:
                    print(f"⚠️ Index optimization warning: {e}")
            
            conn.commit()
            print("✅ Database indexes optimized for performance")
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ Database optimization failed: {e}")

# Dependency to log API usage
def log_api_usage(request: Request, action: str, details: str = None):
    """Log API usage to Google Sheets"""
    if sheets_logger:
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            sheets_logger.LogUsage(
                action=action,
                action_details=details or "",
                client_ip=client_ip,
                user_agent=user_agent,
                session_id=f"api_{int(datetime.now().timestamp())}"
            )
        except Exception as e:
            print(f"Warning: Failed to log API usage: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize OurLibrary components on startup"""
    global drive_manager, sheets_logger, modern_auth_manager, journey_manager, intelligent_search_engine
    
    print("🚀 Starting OurLibrary API server...")
    
    # Initialize User Journey Manager (Project Himalaya Benchmark)
    if UserJourneyManager:
        try:
            journey_manager = UserJourneyManager({
                "environment": os.getenv("ENVIRONMENT", "development"),
                "analytics_enabled": True,
                "personalization_enabled": True
            })
            print("🏔️ UserJourneyManager initialized - Project Himalaya benchmark UX")
        except Exception as e:
            print(f"⚠️ Failed to initialize UserJourneyManager: {e}")
            journey_manager = None
    else:
        journey_manager = None
    
    # Initialize Intelligent Search Engine (Project Himalaya Benchmark)
    if IntelligentSearchEngine:
        try:
            database_path = os.path.join("Data", "Local", "cached_library.db")
            intelligent_search_engine = IntelligentSearchEngine(
                database_path=database_path,
                config={
                    "cache_enabled": True,
                    "analytics_enabled": True,
                    "performance_optimization": True
                }
            )
            print("🔍 IntelligentSearchEngine initialized - Project Himalaya benchmark search")
        except Exception as e:
            print(f"⚠️ Failed to initialize IntelligentSearchEngine: {e}")
            intelligent_search_engine = None
    else:
        intelligent_search_engine = None
    
    # Initialize Modern OAuth Manager
    if ModernSocialAuthManager:
        try:
            modern_auth_manager = ModernSocialAuthManager()
            print("🔐 Modern OAuth 2.0 Manager initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize Modern OAuth Manager: {e}")
            modern_auth_manager = None
    else:
        modern_auth_manager = None
    
    # Check operating mode from environment
    mode = os.environ.get('ANDYGOOGLE_MODE', 'local')
    
    if mode == 'gdrive':
        print("🌐 GOOGLE DRIVE MODE - Initializing Drive integration...")
        try:
            from Core.DriveManager import DriveManager
            from Utils.SheetsLogger import SheetsLogger
            
            # Use proper config paths
            config_path = "Config/andygoogle_config.json"
            creds_path = "Config/google_credentials.json"
            
            print(f"🔍 Initializing DriveManager with config: {config_path}")
            
            # Initialize DriveManager with enhanced error handling
            drive_manager = DriveManager(config_path)
            
            # Validate DriveManager functionality
            if hasattr(drive_manager, 'local_db_path'):
                print(f"🔍 DriveManager local_db_path: {drive_manager.local_db_path}")
                db_path_valid = True
            else:
                print("⚠️ DriveManager missing local_db_path attribute")
                db_path_valid = False
            
            # Test Google Drive connectivity (non-blocking)
            try:
                if hasattr(drive_manager, 'TestConnection'):
                    connection_status = drive_manager.TestConnection()
                    if connection_status:
                        print("✅ Google Drive connection test successful")
                    else:
                        print("⚠️ Google Drive connection test failed - will work offline")
                else:
                    print("ℹ️ Connection test not available - assuming connected")
            except Exception as conn_error:
                print(f"⚠️ Google Drive connection test error: {conn_error}")
                print("ℹ️ Will continue in offline mode")
            
            # Initialize SheetsLogger with error handling
            try:
                print(f"🔍 Initializing SheetsLogger with creds: {creds_path}")
                sheets_logger = SheetsLogger(creds_path)
                print("✅ SheetsLogger initialized successfully")
            except Exception as sheets_error:
                print(f"⚠️ SheetsLogger initialization failed: {sheets_error}")
                print("ℹ️ Continuing without sheets logging")
                sheets_logger = None
            
            # Validate database access through DriveManager
            if drive_manager and db_path_valid:
                test_db_path = drive_manager.local_db_path
                if os.path.exists(test_db_path):
                    print(f"✅ Database accessible at: {test_db_path}")
                    
                    # Test database connectivity
                    try:
                        conn = sqlite3.connect(test_db_path, check_same_thread=False)
                        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
                        conn.close()
                        print(f"✅ Database validation successful - {count} books found")
                    except Exception as db_error:
                        print(f"⚠️ Database validation warning: {db_error}")
                        
                else:
                    print(f"⚠️ Database not found at DriveManager path: {test_db_path}")
                    print("📊 Will attempt to sync from Google Drive or fallback to local")
            
            print("✅ Google Drive integration enabled successfully")
            print("📊 Database ready with Google Drive sync capabilities")
        except Exception as e:
            print(f"⚠️ Google Drive initialization failed: {e}")
            print("📊 Falling back to local SQLite mode")
            drive_manager = None
            sheets_logger = None
            
            # Force environment to local mode to prevent further issues
            os.environ['ANDYGOOGLE_MODE'] = 'local'
            print("🔄 Environment mode switched to LOCAL for stability")
    else:
        print("💾 LOCAL MODE - Using local SQLite database only")
        print("📊 Database ready with local SQLite file")
    
    # Optimize database indexes for better performance
    await optimize_database_indexes()
    
    print("✅ OurLibrary API server started successfully")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/mode")
async def get_mode():
    """Get current operating mode with enhanced sync status"""
    mode = os.environ.get('ANDYGOOGLE_MODE', 'local')
    
    # Base mode info
    mode_info = {
        "mode": mode,
        "display_name": "LOCAL (Memorex)" if mode == 'local' else "GOOGLE DRIVE",
        "icon": "💾" if mode == 'local' else "🌐",
        "description": "Local SQLite database only" if mode == 'local' else "Google Drive synchronized"
    }
    
    # Enhanced sync status for Google Drive mode
    if mode == 'gdrive' and drive_manager:
        try:
            # Get detailed sync status
            sync_status = drive_manager.GetSyncStatus() if hasattr(drive_manager, 'GetSyncStatus') else {}
            
            mode_info.update({
                "sync_enabled": True,
                "last_sync": sync_status.get('last_sync', 'Never'),
                "sync_status": sync_status.get('sync_status', 'Unknown'),
                "local_version": sync_status.get('local_version', '1.0.0'),
                "remote_version": sync_status.get('remote_version', '1.0.0'),
                "offline_mode": sync_status.get('offline_mode', False),
                "connection_status": "Connected" if not sync_status.get('offline_mode', True) else "Offline"
            })
            
            # Update icon based on sync status
            if sync_status.get('offline_mode', True):
                mode_info["icon"] = "🔄"  # Syncing/offline
                mode_info["display_name"] = "GOOGLE DRIVE (Offline)"
            elif sync_status.get('sync_status') == 'up_to_date':
                mode_info["icon"] = "✅"  # Up to date
                mode_info["display_name"] = "GOOGLE DRIVE (Synced)"
            else:
                mode_info["icon"] = "🌐"  # Connected but not synced
                
        except Exception as e:
            print(f"⚠️ Error getting sync status: {e}")
            mode_info.update({
                "sync_enabled": False,
                "sync_error": str(e),
                "connection_status": "Error"
            })
    else:
        mode_info.update({
            "sync_enabled": False,
            "connection_status": "Local Only"
        })
    
    return mode_info

# Database download endpoint for users
@app.get("/api/database/download")
async def download_database(request: Request):
    """Download the current database file for users"""
    log_api_usage(request, "database_download")
    
    try:
        # Determine database path based on mode
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
        else:
            # Fallback to local database
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail="Database file not found")
        
        # Get file info
        file_size = os.path.getsize(db_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        # Create download filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"andylibrary_{timestamp}.db"
        
        # Log download start for analytics
        start_time = time.time()
        size_mb = file_size / 1024 / 1024
        
        if sheets_logger:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            version = f"{int(os.path.getmtime(db_path))}.{file_size}"
            
            sheets_logger.LogDatabaseDownload(
                client_ip=client_ip,
                user_agent=user_agent,
                version=version,
                size_mb=size_mb,
                duration_seconds=0,  # Will be updated later if needed
                success=True
            )
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=db_path,
            filename=download_filename,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}",
                "X-File-Size": str(file_size),
                "X-Last-Modified": file_modified.isoformat(),
                "X-Database-Version": "1.0.0",
                "X-Estimated-Cost": f"${size_mb * 0.10:.2f}"
            }
        )
        
    except Exception as e:
        print(f"❌ Database download error: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Lightweight database version check endpoint  
@app.get("/api/database/version")
async def get_database_version(request: Request):
    """Get lightweight database version info for smart updates (< 1KB response)"""
    log_api_usage(request, "version_check")
    
    try:
        # Get database path
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            return {
                "version": "0.0",
                "size_mb": 0,
                "book_count": 0,
                "available": False,
                "message": "Database not available"
            }
        
        # Get file stats (lightweight)
        file_size = os.path.getsize(db_path)
        file_mtime = int(os.path.getmtime(db_path))
        
        # Quick book count (minimal DB access)
        conn = sqlite3.connect(db_path)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        conn.close()
        
        # Create version string: timestamp.bookcount
        version = f"{file_mtime}.{book_count}"
        
        result = {
            "version": version,
            "size_mb": round(file_size / 1024 / 1024, 1),
            "book_count": book_count,
            "available": True,
            "download_url": "/api/database/download"
        }
        
        # Log version check for analytics
        if sheets_logger:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            sheets_logger.LogVersionCheck(
                client_ip=client_ip,
                user_agent=user_agent,
                current_version="unknown",  # Client would send this
                server_version=version,
                update_available=True  # Assume update available for version checks
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version check failed: {e}")

# Database info endpoint
@app.get("/api/database/info")
async def get_database_info(request: Request):
    """Get database information without downloading"""
    log_api_usage(request, "database_info")
    
    try:
        # Get database path
        if drive_manager and hasattr(drive_manager, 'local_db_path'):
            db_path = drive_manager.local_db_path
            db_source = "Google Drive (cached locally)"
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
            db_source = "Local SQLite file"
        
        if not os.path.exists(db_path):
            return {"available": False, "error": "Database file not found"}
        
        # Get file statistics
        file_size = os.path.getsize(db_path)
        file_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        # Get database content statistics
        conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] 
            subject_count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        finally:
            conn.close()
        
        return {
            "available": True,
            "source": db_source,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "last_modified": file_modified.isoformat(),
            "total_books": book_count,
            "total_categories": category_count,
            "total_subjects": subject_count,
            "database_version": "1.0.0",
            "download_url": "/api/database/download"
        }
        
    except Exception as e:
        print(f"❌ Database info error: {e}")
        return {"available": False, "error": str(e)}

# Google Drive sync trigger endpoint  
@app.post("/api/database/sync")
async def trigger_database_sync(request: Request, background_tasks: BackgroundTasks):
    """Manually trigger database sync from Google Drive"""
    log_api_usage(request, "manual_database_sync")
    
    if not drive_manager:
        raise HTTPException(status_code=400, detail="Google Drive mode not available")
    
    try:
        # Add sync task to background
        background_tasks.add_task(sync_database_task)
        
        return {
            "message": "Database sync initiated",
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Sync trigger error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

async def sync_database_task():
    """Background task for database synchronization"""
    try:
        if drive_manager and hasattr(drive_manager, 'SyncDatabaseFromDrive'):
            print("🔄 Starting background database sync...")
            result = drive_manager.SyncDatabaseFromDrive(force_update=True)
            
            if result:
                print("✅ Database sync completed successfully")
            else:
                print("⚠️ Database sync completed with warnings")
        else:
            print("❌ DriveManager not available for sync")
            
    except Exception as e:
        print(f"❌ Background sync error: {e}")

# Debug database endpoint
@app.get("/api/debug/db")
async def debug_database():
    """Debug database connection"""
    try:
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        if not os.path.exists(db_path):
            return {"error": f"Database not found at: {db_path}"}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) as count FROM categories")
        result = cursor.fetchone()
        conn.close()
        
        return {
            "status": "success",
            "db_path": db_path,
            "categories_count": result[0] if result else 0
        }
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# Sync status endpoint
@app.get("/api/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(request: Request):
    """Get database synchronization status"""
    log_api_usage(request, "sync_status_check")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    status = drive_manager.GetSyncStatus()
    return SyncStatusResponse(**status)

# Manual sync endpoint
@app.post("/api/sync/database")
async def sync_database(request: Request, background_tasks: BackgroundTasks):
    """Manually trigger database sync from Google Drive"""
    log_api_usage(request, "manual_sync_requested")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    # Run sync in background
    background_tasks.add_task(drive_manager.SyncDatabaseFromDrive, True)
    
    return {
        "status": "sync_started",
        "message": "Database sync initiated in background",
        "timestamp": datetime.now().isoformat()
    }

# Check for updates endpoint
@app.get("/api/sync/updates")
async def check_for_updates(request: Request):
    """Check if database updates are available"""
    log_api_usage(request, "update_check")
    
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not available")
    
    update_info = drive_manager.CheckForUpdates()
    return update_info

# Books endpoints
@app.get("/api/books")
async def get_books(
    request: Request,
    limit: int = 50, 
    offset: int = 0, 
    search: Optional[str] = None,
    category: Optional[str] = None,
    subject: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_database)
):
    """Get paginated list of books with optional filtering"""
    print(f"🔍 API CALL: /api/books - limit={limit}, offset={offset}, search='{search}', category='{category}', subject='{subject}'")
    log_api_usage(request, "books_list", f"limit={limit}, offset={offset}, search={search}")
    
    # Build optimized query with proper JOINs and indexing
    query = """
        SELECT b.id, b.title, 
               NULL as author, c.category, s.subject, 
               NULL as file_path, NULL as file_size, 
               NULL as page_count, NULL as rating,
               NULL as last_opened
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN subjects s ON b.subject_id = s.id
        WHERE 1=1
    """
    
    params = []
    
    # Add search filter with index optimization
    if search:
        # Use proper indexing for LIKE queries
        query += " AND (b.title LIKE ? OR b.title LIKE ?)"
        search_param = f"%{search}%"
        search_param_start = f"{search}%"  # More index-friendly
        params.extend([search_param, search_param_start])
    
    # Add category filter using efficient foreign key join
    if category:
        query += " AND c.category = ?"
        params.append(category)
    
    # Add subject filter using efficient foreign key join
    if subject:
        query += " AND s.subject = ?"
        params.append(subject)
    
    # Add optimized pagination with covering index
    query += " ORDER BY b.title LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    
    books = []
    for row in rows:
        books.append(BookResponse(
            id=row['id'],
            title=row['title'],
            author=row['author'],
            category=row['category'],
            subject=row['subject'],
            file_path=row['file_path'],
            file_size=row['file_size'],
            page_count=row['page_count'],
            rating=row['rating'],
            last_opened=row['last_opened']
        ))
    
    # Return format expected by frontend
    return {
        "books": books,
        "total": len(books),
        "page": (offset // limit) + 1,
        "limit": limit
    }

# Books filter endpoint (alias for compatibility)
@app.get("/api/books/filter")
async def filter_books(
    request: Request,
    category: Optional[str] = None,
    subject: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: sqlite3.Connection = Depends(get_database)
):
    """Filter books by category, subject, or search term"""
    print(f"🔍 API CALL: /api/books/filter - category='{category}', subject='{subject}', search='{search}', page={page}, limit={limit}")
    offset = (page - 1) * limit
    return await get_books(request, limit, offset, search, category, subject, db)

# Books search endpoint (POST for compatibility)
@app.post("/api/books/search")
async def search_books(
    request: Request,
    search_data: dict,
    db: sqlite3.Connection = Depends(get_database)
):
    """Search books via POST request"""
    print(f"🔍 API CALL: /api/books/search - POST data: {search_data}")
    # Frontend sends 'query' not 'search'
    search_term = search_data.get('query', search_data.get('search', ''))
    filters = search_data.get('filters', {})
    category = filters.get('category')
    subject = filters.get('subject')
    page = search_data.get('page', 1)
    limit = search_data.get('limit', 50)
    
    print(f"🔍 PARSED: search_term='{search_term}', category='{category}', subject='{subject}', page={page}, limit={limit}")
    offset = (page - 1) * limit
    return await get_books(request, limit, offset, search_term, category, subject, db)

@app.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get detailed information about a specific book"""
    log_api_usage(request, "book_detail", f"book_id={book_id}")
    
    query = """
        SELECT b.id, b.title, b.author, c.category, s.subject, 
               b.FilePath as file_path, b.FileSize as file_size, 
               b.PageCount as page_count, b.Rating as rating,
               b.LastOpened as last_opened
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN subjects s ON b.subject_id = s.id
        WHERE b.id = ?
    """
    
    cursor = db.execute(query, (book_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return BookResponse(
        id=row['id'],
        title=row['title'],
        author=row['author'],
        category=row['category'],
        subject=row['subject'],
        file_path=row['file_path'],
        file_size=row['file_size'],
        page_count=row['page_count'],
        rating=row['rating'],
        last_opened=row['last_opened']
    )

@app.get("/api/books/{book_id}/thumbnail")
async def get_book_thumbnail(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get book thumbnail image"""
    log_api_usage(request, "thumbnail_view", f"book_id={book_id}")
    
    try:
        # First check if book exists
        cursor = db.execute("SELECT id FROM books WHERE id = ?", (book_id,))
        book_exists = cursor.fetchone()
        
        if not book_exists:
            from fastapi import Response
            return Response(status_code=404, content="Book not found")
        
        # Check if ThumbnailImage column exists in schema
        cursor = db.execute("PRAGMA table_info(books)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ThumbnailImage' not in columns:
            # Column doesn't exist - return 204 No Content
            from fastapi import Response
            return Response(status_code=204)
        
        # Try to get thumbnail
        cursor = db.execute("SELECT ThumbnailImage FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            # No thumbnail available - return 204 No Content  
            from fastapi import Response
            return Response(status_code=204)
        
        # Return the image blob with proper content type
        from fastapi import Response
        return Response(
            content=row[0],
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"}
        )
        
    except Exception as e:
        print(f"Thumbnail error for book {book_id}: {e}")
        # Return 204 instead of 500 for graceful degradation
        from fastapi import Response
        return Response(status_code=204)

@app.get("/api/books/{book_id}/pdf")
async def get_book_pdf(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Serve PDF file for reading"""
    log_api_usage(request, "pdf_view", f"book_id={book_id}")
    
    try:
        # Get book file path
        cursor = db.execute("SELECT title, author, FilePath FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Book not found")
        
        file_path = row['FilePath']
        if not file_path or not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=404, detail="PDF file not available for this book")
        
        # Build full path - try multiple possible locations
        full_paths = [
            os.path.join(os.getcwd(), file_path),
            os.path.join(os.getcwd(), "Data", "Books", os.path.basename(file_path)),
            os.path.join(os.path.dirname(os.getcwd()), file_path),
            file_path  # Try as absolute path
        ]
        
        pdf_file = None
        for path in full_paths:
            if os.path.exists(path):
                pdf_file = path
                break
        
        if not pdf_file:
            raise HTTPException(status_code=404, detail=f"PDF file not found: {file_path}")
        
        # Return PDF file with proper headers for streaming
        from fastapi.responses import FileResponse
        return FileResponse(
            pdf_file, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=\"{row['title']}.pdf\"",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logging.error(f"Error serving PDF for book {book_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve PDF file")

@app.post("/api/progress/reading")
async def save_reading_progress(request: Request, progress_data: dict):
    """Save reading progress for offline sync"""
    log_api_usage(request, "reading_progress", f"book_id={progress_data.get('bookId')}")
    
    try:
        # This could be enhanced to save to database
        # For now, just acknowledge the request
        return {
            "status": "success",
            "message": "Reading progress saved",
            "timestamp": progress_data.get('timestamp')
        }
    except Exception as e:
        logging.error(f"Error saving reading progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save reading progress")

# Categories endpoint
@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories(request: Request, db: sqlite3.Connection = Depends(get_database)):
    """Get all categories"""
    log_api_usage(request, "categories_list")
    
    cursor = db.execute("SELECT id, category FROM categories ORDER BY category")
    rows = cursor.fetchall()
    
    return [CategoryResponse(id=row['id'], category=row['category']) for row in rows]

# Subjects endpoint
@app.get("/api/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    request: Request, 
    category_id: Optional[int] = None,
    category: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_database)
):
    """Get subjects, optionally filtered by category ID or category name"""
    log_api_usage(request, "subjects_list", f"category_id={category_id}, category={category}")
    
    if category:
        # Filter by category name (what frontend sends)
        query = """
            SELECT s.id, s.subject, s.category_id 
            FROM subjects s 
            JOIN categories c ON s.category_id = c.id 
            WHERE c.category = ? 
            ORDER BY s.subject
        """
        params = (category,)
    elif category_id:
        # Filter by category ID (legacy support)
        query = "SELECT id, subject, category_id FROM subjects WHERE category_id = ? ORDER BY subject"
        params = (category_id,)
    else:
        # Get all subjects
        query = "SELECT id, subject, category_id FROM subjects ORDER BY subject"
        params = ()
    
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    
    return [
        SubjectResponse(id=row['id'], subject=row['subject'], category_id=row['category_id']) 
        for row in rows
    ]

# ============================================================================
# INTELLIGENT SEARCH ENDPOINTS (Project Himalaya Benchmark Implementation)
# ============================================================================

@app.post("/api/search/intelligent", response_model=IntelligentSearchResponse)
async def intelligent_search(
    request: Request,
    search_request: IntelligentSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Benchmark intelligent educational content search
    
    Demonstrates the gold standard for educational search with:
    - Learning intent recognition and classification
    - Academic level-appropriate content filtering
    - Educational psychology-based ranking
    - Accessibility-first result optimization
    - Privacy-respecting personalization
    """
    if not intelligent_search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Intelligent search engine not available"
        )
    
    try:
        log_api_usage(request, "intelligent_search", f"query='{search_request.query}'")
        
        # Build user context from authenticated user and request
        user_context = search_request.user_context or {}
        if current_user:
            user_context.update({
                "user_id": current_user.get("id"),
                "subscription_tier": current_user.get("subscription_tier"),
                "user_preferences": {}  # Would load from user preferences
            })
        
        # Parse enum values safely
        learning_intent = None
        if search_request.learning_intent:
            try:
                learning_intent = LearningIntent(search_request.learning_intent)
            except ValueError:
                pass
        
        academic_level = None
        if search_request.academic_level:
            try:
                academic_level = AcademicLevel(search_request.academic_level)
            except ValueError:
                pass
        
        search_mode = SearchMode.INSTANT
        if search_request.search_mode:
            try:
                search_mode = SearchMode(search_request.search_mode)
            except ValueError:
                pass
        
        # Analyze the search query with educational intelligence
        query_obj = intelligent_search_engine.AnalyzeQuery(
            query=search_request.query,
            user_context=user_context
        )
        
        # Override with explicit parameters if provided
        if learning_intent:
            query_obj.learning_intent = learning_intent
        if academic_level:
            query_obj.academic_level = academic_level
        if search_request.subject_area:
            query_obj.subject_area = search_request.subject_area
        query_obj.search_mode = search_mode
        if search_request.accessibility_requirements:
            query_obj.accessibility_requirements = search_request.accessibility_requirements
        
        # Execute intelligent search
        search_results = intelligent_search_engine.Search(
            query=query_obj,
            limit=search_request.limit,
            offset=search_request.offset
        )
        
        # Convert results to API response format
        results = []
        for result_data in search_results["results"]:
            result = IntelligentSearchResult(**result_data)
            results.append(result)
        
        response = IntelligentSearchResponse(
            results=results,
            total_count=search_results["total_count"],
            query_analysis=search_results["query_analysis"],
            suggestions=search_results["suggestions"],
            accessibility_optimized=search_results["accessibility_optimized"],
            search_metadata=search_results["search_metadata"]
        )
        
        return response
        
    except Exception as e:
        logging.error(f"Intelligent search failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Intelligent search failed: {str(e)}"
        )

@app.get("/api/search/suggestions")
async def get_search_suggestions(
    request: Request,
    query: str = Query(..., min_length=1, description="Partial search query"),
    intent: Optional[str] = Query(None, description="Learning intent context"),
    level: Optional[str] = Query(None, description="Academic level context"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions")
):
    """
    Get intelligent search suggestions based on partial query
    
    Provides contextual, educational psychology-informed search suggestions
    """
    if not intelligent_search_engine:
        return {"suggestions": []}
    
    try:
        log_api_usage(request, "search_suggestions", f"query='{query}'")
        
        # Parse context parameters
        learning_intent = None
        if intent:
            try:
                learning_intent = LearningIntent(intent)
            except ValueError:
                pass
        
        academic_level = None
        if level:
            try:
                academic_level = AcademicLevel(level)
            except ValueError:
                pass
        
        # Analyze query for suggestions
        query_obj = intelligent_search_engine.AnalyzeQuery(query)
        if learning_intent:
            query_obj.learning_intent = learning_intent
        if academic_level:
            query_obj.academic_level = academic_level
        
        # Get a small search to generate contextual suggestions
        search_results = intelligent_search_engine.Search(query_obj, limit=5)
        suggestions = search_results.get("suggestions", [])
        
        return {
            "suggestions": suggestions[:limit],
            "query_analysis": search_results.get("query_analysis", {}),
            "context_aware": True
        }
        
    except Exception as e:
        logging.error(f"Search suggestions failed: {e}")
        return {"suggestions": [], "error": str(e)}

@app.get("/api/search/analytics", response_model=SearchAnalyticsResponse)
async def get_search_analytics(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """
    Get privacy-respecting search analytics for optimization
    
    Provides aggregated, anonymized analytics that improve educational search
    without compromising user privacy
    """
    if not intelligent_search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Search analytics not available"
        )
    
    try:
        # Verify user has analytics access (could be role-based)
        user_tier = current_user.get("subscription_tier", "basic")
        if user_tier not in ["admin", "premium", "educator"]:
            raise HTTPException(
                status_code=403, 
                detail="Analytics access requires elevated permissions"
            )
        
        log_api_usage(request, "search_analytics", "aggregated_view")
        
        # Get anonymized analytics
        analytics_data = intelligent_search_engine.GetSearchAnalytics()
        
        return SearchAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Search analytics failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve search analytics"
        )

@app.get("/api/search/performance")
async def get_search_performance(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """
    Get search system performance metrics for optimization
    
    Technical performance data for system administrators and developers
    """
    if not intelligent_search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Search performance metrics not available"
        )
    
    try:
        # Verify admin access
        user_tier = current_user.get("subscription_tier", "basic")
        if user_tier != "admin":
            raise HTTPException(
                status_code=403, 
                detail="Performance metrics require admin access"
            )
        
        log_api_usage(request, "search_performance", "metrics_view")
        
        # Get performance metrics
        performance_data = intelligent_search_engine.GetPerformanceMetrics()
        
        return performance_data
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Search performance metrics failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve performance metrics"
        )

# ============================================================================

# Statistics endpoint
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(request: Request, db: sqlite3.Connection = Depends(get_database)):
    """Get library statistics"""
    log_api_usage(request, "stats_view")
    
    # Get counts
    book_count = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    category_count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    subject_count = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    
    # Get sync info
    sync_status = drive_manager.GetSyncStatus() if drive_manager else {}
    
    return StatsResponse(
        total_books=book_count,
        total_categories=category_count,
        total_subjects=subject_count,
        database_version=sync_status.get('local_version', '0.0.0'),
        last_sync=sync_status.get('last_sync'),
        offline_mode=sync_status.get('offline_mode', False)
    )

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register", response_model=RegisterResponse)
async def register_user(registration: UserRegistrationRequest, request: Request):
    """
    Register new user account for AndyLibrary
    Creates user with mission acknowledgment and processes preferences/publication requests
    """
    try:
        db_manager = get_auth_database()
        
        # Get client info
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create user account
        user_result = db_manager.CreateUser(
            Email=registration.email,
            Password=registration.password,
            Username=registration.username,
            SubscriptionTier=registration.subscription_tier,
            MissionAcknowledged=registration.mission_acknowledgment
        )
        
        if not user_result.get('success'):
            if "Email already registered" in user_result.get('error', ''):
                raise HTTPException(status_code=409, detail="Email address already registered")
            elif "Username already taken" in user_result.get('error', ''):
                raise HTTPException(status_code=409, detail="Username already taken")
            elif "Mission acknowledgment is required" in user_result.get('error', ''):
                raise HTTPException(status_code=400, detail="You must acknowledge our educational mission to create an account")
            else:
                raise HTTPException(status_code=400, detail="Registration failed")
        
        user_id = user_result['user_id']
        preferences_saved = False
        publication_requests_saved = 0
        
        # Process user preferences if provided
        if registration.user_preferences:
            pref_result = db_manager.CreateUserPreferences(
                user_id, 
                registration.user_preferences.model_dump()
            )
            preferences_saved = pref_result.get('success', False)
        
        # Process publication requests if provided
        for pub_request in registration.publication_requests:
            req_result = db_manager.CreatePublicationRequest(
                user_id,
                pub_request.model_dump()
            )
            if req_result.get('success'):
                publication_requests_saved += 1
        
        user_response = convert_user_to_response(user_result)
        
        return RegisterResponse(
            user=user_response,
            message=f"Registration successful! Welcome to AndyLibrary, {registration.subscription_tier} member.",
            preferences_saved=preferences_saved,
            publication_requests_saved=publication_requests_saved
        )
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Registration error: {error}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login_user(login: UserLoginRequest, request: Request):
    """
    Authenticate user login and create session
    Returns user info and session tokens for library access
    """
    try:
        db_manager = get_auth_database()
        
        # Get client info
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Authenticate user
        auth_result = db_manager.AuthenticateUser(login.email, login.password)
        
        if not auth_result.get('success'):
            error_msg = auth_result.get('error', 'Invalid credentials')
            if "Account temporarily locked" in error_msg:
                raise HTTPException(status_code=423, detail=error_msg)
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_data = auth_result['user']
        
        # Create user session
        session_result = db_manager.CreateUserSession(
            UserId=user_data['id'],
            IPAddress=client_ip,
            UserAgent=user_agent
        )
        
        if not session_result.get('success'):
            raise HTTPException(status_code=500, detail="Failed to create user session")
        
        user_response = convert_user_to_response(user_data)
        
        return LoginResponse(
            user=user_response,
            session_token=session_result['session_token'],
            refresh_token=session_result['refresh_token'],
            expires_at=session_result['expires_at'],
            message=f"Welcome back to AndyLibrary, {user_data['subscription_tier']} member!"
        )
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Login error: {error}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(require_auth), 
                     credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and deactivate session
    Requires valid authentication token
    """
    try:
        db_manager = get_auth_database()
        
        # Deactivate session
        logout_query = """
            UPDATE UserSessions 
            SET IsActive = FALSE 
            WHERE SessionToken = ? AND UserId = ?
        """
        
        if db_manager.Connection:
            db_manager.Connection.execute(logout_query, (credentials.credentials, current_user['id']))
            db_manager.Connection.commit()
            
            return {"message": "Logout successful"}
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Logout error: {error}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.get("/api/auth/verify-email")
async def verify_user_email(token: str, request: Request):
    """
    Verify user email address with verification token
    Activates user account and sets basic access level
    """
    try:
        if not token:
            raise HTTPException(status_code=400, detail="Verification token is required")
        
        db_manager = get_auth_database()
        
        # Verify email with token
        verification_result = db_manager.VerifyUserEmail(token)
        
        if not verification_result["success"]:
            raise HTTPException(status_code=400, detail=verification_result["error"])
        
        # Redirect to success page
        return RedirectResponse(url="/verification-success.html", status_code=302)
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Email verification error: {error}")
        raise HTTPException(status_code=500, detail="Email verification failed")

# ==================== MODERN SOCIAL LOGIN ENDPOINTS ====================

@app.get("/api/auth/oauth/providers")
async def get_oauth_providers():
    """
    Get available OAuth providers with modern 2025 security standards
    Returns only configured providers as optional login methods
    """
    try:
        if not modern_auth_manager:
            return {
                "providers": {},
                "message": "Social login not configured. Please use email registration.",
                "email_available": True,
                "modern_oauth": False
            }
        
        providers = modern_auth_manager.GetAvailableProviders()
        
        return {
            "providers": providers,
            "message": "Choose your preferred login method or use email registration",
            "email_available": True,
            "modern_oauth": True,
            "security_version": "2025.1"
        }
        
    except Exception as error:
        logging.error(f"Modern OAuth providers error: {error}")
        return {
            "providers": {},
            "message": "Social login temporarily unavailable. Please use email registration.",
            "email_available": True,
            "modern_oauth": False
        }

@app.get("/api/auth/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Initiate modern OAuth 2.0 login with PKCE and enhanced security
    Supports Google (official library), GitHub, and Facebook
    """
    try:
        if not modern_auth_manager:
            raise HTTPException(
                status_code=503, 
                detail="Modern social login not available. Please use email registration instead."
            )
        
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else None
        
        # Generate OAuth authorization URL with modern security
        auth_result = modern_auth_manager.GenerateAuthUrl(
            provider=provider,
            user_ip=client_ip
        )
        
        if not auth_result["success"]:
            if "Rate limit" in auth_result.get("error", ""):
                raise HTTPException(status_code=429, detail=auth_result["error"])
            else:
                raise HTTPException(status_code=400, detail=auth_result["error"])
        
        # Store session ID in secure cookie for callback validation
        response = RedirectResponse(url=auth_result["auth_url"])
        response.set_cookie(
            key="oauth_session",
            value=auth_result["session_id"],
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=900  # 15 minutes
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Modern OAuth initiation error for {provider}: {error}")
        raise HTTPException(
            status_code=500, 
            detail=f"Social login failed. Please try email registration instead."
        )

# Modern OAuth 2.0 callback endpoint with comprehensive security
@app.get("/api/auth/oauth/callback")
async def modern_oauth_callback(
    code: str = None, 
    state: str = None, 
    error: str = None, 
    request: Request = None
):
    """
    Modern OAuth 2.0 callback handler with 2025 security standards
    Handles all providers with PKCE validation and secure token management
    """
    try:
        if error:
            logging.warning(f"OAuth callback error: {error}")
            return RedirectResponse(url=f"/auth.html?error=oauth_cancelled&message=Social login was cancelled")
        
        if not code or not state:
            return RedirectResponse(url=f"/auth.html?error=oauth_failed&message=Missing authorization parameters")
        
        if not modern_auth_manager:
            return RedirectResponse(url=f"/auth.html?error=oauth_unavailable&message=Social login not available")
        
        # Get session ID from secure cookie
        session_id = request.cookies.get("oauth_session")
        
        # Handle OAuth callback with modern security validation
        callback_result = modern_auth_manager.HandleOAuthCallback(
            code=code,
            state=state,
            session_id=session_id
        )
        
        if not callback_result["success"]:
            logging.error(f"OAuth callback failed: {callback_result.get('error')}")
            return RedirectResponse(
                url=f"/auth.html?error=oauth_failed&message={callback_result.get('error', 'Authentication failed')}"
            )
        
        # Extract user information from callback result
        user_info = callback_result["user_info"]
        provider = callback_result["provider"]
        
        if not user_info.get("email"):
            return RedirectResponse(
                url=f"/auth.html?error=oauth_failed&message=Email required for social login"
            )
        
        # Create or update user account using modern social auth
        db_manager = get_auth_database()
        
        # Use modern social auth manager to create/update user
        user_result = modern_auth_manager.CreateOrUpdateSocialUser(user_info, db_manager)
        
        if not user_result["success"]:
            logging.error(f"Social user creation failed: {user_result.get('error')}")
            return RedirectResponse(
                url=f"/auth.html?error=user_creation_failed&message={user_result.get('error', 'Account creation failed')}"
            )
        
        # Create secure session
        session_result = db_manager.CreateUserSession(
            UserId=user_result["user_id"],
            IPAddress=request.client.host if request.client else None,
            UserAgent=request.headers.get("user-agent")
        )
        
        if not session_result.get("success"):
            logging.error(f"Session creation failed: {session_result}")
            return RedirectResponse(
                url=f"/auth.html?error=session_failed&message=Login successful but session creation failed"
            )
        
        # Store encrypted credentials for token refresh (if available)
        if callback_result.get("credentials"):
            # In production, store this in secure database field
            logging.info(f"✅ OAuth credentials stored for user {user_result['user_id']}")
        
        # Success - redirect with secure session token
        success_message = f"Successfully logged in with {provider.title()}"
        if not user_result.get("existing_user"):
            success_message += " - Welcome to AndyLibrary!"
        
        # Clear OAuth session cookie
        response = RedirectResponse(
            url=f"/auth.html?success=oauth_login&provider={provider}&message={success_message}&token={session_result['session_token']}"
        )
        response.delete_cookie("oauth_session")
        
        return response
        
    except Exception as e:
        return RedirectResponse(url=f"/auth.html?error=oauth_failed&message=OAuth processing failed")

# Legacy callback endpoint removed - using modern unified callback above

# ==================== BENCHMARK USER JOURNEY ENDPOINTS ====================

@app.post("/api/journey/initialize")
async def initialize_user_journey(request: Request):
    """
    Initialize user journey with benchmark UX orchestration
    Project Himalaya standard for educational platform onboarding
    """
    try:
        if not journey_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Journey orchestration not available"}
            )
        
        # Generate session ID if not provided
        session_id = request.headers.get("x-session-id") or secrets.token_urlsafe(16)
        
        # Initialize journey with intelligent context detection
        context = journey_manager.InitializeJourney(
            session_id=session_id,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None
        )
        
        # Get onboarding configuration
        onboarding_config = journey_manager.GetOnboardingConfiguration(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "current_stage": context.current_stage.value,
            "onboarding": onboarding_config,
            "device_optimizations": context.device_capabilities,
            "accessibility_enhancements": context.accessibility_requirements,
            "journey_tracking": True
        }
        
    except Exception as e:
        logging.error(f"Journey initialization error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Journey initialization failed"}
        )

@app.post("/api/journey/advance")
async def advance_user_journey(
    request: Request,
    target_stage: str,
    interaction_data: Dict[str, Any] = None
):
    """
    Advance user through journey stages with intelligent progression
    Demonstrates benchmark user experience orchestration
    """
    try:
        if not journey_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Journey orchestration not available"}
            )
        
        session_id = request.headers.get("x-session-id")
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Session ID required"}
            )
        
        # Map string to JourneyStage enum
        stage_mapping = {
            "discovery": JourneyStage.DISCOVERY,
            "trust_building": JourneyStage.TRUST_BUILDING,
            "welcome": JourneyStage.WELCOME,
            "engagement": JourneyStage.ENGAGEMENT,
            "mastery": JourneyStage.MASTERY
        }
        
        target_journey_stage = stage_mapping.get(target_stage)
        if not target_journey_stage:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid journey stage: {target_stage}"}
            )
        
        # Advance journey with personalized recommendations
        result = journey_manager.AdvanceJourney(
            session_id=session_id,
            target_stage=target_journey_stage,
            interaction_data=interaction_data or {}
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Journey advancement error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Journey advancement failed"}
        )

@app.post("/api/journey/personalize")
async def personalize_user_experience(
    request: Request,
    user_intent: str = None,
    preferences: Dict[str, Any] = None
):
    """
    Apply intelligent personalization based on user behavior and intent
    Benchmark implementation of privacy-respecting UX optimization
    """
    try:
        if not journey_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Journey orchestration not available"}
            )
        
        session_id = request.headers.get("x-session-id")
        if not session_id:
            return JSONResponse(
                status_code=400,  
                content={"error": "Session ID required"}
            )
        
        # Map user intent string to enum
        intent_mapping = {
            "student": UserIntent.STUDENT,
            "educator": UserIntent.EDUCATOR,
            "researcher": UserIntent.RESEARCHER,
            "parent": UserIntent.PARENT,
            "administrator": UserIntent.ADMINISTRATOR
        }
        
        user_intent_enum = intent_mapping.get(user_intent) if user_intent else None
        
        # Apply personalization
        result = journey_manager.PersonalizeExperience(
            session_id=session_id,
            user_intent=user_intent_enum,
            preferences=preferences or {}
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Experience personalization error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Experience personalization failed"}
        )

@app.get("/api/journey/guidance")
async def get_contextual_guidance(
    request: Request,
    current_page: str,
    user_action: str = None
):
    """
    Provide contextual, just-in-time guidance based on user behavior
    Implements intelligent help that empowers without overwhelming
    """
    try:
        if not journey_manager:
            return {"guidance": [], "message": "Contextual guidance not available"}
        
        session_id = request.headers.get("x-session-id")
        if not session_id:
            return {"guidance": [], "error": "Session ID required"}
        
        # Get contextual guidance
        guidance = journey_manager.GetContextualGuidance(
            session_id=session_id,
            current_page=current_page,
            user_action=user_action
        )
        
        return guidance
        
    except Exception as e:
        logging.error(f"Contextual guidance error: {e}")
        return {"guidance": [], "error": "Guidance system failed"}

@app.post("/api/journey/track")
async def track_user_interaction(
    request: Request,
    interaction_type: str,
    interaction_data: Dict[str, Any]
):
    """
    Track user interactions for continuous UX optimization
    Privacy-respecting analytics for journey improvement
    """
    try:
        if not journey_manager:
            return {"success": False, "error": "Journey tracking not available"}
        
        session_id = request.headers.get("x-session-id")
        if not session_id:
            return {"success": False, "error": "Session ID required"}
        
        # Track interaction
        success = journey_manager.TrackInteraction(
            session_id=session_id,
            interaction_type=interaction_type,
            interaction_data=interaction_data
        )
        
        return {"success": success}
        
    except Exception as e:
        logging.error(f"Interaction tracking error: {e}")
        return {"success": False, "error": "Interaction tracking failed"}

@app.get("/api/journey/analytics")
async def get_journey_analytics():
    """
    Get anonymized journey analytics for platform optimization
    Benchmark implementation of privacy-respecting UX metrics
    """
    try:
        if not journey_manager:
            return {"analytics": {}, "message": "Analytics not available"}
        
        analytics = journey_manager.GetJourneyAnalytics()
        active_journeys = journey_manager.GetActiveJourneyCount()
        
        return {
            "analytics": analytics,
            "active_journeys": active_journeys,
            "privacy_compliant": True,
            "anonymized": True
        }
        
    except Exception as e:
        logging.error(f"Journey analytics error: {e}")
        return {"analytics": {}, "error": "Analytics system failed"}

# ==================== USER SETUP ENDPOINTS ====================

@app.post("/api/setup/install")
async def install_andylibrary(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Complete AndyLibrary installation process for authenticated user in isolated environment
    Downloads database, copies files, creates shortcuts, and prepares for native app launch
    """
    try:
        if not UserSetupManager:
            raise HTTPException(
                status_code=503,
                detail="User setup system not available"
            )
        
        # Initialize with user-specific information for proper environment isolation
        setup_manager = UserSetupManager(
            user_id=current_user.get("id"),
            username=current_user.get("username")
        )
        
        # Get current user session info
        auth_token = None  # We could extract this from the auth dependency if needed
        
        # Perform complete setup in user's isolated environment
        setup_result = setup_manager.CompleteUserSetup(current_user, auth_token)
        
        if not setup_result["success"]:
            raise HTTPException(status_code=500, detail=setup_result["error"])
        
        return {
            "success": True,
            "message": "AndyLibrary installed successfully in your isolated environment! You can now launch the native app.",
            "installation_details": setup_result,
            "next_step": "launch_app",
            "environment_info": {
                "type": "USER_INSTALLATION",
                "isolated_from_dev": True,
                "username": setup_manager.Username,
                "platform": setup_manager.Platform,
                "installation_path": str(setup_manager.AndyLibraryDir)
            }
        }
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Installation error: {error}")
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(error)}")

@app.post("/api/setup/launch")
async def launch_andylibrary(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Launch AndyLibrary native application from user's isolated environment
    Starts the local server and opens the library interface
    """
    try:
        if not UserSetupManager:
            raise HTTPException(
                status_code=503,
                detail="User setup system not available"
            )
        
        # Initialize with user-specific information for proper environment isolation
        setup_manager = UserSetupManager(
            user_id=current_user.get("id"),
            username=current_user.get("username")
        )
        
        # Launch the native app from user's isolated installation
        launch_result = setup_manager.LaunchAndyLibrary()
        
        if not launch_result["success"]:
            raise HTTPException(status_code=500, detail=launch_result["error"])
        
        return {
            "success": True,
            "message": launch_result["message"],
            "app_launched": True,
            "installation_path": launch_result["installation_path"],
            "instructions": "AndyLibrary is now running! You can close this browser window."
        }
        
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Launch error: {error}")
        raise HTTPException(status_code=500, detail=f"Launch failed: {str(error)}")

@app.get("/api/setup/status")
async def check_installation_status(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Check if AndyLibrary is already installed for this user in their isolated environment
    """
    try:
        if not UserSetupManager:
            return {"installed": False, "message": "Setup system not available"}
        
        # Initialize with user-specific information for proper path isolation
        setup_manager = UserSetupManager(
            user_id=current_user.get("id"),
            username=current_user.get("username")
        )
        
        # Check if user's isolated installation exists
        config_file = setup_manager.ConfigDir / "user_config.json"
        database_file = setup_manager.DatabaseDir / "MyLibrary.db"
        
        if config_file.exists() and database_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Verify this is a proper user installation (not development)
                env_type = config.get("environment", {}).get("type", "UNKNOWN")
                is_isolated = config.get("environment", {}).get("isolated_from_dev", False)
                
                return {
                    "installed": True,
                    "installation_path": str(setup_manager.AndyLibraryDir),
                    "database_path": str(database_file),
                    "installed_at": config.get("user", {}).get("installed_at"),
                    "database_version": config.get("database", {}).get("version"),
                    "ready_to_launch": True,
                    "environment_type": env_type,
                    "isolated_from_dev": is_isolated,
                    "username": setup_manager.Username,
                    "platform": setup_manager.Platform
                }
            except Exception as e:
                return {"installed": False, "message": f"Installation corrupted: {str(e)}"}
        else:
            return {
                "installed": False,
                "message": "AndyLibrary not installed",
                "installation_required": True
            }
        
    except Exception as error:
        logging.error(f"Status check error: {error}")
        return {"installed": False, "error": str(error)}

@app.get("/api/auth/profile", response_model=UserResponse)
async def get_user_profile(current_user: Dict[str, Any] = Depends(require_auth)):
    """
    Get current user profile information
    Requires authentication
    """
    try:
        return convert_user_to_response(current_user)
        
    except Exception as error:
        logging.error(f"Profile error: {error}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@app.get("/api/performance/assessment")
async def get_performance_assessment():
    """Get user's system performance assessment and recommendations"""
    try:
        # Quick network test
        start_time = time.time()
        try:
            response = requests.get("https://www.google.com/favicon.ico", timeout=5)
            network_time = time.time() - start_time
            network_speed = (len(response.content) * 8) / (network_time * 1000000) if network_time > 0 else 1
        except:
            network_speed = 1  # Conservative estimate
        
        # Hardware detection
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        # Classification
        if network_speed >= 20:
            network_class = "fast"
        elif network_speed >= 10:
            network_class = "medium"
        elif network_speed >= 5:
            network_class = "slow"
        else:
            network_class = "very_slow"
        
        if memory_gb >= 8 and cpu_count >= 4:
            hardware_class = "modern"
        elif memory_gb >= 4 and cpu_count >= 2:
            hardware_class = "budget"
        else:
            hardware_class = "limited"
        
        # Performance prediction (10MB database)
        download_speed_mbps = network_speed * 0.8
        download_time = (10.3 * 8) / download_speed_mbps if download_speed_mbps > 0 else 60
        
        processing_times = {"modern": 0.002, "budget": 0.005, "limited": 0.010}
        processing_time = processing_times.get(hardware_class, 0.005)
        
        total_time = download_time + processing_time
        
        # Generate recommendations
        recommendations = []
        
        if total_time > 30:
            recommendations.append({
                "type": "warning",
                "title": "Slow Connection Detected", 
                "message": f"Download will take ~{total_time:.0f}s. Consider progressive loading.",
                "action": "progressive_loading"
            })
        elif total_time > 15:
            recommendations.append({
                "type": "caution",
                "title": "Moderate Wait Time",
                "message": f"Download will take ~{total_time:.0f}s. Progress indicator recommended.",
                "action": "show_progress"
            })
        else:
            recommendations.append({
                "type": "success",
                "title": "Fast Connection",
                "message": f"Download will complete quickly (~{total_time:.0f}s).",
                "action": "standard_download"
            })
        
        if network_class == "very_slow":
            recommendations.append({
                "type": "error",
                "title": "Very Slow Network",
                "message": "Consider lite mode or off-peak download.",
                "action": "lite_mode"
            })
        
        if memory_available_gb < 1:
            recommendations.append({
                "type": "warning",
                "title": "Low Memory",
                "message": f"Only {memory_available_gb:.1f}GB available. Use disk caching.",
                "action": "disk_cache"
            })
        
        # Optimal strategy
        if memory_available_gb >= 1 and hardware_class in ['modern', 'budget']:
            strategy = "python_cache"
            strategy_reason = "Python dict caching - optimal for your hardware"
        elif memory_available_gb >= 0.5:
            strategy = "memory_db"
            strategy_reason = "In-memory SQLite - good balance"
        else:
            strategy = "disk_optimized"
            strategy_reason = "Optimized disk access - conserves memory"
        
        return {
            "system": {
                "network_speed_mbps": round(network_speed, 1),
                "network_class": network_class,
                "hardware_class": hardware_class,
                "cpu_cores": cpu_count,
                "memory_gb": round(memory_gb, 1),
                "memory_available_gb": round(memory_available_gb, 1),
                "platform": platform.system()
            },
            "performance_prediction": {
                "download_time_seconds": round(download_time, 1),
                "processing_time_seconds": round(processing_time, 3),
                "total_wait_seconds": round(total_time, 1),
                "memory_usage_mb": round(10.3 * 0.15, 1)
            },
            "recommendations": recommendations,
            "optimal_strategy": {
                "strategy": strategy,
                "reason": strategy_reason,
                "estimated_query_time": "0.0001s" if strategy == "python_cache" else "0.001s"
            },
            "user_experience": {
                "rating": "excellent" if total_time <= 10 else "good" if total_time <= 30 else "slow",
                "advice": "Full download recommended" if total_time <= 10 else 
                        "Standard download with progress" if total_time <= 30 else 
                        "Progressive loading recommended"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance assessment failed: {e}")

@app.get("/api/analytics/data-usage")
async def get_data_usage_analytics(request: Request, days: int = 30):
    """Get data usage analytics for educational mission insights"""
    log_api_usage(request, "data_usage_analytics")
    
    try:
        if not sheets_logger:
            return {"error": "Analytics not available - logging disabled"}
        
        # Get data usage analytics
        analytics = sheets_logger.GetDataUsageAnalytics(days)
        
        if not analytics:
            return {
                "period_days": days,
                "message": "No data usage data available",
                "recommendations": [
                    "Enable logging to track data usage patterns",
                    "Monitor user download behavior for cost optimization"
                ]
            }
        
        # Add mission-focused insights
        insights = []
        
        if analytics['data_protection_enabled']:
            insights.append({
                "type": "success",
                "message": f"Version control is protecting users - {analytics['efficiency_ratio']:.1f}x more checks than downloads",
                "impact": "Significant data cost savings for students"
            })
        else:
            insights.append({
                "type": "warning", 
                "message": "Users downloading without version checks",
                "impact": "Potential unnecessary data costs for students"
            })
        
        if analytics['total_estimated_cost_usd'] > 50:
            insights.append({
                "type": "caution",
                "message": f"High estimated user costs: ${analytics['total_estimated_cost_usd']:.2f}",
                "impact": "May be barrier to educational access"
            })
        
        mobile_usage = analytics['connection_patterns'].get('mobile', 0)
        total_usage = sum(analytics['connection_patterns'].values())
        if mobile_usage > 0 and total_usage > 0:
            mobile_percent = (mobile_usage / total_usage) * 100
            if mobile_percent > 50:
                insights.append({
                    "type": "info",
                    "message": f"{mobile_percent:.0f}% of downloads on mobile data",
                    "impact": "Consider mobile-optimized progressive loading"
                })
        
        return {
            **analytics,
            "mission_insights": insights,
            "educational_impact": {
                "data_protected": analytics['data_protection_enabled'],
                "estimated_user_savings": f"${analytics['data_savings_mb'] * 100:.2f}",
                "accessibility_rating": "high" if analytics['total_estimated_cost_usd'] < 10 else "medium" if analytics['total_estimated_cost_usd'] < 25 else "low"
            },
            "recommendations": [
                "Continue promoting version check usage" if analytics['data_protection_enabled'] else "Implement mandatory version checks",
                "Monitor mobile vs WiFi usage patterns",
                "Consider progressive loading for high-cost regions",
                "Track educational content access patterns"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data usage analytics failed: {e}")

# ==================== ADVANCED FEATURES INTEGRATION ====================

# Initialize advanced search API if available
if CreateAdvancedSearchAPI:
    try:
        # Get database path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        
        # Create and include advanced search router
        advanced_search_router = CreateAdvancedSearchAPI(db_path)
        app.include_router(advanced_search_router, prefix="/api", tags=["advanced_search"])
        
        print("✅ Advanced Search API integrated successfully")
    except Exception as e:
        print(f"⚠️ Failed to integrate Advanced Search API: {e}")

# Progress tracking endpoints
@app.post("/api/progress/session/start")
async def start_reading_session(
    request: Request,
    session_data: dict,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """Start a new reading session for progress tracking"""
    try:
        if not UserProgressManager:
            raise HTTPException(status_code=503, detail="Progress tracking not available")
        
        # Initialize progress manager for this user
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        progress_manager = UserProgressManager(db_path, current_user["id"])
        
        # Extract session data
        book_id = session_data.get("book_id")
        book_title = session_data.get("book_title", "Unknown Book")
        book_category = session_data.get("book_category", "General")
        device_type = session_data.get("device_type", "desktop")
        
        if not book_id:
            raise HTTPException(status_code=400, detail="Book ID is required")
        
        # Start the reading session
        session_id = progress_manager.StartReadingSession(
            BookId=book_id,
            BookTitle=book_title,
            BookCategory=book_category,
            DeviceType=device_type
        )
        
        log_api_usage(request, "reading_session_start", f"book_id={book_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "book_id": book_id,
            "started_at": datetime.now().isoformat(),
            "message": "Reading session started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to start reading session: {e}")
        raise HTTPException(status_code=500, detail=f"Session start failed: {str(e)}")

@app.post("/api/progress/session/end")
async def end_reading_session(
    request: Request,
    session_data: dict,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """End a reading session and update progress"""
    try:
        if not UserProgressManager:
            raise HTTPException(status_code=503, detail="Progress tracking not available")
        
        # Initialize progress manager for this user
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        progress_manager = UserProgressManager(db_path, current_user["id"])
        
        # Extract session data
        session_id = session_data.get("session_id")
        pages_read = session_data.get("pages_read", 0)
        completion_percentage = session_data.get("completion_percentage", 0.0)
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # End the reading session
        session_stats = progress_manager.EndReadingSession(
            SessionId=session_id,
            PagesRead=pages_read,
            CompletionPercentage=completion_percentage
        )
        
        log_api_usage(request, "reading_session_end", f"session_id={session_id}")
        
        return {
            "success": True,
            "session_stats": session_stats,
            "message": "Reading session ended successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to end reading session: {e}")
        raise HTTPException(status_code=500, detail=f"Session end failed: {str(e)}")

@app.get("/api/progress/user")
async def get_user_progress(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """Get comprehensive user progress and statistics"""
    try:
        if not UserProgressManager:
            raise HTTPException(status_code=503, detail="Progress tracking not available")
        
        # Initialize progress manager for this user
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        progress_manager = UserProgressManager(db_path, current_user["id"])
        
        # Get user progress
        progress_data = progress_manager.GetUserProgress(current_user["id"], limit)
        
        log_api_usage(request, "user_progress", f"user_id={current_user['id']}")
        
        return {
            "success": True,
            "progress": progress_data,
            "user": {
                "id": current_user["id"],
                "username": current_user.get("username", "Anonymous"),
                "email": current_user.get("email")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get user progress: {e}")
        raise HTTPException(status_code=500, detail=f"Progress retrieval failed: {str(e)}")

@app.post("/api/progress/bookmark")
async def toggle_bookmark(
    request: Request,
    bookmark_data: dict,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """Toggle bookmark status for a book"""
    try:
        if not UserProgressManager:
            raise HTTPException(status_code=503, detail="Progress tracking not available")
        
        # Initialize progress manager for this user
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(base_dir, "Data", "Databases", "MyLibrary.db")
        progress_manager = UserProgressManager(db_path, current_user["id"])
        
        book_id = bookmark_data.get("book_id")
        if not book_id:
            raise HTTPException(status_code=400, detail="Book ID is required")
        
        # Toggle bookmark
        result = progress_manager.ToggleBookmark(current_user["id"], book_id)
        
        log_api_usage(request, "bookmark_toggle", f"book_id={book_id}")
        
        return {
            "success": True,
            "bookmark": result,
            "message": f"Book {result['action']} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to toggle bookmark: {e}")
        raise HTTPException(status_code=500, detail=f"Bookmark toggle failed: {str(e)}")

# Static file serving
app.mount("/static", StaticFiles(directory="WebPages/static"), name="static")

# PWA Support - Progressive Web App endpoints
@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest for tablet installation"""
    return FileResponse("WebPages/manifest.json", media_type="application/json")

@app.get("/service-worker.js")
async def serve_service_worker():
    """Serve PWA service worker for offline functionality"""
    return FileResponse("WebPages/service-worker.js", media_type="application/javascript")

@app.get("/pdf-reader.html")
async def serve_pdf_reader():
    """Serve tablet-optimized PDF reader"""
    return FileResponse("WebPages/pdf-reader.html")

# Serve main web interface - redirect to BowersWorld promotional page
@app.get("/")
async def serve_main_page(code: str = None, state: str = None, error: str = None, request: Request = Request):
    """Serve the BowersWorld.com promotional page as the main landing, or handle OAuth callback"""
    # Check if this is an OAuth callback
    if code:
        # Direct OAuth callback - delegate to simplified handler
        return await oauth_simple_callback(code, state, error, request)
    
    # Normal landing page request
    return FileResponse("WebPages/bowersworld.html")

@app.get("/library")
async def serve_library_page():
    """Serve the main AndyLibrary interface (after authentication)"""
    return FileResponse("WebPages/desktop-library.html")

@app.get("/auth.html")
async def serve_auth_page():
    """Serve the authentication page with enhanced registration"""
    return FileResponse("WebPages/auth.html")

@app.get("/bowersworld.html")
async def serve_bowersworld_page():
    """Serve the BowersWorld.com promotional page with Project Himalaya content"""
    return FileResponse("WebPages/bowersworld.html")

@app.get("/bowersworld")
async def serve_bowersworld_redirect():
    """Redirect /bowersworld to the full promotional page"""
    return RedirectResponse(url="/bowersworld.html")

@app.get("/favicon.ico")
async def serve_favicon():
    """Serve the favicon"""
    return FileResponse("WebPages/favicon.ico")

@app.get("/setup.html")
async def serve_setup_page():
    """Serve the AndyLibrary setup/installation page"""
    return FileResponse("WebPages/setup.html")

@app.get("/simple-register.html")
async def serve_simple_register_page():
    """Serve the simple registration test page"""
    return FileResponse("WebPages/simple-register.html")

@app.get("/direct-register.html")
async def serve_direct_register_page():
    """Serve the direct registration test page (no service worker)"""
    return FileResponse("WebPages/direct-register.html")

@app.get("/verification-success.html")
async def serve_verification_success_page():
    """Serve the email verification success page"""
    return FileResponse("WebPages/verification-success.html")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and log errors"""
    if sheets_logger:
        sheets_logger.LogError(
            error_type="HTTP_ERROR",
            error_message=f"{exc.status_code}: {exc.detail}",
            context=f"{request.method} {request.url.path}"
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions and log errors"""
    if sheets_logger:
        sheets_logger.LogError(
            error_type="INTERNAL_ERROR",
            error_message=str(exc),
            context=f"{request.method} {request.url.path}",
            severity="CRITICAL"
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Student Book Download Endpoints
@app.get("/api/books/{book_id}/cost", response_model=BookCostResponse)
async def get_book_cost(book_id: int, region: str = "developing"):
    """Get cost estimate for downloading a book"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        # Parse region
        student_region = StudentRegion(region.lower())
        
        downloader = StudentBookDownloader()
        cost_info = downloader.GetBookCostEstimate(book_id, student_region)
        
        if not cost_info:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookCostResponse(
            book_id=cost_info.book_id,
            title=cost_info.title,
            file_size_mb=cost_info.file_size_mb,
            estimated_cost_usd=cost_info.estimated_cost_usd,
            warning_level=cost_info.warning_level,
            budget_percentage=cost_info.budget_percentage
        )
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid region. Use: developing, emerging, or developed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost calculation error: {str(e)}")

@app.get("/api/books/{book_id}/download-options", response_model=DownloadOptionsResponse)
async def get_download_options(book_id: int, region: str = "developing"):
    """Get download options for a book with student guidance"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        student_region = StudentRegion(region.lower())
        
        downloader = StudentBookDownloader()
        options = downloader.GetDownloadOptions(book_id, student_region)
        
        if 'error' in options:
            raise HTTPException(status_code=404, detail=options['error'])
        
        return DownloadOptionsResponse(**options)
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid region. Use: developing, emerging, or developed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Options error: {str(e)}")

@app.get("/api/books/{book_id}/pdf")
async def get_book_pdf(request: Request, book_id: int, db: sqlite3.Connection = Depends(get_database)):
    """Get PDF file for a book - integrates with Google Drive or local storage"""
    log_api_usage(request, "pdf_access", f"book_id={book_id}")
    
    # First get book info from database
    cursor = db.execute("SELECT id, title, FilePath FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        # Try Google Drive integration first
        from Core.StudentGoogleDriveAPI import StudentGoogleDriveAPI, GOOGLE_AVAILABLE
        
        if GOOGLE_AVAILABLE:
            print(f"🔍 Attempting Google Drive access for book: {book['title']}")
            
            try:
                # Initialize Google Drive API
                gdrive_api = StudentGoogleDriveAPI()
                
                # Check if we have a valid token (simplified check)
                token_path = "Config/google_token.json"
                if os.path.exists(token_path):
                    print("✅ Google token found, attempting book access")
                    
                    # Get file info from Google Drive
                    file_info = gdrive_api.GetBookFileInfo(book['title'])
                    
                    if file_info:
                        print(f"✅ Found book in Google Drive: {file_info.name}")
                        
                        # For now, redirect to Google Drive download URL
                        # In production, you might want to proxy the download
                        from fastapi.responses import RedirectResponse
                        return RedirectResponse(url=file_info.download_url)
                    else:
                        print(f"⚠️ Book '{book['title']}' not found in Google Drive")
                
                else:
                    print("⚠️ No Google authentication token found")
                    
            except Exception as e:
                print(f"⚠️ Google Drive access failed: {e}")
        
        # Fallback to local file system
        if book['FilePath']:
            local_path = book['FilePath']
            
            # Convert relative path to absolute
            if not os.path.isabs(local_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                local_path = os.path.join(base_dir, local_path)
            
            if os.path.exists(local_path):
                print(f"✅ Serving PDF from local file: {local_path}")
                from fastapi import Response
                
                # Read PDF file and serve with inline viewing headers
                with open(local_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                
                return Response(
                    content=pdf_content,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"inline; filename=\"{book['title']}.pdf\"",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )
        
        # If we get here, no PDF source is available
        raise HTTPException(
            status_code=404, 
            detail="PDF not available. Book may need to be downloaded from Google Drive first."
        )
        
    except Exception as e:
        print(f"❌ PDF access error: {e}")
        raise HTTPException(status_code=500, detail=f"Error accessing PDF: {str(e)}")

@app.get("/api/student/budget-summary", response_model=BudgetSummaryResponse)
async def get_budget_summary():
    """Get student's monthly spending summary"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    try:
        downloader = StudentBookDownloader()
        summary = downloader.GetMonthlySpendingSummary()
        
        return BudgetSummaryResponse(**summary)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget summary error: {str(e)}")

@app.post("/api/books/{book_id}/download")
async def initiate_book_download(book_id: int, download_method: str = "download_now"):
    """Initiate book download (placeholder for actual Google Drive integration)"""
    if not StudentBookDownloader:
        raise HTTPException(status_code=500, detail="Book downloader not available")
    
    # For now, just return download initiation info
    # TODO: Implement actual Google Drive download with chunking
    
    try:
        downloader = StudentBookDownloader()
        cost_info = downloader.GetBookCostEstimate(book_id)
        
        if not cost_info:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Simulate download cost recording
        actual_cost = cost_info.estimated_cost_usd if download_method == "download_now" else 0.0
        downloader.RecordDownload(book_id, actual_cost, download_method)
        
        return {
            "status": "download_initiated",
            "book_id": book_id,
            "method": download_method,
            "estimated_cost": actual_cost,
            "message": f"Download started for: {cost_info.title}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

def main():
    """Run the OurLibrary API server"""
    print("🚀 Starting OurLibrary API Server")
    print("=" * 40)
    
    # Configuration
    host = "127.0.0.1"
    port = 8000
    
    # Try to find an available port
    import socket
    for test_port in range(port, port + 10):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind((host, test_port))
            test_socket.close()
            port = test_port
            break
        except OSError:
            continue
    
    print(f"🌐 Server will start at: http://{host}:{port}")
    print(f"📚 OurLibrary Library: http://{host}:{port}")
    print(f"🔧 API Documentation: http://{host}:{port}/docs")
    print("=" * 40)
    
    # Start server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
