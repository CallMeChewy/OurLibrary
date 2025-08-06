#!/usr/bin/env python3
# File: test_pwa_features.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_pwa_features.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-27
# Last Modified: 2025-07-27 11:58PM

"""
Test suite for Progressive Web App (PWA) features
Tests PWA manifest, service worker, and offline functionality
"""

import unittest
import os
import sys
import json
import requests
import time
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPWAFeatures(unittest.TestCase):
    """Test Progressive Web App functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_dir = Path(__file__).parent.parent
        cls.webpages_dir = cls.base_dir / "WebPages"
        cls.test_server_url = "http://127.0.0.1:8000"
        
    def test_manifest_file_exists(self):
        """Test that PWA manifest file exists and is valid"""
        manifest_path = self.webpages_dir / "manifest.json"
        self.assertTrue(manifest_path.exists(), "PWA manifest.json should exist")
        
        # Test manifest content
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Required PWA manifest fields
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        for field in required_fields:
            self.assertIn(field, manifest, f"Manifest should contain '{field}' field")
        
        # Educational mission validation
        self.assertIn('education', manifest['description'].lower(), 
                     "Manifest should mention educational mission")
        self.assertEqual(manifest['display'], 'standalone', 
                        "PWA should display as standalone app")
    
    def test_service_worker_exists(self):
        """Test that service worker file exists and has core functionality"""
        sw_path = self.webpages_dir / "service-worker.js"
        self.assertTrue(sw_path.exists(), "Service worker should exist")
        
        # Test service worker content
        with open(sw_path, 'r') as f:
            sw_content = f.read()
        
        # Required service worker features
        required_features = [
            'addEventListener', 'install', 'activate', 'fetch',
            'caches.open', 'cache.put', 'cache.match',
            'andylibrary', 'educational'
        ]
        
        for feature in required_features:
            self.assertIn(feature, sw_content, 
                         f"Service worker should contain '{feature}'")
    
    def test_pwa_html_integration(self):
        """Test that HTML pages have PWA integration"""
        bowersworld_path = self.webpages_dir / "bowersworld.html"
        self.assertTrue(bowersworld_path.exists(), "BowersWorld page should exist")
        
        with open(bowersworld_path, 'r') as f:
            html_content = f.read()
        
        # PWA integration requirements
        pwa_elements = [
            'rel="manifest"',
            'meta name="theme-color"',
            'apple-mobile-web-app-capable',
            'serviceWorker.register',
            'beforeinstallprompt'
        ]
        
        for element in pwa_elements:
            self.assertIn(element, html_content, 
                         f"HTML should contain PWA element: {element}")
    
    def test_offline_cache_strategy(self):
        """Test that offline caching strategy is educational mission focused"""
        sw_path = self.webpages_dir / "service-worker.js"
        
        with open(sw_path, 'r') as f:
            sw_content = f.read()
        
        # Educational mission caching priorities
        cache_priorities = [
            'thumbnails',  # Images expensive on limited data
            'pdf',         # Large files need aggressive caching
            'educational', # Mission-focused content
            'offline'      # Offline-first approach
        ]
        
        for priority in cache_priorities:
            self.assertIn(priority.lower(), sw_content.lower(),
                         f"Service worker should prioritize '{priority}' caching")
    
    def test_tablet_optimization(self):
        """Test that PWA is optimized for tablet devices"""
        bowersworld_path = self.webpages_dir / "bowersworld.html"
        
        with open(bowersworld_path, 'r') as f:
            html_content = f.read()
        
        # Tablet optimization elements
        tablet_features = [
            'min-width: 768px',  # Tablet media queries
            'max-width: 1024px', # Tablet screen sizes
            'touch-action',      # Touch gesture support
            'hover: none',       # Touch device detection
            'pointer: coarse',   # Touch pointer detection
            'min-height: 44px'   # Touch target size
        ]
        
        tablet_feature_count = sum(1 for feature in tablet_features 
                                  if feature in html_content)
        
        self.assertGreaterEqual(tablet_feature_count, 4,
                               "HTML should have significant tablet optimizations")

class TestPWAInstallation(unittest.TestCase):
    """Test PWA installation prompts and UX"""
    
    def setUp(self):
        """Set up for installation tests"""
        self.webpages_dir = Path(__file__).parent.parent / "WebPages"
    
    def test_install_prompt_messaging(self):
        """Test that install prompts use educational messaging"""
        bowersworld_path = self.webpages_dir / "bowersworld.html"
        
        with open(bowersworld_path, 'r') as f:
            html_content = f.read()
        
        # Educational install messaging
        educational_messages = [
            'Install AndyLibrary',
            'Offline access',
            'Home screen',
            'educational',
            'reading'
        ]
        
        message_count = sum(1 for msg in educational_messages 
                           if msg.lower() in html_content.lower())
        
        self.assertGreaterEqual(message_count, 3,
                               "Install prompts should use educational messaging")
    
    def test_install_banner_implementation(self):
        """Test that install banner is properly implemented"""
        bowersworld_path = self.webpages_dir / "bowersworld.html"
        
        with open(bowersworld_path, 'r') as f:
            html_content = f.read()
        
        # Install banner functionality
        banner_features = [
            'showInstallBanner',
            'beforeinstallprompt',
            'prompt.prompt()',
            'installPWA',
            'deferredPrompt'
        ]
        
        for feature in banner_features:
            self.assertIn(feature, html_content,
                         f"Install banner should implement '{feature}'")

if __name__ == '__main__':
    # Run PWA tests
    print("🧪 Running PWA Feature Tests...")
    unittest.main(verbosity=2)