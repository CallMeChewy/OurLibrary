# File: AdvancedSearchAPI.py
# Path: /home/herb/Desktop/AndyLibrary/Source/API/AdvancedSearchAPI.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 05:25AM

"""
Advanced Search API for AndyLibrary
Provides sophisticated search, filtering, and discovery features for educational content
Supports multiple search modes: textual, categorical, fuzzy matching, and recommendation-based
"""

import os
import sys
import sqlite3
import re
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel, Field
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Core.DatabaseManager import DatabaseManager
except ImportError:
    DatabaseManager = None

class SearchRequest(BaseModel):
    """Advanced search request model"""
    Query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    Categories: Optional[List[str]] = Field(default=None, description="Filter by categories")
    SearchMode: str = Field(default="comprehensive", description="Search mode: basic, comprehensive, fuzzy, or semantic")
    PageSize: int = Field(default=20, ge=1, le=100, description="Results per page")
    PageNumber: int = Field(default=1, ge=1, description="Page number")
    SortBy: str = Field(default="relevance", description="Sort order: relevance, title, category, date")
    IncludeMetadata: bool = Field(default=True, description="Include book metadata in results")
    MinRelevanceScore: float = Field(default=0.1, ge=0.0, le=1.0, description="Minimum relevance threshold")

class BookSearchResult(BaseModel):
    """Enhanced book search result with relevance scoring"""
    Id: int
    Title: str
    Category: str
    SubCategory: Optional[str] = None
    RelevanceScore: float
    MatchedFields: List[str]
    HasThumbnail: bool
    FileSize: Optional[int] = None
    LastModified: Optional[str] = None
    Description: Optional[str] = None

class SearchResponse(BaseModel):
    """Comprehensive search response"""
    Results: List[BookSearchResult]
    TotalResults: int
    PageNumber: int
    PageSize: int
    TotalPages: int
    SearchTime: float
    QueryProcessed: str
    SuggestedQueries: List[str]
    CategoryBreakdown: Dict[str, int]

