# File: run_automated_tests.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/run_automated_tests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 10:24AM

"""
Automated Test Runner for AndyLibrary
Runs all automated tests and provides comprehensive reporting
"""

import os
import sys
import unittest
import time
from pathlib import Path
from datetime import datetime
import json

# Add source directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

class AndyLibraryTestRunner:
    """Comprehensive test runner for AndyLibrary automated tests"""
    
    def __init__(self):
        self.test_directory = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version,
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "duration": 0
            }
        }
    
    def discover_and_run_tests(self):
        """Discover and run all test suites"""
        print("🚀 Starting AndyLibrary Automated Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test modules to run
        test_modules = [
            "test_user_environment_simple",
            "test_database_manager_isolated", 
            "test_pwa_features",
            "test_pdf_reader"
        ]
        
        total_suite = unittest.TestSuite()
        
        for module_name in test_modules:
            print(f"\n📋 Loading {module_name}...")
            
            try:
                # Import and discover tests from module
                module = __import__(module_name)
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                
                # Run tests for this module
                runner = unittest.TextTestRunner(
                    verbosity=2,
                    stream=sys.stdout,
                    buffer=True
                )
                
                print(f"🧪 Running {suite.countTestCases()} tests from {module_name}")
                result = runner.run(suite)
                
                # Record results
                self.results["test_suites"][module_name] = {
                    "tests_run": result.testsRun,
                    "failures": len(result.failures),
                    "errors": len(result.errors),
                    "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
                    "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
                }
                
                # Add to totals
                self.results["summary"]["total_tests"] += result.testsRun
                self.results["summary"]["failed"] += len(result.failures)
                self.results["summary"]["errors"] += len(result.errors)
                if hasattr(result, 'skipped'):
                    self.results["summary"]["skipped"] += len(result.skipped)
                
                total_suite.addTest(suite)
                
            except ImportError as e:
                print(f"❌ Failed to import {module_name}: {e}")
                self.results["test_suites"][module_name] = {
                    "import_error": str(e)
                }
            except Exception as e:
                print(f"❌ Error running {module_name}: {e}")
                self.results["test_suites"][module_name] = {
                    "runtime_error": str(e)
                }
        
        end_time = time.time()
        self.results["summary"]["duration"] = round(end_time - start_time, 2)
        self.results["summary"]["passed"] = (
            self.results["summary"]["total_tests"] - 
            self.results["summary"]["failed"] - 
            self.results["summary"]["errors"] -
            self.results["summary"]["skipped"]
        )
        
        self.print_summary()
        self.save_results()
        
        return self.results
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        
        print(f"⏱️  Total Duration: {summary['duration']} seconds")
        print(f"🧪 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"🚨 Errors: {summary['errors']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        
        if summary['total_tests'] > 0:
            success_rate = (summary['passed'] / summary['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Per Test Suite Results:")
        for suite_name, suite_results in self.results["test_suites"].items():
            if "import_error" in suite_results:
                print(f"  {suite_name}: ❌ Import Error - {suite_results['import_error']}")
            elif "runtime_error" in suite_results:
                print(f"  {suite_name}: ❌ Runtime Error - {suite_results['runtime_error']}")
            else:
                success_rate = suite_results.get("success_rate", 0)
                tests_run = suite_results.get("tests_run", 0)
                print(f"  {suite_name}: {tests_run} tests, {success_rate:.1f}% success")
        
        # Overall assessment
        if summary['errors'] > 0 or summary['failed'] > 0:
            print("\n🚨 SOME TESTS FAILED - Review failures above")
        elif summary['total_tests'] == 0:
            print("\n⚠️  NO TESTS FOUND - Check test discovery")
        else:
            print("\n🎉 ALL TESTS PASSED - System Ready!")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.test_directory / "test_results.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n💾 Test results saved to: {results_file}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    def run_specific_test_category(self, category):
        """Run tests for a specific category"""
        category_tests = {
            "isolation": ["test_user_environment_isolation"],
            "api": ["test_api_endpoints"],
            "auth": ["test_authentication_system"],
            "core": ["test_user_environment_isolation", "test_authentication_system"],
            "integration": ["test_api_endpoints"],
        }
        
        if category in category_tests:
            print(f"🎯 Running {category} tests...")
            
            for test_module in category_tests[category]:
                try:
                    module = __import__(test_module)
                    loader = unittest.TestLoader()
                    suite = loader.loadTestsFromModule(module)
                    
                    runner = unittest.TextTestRunner(verbosity=2)
                    result = runner.run(suite)
                    
                except ImportError as e:
                    print(f"❌ Failed to import {test_module}: {e}")
        else:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {list(category_tests.keys())}")

def main():
    """Main test runner function"""
    test_runner = AndyLibraryTestRunner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        category = sys.argv[1]
        test_runner.run_specific_test_category(category)
    else:
        # Run all tests
        results = test_runner.discover_and_run_tests()
        
        # Exit with appropriate code
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()