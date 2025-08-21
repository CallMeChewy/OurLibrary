# File: RealTimeTestValidator.py
# Path: /home/herb/Desktop/OurLibrary/Tests/RealTimeTestValidator.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 07:35PM
# Description: Real-time interactive testing validator for OurLibrary

import time
import json
import webbrowser
import input
from datetime import datetime

class RealTimeTestValidator:
    def __init__(self):
        self.test_results = []
        self.current_test = None
        
    def log_test(self, test_name, status, details="", user_input=""):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "user_input": user_input,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️" if status == "WARNING" else "ℹ️"
        print(f"{emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def get_user_confirmation(self, question, expected_answers=None):
        """Get user confirmation for test steps"""
        if expected_answers is None:
            expected_answers = ["y", "yes", "n", "no"]
        
        while True:
            response = input(f"{question} ({'/'.join(expected_answers)}): ").strip().lower()
            if response in expected_answers:
                return response
            print(f"Please answer with one of: {', '.join(expected_answers)}")
    
    def test_email_registration_flow(self):
        """Interactive email registration testing"""
        print("\n📧 EMAIL REGISTRATION FLOW TEST")
        print("=" * 40)
        
        # Step 1: Navigate to site
        print("1. Opening OurLibrary main site...")
        webbrowser.open("https://callmechewy.github.io/OurLibrary/")
        
        response = self.get_user_confirmation("Did the main site load successfully?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Main site failed to load")
            return False
        
        # Step 2: Find registration
        print("\n2. Look for registration button/option on the main page")
        response = self.get_user_confirmation("Can you see a way to register (button, link, form)?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Registration option not visible")
            return False
        
        # Step 3: Start registration
        print("\n3. Click on the registration option")
        response = self.get_user_confirmation("Did a registration form appear?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Registration form not working")
            return False
        
        # Step 4: Create test email
        print("\n4. Create a new email account for testing:")
        print("   - Gmail: https://accounts.google.com/signup")
        print("   - Yahoo: https://login.yahoo.com/account/create")
        print("   - Outlook: https://outlook.live.com/owa/")
        
        test_email = input("Enter the new email address you created: ").strip()
        if not test_email or "@" not in test_email:
            self.log_test("Email Registration Flow", "WARNING", "Invalid email format provided")
        
        # Step 5: Fill registration form
        print(f"\n5. Fill out the registration form with:")
        print(f"   Email: {test_email}")
        print("   Password: (choose a secure password)")
        print("   Any other required fields")
        
        response = self.get_user_confirmation("Have you filled out and submitted the registration form?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "User could not complete registration form")
            return False
        
        # Step 6: Check for confirmation
        response = self.get_user_confirmation("Did you see a confirmation message about checking your email?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "WARNING", "No email confirmation message shown")
        
        # Step 7: Email verification
        print(f"\n7. Check the email inbox for {test_email}")
        print("   - Check main inbox and spam/junk folder")
        print("   - Look for email from OurLibrary or Firebase")
        
        response = self.get_user_confirmation("Did you receive a verification email?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Verification email not received", test_email)
            return False
        
        # Step 8: Click verification link
        response = self.get_user_confirmation("Did you click the verification link in the email?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "User did not click verification link")
            return False
        
        response = self.get_user_confirmation("Did the verification link work (success page or redirect)?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Verification link failed", test_email)
            return False
        
        # Step 9: Test login
        print("\n9. Now test logging in with your verified account")
        print("   - Return to the OurLibrary site")
        print("   - Find the login option")
        print(f"   - Login with: {test_email}")
        
        response = self.get_user_confirmation("Were you able to successfully login with your verified email?")
        if response in ["n", "no"]:
            self.log_test("Email Registration Flow", "FAIL", "Login failed after verification", test_email)
            return False
        
        self.log_test("Email Registration Flow", "PASS", "Complete email registration and login successful", test_email)
        return True
    
    def test_google_oauth_flow(self):
        """Interactive Google OAuth testing"""
        print("\n🔐 GOOGLE OAUTH FLOW TEST")
        print("=" * 40)
        
        # Step 1: Navigate to site
        print("1. Navigate to OurLibrary (if not already there)")
        webbrowser.open("https://callmechewy.github.io/OurLibrary/")
        
        # Step 2: Find Google auth
        print("\n2. Look for 'Sign in with Google' or Google authentication button")
        response = self.get_user_confirmation("Can you see a Google authentication option?")
        if response in ["n", "no"]:
            self.log_test("Google OAuth Flow", "FAIL", "Google auth button not visible")
            return False
        
        # Step 3: Click Google auth
        print("\n3. Click on the Google authentication button")
        response = self.get_user_confirmation("Did a Google OAuth popup or redirect appear?")
        if response in ["n", "no"]:
            self.log_test("Google OAuth Flow", "FAIL", "Google OAuth not triggered")
            return False
        
        # Step 4: Complete OAuth
        print("\n4. Complete the Google OAuth flow:")
        print("   - Select your Google account")
        print("   - Grant permissions to OurLibrary")
        print("   - Allow access to basic profile info")
        
        response = self.get_user_confirmation("Did you successfully complete the Google OAuth flow?")
        if response in ["n", "no"]:
            self.log_test("Google OAuth Flow", "FAIL", "Google OAuth flow failed")
            return False
        
        # Step 5: Check authentication
        response = self.get_user_confirmation("Are you now logged into OurLibrary with your Google account?")
        if response in ["n", "no"]:
            self.log_test("Google OAuth Flow", "FAIL", "Google authentication unsuccessful")
            return False
        
        google_email = input("What Google email address did you use? ").strip()
        self.log_test("Google OAuth Flow", "PASS", "Google OAuth authentication successful", google_email)
        return True
    
    def test_firebase_console_validation(self):
        """Interactive Firebase console validation"""
        print("\n🔍 FIREBASE CONSOLE VALIDATION")
        print("=" * 40)
        
        print("1. Opening Firebase Console...")
        webbrowser.open("https://console.firebase.google.com/project/our-library-d7b60/authentication/users")
        
        print("\n2. Firebase Console Instructions:")
        print("   - Login with your Google account if prompted")
        print("   - Navigate to Authentication > Users")
        print("   - Look for the users you just created")
        
        response = self.get_user_confirmation("Can you access the Firebase Console?")
        if response in ["n", "no"]:
            self.log_test("Firebase Console Access", "FAIL", "Cannot access Firebase Console")
            return False
        
        response = self.get_user_confirmation("Do you see users in the Authentication > Users section?")
        if response in ["n", "no"]:
            self.log_test("Firebase User Validation", "WARNING", "No users visible in Firebase")
        else:
            user_count = input("How many users do you see? ").strip()
            self.log_test("Firebase User Validation", "PASS", f"Users visible in Firebase: {user_count}")
        
        # Validate specific users
        response = self.get_user_confirmation("Do you see the email user you just registered?")
        if response in ["y", "yes"]:
            self.log_test("Email User in Firebase", "PASS", "Email user confirmed in Firebase")
        else:
            self.log_test("Email User in Firebase", "FAIL", "Email user not in Firebase")
        
        response = self.get_user_confirmation("Do you see the Google user you just authenticated?")
        if response in ["y", "yes"]:
            self.log_test("Google User in Firebase", "PASS", "Google user confirmed in Firebase")
        else:
            self.log_test("Google User in Firebase", "FAIL", "Google user not in Firebase")
        
        return True
    
    def test_edge_cases(self):
        """Interactive edge case testing"""
        print("\n⚠️ EDGE CASE TESTING")
        print("=" * 40)
        
        # Test duplicate registration
        print("1. Testing duplicate email registration...")
        print("   - Try to register again with the same email you used before")
        
        response = self.get_user_confirmation("Did you try to register with the duplicate email?")
        if response in ["y", "yes"]:
            error_response = self.get_user_confirmation("Did you get an appropriate error message?")
            if error_response in ["y", "yes"]:
                self.log_test("Duplicate Email Handling", "PASS", "Duplicate email properly rejected")
            else:
                self.log_test("Duplicate Email Handling", "FAIL", "Duplicate email not properly handled")
        
        # Test invalid inputs
        print("\n2. Testing invalid email formats...")
        print("   - Try entering 'notanemail' in the email field")
        print("   - Try entering '@gmail.com' in the email field")
        
        response = self.get_user_confirmation("Did invalid email formats get rejected?")
        if response in ["y", "yes"]:
            self.log_test("Email Validation", "PASS", "Invalid email formats rejected")
        else:
            self.log_test("Email Validation", "FAIL", "Invalid email formats accepted")
        
        # Test weak passwords
        print("\n3. Testing weak passwords...")
        print("   - Try entering '123' as password")
        print("   - Try entering 'password' as password")
        
        response = self.get_user_confirmation("Did weak passwords get rejected?")
        if response in ["y", "yes"]:
            self.log_test("Password Validation", "PASS", "Weak passwords rejected")
        else:
            self.log_test("Password Validation", "WARNING", "Weak passwords may be accepted")
        
        return True
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n📊 GENERATING FINAL REPORT")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.test_results if r["status"] == "WARNING")
        
        report = f"""
# OurLibrary Authentication Testing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- ✅ PASSED: {passed}
- ❌ FAILED: {failed}
- ⚠️  WARNINGS: {warnings}
- 📋 TOTAL TESTS: {len(self.test_results)}

## Detailed Results
"""
        
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            report += f"\n{status_emoji} **{result['test']}**: {result['status']}\n"
            if result["details"]:
                report += f"   Details: {result['details']}\n"
            if result["user_input"]:
                report += f"   User Input: {result['user_input']}\n"
            report += f"   Time: {result['timestamp']}\n"
        
        # Save report
        with open("/home/herb/Desktop/OurLibrary/Tests/FinalTestReport.md", "w") as f:
            f.write(report)
        
        print(f"\n📄 Final report saved to: Tests/FinalTestReport.md")
        print(f"\n🎯 FINAL RESULTS: {passed} PASSED, {failed} FAILED, {warnings} WARNINGS")
        
        return failed == 0
    
    def run_comprehensive_testing(self):
        """Run comprehensive interactive testing"""
        print("🚀 OURLIBRARY COMPREHENSIVE AUTHENTICATION TESTING")
        print("=" * 60)
        print("This interactive test will guide you through testing both")
        print("email registration and Google OAuth authentication.")
        print("\nPlease follow the prompts carefully and test with REAL accounts.")
        print("=" * 60)
        
        # Ask user if ready
        ready = self.get_user_confirmation("\nAre you ready to begin comprehensive testing?")
        if ready in ["n", "no"]:
            print("Testing cancelled by user.")
            return False
        
        try:
            # Run test sequences
            self.test_email_registration_flow()
            print("\n" + "="*50)
            
            self.test_google_oauth_flow()
            print("\n" + "="*50)
            
            self.test_firebase_console_validation()
            print("\n" + "="*50)
            
            self.test_edge_cases()
            print("\n" + "="*50)
            
            # Generate final report
            success = self.generate_final_report()
            
            if success:
                print("\n🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
                print("✅ OurLibrary authentication system is ready for production!")
            else:
                print("\n⚠️ TESTING COMPLETED WITH ISSUES")
                print("❌ Review failed tests before production deployment.")
            
            return success
            
        except KeyboardInterrupt:
            print("\n\nTesting interrupted by user.")
            return False
        except Exception as e:
            print(f"\n\nTesting failed with error: {e}")
            return False

if __name__ == "__main__":
    validator = RealTimeTestValidator()
    validator.run_comprehensive_testing()