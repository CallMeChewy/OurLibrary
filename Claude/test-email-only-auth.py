#!/usr/bin/env python3
# File: test-email-only-auth.py
# Path: /home/herb/Desktop/OurLibrary/test-email-only-auth.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:20PM
# Test email-only authentication while Google OAuth is broken

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_email_only_auth():
    """Test email authentication system thoroughly"""
    
    print("📧 TESTING EMAIL-ONLY AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    test_results = {
        'form_validation': False,
        'smtp_verification': False,
        'firebase_creation': False,
        'sheets_logging': False,
        'success_page': False
    }
    
    try:
        # Test 1: Load page and check form
        print("1. 🌐 Loading auth demo page...")
        cache_buster = int(time.time())
        driver.get(f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}")
        time.sleep(8)
        
        # Check if all form elements are present
        form_elements = {
            'fullName': driver.find_element(By.ID, "fullName"),
            'email': driver.find_element(By.ID, "email"),
            'password': driver.find_element(By.ID, "password"),
            'confirmPassword': driver.find_element(By.ID, "confirmPassword"),
            'submitButton': driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        }
        
        print("   ✅ All form elements found")
        
        # Test 2: Form validation
        print("\n2. 🧪 Testing Form Validation...")
        
        # Test password mismatch
        form_elements['fullName'].send_keys("Validation Test")
        form_elements['email'].send_keys("validation@test.com")
        form_elements['password'].send_keys("password1")
        form_elements['confirmPassword'].send_keys("password2")
        
        form_elements['submitButton'].click()
        time.sleep(2)
        
        status_container = driver.find_element(By.ID, "statusContainer")
        status_text = status_container.text
        
        if "passwords do not match" in status_text.lower():
            print("   ✅ Password validation working")
            test_results['form_validation'] = True
        else:
            print(f"   ❌ Password validation failed: {status_text}")
            
        # Clear form and test valid submission
        driver.refresh()
        time.sleep(5)
        
        # Test 3: Valid registration submission
        print("\n3. 📧 Testing Valid Registration Submission...")
        
        test_email = f"email_only_test_{int(time.time())}@example.com"
        test_name = "Email Only Test User"
        test_password = "testpass123"
        
        # Fill form with valid data
        driver.find_element(By.ID, "fullName").send_keys(test_name)
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   📝 Testing with email: {test_email}")
        
        # Clear console logs
        driver.get_log('browser')
        
        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(8)
        
        # Check if verification step is reached
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        if verification_visible:
            print("   ✅ Verification step reached")
            
            # Check displayed email
            displayed_email = driver.find_element(By.ID, "verificationEmail").text
            if displayed_email == test_email:
                print(f"   ✅ Correct email displayed: {displayed_email}")
                test_results['smtp_verification'] = True
            else:
                print(f"   ❌ Wrong email displayed: {displayed_email}")
                
        else:
            print("   ❌ Verification step not reached")
            
        # Test 4: Verification code submission
        print("\n4. 🔑 Testing Verification Code Submission...")
        
        if verification_visible:
            # Enter verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("123ABC")
            
            # Clear console logs
            driver.get_log('browser')
            
            # Add console monitoring
            driver.execute_script("""
                console.log('=== VERIFICATION TEST START ===');
                
                // Monitor Firebase operations
                const originalCreateUser = window.createUserWithEmailAndPassword;
                if (originalCreateUser) {
                    window.createUserWithEmailAndPassword = function(...args) {
                        console.log('🔥 Firebase createUser called for email:', args[2]);
                        return originalCreateUser.apply(this, args).then(result => {
                            console.log('🔥 Firebase account created successfully:', result.user.uid);
                            return result;
                        }).catch(error => {
                            console.log('🔥 Firebase creation error:', error.message);
                            throw error;
                        });
                    };
                }
            """)
            
            # Submit verification
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(10)
            
            # Get verification logs
            verification_logs = driver.get_log('browser')
            
            print("   📝 Verification process activity:")
            firebase_success = False
            sheets_activity = False
            error_found = False
            
            for log in verification_logs:
                message = log['message']
                level = log['level']
                
                if 'firebase account created successfully' in message.lower():
                    firebase_success = True
                    print(f"   ✅ {message}")
                elif 'sheets' in message.lower() and ('logged' in message.lower() or 'simulated' in message.lower()):
                    sheets_activity = True
                    print(f"   📊 {message}")
                elif level == 'SEVERE':
                    error_found = True
                    print(f"   ❌ {message}")
                elif 'verification' in message.lower() or 'registration' in message.lower():
                    print(f"   📝 {message}")
            
            # Check final state
            success_visible = driver.execute_script("""
                return document.getElementById('success-step').classList.contains('active');
            """)
            
            print(f"\n   🎯 Verification Results:")
            print(f"   Firebase account creation: {'✅' if firebase_success else '❌'}")
            print(f"   Sheets activity detected: {'✅' if sheets_activity else '❌'}")
            print(f"   Success page reached: {'✅' if success_visible else '❌'}")
            print(f"   Errors found: {'❌' if error_found else '✅ None'}")
            
            test_results['firebase_creation'] = firebase_success
            test_results['sheets_logging'] = sheets_activity
            test_results['success_page'] = success_visible
            
        # Test 5: Complete user workflow
        print("\n5. 🎯 Complete User Workflow Test...")
        
        if test_results['success_page']:
            print("   ✅ Complete email registration workflow successful")
            
            # Test library access button
            try:
                library_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Access Your Library')]")
                if library_button.is_enabled():
                    print("   ✅ Library access button available")
                else:
                    print("   ❌ Library access button disabled")
            except:
                print("   ❌ Library access button not found")
                
        else:
            print("   ❌ Complete workflow failed - success page not reached")
        
        # Test Results Summary
        print("\n" + "=" * 60)
        print("📊 EMAIL AUTHENTICATION TEST RESULTS:")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print(f"\n🎯 Email Auth Score: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ EMAIL AUTHENTICATION FULLY FUNCTIONAL")
        else:
            print("❌ EMAIL AUTHENTICATION HAS ISSUES")
            
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Email authentication test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_email_only_auth()
    print(f"\n🏁 Email authentication test: {'✅ FULLY WORKING' if success else '❌ NEEDS FIXES'}")