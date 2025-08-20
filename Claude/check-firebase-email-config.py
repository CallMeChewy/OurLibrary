#!/usr/bin/env python3
# File: check-firebase-email-config.py
# Path: /home/herb/Desktop/OurLibrary/check-firebase-email-config.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 11:35AM
# Check Firebase email configuration to identify dual email issue

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def check_firebase_email_config():
    """Check if Firebase is configured to send automatic verification emails"""
    
    print("🔥 Checking Firebase Email Configuration")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Go to auth demo page
        print("1. 🌐 Loading auth demo page...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(8)  # Wait for Firebase to fully initialize
        
        # Check Firebase configuration and methods available
        firebase_info = driver.execute_script("""
            const info = {
                firebaseReady: window.firebaseReady || false,
                firebaseAuth: typeof window.firebaseAuth !== 'undefined',
                createUserMethod: typeof window.createUserWithEmailAndPassword !== 'undefined',
                firebaseConfig: !!window.firebaseAuth?.app?.options,
                projectId: window.firebaseAuth?.app?.options?.projectId || 'not found'
            };
            
            // Check if Firebase auth has email verification methods
            if (window.firebaseAuth) {
                info.sendEmailVerification = typeof window.firebaseAuth.sendEmailVerification !== 'undefined';
            }
            
            return info;
        """)
        
        print("2. 🔥 Firebase Configuration:")
        for key, value in firebase_info.items():
            print(f"   {key}: {value}")
        
        # Test a complete registration flow to see what emails are triggered
        print("\n3. 🧪 Testing Complete Registration Flow...")
        
        test_email = f"firebase_email_test_{int(time.time())}@example.com"
        test_name = "Firebase Email Test User"
        test_password = "testpass123"
        
        # Fill form
        driver.find_element(By.ID, "fullName").send_keys(test_name)
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   📧 Testing with email: {test_email}")
        
        # Submit form and monitor what happens
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        
        # Clear any existing logs
        driver.get_log('browser')
        
        # Add console monitoring
        driver.execute_script("""
            console.log('=== EMAIL TEST START ===');
            
            // Override createUserWithEmailAndPassword to see if it's called
            if (window.createUserWithEmailAndPassword) {
                const originalCreate = window.createUserWithEmailAndPassword;
                window.createUserWithEmailAndPassword = function(...args) {
                    console.log('🔥 createUserWithEmailAndPassword called with email:', args[1]);
                    return originalCreate.apply(this, args).then(result => {
                        console.log('🔥 Firebase user created:', result.user.email);
                        console.log('🔥 Email verified status:', result.user.emailVerified);
                        return result;
                    }).catch(error => {
                        console.log('🔥 Firebase creation error:', error.message);
                        throw error;
                    });
                };
            }
        """)
        
        submit_button.click()
        time.sleep(5)
        
        # Get all console logs
        console_logs = driver.get_log('browser')
        
        print("\n4. 📝 Console Activity During Registration:")
        firebase_activity = []
        
        for log in console_logs:
            if any(keyword in log['message'].lower() for keyword in 
                   ['firebase', 'createuser', 'emailverified', 'verification']):
                firebase_activity.append(log['message'])
                print(f"   {log['message']}")
        
        # Check if verification step is reached
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        print(f"\n5. 🎯 Registration Flow Results:")
        print(f"   Verification step reached: {'✅' if verification_visible else '❌'}")
        print(f"   Firebase activity detected: {len(firebase_activity)} events")
        
        if verification_visible:
            # Try the verification code step
            print("\n6. 🔑 Testing Verification Code Step...")
            
            # Enter a dummy verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("123ABC")
            
            # Clear logs again
            driver.get_log('browser')
            
            # Submit verification
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(5)
            
            # Check logs for Firebase account creation
            verification_logs = driver.get_log('browser')
            
            print("   Verification step console activity:")
            for log in verification_logs:
                if any(keyword in log['message'].lower() for keyword in 
                       ['firebase', 'createuser', 'account', 'uid']):
                    print(f"   {log['message']}")
        
        # Check current page state
        success_visible = driver.execute_script("""
            return document.getElementById('success-step').classList.contains('active');
        """)
        
        print(f"\n7. 🏁 Final State:")
        print(f"   Success step reached: {'✅' if success_visible else '❌'}")
        
        # Summary analysis
        print(f"\n📊 Email System Analysis:")
        print(f"   Custom SMTP system: Active (sends verification codes)")
        print(f"   Firebase native system: {'May be active' if len(firebase_activity) > 0 else 'Appears inactive'}")
        
        if len(firebase_activity) > 0:
            print(f"   ⚠️ POTENTIAL DUAL EMAIL ISSUE:")
            print(f"   - User receives custom SMTP verification email")
            print(f"   - Firebase may also send automatic verification email")
            print(f"   - User sees Firebase email and thinks it's wrong format/sender")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = check_firebase_email_config()
    print(f"\n🏁 Firebase email configuration check: {'✅ COMPLETED' if success else '❌ FAILED'}")