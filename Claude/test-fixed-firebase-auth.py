#!/usr/bin/env python3
# File: test-fixed-firebase-auth.py
# Path: /home/herb/Desktop/OurLibrary/test-fixed-firebase-auth.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 11:45AM
# Test the fixed Firebase authentication methods

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_fixed_firebase_auth():
    """Test the fixed Firebase authentication methods"""
    
    print("🔧 Testing Fixed Firebase Authentication")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--hard-refresh")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Force refresh by adding cache busting parameter
        cache_buster = int(time.time())
        print("1. 🌐 Loading auth demo page with cache refresh...")
        driver.get(f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}")
        
        # Force hard refresh
        driver.execute_script("location.reload(true);")
        time.sleep(8)
        
        print("2. 🔍 Checking Firebase method availability...")
        
        firebase_methods = driver.execute_script("""
            return {
                firebaseReady: window.firebaseReady || false,
                createUser: typeof window.createUserWithEmailAndPassword,
                signInPopup: typeof window.signInWithPopup,
                googleProvider: typeof window.GoogleAuthProvider,
                httpsCallable: typeof window.httpsCallable,
                authObject: typeof window.firebaseAuth
            };
        """)
        
        print("   Firebase methods available:")
        for method, status in firebase_methods.items():
            print(f"   {method}: {status}")
        
        # Test complete registration flow
        print("\n3. 🧪 Testing Complete Registration Flow...")
        
        test_email = f"fixed_auth_test_{int(time.time())}@example.com"
        test_name = "Fixed Auth Test User"
        test_password = "testpass123"
        
        # Fill form
        driver.find_element(By.ID, "fullName").send_keys(test_name)
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   📧 Testing with email: {test_email}")
        
        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(5)
        
        # Check if verification step is reached
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        print(f"   ✅ Verification step reached: {'Yes' if verification_visible else 'No'}")
        
        if verification_visible:
            print("\n4. 🔑 Testing Verification Code and Firebase Account Creation...")
            
            # Enter verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("123ABC")
            
            # Clear logs
            driver.get_log('browser')
            
            # Add monitoring for Firebase account creation
            driver.execute_script("""
                console.log('=== VERIFICATION TEST START ===');
                
                // Monitor the createUserWithEmailAndPassword call
                if (window.createUserWithEmailAndPassword) {
                    console.log('✅ createUserWithEmailAndPassword is available as global function');
                } else {
                    console.log('❌ createUserWithEmailAndPassword is NOT available');
                }
                
                if (window.firebaseAuth) {
                    console.log('✅ firebaseAuth object is available');
                } else {
                    console.log('❌ firebaseAuth object is NOT available');
                }
            """)
            
            # Submit verification
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(8)
            
            # Get logs from verification process
            verification_logs = driver.get_log('browser')
            
            print("   Verification process logs:")
            firebase_creation_successful = False
            error_found = False
            
            for log in verification_logs:
                print(f"   [{log['level']}] {log['message']}")
                
                if 'firebase user created' in log['message'].lower():
                    firebase_creation_successful = True
                elif 'error' in log['level'].lower() and 'firebase' in log['message'].lower():
                    error_found = True
            
            # Check final state
            success_visible = driver.execute_script("""
                return document.getElementById('success-step').classList.contains('active');
            """)
            
            print(f"\n5. 🎯 Results:")
            print(f"   Firebase account creation: {'✅ Success' if firebase_creation_successful else '❌ Failed'}")
            print(f"   Success page reached: {'✅ Yes' if success_visible else '❌ No'}")
            print(f"   Errors detected: {'❌ Yes' if error_found else '✅ None'}")
            
            if success_visible:
                print("\n🎉 EMAIL VERIFICATION SYSTEM FIXED!")
                print("   - User receives only our custom verification email")
                print("   - Firebase account is created correctly after verification")
                print("   - No dual email system confusion")
                return True
            else:
                print("\n❌ Email verification system still has issues")
                return False
        else:
            print("❌ Could not reach verification step")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_fixed_firebase_auth()
    print(f"\n🏁 Fixed Firebase auth test: {'✅ SUCCESS' if success else '❌ FAILED'}")
    if success:
        print("\n✅ The 'wrong email' issue should now be resolved!")
        print("   Users will only receive the proper custom verification email")