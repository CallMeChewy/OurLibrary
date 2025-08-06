# File: test_functional.py
# Path: /home/herb/Desktop/AndyLibrary/test_functional.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 09:43AM

import sys
import os
import socket
import time
import subprocess
import json
from StartOurLibrary import OurLibraryStarter

def TestPortDetection():
    """Test the smart port detection system"""
    print("🔍 Testing Port Detection...")
    
    starter = OurLibraryStarter()
    
    # Test finding available port
    port = starter.find_available_port(9000, max_attempts=5)
    if port:
        print(f"✅ Found available port: {port}")
        return True
    else:
        print("❌ Could not find available port")
        return False

def TestConfigLoading():
    """Test configuration file loading"""
    print("🔍 Testing Config Loading...")
    
    starter = OurLibraryStarter()
    
    # Check config loaded
    if starter.config:
        print(f"✅ Config loaded with {len(starter.config)} settings")
        
        # Check key settings
        expected_keys = ['server_port', 'local_database_path', 'google_credentials_path']
        missing = [key for key in expected_keys if key not in starter.config]
        
        if missing:
            print(f"⚠️ Missing config keys: {missing}")
        else:
            print("✅ All expected config keys present")
        
        return True
    else:
        print("❌ No config loaded")
        return False

def TestDatabaseConnectivity():
    """Test SQLite database connectivity"""
    print("🔍 Testing Database Connectivity...")
    
    import sqlite3
    
    try:
        db_path = "Data/Local/cached_library.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Database connected, found {len(tables)} tables: {[t[0] for t in tables]}")
            
            # Check book count
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            print(f"✅ Database has {count} books")
            
            conn.close()
            return True
        else:
            print("⚠️ Database connected but no tables found")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def TestAPIServerStartup():
    """Test if the main API server can start"""
    print("🔍 Testing API Server Startup...")
    
    try:
        # Test environment check first
        starter = OurLibraryStarter()
        issues = starter.check_environment()
        
        if issues:
            print(f"⚠️ Environment issues: {issues}")
            return False
        
        print("✅ Environment check passed")
        
        # Test port detection
        port = starter.find_available_port(8999)
        if not port:
            print("❌ Could not find available port for testing")
            return False
        
        print(f"✅ Found test port: {port}")
        return True
        
    except Exception as e:
        print(f"❌ API server startup test failed: {e}")
        return False

def TestDirectoryStructure():
    """Test that required directories exist"""
    print("🔍 Testing Directory Structure...")
    
    required_dirs = [
        "Source/API",
        "Source/Core", 
        "Source/Utils",
        "Config",
        "Data/Local",
        "Tests"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing directories: {missing}")
        return False
    else:
        print(f"✅ All {len(required_dirs)} required directories present")
        return True

def main():
    """Run all functional tests"""
    print("🧪 AndyLibrary Functional Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", TestDirectoryStructure),
        ("Config Loading", TestConfigLoading),
        ("Database Connectivity", TestDatabaseConnectivity),
        ("Port Detection", TestPortDetection),
        ("API Server Startup", TestAPIServerStartup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All functional tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed - system may have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())