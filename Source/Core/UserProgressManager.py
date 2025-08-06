# File: UserProgressManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/UserProgressManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 05:30AM

"""
User Progress Manager for AndyLibrary
Tracks student learning progress, bookmarks, reading history, and educational analytics
Supports offline-first design with local storage and optional cloud sync
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

@dataclass
class ReadingSession:
    """Represents a single reading session"""
    BookId: int
    UserId: int
    StartTime: datetime
    EndTime: Optional[datetime] = None
    PagesRead: int = 0
    TimeSpent: int = 0  # seconds
    CompletionPercentage: float = 0.0
    DeviceType: str = "desktop"
    SessionId: str = ""

@dataclass
class BookProgress:
    """Represents user's progress on a specific book"""
    BookId: int
    UserId: int
    Title: str
    Category: str
    FirstAccessed: datetime
    LastAccessed: datetime
    TotalTimeSpent: int  # seconds
    TotalSessions: int
    CompletionPercentage: float
    IsBookmarked: bool = False
    IsFavorite: bool = False
    UserRating: Optional[int] = None  # 1-5 stars
    Notes: Optional[str] = None

@dataclass
class LearningStatistics:
    """User's overall learning statistics"""
    UserId: int
    TotalBooksAccessed: int
    TotalReadingTime: int  # seconds
    TotalSessions: int
    FavoriteCategory: str
    ReadingStreak: int  # consecutive days
    LastActiveDate: datetime
    BooksCompleted: int
    AverageSessionTime: int
    PreferredReadingTimes: List[int]  # hours of day

