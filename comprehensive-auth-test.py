#!/usr/bin/env python3
# File: comprehensive-auth-test.py
# Path: /home/herb/Desktop/OurLibrary/comprehensive-auth-test.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:00PM
# Comprehensive authentication test suite - all levels

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def comprehensive_auth_test():
    """Run comprehensive authentication tests at all levels"""
    
    print("🔬 COMPREHENSIVE AUTHENTICATION TEST SUITE")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    test_results = {
        'page_load': False,
        'firebase_init': False,
        'google_auth_config': False,
        'google_oauth_button': False,
        'email_form': False,
        'verification_flow': False,
        'sheets_integration': False,
        'error_handling': False
    }
    
    try:
        # Test 1: Page Load and Initialization
        print("\n1. 🌐 Testing Page Load and Initialization...")
        cache_buster = int(time.time())
        driver.get(f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}")
        time.sleep(8)
        
        page_title = driver.title
        print(f"   Page title: {page_title}")
        
        if "OurLibrary" in page_title:
            test_results['page_load'] = True
            print("   ✅ Page loaded successfully")
        else:
            print("   ❌ Page load failed")
            
        # Test 2: Firebase Initialization
        print("\n2. 🔥 Testing Firebase Initialization...")
        firebase_status = driver.execute_script("""
            return {
                firebaseReady: window.firebaseReady || false,
                firebaseAuth: typeof window.firebaseAuth !== 'undefined',
                firebaseFunctions: typeof window.firebaseFunctions !== 'undefined',
                createUser: typeof window.createUserWithEmailAndPassword,
                signInPopup: typeof window.signInWithPopup,
                googleProvider: typeof window.GoogleAuthProvider,
                httpsCallable: typeof window.httpsCallable
            };
        """)
        
        print("   Firebase components:")
        all_firebase_ready = True
        for component, status in firebase_status.items():
            status_icon = "✅" if (status == True or status == "function") else "❌"
            print(f"   {component}: {status} {status_icon}")
            if component in ['firebaseReady', 'firebaseAuth', 'createUser'] and status != True and status != "function":
                all_firebase_ready = False
                
        test_results['firebase_init'] = all_firebase_ready
        
        # Test 3: Google OAuth Configuration
        print("\n3. 🔑 Testing Google OAuth Configuration...")
        google_config = driver.execute_script("""
            try {
                const config = window.googleAuth ? window.googleAuth.config : null;
                return {
                    googleAuth: typeof window.googleAuth !== 'undefined',
                    clientId: config ? config.clientId : 'not found',
                    hasRealClientId: config ? !config.clientId.includes('himalaya2025ourlibrary') : false,
                    simulateMode: config ? config.simulateMode : 'unknown'
                };
            } catch (error) {
                return { error: error.message };
            }
        """)
        
        print(f"   Google Auth object: {'✅' if google_config.get('googleAuth') else '❌'}")
        print(f"   Client ID: {google_config.get('clientId', 'not found')}")
        print(f"   Real Client ID: {'✅' if google_config.get('hasRealClientId') else '❌'}")
        print(f"   Simulate mode: {google_config.get('simulateMode', 'unknown')}")
        
        test_results['google_auth_config'] = google_config.get('hasRealClientId', False)
        
        # Test 4: Google OAuth Button Click Test
        print("\n4. 🖱️ Testing Google OAuth Button...")
        try:
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
            print("   ✅ Google OAuth button found")
            
            # Check if button is clickable
            if google_button.is_enabled():
                print("   ✅ Google OAuth button is enabled")
                
                # Clear any existing logs
                driver.get_log('browser')
                
                # Try clicking (but expect it to fail with redirect_uri_mismatch)
                print("   🧪 Testing Google OAuth click (expecting redirect_uri error)...")
                google_button.click()
                time.sleep(3)
                
                # Check for OAuth popup or error
                current_url = driver.current_url
                page_source = driver.page_source
                
                if "redirect_uri_mismatch" in page_source or "Error 400" in page_source:
                    print("   ❌ Google OAuth has redirect_uri_mismatch error")
                    test_results['google_oauth_button'] = False
                elif "accounts.google.com" in current_url:
                    print("   ✅ Google OAuth popup opened successfully")
                    test_results['google_oauth_button'] = True
                else:
                    print("   ⚠️ Google OAuth behavior unclear")
                    
                # Go back to main page
                driver.get(f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}")
                time.sleep(3)
                
            else:
                print("   ❌ Google OAuth button is disabled")
                
        except NoSuchElementException:
            print("   ❌ Google OAuth button not found")
            
        # Test 5: Email Registration Form
        print("\n5. 📧 Testing Email Registration Form...")
        
        test_email = f"comprehensive_test_{int(time.time())}@example.com"
        test_name = "Comprehensive Test User"
        test_password = "testpass123"
        
        try:
            # Fill form
            driver.find_element(By.ID, "fullName").send_keys(test_name)
            driver.find_element(By.ID, "email").send_keys(test_email)
            driver.find_element(By.ID, "password").send_keys(test_password)
            driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
            
            print(f"   ✅ Form filled with email: {test_email}")
            
            # Submit form
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
            submit_button.click()
            time.sleep(5)
            
            # Check if verification step is reached
            verification_visible = driver.execute_script("""
                return document.getElementById('verification-step').classList.contains('active');
            """)
            
            if verification_visible:
                print("   ✅ Verification step reached")
                test_results['email_form'] = True
                
                # Test 6: Verification Flow
                print("\n6. 🔑 Testing Verification Flow...")
                
                # Check displayed email
                displayed_email = driver.find_element(By.ID, "verificationEmail").text
                if displayed_email == test_email:
                    print(f"   ✅ Correct email displayed: {displayed_email}")
                else:
                    print(f"   ❌ Wrong email displayed: {displayed_email} (expected {test_email})")
                
                # Enter verification code
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.send_keys("123ABC")
                
                # Clear logs
                driver.get_log('browser')
                
                # Submit verification
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                time.sleep(8)
                
                # Check results
                success_visible = driver.execute_script("""
                    return document.getElementById('success-step').classList.contains('active');
                """)
                
                verification_logs = driver.get_log('browser')
                
                print("   Verification process results:")
                firebase_success = False
                sheets_activity = False
                errors = []
                
                for log in verification_logs:
                    if 'firebase user created' in log['message'].lower() or 'real firebase' in log['message'].lower():
                        firebase_success = True
                    elif 'sheets' in log['message'].lower() and 'logged' in log['message'].lower():
                        sheets_activity = True
                    elif log['level'] == 'SEVERE':
                        errors.append(log['message'])
                
                print(f"   Firebase account creation: {'✅' if firebase_success else '❌'}")
                print(f"   Success page reached: {'✅' if success_visible else '❌'}")
                print(f"   Sheets activity: {'✅' if sheets_activity else '❌'}")
                
                if errors:
                    print("   ❌ Errors found:")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"      {error[:100]}...")
                
                test_results['verification_flow'] = success_visible and not errors
                test_results['sheets_integration'] = sheets_activity
                
            else:
                print("   ❌ Verification step not reached")
                
        except Exception as e:
            print(f"   ❌ Email form test failed: {str(e)}")
            
        # Test 7: Error Handling
        print("\n7. 🛠️ Testing Error Handling...")
        
        # Go back to registration
        driver.get(f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}")
        time.sleep(3)
        
        # Test password mismatch
        try:
            driver.find_element(By.ID, "fullName").send_keys("Error Test")
            driver.find_element(By.ID, "email").send_keys("error@test.com")
            driver.find_element(By.ID, "password").send_keys("password1")
            driver.find_element(By.ID, "confirmPassword").send_keys("password2")
            
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
            submit_button.click()
            time.sleep(2)
            
            # Check for error message
            status_container = driver.find_element(By.ID, "statusContainer")
            status_text = status_container.text
            
            if "passwords do not match" in status_text.lower():
                print("   ✅ Password mismatch error handled correctly")
                test_results['error_handling'] = True
            else:
                print(f"   ❌ Password mismatch not handled: {status_text}")
                
        except Exception as e:
            print(f"   ❌ Error handling test failed: {str(e)}")
        
        # Test Results Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS:")
        print("=" * 60)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
        
        # Critical Issues Identification
        critical_issues = []
        if not test_results['firebase_init']:
            critical_issues.append("Firebase initialization failure")
        if not test_results['google_oauth_button']:
            critical_issues.append("Google OAuth redirect_uri_mismatch")
        if not test_results['verification_flow']:
            critical_issues.append("Email verification flow broken")
            
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES - System functional")
            
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = comprehensive_auth_test()
    print(f"\n🏁 Comprehensive auth test: {'✅ ALL SYSTEMS FUNCTIONAL' if success else '❌ ISSUES FOUND'}")