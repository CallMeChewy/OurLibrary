# File: QuickTestValidation.py
# Path: /home/herb/Desktop/OurLibrary/Tests/QuickTestValidation.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 07:30PM
# Description: Quick validation tests for OurLibrary authentication system

import requests
import json
import time

class QuickAuthValidator:
    def __init__(self):
        self.main_url = "https://callmechewy.github.io/OurLibrary/"
        self.auth_url = "https://callmechewy.github.io/OurLibrary/auth-demo.html"
        self.results = []
        
    def log_result(self, test, status, details=""):
        """Log test result"""
        result = f"{'✅' if status == 'PASS' else '❌' if status == 'FAIL' else 'ℹ️'} {test}: {status}"
        if details:
            result += f"\n   {details}"
        print(result)
        self.results.append({"test": test, "status": status, "details": details})
    
    def test_site_accessibility(self):
        """Test if sites are accessible"""
        try:
            # Test main site
            response = requests.get(self.main_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Main Site Accessibility", "PASS", f"Status: {response.status_code}")
            else:
                self.log_result("Main Site Accessibility", "FAIL", f"Status: {response.status_code}")
                return False
                
            # Test auth page
            response = requests.get(self.auth_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Auth Page Accessibility", "PASS", f"Status: {response.status_code}")
            else:
                self.log_result("Auth Page Accessibility", "FAIL", f"Status: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Site Accessibility", "FAIL", str(e))
            return False
    
    def test_required_resources(self):
        """Test if required resources load"""
        try:
            response = requests.get(self.main_url, timeout=10)
            content = response.text
            
            # Check for Firebase SDK
            if "firebase" in content.lower():
                self.log_result("Firebase SDK Present", "PASS", "Firebase references found")
            else:
                self.log_result("Firebase SDK Present", "FAIL", "No Firebase references")
            
            # Check for authentication elements
            if "registration" in content.lower() or "register" in content.lower():
                self.log_result("Registration Elements", "PASS", "Registration functionality present")
            else:
                self.log_result("Registration Elements", "FAIL", "Registration elements missing")
            
            # Check for Google OAuth
            if "google" in content.lower():
                self.log_result("Google OAuth Elements", "PASS", "Google OAuth references found")
            else:
                self.log_result("Google OAuth Elements", "FAIL", "Google OAuth missing")
                
            return True
            
        except Exception as e:
            self.log_result("Required Resources", "FAIL", str(e))
            return False
    
    def test_auth_page_structure(self):
        """Test auth page structure"""
        try:
            response = requests.get(self.auth_url, timeout=10)
            content = response.text
            
            # Check for email input
            if 'type="email"' in content:
                self.log_result("Email Input Present", "PASS", "Email input field found")
            else:
                self.log_result("Email Input Present", "FAIL", "Email input missing")
            
            # Check for password input
            if 'type="password"' in content:
                self.log_result("Password Input Present", "PASS", "Password input field found")
            else:
                self.log_result("Password Input Present", "FAIL", "Password input missing")
            
            # Check for Firebase config
            if "firebaseConfig" in content:
                self.log_result("Firebase Config Present", "PASS", "Firebase configuration found")
            else:
                self.log_result("Firebase Config Present", "FAIL", "Firebase config missing")
                
            return True
            
        except Exception as e:
            self.log_result("Auth Page Structure", "FAIL", str(e))
            return False
    
    def run_quick_validation(self):
        """Run quick validation tests"""
        print("🚀 OurLibrary Quick Validation Suite")
        print("=" * 50)
        
        tests = [
            self.test_site_accessibility,
            self.test_required_resources,
            self.test_auth_page_structure
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                self.log_result(test.__name__, "FAIL", str(e))
            
            time.sleep(0.5)
        
        print("\n" + "=" * 50)
        print(f"📊 QUICK VALIDATION: {passed} PASSED, {failed} FAILED")
        print("=" * 50)
        
        return failed == 0

def create_manual_test_guide():
    """Create comprehensive manual testing guide"""
    guide = """
🧪 COMPREHENSIVE MANUAL TESTING GUIDE
=====================================

📧 STEP 1: EMAIL REGISTRATION TEST
----------------------------------
1. Open: https://callmechewy.github.io/OurLibrary/
2. Look for "Get Started" or registration button
3. Create new email account if needed: 
   - Gmail: https://accounts.google.com/signup
   - Yahoo: https://login.yahoo.com/account/create
   - Outlook: https://outlook.live.com/owa/

4. Complete email registration:
   ✓ Enter new email address
   ✓ Enter secure password (8+ characters)
   ✓ Submit registration form
   ✓ Check for success/confirmation message

5. Email verification:
   ✓ Check email inbox (including spam/junk)
   ✓ Find verification email from OurLibrary
   ✓ Click verification link
   ✓ Confirm verification success page

6. Login test:
   ✓ Return to site and try logging in
   ✓ Use verified email and password
   ✓ Confirm successful authentication

🔐 STEP 2: GOOGLE OAUTH TEST
----------------------------
1. Navigate to site: https://callmechewy.github.io/OurLibrary/
2. Look for "Sign in with Google" button
3. Click Google authentication
4. Complete OAuth flow:
   ✓ Google popup appears
   ✓ Select Google account
   ✓ Grant permissions
   ✓ Successful authentication
   ✓ Return to OurLibrary authenticated

🔍 STEP 3: FIREBASE VALIDATION
------------------------------
1. Open Firebase Console: https://console.firebase.google.com/
2. Navigate to our-library-d7b60 project
3. Go to Authentication > Users
4. Verify both users appear:
   ✓ Email user with verified email
   ✓ Google user with Google provider
   ✓ Unique UIDs for each user
   ✓ Correct creation timestamps

⚠️ STEP 4: EDGE CASE TESTING
-----------------------------
1. Duplicate email test:
   ✓ Try registering same email twice
   ✓ Should get appropriate error message

2. Invalid input tests:
   ✓ Invalid email formats: "notanemail", "@gmail.com"
   ✓ Weak passwords: "123", "password"
   ✓ Empty fields
   ✓ Special characters in fields

3. Network condition tests:
   ✓ Slow internet connection
   ✓ Interrupted connection during registration
   ✓ Mobile device testing

4. Browser compatibility:
   ✓ Chrome (desktop & mobile)
   ✓ Firefox
   ✓ Safari (if available)
   ✓ Edge

🚨 STEP 5: SECURITY VALIDATION
------------------------------
1. HTTPS verification:
   ✓ All pages use HTTPS
   ✓ No mixed content warnings
   ✓ Valid SSL certificates

2. Data protection:
   ✓ Passwords not visible in network requests
   ✓ No credentials in browser console
   ✓ Proper error messages (no stack traces)

3. Firebase security:
   ✓ Only authenticated users in Firebase Console
   ✓ No unauthorized access to database
   ✓ Proper authentication rules

📱 STEP 6: USER EXPERIENCE TEST
-------------------------------
1. Mobile responsiveness:
   ✓ Site works on phone/tablet
   ✓ Forms are easily usable
   ✓ Text is readable
   ✓ Buttons are properly sized

2. Loading performance:
   ✓ Pages load within 3 seconds
   ✓ No broken images or resources
   ✓ Smooth transitions

3. Error handling:
   ✓ Clear error messages
   ✓ Recovery from errors possible
   ✓ No confusing technical jargon

📋 TESTING CHECKLIST
====================
□ Email registration completed successfully
□ Email verification received and worked
□ Google OAuth flow completed
□ Both users visible in Firebase Console
□ Duplicate email properly rejected
□ Invalid inputs properly handled
□ Site works on mobile device
□ HTTPS security verified
□ No console errors observed
□ Performance is acceptable

🎯 SUCCESS CRITERIA
===================
✅ All tests pass without critical issues
✅ Both email and Google auth work end-to-end
✅ Users appear correctly in Firebase
✅ Security measures are effective
✅ User experience is smooth

Report any issues found during testing!
"""
    
    with open("/home/herb/Desktop/OurLibrary/Tests/ManualTestGuide.txt", "w") as f:
        f.write(guide)
    
    print("📋 Manual test guide saved to: Tests/ManualTestGuide.txt")
    return guide

if __name__ == "__main__":
    validator = QuickAuthValidator()
    
    print("Starting quick validation...")
    success = validator.run_quick_validation()
    
    print("\n" + create_manual_test_guide())
    
    if success:
        print("\n🎉 Quick validation passed! Proceed with manual testing.")
    else:
        print("\n⚠️ Quick validation found issues. Review before manual testing.")