class UserProgressManager:
    """
    Manages user progress tracking for AndyLibrary
    Provides offline-first learning analytics and progress tracking
    """
    
    def __init__(self, DatabasePath: str = None, UserId: int = None):
        """
        Initialize User Progress Manager
        
        Args:
            DatabasePath: Path to SQLite database
            UserId: Current user ID
        """
        self.DatabasePath = DatabasePath or "/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db"
        self.UserId = UserId
        self.Logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize progress tracking tables
        self.InitializeProgressTables()
    
    def InitializeProgressTables(self) -> None:
        """Initialize database tables for progress tracking"""
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Reading sessions table
                Cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reading_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        session_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        pages_read INTEGER DEFAULT 0,
                        time_spent INTEGER DEFAULT 0,
                        completion_percentage REAL DEFAULT 0.0,
                        device_type TEXT DEFAULT 'desktop',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (book_id) REFERENCES books (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Book progress table
                Cursor.execute("""
                    CREATE TABLE IF NOT EXISTS book_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        first_accessed TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        total_time_spent INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        completion_percentage REAL DEFAULT 0.0,
                        is_bookmarked INTEGER DEFAULT 0,
                        is_favorite INTEGER DEFAULT 0,
                        user_rating INTEGER,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(book_id, user_id),
                        FOREIGN KEY (book_id) REFERENCES books (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Learning statistics table
                Cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL UNIQUE,
                        total_books_accessed INTEGER DEFAULT 0,
                        total_reading_time INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        favorite_category TEXT,
                        reading_streak INTEGER DEFAULT 0,
                        last_active_date TEXT,
                        books_completed INTEGER DEFAULT 0,
                        average_session_time INTEGER DEFAULT 0,
                        preferred_reading_times TEXT,  -- JSON array
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Create indexes for performance
                Cursor.execute("CREATE INDEX IF NOT EXISTS idx_reading_sessions_user_book ON reading_sessions(user_id, book_id)")
                Cursor.execute("CREATE INDEX IF NOT EXISTS idx_book_progress_user ON book_progress(user_id)")
                Cursor.execute("CREATE INDEX IF NOT EXISTS idx_book_progress_last_accessed ON book_progress(last_accessed)")
                
                Conn.commit()
                self.Logger.info("Progress tracking tables initialized successfully")
                
        except Exception as e:
            self.Logger.error(f"Failed to initialize progress tables: {e}")
            raise
    
    def StartReadingSession(self, BookId: int, BookTitle: str, BookCategory: str, DeviceType: str = "desktop") -> str:
        """
        Start a new reading session
        
        Args:
            BookId: ID of the book being read
            BookTitle: Title of the book
            BookCategory: Category of the book
            DeviceType: Type of device (desktop, tablet, mobile)
            
        Returns:
            Session ID for tracking
        """
        if not self.UserId:
            raise ValueError("User ID is required for progress tracking")
        
        try:
            SessionId = f"session_{int(time.time())}_{BookId}_{self.UserId}"
            CurrentTime = datetime.now().isoformat()
            
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Insert reading session
                Cursor.execute("""
                    INSERT INTO reading_sessions 
                    (book_id, user_id, session_id, start_time, device_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (BookId, self.UserId, SessionId, CurrentTime, DeviceType))
                
                # Update or create book progress
                Cursor.execute("""
                    INSERT INTO book_progress 
                    (book_id, user_id, title, category, first_accessed, last_accessed, total_sessions)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(book_id, user_id) DO UPDATE SET
                        last_accessed = ?,
                        total_sessions = total_sessions + 1,
                        updated_at = CURRENT_TIMESTAMP
                """, (BookId, self.UserId, BookTitle, BookCategory, CurrentTime, CurrentTime, CurrentTime))
                
                Conn.commit()
                
                self.Logger.info(f"Started reading session {SessionId} for book {BookId}")
                return SessionId
                
        except Exception as e:
            self.Logger.error(f"Failed to start reading session: {e}")
            raise
    
    def EndReadingSession(self, SessionId: str, PagesRead: int = 0, CompletionPercentage: float = 0.0) -> Dict[str, Any]:
        """
        End a reading session and update progress
        
        Args:
            SessionId: ID of the session to end
            PagesRead: Number of pages read in this session
            CompletionPercentage: Estimated completion percentage of the book
            
        Returns:
            Dict with session statistics
        """
        try:
            CurrentTime = datetime.now().isoformat()
            
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Get session details
                Cursor.execute("""
                    SELECT book_id, user_id, start_time
                    FROM reading_sessions
                    WHERE session_id = ? AND end_time IS NULL
                """, (SessionId,))
                
                SessionData = Cursor.fetchone()
                if not SessionData:
                    raise ValueError(f"Active session {SessionId} not found")
                
                BookId, UserId, StartTimeStr = SessionData
                StartTime = datetime.fromisoformat(StartTimeStr)
                EndTime = datetime.now()
                TimeSpent = int((EndTime - StartTime).total_seconds())
                
                # Update reading session
                Cursor.execute("""
                    UPDATE reading_sessions 
                    SET end_time = ?, pages_read = ?, time_spent = ?, completion_percentage = ?
                    WHERE session_id = ?
                """, (CurrentTime, PagesRead, TimeSpent, CompletionPercentage, SessionId))
                
                # Update book progress
                Cursor.execute("""
                    UPDATE book_progress 
                    SET last_accessed = ?,
                        total_time_spent = total_time_spent + ?,
                        completion_percentage = MAX(completion_percentage, ?),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE book_id = ? AND user_id = ?
                """, (CurrentTime, TimeSpent, CompletionPercentage, BookId, UserId))
                
                Conn.commit()
                
                # Update learning statistics
                self.UpdateLearningStatistics(UserId)
                
                SessionStats = {
                    "session_id": SessionId,
                    "book_id": BookId,
                    "time_spent": TimeSpent,
                    "pages_read": PagesRead,
                    "completion_percentage": CompletionPercentage,
                    "session_duration_minutes": round(TimeSpent / 60, 1)
                }
                
                self.Logger.info(f"Ended reading session {SessionId}, duration: {TimeSpent}s")
                return SessionStats
                
        except Exception as e:
            self.Logger.error(f"Failed to end reading session: {e}")
            raise
    
    def UpdateLearningStatistics(self, UserId: int) -> None:
        """Update overall learning statistics for a user"""
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Calculate statistics from progress data
                Cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT book_id) as total_books,
                        SUM(total_time_spent) as total_time,
                        SUM(total_sessions) as total_sessions,
                        COUNT(CASE WHEN completion_percentage >= 100.0 THEN 1 END) as completed_books
                    FROM book_progress 
                    WHERE user_id = ?
                """, (UserId,))
                
                Stats = Cursor.fetchone()
                if not Stats:
                    return
                
                TotalBooks, TotalTime, TotalSessions, CompletedBooks = Stats
                TotalTime = TotalTime or 0
                TotalSessions = TotalSessions or 0
                
                # Find favorite category
                Cursor.execute("""
                    SELECT category, SUM(total_time_spent) as time_in_category
                    FROM book_progress 
                    WHERE user_id = ?
                    GROUP BY category
                    ORDER BY time_in_category DESC
                    LIMIT 1
                """, (UserId,))
                
                FavoriteCategoryResult = Cursor.fetchone()
                FavoriteCategory = FavoriteCategoryResult[0] if FavoriteCategoryResult else "General"
                
                # Calculate average session time
                AvgSessionTime = int(TotalTime / TotalSessions) if TotalSessions > 0 else 0
                
                # Calculate reading streak (simplified - days with activity)
                Cursor.execute("""
                    SELECT COUNT(DISTINCT DATE(last_accessed)) as active_days
                    FROM book_progress 
                    WHERE user_id = ? AND last_accessed >= date('now', '-30 days')
                """, (UserId,))
                
                ReadingStreak = Cursor.fetchone()[0] or 0
                CurrentTime = datetime.now().isoformat()
                
                # Update or insert statistics
                Cursor.execute("""
                    INSERT INTO learning_statistics 
                    (user_id, total_books_accessed, total_reading_time, total_sessions, 
                     favorite_category, reading_streak, last_active_date, books_completed, average_session_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        total_books_accessed = ?,
                        total_reading_time = ?,
                        total_sessions = ?,
                        favorite_category = ?,
                        reading_streak = ?,
                        last_active_date = ?,
                        books_completed = ?,
                        average_session_time = ?,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    UserId, TotalBooks, TotalTime, TotalSessions, FavoriteCategory, 
                    ReadingStreak, CurrentTime, CompletedBooks, AvgSessionTime,
                    TotalBooks, TotalTime, TotalSessions, FavoriteCategory,
                    ReadingStreak, CurrentTime, CompletedBooks, AvgSessionTime
                ))
                
                Conn.commit()
                self.Logger.info(f"Updated learning statistics for user {UserId}")
                
        except Exception as e:
            self.Logger.error(f"Failed to update learning statistics: {e}")
    
    def GetUserProgress(self, UserId: int, Limit: int = 20) -> Dict[str, Any]:
        """
        Get comprehensive user progress information
        
        Args:
            UserId: User ID to get progress for
            Limit: Maximum number of recent books to return
            
        Returns:
            Dict with user progress data
        """
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Get learning statistics
                Cursor.execute("""
                    SELECT * FROM learning_statistics WHERE user_id = ?
                """, (UserId,))
                
                StatsRow = Cursor.fetchone()
                if StatsRow:
                    StatsColumns = [desc[0] for desc in Cursor.description]
                    Statistics = dict(zip(StatsColumns, StatsRow))
                else:
                    Statistics = {
                        "total_books_accessed": 0,
                        "total_reading_time": 0,
                        "total_sessions": 0,
                        "favorite_category": "General",
                        "reading_streak": 0,
                        "books_completed": 0,
                        "average_session_time": 0
                    }
                
                # Get recent book progress
                Cursor.execute("""
                    SELECT * FROM book_progress 
                    WHERE user_id = ?
                    ORDER BY last_accessed DESC
                    LIMIT ?
                """, (UserId, Limit))
                
                RecentBooks = []
                for Row in Cursor.fetchall():
                    Columns = [desc[0] for desc in Cursor.description]
                    BookProgress = dict(zip(Columns, Row))
                    RecentBooks.append(BookProgress)
                
                # Get bookmarks
                Cursor.execute("""
                    SELECT book_id, title, category FROM book_progress 
                    WHERE user_id = ? AND is_bookmarked = 1
                    ORDER BY updated_at DESC
                """, (UserId,))
                
                Bookmarks = [
                    {"book_id": Row[0], "title": Row[1], "category": Row[2]}
                    for Row in Cursor.fetchall()
                ]
                
                # Get reading activity for the last 30 days
                Cursor.execute("""
                    SELECT DATE(start_time) as reading_date, 
                           COUNT(*) as sessions,
                           SUM(time_spent) as total_time
                    FROM reading_sessions 
                    WHERE user_id = ? AND start_time >= date('now', '-30 days')
                    GROUP BY DATE(start_time)
                    ORDER BY reading_date DESC
                """, (UserId,))
                
                RecentActivity = [
                    {
                        "date": Row[0],
                        "sessions": Row[1],
                        "total_time": Row[2]
                    }
                    for Row in Cursor.fetchall()
                ]
                
                return {
                    "user_id": UserId,
                    "statistics": Statistics,
                    "recent_books": RecentBooks,
                    "bookmarks": Bookmarks,
                    "recent_activity": RecentActivity,
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.Logger.error(f"Failed to get user progress: {e}")
            raise
    
    def ToggleBookmark(self, UserId: int, BookId: int) -> Dict[str, Any]:
        """Toggle bookmark status for a book"""
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Check current bookmark status
                Cursor.execute("""
                    SELECT is_bookmarked FROM book_progress 
                    WHERE user_id = ? AND book_id = ?
                """, (UserId, BookId))
                
                Result = Cursor.fetchone()
                if not Result:
                    raise ValueError(f"No progress record found for book {BookId}")
                
                CurrentStatus = bool(Result[0])
                NewStatus = not CurrentStatus
                
                # Update bookmark status
                Cursor.execute("""
                    UPDATE book_progress 
                    SET is_bookmarked = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND book_id = ?
                """, (int(NewStatus), UserId, BookId))
                
                Conn.commit()
                
                return {
                    "book_id": BookId,
                    "is_bookmarked": NewStatus,
                    "action": "bookmarked" if NewStatus else "unbookmarked"
                }
                
        except Exception as e:
            self.Logger.error(f"Failed to toggle bookmark: {e}")
            raise
    
    def SetBookRating(self, UserId: int, BookId: int, Rating: int, Notes: str = None) -> Dict[str, Any]:
        """
        Set user rating and notes for a book
        
        Args:
            UserId: User ID
            BookId: Book ID
            Rating: Rating from 1-5 stars
            Notes: Optional user notes
            
        Returns:
            Dict with updated rating info
        """
        if not (1 <= Rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Update rating and notes
                Cursor.execute("""
                    UPDATE book_progress 
                    SET user_rating = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND book_id = ?
                """, (Rating, Notes, UserId, BookId))
                
                if Cursor.rowcount == 0:
                    raise ValueError(f"No progress record found for book {BookId}")
                
                Conn.commit()
                
                return {
                    "book_id": BookId,
                    "user_rating": Rating,
                    "notes": Notes,
                    "updated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.Logger.error(f"Failed to set book rating: {e}")
            raise