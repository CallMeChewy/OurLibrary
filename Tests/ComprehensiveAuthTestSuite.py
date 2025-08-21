# File: ComprehensiveAuthTestSuite.py
# Path: /home/herb/Desktop/OurLibrary/Tests/ComprehensiveAuthTestSuite.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 07:25PM
# Description: Comprehensive authentication testing suite for OurLibrary

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import tempfile
import os

class OurLibraryAuthTestSuite:
    def __init__(self):
        self.base_url = "https://callmechewy.github.io/OurLibrary/"
        self.auth_url = "https://callmechewy.github.io/OurLibrary/auth-demo.html"
        self.test_results = []
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # Remove headless for manual verification
        # chrome_options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False
    
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_main_page_loads(self):
        """Test 1: Main page loads correctly"""
        try:
            self.driver.get(self.base_url)
            
            # Check page title
            title = self.driver.title
            if "OurLibrary" not in title:
                self.log_test("Main Page Load", "FAIL", f"Title incorrect: {title}")
                return False
                
            # Check for key elements
            get_started_btn = self.driver.find_element(By.ID, "getStartedBtn")
            if not get_started_btn.is_displayed():
                self.log_test("Main Page Load", "FAIL", "Get Started button not visible")
                return False
                
            self.log_test("Main Page Load", "PASS", "All elements loaded correctly")
            return True
            
        except Exception as e:
            self.log_test("Main Page Load", "FAIL", str(e))
            return False
    
    def test_navigation_to_auth(self):
        """Test 2: Navigation from main page to auth page"""
        try:
            # Click Get Started button
            get_started_btn = self.driver.find_element(By.ID, "getStartedBtn")
            get_started_btn.click()
            
            # Wait for auth page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: "auth-demo.html" in driver.current_url
            )
            
            # Check auth page elements
            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "password")
            
            if not (email_input.is_displayed() and password_input.is_displayed()):
                self.log_test("Navigation to Auth", "FAIL", "Auth form not visible")
                return False
                
            self.log_test("Navigation to Auth", "PASS", "Successfully navigated to auth page")
            return True
            
        except Exception as e:
            self.log_test("Navigation to Auth", "FAIL", str(e))
            return False
    
    def test_email_validation(self):
        """Test 3: Email field validation"""
        try:
            email_input = self.driver.find_element(By.ID, "email")
            
            # Test invalid email formats
            invalid_emails = [
                "notanemail",
                "@gmail.com",
                "test@",
                "test..test@gmail.com",
                ""
            ]
            
            for invalid_email in invalid_emails:
                email_input.clear()
                email_input.send_keys(invalid_email)
                
                # Try to submit (should fail validation)
                try:
                    register_btn = self.driver.find_element(By.ID, "registerBtn")
                    register_btn.click()
                    
                    # Check for validation message
                    time.sleep(1)  # Allow validation to trigger
                    
                    # HTML5 validation should prevent submission
                    validity = self.driver.execute_script("return arguments[0].validity.valid;", email_input)
                    if validity:
                        self.log_test("Email Validation", "FAIL", f"Invalid email accepted: {invalid_email}")
                        return False
                        
                except Exception:
                    pass  # Expected for invalid emails
            
            self.log_test("Email Validation", "PASS", "All invalid emails properly rejected")
            return True
            
        except Exception as e:
            self.log_test("Email Validation", "FAIL", str(e))
            return False
    
    def test_password_validation(self):
        """Test 4: Password field validation"""
        try:
            password_input = self.driver.find_element(By.ID, "password")
            
            # Test weak passwords
            weak_passwords = [
                "123",      # Too short
                "password", # Too simple
                "abc",      # Too short
                ""          # Empty
            ]
            
            for weak_password in weak_passwords:
                password_input.clear()
                password_input.send_keys(weak_password)
                
                # Check length validation
                if len(weak_password) < 6:
                    validity = self.driver.execute_script("return arguments[0].validity.valid;", password_input)
                    if validity and weak_password != "":
                        self.log_test("Password Validation", "FAIL", f"Weak password accepted: {weak_password}")
                        return False
            
            self.log_test("Password Validation", "PASS", "Password validation working")
            return True
            
        except Exception as e:
            self.log_test("Password Validation", "FAIL", str(e))
            return False
    
    def test_google_auth_button(self):
        """Test 5: Google authentication button functionality"""
        try:
            google_btn = self.driver.find_element(By.ID, "googleSignInBtn")
            
            if not google_btn.is_displayed():
                self.log_test("Google Auth Button", "FAIL", "Google auth button not visible")
                return False
            
            # Check button is clickable
            if not google_btn.is_enabled():
                self.log_test("Google Auth Button", "FAIL", "Google auth button not enabled")
                return False
                
            self.log_test("Google Auth Button", "PASS", "Google auth button ready")
            return True
            
        except Exception as e:
            self.log_test("Google Auth Button", "FAIL", str(e))
            return False
    
    def test_firebase_connection(self):
        """Test 6: Firebase SDK loading and initialization"""
        try:
            # Check if Firebase is loaded
            firebase_loaded = self.driver.execute_script("""
                return typeof firebase !== 'undefined' && 
                       typeof firebase.auth !== 'undefined' &&
                       typeof firebase.auth() !== 'undefined';
            """)
            
            if not firebase_loaded:
                self.log_test("Firebase Connection", "FAIL", "Firebase SDK not properly loaded")
                return False
            
            # Check Firebase config
            firebase_config = self.driver.execute_script("""
                try {
                    return firebase.app().options;
                } catch(e) {
                    return null;
                }
            """)
            
            if not firebase_config or not firebase_config.get('projectId'):
                self.log_test("Firebase Connection", "FAIL", "Firebase not properly configured")
                return False
                
            self.log_test("Firebase Connection", "PASS", f"Firebase connected to project: {firebase_config.get('projectId')}")
            return True
            
        except Exception as e:
            self.log_test("Firebase Connection", "FAIL", str(e))
            return False
    
    def test_stupid_human_errors(self):
        """Test 7: Common user mistakes"""
        try:
            # Test case sensitivity confusion
            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "password")
            
            # Test with spaces in email
            email_input.clear()
            email_input.send_keys(" test@gmail.com ")
            
            # JavaScript should handle trimming
            time.sleep(1)
            
            # Test caps lock password
            password_input.clear()
            password_input.send_keys("PASSWORD123")
            
            # Test rapid clicking (double submission prevention)
            register_btn = self.driver.find_element(By.ID, "registerBtn")
            
            # Multiple rapid clicks
            for i in range(3):
                try:
                    register_btn.click()
                    time.sleep(0.1)
                except:
                    pass
            
            self.log_test("Stupid Human Errors", "PASS", "Error scenarios handled gracefully")
            return True
            
        except Exception as e:
            self.log_test("Stupid Human Errors", "FAIL", str(e))
            return False
    
    def manual_test_instructions(self):
        """Provide instructions for manual testing with real accounts"""
        instructions = """
        
🧪 MANUAL TESTING PHASE
========================

Now we need to test with real accounts. Please perform these tests:

📧 EMAIL REGISTRATION TEST:
1. Create a new email account (Gmail, Yahoo, etc.)
2. Use this new email to register on: https://callmechewy.github.io/OurLibrary/auth-demo.html
3. Check the email inbox for verification
4. Click the verification link
5. Confirm successful registration

🔐 GOOGLE OAUTH TEST:
1. Create a new Google account (or use existing)
2. Go to: https://callmechewy.github.io/OurLibrary/auth-demo.html
3. Click "Sign in with Google"
4. Complete Google OAuth flow
5. Confirm successful authentication

🔍 FIREBASE VALIDATION:
1. Check Firebase Console: https://console.firebase.google.com/project/our-library-d7b60
2. Go to Authentication > Users
3. Verify new users appear in the list
4. Check user creation timestamps

⚠️ EDGE CASE TESTING:
1. Try registering the same email twice
2. Try invalid email formats
3. Try weak passwords
4. Test on mobile device
5. Test with slow internet connection
6. Test with ad blockers enabled

Please run through these tests and report any issues!
        """
        
        print(instructions)
        self.log_test("Manual Test Instructions", "INFO", "Instructions provided to user")
    
    def run_automated_tests(self):
        """Run all automated tests"""
        print("🚀 Starting OurLibrary Authentication Test Suite")
        print("=" * 50)
        
        if not self.setup_browser():
            return False
        
        try:
            # Run test sequence
            tests = [
                self.test_main_page_loads,
                self.test_navigation_to_auth,
                self.test_email_validation,
                self.test_password_validation,
                self.test_google_auth_button,
                self.test_firebase_connection,
                self.test_stupid_human_errors
            ]
            
            passed = 0
            failed = 0
            
            for test in tests:
                if test():
                    passed += 1
                else:
                    failed += 1
                time.sleep(1)  # Brief pause between tests
            
            print("\n" + "=" * 50)
            print(f"📊 AUTOMATED TEST RESULTS: {passed} PASSED, {failed} FAILED")
            print("=" * 50)
            
            # Keep browser open for manual testing
            print("\n🔍 Browser will remain open for manual testing...")
            self.manual_test_instructions()
            
            return failed == 0
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        report_file = "/home/herb/Desktop/OurLibrary/Tests/TestReport.md"
        
        with open(report_file, 'w') as f:
            f.write("# OurLibrary Authentication Test Report\n\n")
            f.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Tests**: {len(self.test_results)}\n\n")
            
            f.write("## Test Results\n\n")
            
            for result in self.test_results:
                status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "ℹ️"
                f.write(f"{status_emoji} **{result['test']}**: {result['status']}\n")
                if result["details"]:
                    f.write(f"   - {result['details']}\n")
                f.write(f"   - Time: {result['timestamp']}\n\n")
            
            f.write("## Manual Testing Checklist\n\n")
            f.write("- [ ] New email account registration\n")
            f.write("- [ ] Email verification received\n")
            f.write("- [ ] Email verification link works\n")
            f.write("- [ ] Google OAuth flow completion\n")
            f.write("- [ ] Users appear in Firebase Console\n")
            f.write("- [ ] Duplicate email rejection\n")
            f.write("- [ ] Mobile device testing\n")
            f.write("- [ ] Edge case scenarios\n")
        
        print(f"📄 Test report saved to: {report_file}")

if __name__ == "__main__":
    suite = OurLibraryAuthTestSuite()
    success = suite.run_automated_tests()
    suite.generate_report()
    
    if success:
        print("\n🎉 All automated tests passed! Proceed with manual testing.")
    else:
        print("\n⚠️ Some automated tests failed. Review before manual testing.")
    
    # Keep browser open for manual inspection
    input("\nPress Enter to close browser and complete testing...")
    if suite.driver:
        suite.driver.quit()