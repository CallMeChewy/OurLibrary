#!/usr/bin/env python3
# File: test-email-verification-system.py
# Path: /home/herb/Desktop/OurLibrary/test-email-verification-system.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 11:30AM
# Test email verification system to identify wrong email issue

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_email_verification_system():
    """Test the email verification system to identify the wrong email issue"""
    
    print("🔍 Testing Email Verification System")
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
        time.sleep(5)
        
        # Check what email verification system is configured
        print("2. 🔍 Checking email verification configuration...")
        
        # Look for Firebase configuration
        firebase_config = driver.execute_script("""
            return window.firebaseConfig || 'not found';
        """)
        
        print(f"   Firebase Config: {firebase_config}")
        
        # Check for custom SMTP configuration
        smtp_configured = driver.execute_script("""
            return typeof window.firebaseFunctions !== 'undefined' && 
                   typeof window.httpsCallable !== 'undefined';
        """)
        
        print(f"   Custom SMTP Available: {'✅' if smtp_configured else '❌'}")
        
        # Test form field mapping
        print("3. 📧 Testing email field mapping...")
        
        # Fill out the registration form with a test email
        test_email = f"email_verification_test_{int(time.time())}@example.com"
        test_name = "Email Verification Test User"
        test_password = "testpass123"
        
        # Fill form fields
        driver.find_element(By.ID, "fullName").send_keys(test_name)
        email_field = driver.find_element(By.ID, "email")
        email_field.send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   ✅ Form filled with email: {test_email}")
        
        # Check if the email field value is correctly captured
        captured_email = driver.execute_script("""
            return document.getElementById('email').value;
        """)
        
        print(f"   📝 Email captured from form: {captured_email}")
        
        if captured_email != test_email:
            print(f"   ❌ EMAIL MISMATCH! Expected: {test_email}, Got: {captured_email}")
            return False
        
        # Try to submit the form and capture what happens
        print("4. 📤 Testing form submission...")
        
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        
        # Monitor console logs during submission
        driver.execute_script("console.log('=== FORM SUBMISSION START ===');")
        
        submit_button.click()
        time.sleep(3)
        
        # Get console logs to see what email verification was triggered
        console_logs = driver.get_log('browser')
        
        print("5. 📝 Console logs during submission:")
        
        email_related_logs = []
        for log in console_logs:
            if any(keyword in log['message'].lower() for keyword in ['email', 'verification', 'smtp', 'firebase']):
                email_related_logs.append(log)
                print(f"   [{log['level']}] {log['message']}")
        
        # Check if verification step is shown
        verification_step_visible = driver.execute_script("""
            const step = document.getElementById('verification-step');
            return step && step.classList.contains('active');
        """)
        
        print(f"6. 🔍 Verification step shown: {'✅' if verification_step_visible else '❌'}")
        
        if verification_step_visible:
            # Check what email address is displayed for verification
            displayed_email = driver.find_element(By.ID, "verificationEmail").text
            print(f"   📧 Email shown for verification: {displayed_email}")
            
            if displayed_email != test_email:
                print(f"   ❌ EMAIL DISPLAY MISMATCH! Expected: {test_email}, Shown: {displayed_email}")
                return False
        
        # Look for status messages that might indicate what email system was used
        status_container = driver.find_element(By.ID, "statusContainer")
        status_text = status_container.text
        
        if status_text:
            print(f"7. 📋 Status message: {status_text}")
        
        print("\n🎯 Email Verification Analysis:")
        print(f"   Form Email Input: {test_email}")
        print(f"   Captured Email: {captured_email}")
        print(f"   Displayed Email: {displayed_email if verification_step_visible else 'N/A'}")
        print(f"   SMTP System: {'Working' if smtp_configured else 'Not Available'}")
        print(f"   Verification Flow: {'Triggered' if verification_step_visible else 'Failed'}")
        
        # Check for potential dual email system conflict
        firebase_email_logs = [log for log in email_related_logs if 'firebase' in log['message'].lower()]
        custom_email_logs = [log for log in email_related_logs if 'smtp' in log['message'].lower() or 'sendverificationemail' in log['message'].lower()]
        
        print(f"\n🔧 Email System Detection:")
        print(f"   Firebase emails detected: {len(firebase_email_logs)}")
        print(f"   Custom SMTP emails detected: {len(custom_email_logs)}")
        
        if len(firebase_email_logs) > 0 and len(custom_email_logs) > 0:
            print("   ⚠️ DUAL EMAIL SYSTEM DETECTED - This could cause confusion!")
            print("   Users might receive both Firebase and custom verification emails")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_email_verification_system()
    print(f"\n🏁 Email verification system test: {'✅ COMPLETED' if success else '❌ FAILED'}")
    print("\n💡 This test helps identify why the user received the 'wrong email'")