#!/usr/bin/env python3
# File: test-real-user-experience.py
# Path: /home/herb/Desktop/OurLibrary/test-real-user-experience.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 05:55PM
# URGENT: Test the actual broken user experience

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_real_broken_user_experience():
    """Test what the user actually experiences - expecting it to be broken"""
    
    print("🚨 TESTING ACTUAL USER EXPERIENCE - EXPECTING BROKEN SYSTEM")
    print("=" * 70)
    print("User reports: No email sent, no verification screen, creates Firebase without validation")
    print("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        
        print(f"\\n1. 🌐 Loading live site: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(5)
        
        print("2. 📝 Filling registration form...")
        test_email = f"broken_test_{timestamp}@example.com"
        
        driver.find_element(By.ID, "fullName").send_keys("Test User")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("test123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
        
        print(f"   Email: {test_email}")
        
        # Take screenshot before submission
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/before_registration.png")
        print("   📸 Before registration: before_registration.png")
        
        print("3. 🚀 Submitting registration...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Monitor what happens for 15 seconds
        print("4. 👀 Monitoring what actually happens...")
        for i in range(15):
            time.sleep(1)
            
            # Check current page state
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
            
            # Check for status messages
            status_container = driver.find_element(By.ID, "statusContainer")
            status_text = status_container.text.strip() if status_container else ""
            
            # Check if Firebase user was created
            firebase_user = driver.execute_script("""
                return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                    uid: window.firebaseAuth.currentUser.uid,
                    email: window.firebaseAuth.currentUser.email
                } : null;
            """)
            
            print(f"   [{i+1}s] Step: {current_step}, Status: '{status_text}', Firebase User: {bool(firebase_user)}")
            
            if firebase_user:
                print(f"   🚨 CONFIRMED BUG: Firebase account created without email verification!")
                print(f"      UID: {firebase_user['uid']}")
                print(f"      Email: {firebase_user['email']}")
            
            if current_step == 'verification':
                print("   ✅ Reached verification step (this would be good)")
                break
            elif current_step == 'success':
                print("   🚨 CONFIRMED BUG: Went straight to success without verification!")
                break
            elif current_step == 'registration' and i > 5:
                print("   🚨 CONFIRMED BUG: Stuck on registration page!")
        
        # Take final screenshot
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/after_registration.png")
        print("   📸 After registration: after_registration.png")
        
        # Check console for errors
        print("5. 📋 Checking console for errors...")
        logs = driver.get_log('browser')
        error_logs = [log for log in logs if log['level'] in ['SEVERE', 'WARNING']]
        
        if error_logs:
            print("   Console errors found:")
            for log in error_logs[-5:]:  # Last 5 errors
                print(f"   [{log['level']}] {log['message']}")
        else:
            print("   No console errors found")
        
        # Final state analysis
        print("\\n6. 🔍 Final State Analysis:")
        final_step = driver.execute_script("""
            const steps = ['registration', 'verification', 'success'];
            for (let step of steps) {
                const element = document.getElementById(step + '-step');
                if (element && element.classList.contains('active')) {
                    return step;
                }
            }
            return 'unknown';
        """)
        
        final_firebase = driver.execute_script("""
            return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                uid: window.firebaseAuth.currentUser.uid,
                email: window.firebaseAuth.currentUser.email,
                emailVerified: window.firebaseAuth.currentUser.emailVerified
            } : null;
        """)
        
        final_status = driver.find_element(By.ID, "statusContainer").text.strip()
        
        print(f"   Final Step: {final_step}")
        print(f"   Final Status: '{final_status}'")
        print(f"   Firebase User Created: {bool(final_firebase)}")
        
        if final_firebase:
            print(f"   Firebase UID: {final_firebase['uid']}")
            print(f"   Email Verified: {final_firebase['emailVerified']}")
        
        # Diagnosis
        print("\\n7. 🩺 DIAGNOSIS:")
        if final_firebase and final_step != 'verification':
            print("   🚨 CRITICAL BUG CONFIRMED: Firebase account created without email verification")
            print("   🚨 SECURITY ISSUE: Users can create accounts without verifying emails")
        
        if final_step == 'registration':
            print("   🚨 UI BUG CONFIRMED: Registration form doesn't progress to verification")
        
        if not final_status or 'error' in final_status.lower():
            print("   🚨 SMTP BUG LIKELY: Email verification system not working")
        
        return {
            'final_step': final_step,
            'firebase_created': bool(final_firebase),
            'firebase_uid': final_firebase['uid'] if final_firebase else None,
            'status_message': final_status,
            'broken': final_firebase and final_step != 'verification'
        }
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/test_error.png")
        return {'error': str(e)}
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🚨 TESTING THE BROKEN USER EXPERIENCE THE USER REPORTED")
    result = test_real_broken_user_experience()
    
    if result.get('broken'):
        print("\\n🚨 USER IS CORRECT - SYSTEM IS BROKEN!")
        print(f"   Firebase account created: {result['firebase_uid']}")
        print(f"   But user stuck at: {result['final_step']}")
        print("   This confirms the user's report of broken functionality")
    else:
        print("\\n🤔 Need to investigate further...")