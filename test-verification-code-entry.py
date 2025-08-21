#!/usr/bin/env python3
# File: test-verification-code-entry.py
# Path: /home/herb/Desktop/OurLibrary/test-verification-code-entry.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:00PM
# TEST: What happens when verification code is entered

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_verification_code_entry():
    """Test what happens when verification code is entered"""
    
    print("🔍 TESTING VERIFICATION CODE ENTRY PROCESS")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        
        print(f"1. 🌐 Loading site: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(5)
        
        print("2. 📝 Filling registration form...")
        test_email = f"verification_test_{timestamp}@example.com"
        
        driver.find_element(By.ID, "fullName").send_keys("Verification Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("verify123")
        driver.find_element(By.ID, "confirmPassword").send_keys("verify123")
        
        print(f"   Test email: {test_email}")
        
        print("3. 🚀 Submitting registration...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Wait for verification step
        time.sleep(8)
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("4. ✅ Reached verification step")
            
            # Try entering various codes to see what happens
            test_codes = ["123456", "VERIFY", "TEST01", "000000"]
            
            for i, code in enumerate(test_codes):
                print(f"\\n   Testing code {i+1}: '{code}'")
                
                # Clear and enter code
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys(code)
                
                # Submit verification
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                # Wait and check result
                time.sleep(5)
                
                # Check current step
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
                
                # Check status message
                status_text = driver.find_element(By.ID, "statusContainer").text.strip()
                
                # Check Firebase user
                firebase_user = driver.execute_script("""
                    return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                        uid: window.firebaseAuth.currentUser.uid,
                        email: window.firebaseAuth.currentUser.email,
                        emailVerified: window.firebaseAuth.currentUser.emailVerified
                    } : null;
                """)
                
                print(f"      Result step: {current_step}")
                print(f"      Status: '{status_text}'")
                print(f"      Firebase created: {bool(firebase_user)}")
                
                if firebase_user:
                    print(f"      🚨 Firebase UID: {firebase_user['uid']}")
                    print(f"      🚨 Email verified: {firebase_user['emailVerified']}")
                    print(f"      ⚠️ ISSUE: Firebase account created with code '{code}'")
                    break
                
                if current_step == 'success':
                    print(f"      🚨 SUCCESS PAGE reached with code '{code}'")
                    break
                elif current_step != 'verification':
                    print(f"      🚨 Unexpected step: {current_step}")
                    break
                elif 'error' in status_text.lower() or 'failed' in status_text.lower():
                    print(f"      ✅ Code '{code}' rejected (good)")
                else:
                    print(f"      🤔 Unclear result for code '{code}'")
        
        else:
            print("❌ Never reached verification step")
            return False
        
        # Take final screenshot
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/verification_test_result.png")
        print("\\n📸 Result screenshot: verification_test_result.png")
        
        # Final analysis
        print("\\n5. 🔍 FINAL ANALYSIS:")
        
        final_firebase = driver.execute_script("""
            return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                uid: window.firebaseAuth.currentUser.uid,
                email: window.firebaseAuth.currentUser.email,
                emailVerified: window.firebaseAuth.currentUser.emailVerified
            } : null;
        """)
        
        if final_firebase:
            print("   🚨 SECURITY ISSUE CONFIRMED:")
            print(f"      Firebase account created: {final_firebase['uid']}")
            print(f"      Without real email verification!")
            print(f"      Email verified flag: {final_firebase['emailVerified']}")
            print("   💥 THIS IS THE BUG THE USER REPORTED!")
            return False
        else:
            print("   ✅ No Firebase account created without proper verification")
            return True
        
    except Exception as e:
        print(f"\\n❌ Test error: {e}")
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/verification_error.png")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🧪 TESTING VERIFICATION CODE PROCESS")
    
    success = test_verification_code_entry()
    
    if not success:
        print("\\n🚨 VERIFICATION PROCESS IS BROKEN!")
        print("   User can create Firebase accounts without real email verification")
        print("   This confirms the user's security concerns")
    else:
        print("\\n✅ Verification process working correctly")