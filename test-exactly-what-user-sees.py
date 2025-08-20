#!/usr/bin/env python3
# File: test-exactly-what-user-sees.py
# Path: /home/herb/Desktop/OurLibrary/test-exactly-what-user-sees.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:25PM
# TEST: Exactly what the user is experiencing right now

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_exactly_what_user_sees():
    """Test exactly what the user is experiencing"""
    
    print("🔍 TESTING EXACTLY WHAT USER SEES RIGHT NOW")
    print("=" * 60)
    print("URL: https://callmechewy.github.io/OurLibrary/auth-demo.html")
    print("Expected: User gets 'Verification failed. Please check your code.'")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        # Load the exact same URL the user uses
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        
        print(f"1. 🌐 Loading EXACT USER URL: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(8)
        
        print("2. 📝 Filling registration exactly like user...")
        test_email = f"user_test_{timestamp}@example.com"
        
        driver.find_element(By.ID, "fullName").send_keys("User Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("usertest123")
        driver.find_element(By.ID, "confirmPassword").send_keys("usertest123")
        
        print(f"   Email: {test_email}")
        
        print("3. 🚀 Submitting registration...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        time.sleep(10)
        
        # Check if we reach verification step
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("4. ✅ Reached verification step")
            
            # Check what code is generated
            real_code = driver.execute_script("return window.pendingVerificationCode || null;")
            expiry = driver.execute_script("return window.verificationExpiry || null;")
            
            print(f"   Generated code: {real_code}")
            print(f"   Code expiry: {expiry}")
            
            # Check status message for code display
            status_text = driver.find_element(By.ID, "statusContainer").text.strip()
            print(f"   Status message: '{status_text}'")
            
            if real_code:
                print(f"\\n5. 🧪 Testing REAL code '{real_code}' (should work)...")
                
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys(real_code)
                
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                time.sleep(8)
                
                # Check result
                result_step = driver.execute_script("""
                    const steps = ['registration', 'verification', 'success'];
                    for (let step of steps) {
                        const element = document.getElementById(step + '-step');
                        if (element && element.classList.contains('active')) {
                            return step;
                        }
                    }
                    return 'unknown';
                """)
                
                result_status = driver.find_element(By.ID, "statusContainer").text.strip()
                
                firebase_user = driver.execute_script("""
                    return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                        uid: window.firebaseAuth.currentUser.uid,
                        email: window.firebaseAuth.currentUser.email
                    } : null;
                """)
                
                print(f"   Result step: {result_step}")
                print(f"   Result status: '{result_status}'")
                print(f"   Firebase account: {bool(firebase_user)}")
                
                if firebase_user:
                    print(f"   ✅ SUCCESS: Firebase UID {firebase_user['uid']}")
                elif 'failed' in result_status.lower() or 'error' in result_status.lower():
                    print(f"   🚨 SAME ERROR USER SEES: {result_status}")
                    
                    # Debug why the real code failed
                    print("\\n6. 🔍 DEBUG: Why did real code fail?")
                    
                    debug_info = driver.execute_script("""
                        return {
                            pendingCode: window.pendingVerificationCode,
                            pendingEmail: window.pendingVerificationEmail,
                            expiry: window.verificationExpiry,
                            currentTime: Date.now(),
                            expired: window.verificationExpiry ? Date.now() > window.verificationExpiry : null,
                            firebaseFunctions: !!window.firebaseFunctions,
                            httpsCallable: !!window.httpsCallable
                        };
                    """)
                    
                    print(f"   Pending code: {debug_info['pendingCode']}")
                    print(f"   Pending email: {debug_info['pendingEmail']}")
                    print(f"   Expiry time: {debug_info['expiry']}")
                    print(f"   Current time: {debug_info['currentTime']}")
                    print(f"   Code expired: {debug_info['expired']}")
                    print(f"   Firebase functions: {debug_info['firebaseFunctions']}")
                    print(f"   HTTPS callable: {debug_info['httpsCallable']}")
                    
                    return "USER_ERROR_REPRODUCED"
                else:
                    print(f"   🤔 Unclear result")
                    return "UNCLEAR"
            else:
                print("   ❌ No verification code generated")
                return "NO_CODE_GENERATED"
        else:
            print("❌ Never reached verification step")
            return "NO_VERIFICATION_STEP"
        
    except Exception as e:
        print(f"\\n❌ Test error: {e}")
        return "TEST_ERROR"
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/user_experience_test.png")
        driver.quit()

if __name__ == "__main__":
    print("🔍 REPRODUCING EXACT USER EXPERIENCE")
    
    result = test_exactly_what_user_sees()
    
    print(f"\\n🎯 RESULT: {result}")
    
    if result == "USER_ERROR_REPRODUCED":
        print("\\n🚨 CONFIRMED: I can reproduce the user's error")
        print("   'Verification failed. Please check your code.'")
        print("   Even with the correct verification code")
        print("   The fix is not working as expected")
    else:
        print(f"\\n🤔 Different result than user reported: {result}")