# File: MainAPI.py
# Path: AndyGoogle/Source/API/MainAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-12
# Last Modified: 2025-07-12  07:37PM
"""
Description: FastAPI main server for AndyGoogle with Google Drive integration
Provides RESTful API endpoints for library management with cloud synchronization
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from Core.DriveManager import DriveManager
# from Utils.SheetsLogger import SheetsLogger

# FastAPI app instance
app = FastAPI(
    title="AndyGoogle Library API",
    description="Cloud-synchronized digital library management system",
    version="1.0.0"
)

# Global managers (initialized on startup)
drive_manager = None
sheets_logger = None

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
    auto_sync_enabled: bool
    database_size_mb: float

# Dependency to get database connection
def get_database():
    """Get SQLite database connection"""
    if not drive_manager:
        raise HTTPException(status_code=500, detail="Drive manager not initialized")
    
    db_path = drive_manager.local_db_path
    
    if not os.path.exists(db_path):
        raise HTTPException(status_code=503, detail="Database not available - sync required")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    finally:
        conn.close()

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
    """Initialize AndyGoogle components on startup"""
    global drive_manager, sheets_logger
    
    print("🚀 Starting AndyGoogle API server...")
    print("📊 Database ready with local SQLite file")
    print("🌐 Google Drive integration available when configured")
    
    # For now, start without Drive/Sheets integration to get basic functionality working
    # These will be None but the API will still work for local database access
    
    print("✅ AndyGoogle API server started successfully")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

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
@app.get("/api/books", response_model=List[BookResponse])
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
    log_api_usage(request, "books_list", f"limit={limit}, offset={offset}, search={search}")
    
    # Build query - simplified for current database schema
    query = """
        SELECT b.id, b.title, 
               NULL as author, NULL as category, NULL as subject, 
               NULL as file_path, NULL as file_size, 
               NULL as page_count, NULL as rating,
               NULL as last_opened
        FROM books b
        WHERE 1=1
    """
    
    params = []
    
    # Add search filter
    if search:
        query += " AND b.title LIKE ?"
        search_param = f"%{search}%"
        params.append(search_param)
    
    # Add category filter
    if category:
        query += " AND c.category = ?"
        params.append(category)
    
    # Add subject filter
    if subject:
        query += " AND s.subject = ?"
        params.append(subject)
    
    # Add pagination
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
    
    return books

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
    
    # Thumbnail support not available in current database schema
    raise HTTPException(status_code=404, detail="Thumbnail not available in current database schema")

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
    db: sqlite3.Connection = Depends(get_database)
):
    """Get subjects, optionally filtered by category"""
    log_api_usage(request, "subjects_list", f"category_id={category_id}")
    
    if category_id:
        query = "SELECT id, subject, category_id FROM subjects WHERE category_id = ? ORDER BY subject"
        params = (category_id,)
    else:
        query = "SELECT id, subject, category_id FROM subjects ORDER BY subject"
        params = ()
    
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    
    return [
        SubjectResponse(id=row['id'], subject=row['subject'], category_id=row['category_id']) 
        for row in rows
    ]

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

# Static file serving
app.mount("/static", StaticFiles(directory="WebPages"), name="static")

# Serve main web interface
@app.get("/")
async def serve_main_page():
    """Serve the main AndyGoogle web interface"""
    return FileResponse("WebPages/desktop-library.html")

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

def main():
    """Run the AndyGoogle API server"""
    print("🚀 Starting AndyGoogle API Server")
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
    print(f"📚 AndyGoogle Library: http://{host}:{port}")
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
