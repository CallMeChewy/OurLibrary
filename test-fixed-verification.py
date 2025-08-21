#!/usr/bin/env python3
# File: test-fixed-verification.py
# Path: /home/herb/Desktop/OurLibrary/test-fixed-verification.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:05PM
# TEST: Fixed verification system

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_fixed_verification():
    """Test the fixed verification system"""
    
    print("🔧 TESTING FIXED VERIFICATION SYSTEM")
    print("=" * 60)
    print("Should reject fake codes and require real verification codes")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        timestamp = int(time.time())
        # Add cache buster to ensure we get the fixed version
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&fixed_test=true"
        
        print(f"1. 🌐 Loading FIXED version: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(8)  # Wait for all JavaScript to load
        
        print("2. 📝 Filling registration form...")
        test_email = f"fixed_test_{timestamp}@example.com"
        
        driver.find_element(By.ID, "fullName").send_keys("Fixed Test User")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("fixed123")
        driver.find_element(By.ID, "confirmPassword").send_keys("fixed123")
        
        print(f"   Test email: {test_email}")
        
        print("3. 🚀 Submitting registration...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Wait for verification step
        time.sleep(10)
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("4. ✅ Reached verification step")
            
            # Check for the temporary verification code in the console
            time.sleep(3)
            real_code = driver.execute_script("return window.pendingVerificationCode;")
            
            if real_code:
                print(f"   🔍 Real verification code generated: {real_code}")
                
                # Test 1: Try fake code first (should fail)
                print("\\n5. 🧪 Testing FAKE code '999999' (should fail)...")
                
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys("999999")
                
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                time.sleep(5)
                
                # Check if Firebase account was created (shouldn't be)
                firebase_user_fake = driver.execute_script("""
                    return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                        uid: window.firebaseAuth.currentUser.uid
                    } : null;
                """)
                
                status_after_fake = driver.find_element(By.ID, "statusContainer").text.strip()
                
                print(f"   Result: {status_after_fake}")
                print(f"   Firebase created with fake code: {bool(firebase_user_fake)}")
                
                if firebase_user_fake:
                    print("   🚨 STILL BROKEN: Fake code created Firebase account!")
                    return False
                else:
                    print("   ✅ FIXED: Fake code rejected!")
                
                # Test 2: Try real code (should work)
                print(f"\\n6. 🧪 Testing REAL code '{real_code}' (should work)...")
                
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys(real_code)
                
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                time.sleep(8)
                
                # Check if Firebase account was created (should be)
                firebase_user_real = driver.execute_script("""
                    return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                        uid: window.firebaseAuth.currentUser.uid,
                        email: window.firebaseAuth.currentUser.email,
                        emailVerified: window.firebaseAuth.currentUser.emailVerified
                    } : null;
                """)
                
                current_step = driver.execute_script("""
                    const steps = ['registration', 'verification', 'success'];
                    for (let step of steps) {
                        const element = document.getElementById(step + '-step');
                        if (element && element.classList.contains('active')) {
                            return step;
                        }
                    }
                    return 'unknown';
                """)
                
                status_after_real = driver.find_element(By.ID, "statusContainer").text.strip()
                
                print(f"   Current step: {current_step}")
                print(f"   Status: {status_after_real}")
                print(f"   Firebase created with real code: {bool(firebase_user_real)}")
                
                if firebase_user_real:
                    print(f"   ✅ SUCCESS: Real code created Firebase account!")
                    print(f"      UID: {firebase_user_real['uid']}")
                    print(f"      Email: {firebase_user_real['email']}")
                    return True
                else:
                    print("   ❌ ISSUE: Real code didn't create Firebase account")
                    return False
            
            else:
                print("   ❌ No verification code generated - system still broken")
                return False
        else:
            print("❌ Never reached verification step")
            return False
        
    except Exception as e:
        print(f"\\n❌ Test error: {e}")
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/fixed_test_error.png")
        return False
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/fixed_verification_test.png")
        driver.quit()

if __name__ == "__main__":
    print("🔧 TESTING FIXED VERIFICATION SYSTEM")
    
    success = test_fixed_verification()
    
    if success:
        print("\\n🎉 VERIFICATION SYSTEM FIXED!")
        print("   ✅ Fake codes rejected")
        print("   ✅ Real codes create Firebase accounts")
        print("   ✅ Security vulnerability patched")
    else:
        print("\\n🚨 VERIFICATION SYSTEM STILL BROKEN")
        print("   Need further fixes")