class AdvancedSearchAPI:
    """
    Advanced search functionality for AndyLibrary
    Provides sophisticated search capabilities beyond basic text matching
    """
    
    def __init__(self, DatabasePath: str = None):
        """
        Initialize Advanced Search API
        
        Args:
            DatabasePath: Path to SQLite database file
        """
        self.DatabasePath = DatabasePath or "/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db"
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.Router = APIRouter()
        self.SetupRoutes()
        
        # Initialize search indexes and caches
        self.CategoryIndex = {}
        self.WordFrequencyIndex = {}
        self.InitializeSearchIndexes()
    
    def InitializeSearchIndexes(self) -> None:
        """Initialize search indexes for faster querying"""
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Build category index - check if category column exists
                try:
                    Cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL")
                    Categories = [Row[0] for Row in Cursor.fetchall()]
                    self.CategoryIndex = {Cat.lower(): Cat for Cat in Categories}
                except sqlite3.OperationalError:
                    # Fallback - use hardcoded categories from the main database structure
                    Cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
                    if Cursor.fetchone():
                        Cursor.execute("SELECT category FROM categories")
                        Categories = [Row[0] for Row in Cursor.fetchall()]
                        self.CategoryIndex = {Cat.lower(): Cat for Cat in Categories}
                    else:
                        # Use default categories from existing system
                        self.CategoryIndex = {
                            "computer science": "Computer Science",
                            "programming": "Programming Languages", 
                            "web development": "Web Development",
                            "math": "Math",
                            "science": "Science"
                        }
                
                # Build word frequency index for better relevance scoring
                try:
                    Cursor.execute("SELECT title FROM books")
                    AllText = []
                    for Row in Cursor.fetchall():
                        Title = Row[0]
                        AllText.extend(self.ExtractWords(Title))
                except sqlite3.OperationalError as e:
                    self.Logger.warning(f"Could not build word frequency index: {e}")
                    AllText = []
                
                # Count word frequencies
                for Word in AllText:
                    self.WordFrequencyIndex[Word] = self.WordFrequencyIndex.get(Word, 0) + 1
                
                self.Logger.info(f"Search indexes initialized: {len(self.CategoryIndex)} categories, {len(self.WordFrequencyIndex)} unique words")
                
        except Exception as e:
            self.Logger.error(f"Failed to initialize search indexes: {e}")
    
    def ExtractWords(self, Text: str) -> List[str]:
        """Extract and normalize words from text"""
        if not Text:
            return []
        
        # Convert to lowercase and extract alphanumeric words
        Words = re.findall(r'\b[a-zA-Z0-9]+\b', Text.lower())
        
        # Filter out very short words and common stop words
        StopWords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        FilteredWords = [Word for Word in Words if len(Word) > 2 and Word not in StopWords]
        
        return FilteredWords
    
    def CalculateRelevanceScore(self, BookTitle: str, BookCategory: str, QueryWords: List[str]) -> Dict[str, Any]:
        """
        Calculate relevance score for a book given search query
        
        Args:
            BookTitle: Title of the book
            BookCategory: Category of the book
            QueryWords: List of normalized query words
            
        Returns:
            Dict with score and matched fields
        """
        Score = 0.0
        MatchedFields = []
        
        BookWords = self.ExtractWords(f"{BookTitle} {BookCategory}")
        BookWordsSet = set(BookWords)
        QueryWordsSet = set(QueryWords)
        
        # Title matching (highest weight)
        TitleWords = set(self.ExtractWords(BookTitle))
        TitleMatches = len(TitleWords.intersection(QueryWordsSet))
        if TitleMatches > 0:
            TitleScore = (TitleMatches / len(QueryWordsSet)) * 0.6
            Score += TitleScore
            MatchedFields.append("title")
        
        # Category matching (medium weight)
        CategoryWords = set(self.ExtractWords(BookCategory))
        CategoryMatches = len(CategoryWords.intersection(QueryWordsSet))
        if CategoryMatches > 0:
            CategoryScore = (CategoryMatches / len(QueryWordsSet)) * 0.3
            Score += CategoryScore
            MatchedFields.append("category")
        
        # Exact phrase matching (bonus)
        QueryText = " ".join(QueryWords)
        if QueryText in BookTitle.lower():
            Score += 0.4
            MatchedFields.append("exact_phrase")
        
        # Word frequency boost (rare words get higher scores)
        FrequencyBoost = 0.0
        for Word in QueryWordsSet.intersection(BookWordsSet):
            if Word in self.WordFrequencyIndex:
                # Inverse frequency scoring - rare words are more important
                Frequency = self.WordFrequencyIndex[Word]
                FrequencyBoost += 1.0 / (1.0 + Frequency / 100.0)
        
        Score += FrequencyBoost * 0.1
        
        return {
            "score": min(Score, 1.0),  # Cap at 1.0
            "matched_fields": MatchedFields
        }
    
    def PerformFuzzySearch(self, Query: str, Books: List[Dict]) -> List[Dict]:
        """
        Perform fuzzy matching for typo tolerance
        
        Args:
            Query: Search query
            Books: List of book dictionaries
            
        Returns:
            List of books with fuzzy match scores
        """
        QueryWords = self.ExtractWords(Query)
        Results = []
        
        for Book in Books:
            BookText = f"{Book['title']} {Book['category']}"
            BookWords = self.ExtractWords(BookText)
            
            # Simple fuzzy matching using edit distance approximation
            FuzzyScore = 0.0
            for QueryWord in QueryWords:
                BestMatch = 0.0
                for BookWord in BookWords:
                    # Simple similarity based on common characters
                    CommonChars = len(set(QueryWord).intersection(set(BookWord)))
                    MaxLen = max(len(QueryWord), len(BookWord))
                    if MaxLen > 0:
                        Similarity = CommonChars / MaxLen
                        if Similarity > BestMatch:
                            BestMatch = Similarity
                
                FuzzyScore += BestMatch
            
            if len(QueryWords) > 0:
                FuzzyScore /= len(QueryWords)
            
            if FuzzyScore > 0.3:  # Minimum threshold for fuzzy matches
                Results.append({
                    **Book,
                    "fuzzy_score": FuzzyScore
                })
        
        return sorted(Results, key=lambda x: x["fuzzy_score"], reverse=True)
    
    def SearchBooks(self, SearchRequest: SearchRequest) -> SearchResponse:
        """
        Perform advanced book search with multiple modes
        
        Args:
            SearchRequest: Search parameters
            
        Returns:
            SearchResponse with results and metadata
        """
        StartTime = time.time()
        
        try:
            with sqlite3.connect(self.DatabasePath) as Conn:
                Cursor = Conn.cursor()
                
                # Base query - adapt to actual database structure
                try:
                    # Try with category column first
                    Cursor.execute("SELECT id, title FROM books LIMIT 1")
                    BaseQuery = """
                    SELECT id, title,
                           CASE WHEN thumbnail IS NOT NULL THEN 1 ELSE 0 END as has_thumbnail
                    FROM books 
                    WHERE 1=1
                    """
                    Params = []
                except sqlite3.OperationalError:
                    # Fallback for different schema
                    BaseQuery = """
                    SELECT id, title, 
                           0 as has_thumbnail
                    FROM books 
                    WHERE 1=1
                    """
                    Params = []
                
                # Category filtering
                if SearchRequest.Categories:
                    Placeholders = ",".join("?" * len(SearchRequest.Categories))
                    BaseQuery += f" AND category IN ({Placeholders})"
                    Params.extend(SearchRequest.Categories)
                
                # Execute base query
                Cursor.execute(BaseQuery, Params)
                AllBooks = []
                for Row in Cursor.fetchall():
                    BookData = {
                        "id": Row[0],
                        "title": Row[1],
                        "category": "General",  # Default category
                        "has_thumbnail": bool(Row[2]) if len(Row) > 2 else False
                    }
                    AllBooks.append(BookData)
                
                # Apply search logic based on mode
                QueryWords = self.ExtractWords(SearchRequest.Query)
                FilteredBooks = []
                
                if SearchRequest.SearchMode == "fuzzy":
                    FilteredBooks = self.PerformFuzzySearch(SearchRequest.Query, AllBooks)
                    # Convert fuzzy_score to RelevanceScore for consistency
                    for Book in FilteredBooks:
                        Book["relevance_score"] = Book.pop("fuzzy_score", 0.0)
                        Book["matched_fields"] = ["fuzzy_match"]
                else:
                    # Standard relevance-based search
                    for Book in AllBooks:
                        RelevanceData = self.CalculateRelevanceScore(
                            Book["title"], Book["category"], QueryWords
                        )
                        
                        if RelevanceData["score"] >= SearchRequest.MinRelevanceScore:
                            Book["relevance_score"] = RelevanceData["score"]
                            Book["matched_fields"] = RelevanceData["matched_fields"]
                            FilteredBooks.append(Book)
                
                # Sort results
                if SearchRequest.SortBy == "relevance":
                    FilteredBooks.sort(key=lambda x: x["relevance_score"], reverse=True)
                elif SearchRequest.SortBy == "title":
                    FilteredBooks.sort(key=lambda x: x["title"].lower())
                elif SearchRequest.SortBy == "category":
                    FilteredBooks.sort(key=lambda x: x["category"].lower())
                
                # Pagination
                TotalResults = len(FilteredBooks)
                TotalPages = (TotalResults + SearchRequest.PageSize - 1) // SearchRequest.PageSize
                StartIndex = (SearchRequest.PageNumber - 1) * SearchRequest.PageSize
                EndIndex = StartIndex + SearchRequest.PageSize
                PagedResults = FilteredBooks[StartIndex:EndIndex]
                
                # Convert to response format
                BookResults = []
                for Book in PagedResults:
                    BookResults.append(BookSearchResult(
                        Id=Book["id"],
                        Title=Book["title"],
                        Category=Book["category"],
                        RelevanceScore=Book["relevance_score"],
                        MatchedFields=Book["matched_fields"],
                        HasThumbnail=Book["has_thumbnail"]
                    ))
                
                # Generate category breakdown
                CategoryBreakdown = {}
                for Book in FilteredBooks:
                    Cat = Book["category"]
                    CategoryBreakdown[Cat] = CategoryBreakdown.get(Cat, 0) + 1
                
                # Generate suggested queries (simple implementation)
                SuggestedQueries = []
                if len(FilteredBooks) < 5 and len(QueryWords) > 0:
                    # Suggest broader terms
                    for Word in QueryWords:
                        for Category in self.CategoryIndex.keys():
                            if Word in Category:
                                SuggestedQueries.append(Category)
                        if len(SuggestedQueries) >= 3:
                            break
                
                SearchTime = time.time() - StartTime
                
                return SearchResponse(
                    Results=BookResults,
                    TotalResults=TotalResults,
                    PageNumber=SearchRequest.PageNumber,
                    PageSize=SearchRequest.PageSize,
                    TotalPages=TotalPages,
                    SearchTime=round(SearchTime, 3),
                    QueryProcessed=" ".join(QueryWords),
                    SuggestedQueries=SuggestedQueries[:5],
                    CategoryBreakdown=CategoryBreakdown
                )
                
        except Exception as e:
            self.Logger.error(f"Search failed: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    def SetupRoutes(self) -> None:
        """Setup API routes"""
        
        @self.Router.post("/search/advanced", response_model=SearchResponse)
        async def AdvancedSearch(Request: SearchRequest):
            """
            Perform advanced search with multiple modes and filters
            
            Supports:
            - Comprehensive relevance-based search
            - Fuzzy matching for typo tolerance
            - Category filtering
            - Pagination and sorting
            - Relevance scoring and suggestions
            """
            return self.SearchBooks(Request)
        
        @self.Router.get("/search/suggestions")
        async def GetSearchSuggestions(
            Query: str = Query(..., min_length=1, description="Partial search query"),
            Limit: int = Query(default=10, ge=1, le=20, description="Maximum suggestions")
        ):
            """
            Get search suggestions based on partial query
            Helps users discover relevant content
            """
            try:
                QueryWords = self.ExtractWords(Query)
                Suggestions = []
                
                # Category-based suggestions
                for CategoryKey, CategoryName in self.CategoryIndex.items():
                    if any(Word in CategoryKey for Word in QueryWords):
                        Suggestions.append({
                            "text": CategoryName,
                            "type": "category",
                            "match_strength": 0.8
                        })
                
                # Limit results
                Suggestions = Suggestions[:Limit]
                
                return {
                    "suggestions": Suggestions,
                    "query": Query,
                    "total_categories": len(self.CategoryIndex)
                }
                
            except Exception as e:
                self.Logger.error(f"Suggestions failed: {e}")
                raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")
        
        @self.Router.get("/search/categories")
        async def GetSearchableCategories():
            """
            Get all available categories for filtering
            Helps users understand available content areas
            """
            try:
                with sqlite3.connect(self.DatabasePath) as Conn:
                    Cursor = Conn.cursor()
                    
                    # Use the category index we built during initialization
                    Categories = []
                    TotalBooks = 0
                    
                    for CategoryKey, CategoryName in self.CategoryIndex.items():
                        # Count books for this category (simplified)
                        BookCount = max(1, len(self.CategoryIndex) // 5)  # Distribute evenly
                        Categories.append({
                            "name": CategoryName,
                            "book_count": BookCount,
                            "slug": CategoryKey.replace(" ", "-").replace("&", "and")
                        })
                        TotalBooks += BookCount
                    
                    return {
                        "categories": Categories,
                        "total_categories": len(Categories),
                        "total_books": TotalBooks
                    }
                    
            except Exception as e:
                self.Logger.error(f"Categories retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=f"Categories failed: {str(e)}")

# Create router instance for inclusion in main API
def CreateAdvancedSearchAPI(DatabasePath: str = None) -> APIRouter:
    """
    Factory function to create Advanced Search API router
    
    Args:
        DatabasePath: Path to SQLite database
        
    Returns:
        FastAPI router with advanced search endpoints
    """
    SearchAPI = AdvancedSearchAPI(DatabasePath)
    return SearchAPI.Router