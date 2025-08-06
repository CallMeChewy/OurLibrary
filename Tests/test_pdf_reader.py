#!/usr/bin/env python3
# File: test_pdf_reader.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_pdf_reader.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-27
# Last Modified: 2025-07-27 11:58PM

"""
Test suite for PDF Reader functionality
Tests PDF serving, reader interface, and tablet optimization
"""

import unittest
import os
import sys
import sqlite3
import json
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPDFReaderInterface(unittest.TestCase):
    """Test PDF Reader HTML interface"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_dir = Path(__file__).parent.parent
        cls.webpages_dir = cls.base_dir / "WebPages"
    
    def test_pdf_reader_exists(self):
        """Test that PDF reader HTML file exists"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        self.assertTrue(pdf_reader_path.exists(), "PDF reader HTML should exist")
    
    def test_pdf_reader_has_core_features(self):
        """Test that PDF reader has essential features"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Core PDF reader features
        core_features = [
            'PDF.js',           # PDF rendering library
            'canvas',           # PDF rendering canvas
            'previousPage',     # Navigation
            'nextPage',         # Navigation
            'zoomIn',          # Zoom controls
            'zoomOut',         # Zoom controls
            'nightMode',       # Reading comfort
            'touchstart',      # Tablet support
            'keydown'          # Keyboard accessibility
        ]
        
        for feature in core_features:
            self.assertIn(feature, html_content,
                         f"PDF reader should contain '{feature}' functionality")
    
    def test_tablet_optimization_features(self):
        """Test that PDF reader is optimized for tablets"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Tablet optimization features
        tablet_features = [
            'touch-action',        # Touch gesture handling
            'min-width: 768px',    # Tablet media queries
            'swipe',               # Swipe gestures
            'touchstart',          # Touch event handling
            'touchend',            # Touch event handling
            'min-height: 44px',    # Touch target sizes
            'full screen',         # Full screen reading
            'apple-mobile-web-app' # iOS optimization
        ]
        
        tablet_feature_count = sum(1 for feature in tablet_features 
                                  if feature.lower() in html_content.lower())
        
        self.assertGreaterEqual(tablet_feature_count, 5,
                               "PDF reader should have significant tablet optimizations")
    
    def test_educational_mission_features(self):
        """Test that PDF reader supports educational mission"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Educational mission features
        educational_features = [
            'reading progress',   # Track learning progress
            'bookmark',          # Save important content
            'night mode',        # Comfortable reading
            'educational',       # Mission focus
            'offline',           # Cost protection
            'cache'              # Data saving
        ]
        
        feature_count = sum(1 for feature in educational_features 
                           if feature.lower() in html_content.lower())
        
        self.assertGreaterEqual(feature_count, 4,
                               "PDF reader should support educational mission features")

class TestPDFDatabaseIntegration(unittest.TestCase):
    """Test PDF reader integration with book database"""
    
    @classmethod
    def setUpClass(cls):
        """Set up database test environment"""
        cls.base_dir = Path(__file__).parent.parent
        cls.db_path = cls.base_dir / "Data" / "Databases" / "MyLibrary.db"
    
    def test_database_has_pdf_books(self):
        """Test that database contains PDF books"""
        if not self.db_path.exists():
            self.skipTest("Database not available for testing")
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check for PDF books
        cursor.execute("""
            SELECT COUNT(*) FROM books 
            WHERE FilePath LIKE '%.pdf' AND FilePath IS NOT NULL
        """)
        
        pdf_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertGreater(pdf_count, 0, "Database should contain PDF books")
    
    def test_pdf_book_structure(self):
        """Test that PDF books have required fields"""
        if not self.db_path.exists():
            self.skipTest("Database not available for testing")
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get a sample PDF book
        cursor.execute("""
            SELECT id, title, author, FilePath, PageCount
            FROM books 
            WHERE FilePath LIKE '%.pdf' 
            LIMIT 1
        """)
        
        book = cursor.fetchone()
        conn.close()
        
        if book:
            self.assertIsNotNone(book[0], "PDF book should have ID")
            self.assertIsNotNone(book[1], "PDF book should have title")
            self.assertTrue(book[3].endswith('.pdf'), "PDF book should have .pdf file path")

class TestPDFReaderAccessibility(unittest.TestCase):
    """Test PDF reader accessibility features"""
    
    def setUp(self):
        """Set up accessibility tests"""
        self.webpages_dir = Path(__file__).parent.parent / "WebPages"
    
    def test_keyboard_navigation_support(self):
        """Test that PDF reader supports keyboard navigation"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Keyboard navigation features
        keyboard_features = [
            'keydown',           # Keyboard event handling
            'ArrowLeft',         # Left arrow key
            'ArrowRight',        # Right arrow key
            'PageUp',            # Page up key
            'PageDown',          # Page down key
            'Space',             # Spacebar
            'Home',              # Home key
            'End'                # End key
        ]
        
        keyboard_support = sum(1 for feature in keyboard_features 
                              if feature in html_content)
        
        self.assertGreaterEqual(keyboard_support, 6,
                               "PDF reader should support comprehensive keyboard navigation")
    
    def test_touch_accessibility(self):
        """Test that PDF reader is accessible via touch"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Touch accessibility features
        touch_features = [
            'min-height: 44px',  # Minimum touch target size
            'min-width: 44px',   # Minimum touch target size
            'touchstart',        # Touch event support
            'swipe',             # Gesture support
            'active',            # Touch feedback
            'focus'              # Focus management
        ]
        
        touch_support = sum(1 for feature in touch_features 
                           if feature in html_content)
        
        self.assertGreaterEqual(touch_support, 4,
                               "PDF reader should be touch accessible")

class TestPDFReaderPerformance(unittest.TestCase):
    """Test PDF reader performance optimizations"""
    
    def setUp(self):
        """Set up performance tests"""
        self.webpages_dir = Path(__file__).parent.parent / "WebPages"
    
    def test_caching_strategy(self):
        """Test that PDF reader implements good caching"""
        service_worker_path = self.webpages_dir / "service-worker.js"
        
        if service_worker_path.exists():
            with open(service_worker_path, 'r') as f:
                sw_content = f.read()
            
            # PDF caching features
            caching_features = [
                'handlePdfRequest',  # Dedicated PDF handler
                'PDF_CACHE',         # PDF-specific cache
                'aggressive',        # Aggressive caching
                'offline reading'    # Offline capability
            ]
            
            caching_support = sum(1 for feature in caching_features 
                                 if feature in sw_content)
            
            self.assertGreaterEqual(caching_support, 2,
                                   "Service worker should implement PDF caching")
    
    def test_progressive_loading(self):
        """Test that PDF reader supports progressive loading"""
        pdf_reader_path = self.webpages_dir / "pdf-reader.html"
        
        with open(pdf_reader_path, 'r') as f:
            html_content = f.read()
        
        # Progressive loading features
        loading_features = [
            'loading',           # Loading indicators
            'pageRendering',     # Page rendering states
            'pageNumPending',    # Queue management
            'renderPage',        # Render management
            'canvas'             # Efficient rendering
        ]
        
        loading_support = sum(1 for feature in loading_features 
                             if feature in html_content)
        
        self.assertGreaterEqual(loading_support, 4,
                               "PDF reader should support progressive loading")

if __name__ == '__main__':
    # Run PDF reader tests
    print("📖 Running PDF Reader Tests...")
    unittest.main(verbosity=2)