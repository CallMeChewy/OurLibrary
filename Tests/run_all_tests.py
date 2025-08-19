# File: run_all_tests.py
# Path: /home/herb/Desktop/OurLibrary/Tests/run_all_tests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-12
# Last Modified: 2025-08-12 01:40PM

"""
Comprehensive test runner for OurLibrary

Runs all test levels with proper reporting and categorization.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_test_category(category, description):
    """Run tests for a specific category."""
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING {category.upper()} TESTS")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "Tests/",
        "-m", category,
        "-v",
        "--tb=short",
        f"--html=Tests/reports/{category}_test_report.html",
        "--self-contained-html"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {category.upper()} TESTS PASSED")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {category.upper()} TESTS FAILED")
        print(e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def run_all_tests():
    """Run all test categories."""
    # Create reports directory
    reports_dir = Path("Tests/reports")
    reports_dir.mkdir(exist_ok=True)
    
    print(f"🚀 OurLibrary - Comprehensive Testing Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Project: Educational Access Platform")
    print(f"🎯 Mission: Getting education into the hands of people who can least afford it")
    
    # Test categories in order of priority
    test_categories = [
        ("browser", "Browser-only functionality and UI tests"),
        ("security", "Security and credential protection tests"),
        ("config", "Configuration validation tests"),
        ("unit", "Unit tests for individual components"),
        ("educational_mission", "Mission-critical educational features"),
        ("performance", "Performance and accessibility tests"),
        ("integration", "Integration tests for future development"),
        ("live", "Live website testing (requires internet)")
    ]
    
    results = {}
    
    for category, description in test_categories:
        try:
            success = run_test_category(category, description)
            results[category] = success
        except KeyboardInterrupt:
            print(f"\n⚠️ Testing interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error running {category} tests: {e}")
            results[category] = False
    
    # Summary report
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY REPORT")
    print(f"{'='*60}")
    
    passed_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{category.ljust(20)} {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed_count}/{total_count} test categories passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! OurLibrary is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the reports above.")
        return False

def run_quick_tests():
    """Run only essential tests for quick validation."""
    print(f"⚡ Quick Test Mode - Essential Tests Only")
    
    essential_categories = [
        ("browser", "Browser functionality"),
        ("security", "Security validation"),
        ("config", "Configuration check")
    ]
    
    for category, description in essential_categories:
        success = run_test_category(category, description)
        if not success:
            print(f"❌ Quick test failed at {category}")
            return False
    
    print("✅ Quick tests passed!")
    return True

if __name__ == "__main__":
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r Tests/requirements.txt")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)