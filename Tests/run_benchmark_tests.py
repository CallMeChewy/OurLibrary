# File: run_benchmark_tests.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/run_benchmark_tests.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-28
# Last Modified: 2025-07-28 09:00AM

"""
Comprehensive Benchmark Test Runner - Project Himalaya
Validates all benchmark components and ensures no regressions as we add features
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class BenchmarkTestRunner:
    """Comprehensive test runner for all Project Himalaya benchmark components"""
    
    def __init__(self):
        self.test_directory = Path(__file__).parent
        self.project_root = self.test_directory.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "execution_time": 0
            },
            "benchmark_status": "UNKNOWN"
        }
        
    def print_banner(self):
        """Print Project Himalaya test banner"""
        print("🏔️" + "=" * 80)
        print("   PROJECT HIMALAYA - COMPREHENSIVE BENCHMARK TEST SUITE")
        print("   Validating AI-Human Synergy Standards Across All Components")
        print("=" * 82)
        print()
    
    def print_section(self, title):
        """Print section header"""
        print(f"\n📋 {title}")
        print("-" * (len(title) + 4))
    
    def run_test_suite(self, test_file, description):
        """Run a specific test suite and capture results"""
        print(f"\n🧪 Running {description}")
        print(f"   File: {test_file}")
        
        start_time = time.time()
        
        try:
            # Run pytest with detailed output
            cmd = [
                sys.executable, "-m", "pytest", 
                str(self.test_directory / test_file),
                "-v", "--tb=short", "--json-report", 
                f"--json-report-file={self.test_directory}/temp_report_{test_file.replace('.py', '.json')}"
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            # Try to load JSON report
            json_report_file = self.test_directory / f"temp_report_{test_file.replace('.py', '.json')}"
            test_details = {}
            
            if json_report_file.exists():
                try:
                    with open(json_report_file, 'r') as f:
                        test_details = json.load(f)
                    json_report_file.unlink()  # Clean up temp file
                except Exception as e:
                    print(f"   ⚠️ Could not parse JSON report: {e}")
            
            # Parse pytest output for basic info
            if result.returncode == 0:
                status = "PASSED"
                print(f"   ✅ {description} - PASSED ({execution_time:.2f}s)")
            else:
                status = "FAILED"
                print(f"   ❌ {description} - FAILED ({execution_time:.2f}s)")
                if result.stdout:
                    print(f"   📝 Output: {result.stdout[-500:]}")  # Last 500 chars
                if result.stderr:
                    print(f"   ⚠️ Errors: {result.stderr[-500:]}")
            
            # Extract test counts from output
            stdout_lines = result.stdout.split('\n') if result.stdout else []
            test_count_info = {}
            
            for line in stdout_lines:
                if " passed" in line or " failed" in line or " skipped" in line:
                    # Look for pytest summary line
                    if "passed" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "passed" in part and i > 0:
                                try:
                                    test_count_info["passed"] = int(parts[i-1])
                                except (ValueError, IndexError):
                                    pass
                    break
            
            # Store results
            self.results["test_suites"][test_file] = {
                "description": description,
                "status": status,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "test_counts": test_count_info,
                "details": test_details.get("summary", {}) if test_details else {}
            }
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {description} - TIMEOUT (exceeded 5 minutes)")
            self.results["test_suites"][test_file] = {
                "description": description,
                "status": "TIMEOUT",
                "execution_time": 300,
                "return_code": -1,
                "test_counts": {},
                "details": {}
            }
            return False
            
        except Exception as e:
            print(f"   ❌ {description} - ERROR: {e}")
            self.results["test_suites"][test_file] = {
                "description": description,
                "status": "ERROR",
                "execution_time": time.time() - start_time,
                "return_code": -1,
                "error": str(e),
                "test_counts": {},
                "details": {}
            }
            return False
    
    def run_all_benchmark_tests(self):
        """Run all benchmark test suites"""
        self.print_banner()
        
        overall_start = time.time()
        
        # Define test suites in order of dependency
        test_suites = [
            # Core component tests
            ("test_modern_oauth.py", "Modern OAuth 2.0 System Tests"),
            ("test_intelligent_search.py", "Intelligent Search Engine Tests"),
            
            # Integration tests
            ("test_benchmark_integration.py", "Benchmark Component Integration Tests"),
            ("test_intelligent_search_api.py", "Intelligent Search API Tests"),
            
            # Performance and reliability tests
            ("test_performance_benchmarks.py", "Performance Benchmark Tests"),
            
            # Existing critical tests
            ("test_authentication_system.py", "Authentication System Tests"),
            ("test_api_endpoints.py", "API Endpoint Tests"),
            ("test_integration_complete_workflow.py", "Complete Workflow Integration Tests")
        ]
        
        passed_suites = 0
        total_suites = len(test_suites)
        
        self.print_section("RUNNING BENCHMARK TEST SUITES")
        
        for test_file, description in test_suites:
            test_file_path = self.test_directory / test_file
            
            if test_file_path.exists():
                success = self.run_test_suite(test_file, description)
                if success:
                    passed_suites += 1
            else:
                print(f"   ⚠️ Test file not found: {test_file}")
                self.results["test_suites"][test_file] = {
                    "description": description,
                    "status": "NOT_FOUND",
                    "execution_time": 0,
                    "return_code": -1,
                    "test_counts": {},
                    "details": {}
                }
        
        total_execution_time = time.time() - overall_start
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for suite_name, suite_info in self.results["test_suites"].items():
            counts = suite_info.get("test_counts", {})
            passed_tests += counts.get("passed", 0)
            failed_tests += counts.get("failed", 0)
            skipped_tests += counts.get("skipped", 0)
        
        total_tests = passed_tests + failed_tests + skipped_tests
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "execution_time": total_execution_time,
            "passed_suites": passed_suites,
            "total_suites": total_suites
        }
        
        # Determine benchmark status
        if passed_suites == total_suites and failed_tests == 0:
            self.results["benchmark_status"] = "EXCELLENT"
        elif passed_suites >= total_suites * 0.9 and failed_tests <= total_tests * 0.05:
            self.results["benchmark_status"] = "GOOD"
        elif passed_suites >= total_suites * 0.8:
            self.results["benchmark_status"] = "ACCEPTABLE"
        else:
            self.results["benchmark_status"] = "NEEDS_ATTENTION"
        
        return self.results
    
    def print_detailed_results(self):
        """Print detailed test results"""
        self.print_section("DETAILED TEST RESULTS")
        
        for suite_name, suite_info in self.results["test_suites"].items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "TIMEOUT": "⏰",
                "ERROR": "🚨",
                "NOT_FOUND": "❓"
            }.get(suite_info["status"], "❓")
            
            print(f"{status_icon} {suite_info['description']}")
            print(f"   Status: {suite_info['status']}")
            print(f"   Execution Time: {suite_info['execution_time']:.2f}s")
            
            counts = suite_info.get("test_counts", {})
            if counts:
                print(f"   Tests: {counts.get('passed', 0)} passed, {counts.get('failed', 0)} failed, {counts.get('skipped', 0)} skipped")
            
            if suite_info["status"] == "FAILED" and "error" in suite_info:
                print(f"   Error: {suite_info['error']}")
            
            print()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        self.print_section("PROJECT HIMALAYA BENCHMARK TEST SUMMARY")
        
        summary = self.results["summary"]
        status = self.results["benchmark_status"]
        
        # Status indicator
        status_indicators = {
            "EXCELLENT": "🌟 EXCELLENT",
            "GOOD": "✅ GOOD", 
            "ACCEPTABLE": "⚠️ ACCEPTABLE",
            "NEEDS_ATTENTION": "❌ NEEDS ATTENTION"
        }
        
        print(f"📊 Overall Status: {status_indicators.get(status, '❓ UNKNOWN')}")
        print(f"⏱️ Total Execution Time: {summary['execution_time']:.2f} seconds")
        print()
        
        print("📈 Test Suite Results:")
        print(f"   Test Suites: {summary['passed_suites']}/{summary['total_suites']} passed")
        print(f"   Individual Tests: {summary['passed_tests']} passed, {summary['failed_tests']} failed, {summary['skipped_tests']} skipped")
        print(f"   Total Tests: {summary['total_tests']}")
        
        if summary['total_tests'] > 0:
            pass_rate = (summary['passed_tests'] / summary['total_tests']) * 100
            print(f"   Pass Rate: {pass_rate:.1f}%")
        
        print()
        
        # Benchmark compliance assessment
        print("🏔️ Project Himalaya Benchmark Compliance:")
        
        compliance_items = [
            ("OAuth 2.0 Security Standards", "test_modern_oauth.py" in self.results["test_suites"]),
            ("Educational Search Intelligence", "test_intelligent_search.py" in self.results["test_suites"]),
            ("Component Integration", "test_benchmark_integration.py" in self.results["test_suites"]),
            ("API Endpoint Functionality", "test_intelligent_search_api.py" in self.results["test_suites"]),
            ("Performance Benchmarks", "test_performance_benchmarks.py" in self.results["test_suites"]),
            ("Authentication System", "test_authentication_system.py" in self.results["test_suites"])
        ]
        
        for item_name, item_tested in compliance_items:
            if item_tested:
                suite_name = [k for k, v in self.results["test_suites"].items() if item_name.lower().replace(" ", "_") in k.lower()]
                if suite_name:
                    suite_status = self.results["test_suites"][suite_name[0]]["status"]
                    status_icon = "✅" if suite_status == "PASSED" else "❌"
                else:
                    status_icon = "✅"
            else:
                status_icon = "❓"
            
            print(f"   {status_icon} {item_name}")
        
        print()
        
        # Recommendations
        if status in ["NEEDS_ATTENTION", "ACCEPTABLE"]:
            print("🔧 Recommendations:")
            
            failed_suites = [name for name, info in self.results["test_suites"].items() 
                           if info["status"] in ["FAILED", "ERROR", "TIMEOUT"]]
            
            if failed_suites:
                print("   • Fix failing test suites:")
                for suite in failed_suites:
                    print(f"     - {suite}")
            
            if summary["failed_tests"] > 0:
                print(f"   • Address {summary['failed_tests']} individual test failures")
            
            print("   • Review error logs for specific issues")
            print("   • Consider running tests individually for detailed debugging")
        elif status == "EXCELLENT":
            print("🎉 Excellent! All benchmark standards are being maintained.")
            print("   • Ready for next benchmark component development")
            print("   • Consider running performance tests regularly")
            print("   • Maintain this quality as new features are added")
    
    def save_results(self):
        """Save test results to file"""
        results_file = self.test_directory / "benchmark_test_results.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n💾 Test results saved to: {results_file}")
            
        except Exception as e:
            print(f"\n⚠️ Could not save results to file: {e}")
    
    def run(self):
        """Main entry point - run all tests and generate report"""
        try:
            results = self.run_all_benchmark_tests()
            self.print_detailed_results()
            self.print_summary()
            self.save_results()
            
            print("\n🏔️ PROJECT HIMALAYA BENCHMARK TESTING COMPLETE")
            print("=" * 82)
            
            # Return appropriate exit code
            if results["benchmark_status"] in ["EXCELLENT", "GOOD"]:
                return 0
            else:
                return 1
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Testing interrupted by user")
            return 130
        except Exception as e:
            print(f"\n❌ Testing failed with error: {e}")
            return 1

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Project Himalaya Benchmark Test Runner")
        print()
        print("Usage: python run_benchmark_tests.py")
        print()
        print("This script runs comprehensive tests for all Project Himalaya")
        print("benchmark components to ensure no regressions as we add features.")
        print()
        print("Test Categories:")
        print("  • Modern OAuth 2.0 System")
        print("  • Intelligent Search Engine") 
        print("  • Benchmark Component Integration")
        print("  • API Endpoint Functionality")
        print("  • Performance Benchmarks")
        print("  • Authentication & Security")
        print()
        print("Exit Codes:")
        print("  0 - All tests passed (EXCELLENT/GOOD status)")
        print("  1 - Some tests failed (ACCEPTABLE/NEEDS_ATTENTION)")
        print("  130 - Interrupted by user")
        return 0
    
    runner = BenchmarkTestRunner()
    return runner.run()

if __name__ == "__main__":
    sys.exit(main())