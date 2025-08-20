#!/usr/bin/env python3
# File: debug-firebase-creation.py
# Path: /home/herb/Desktop/OurLibrary/debug-firebase-creation.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:30PM
# Debug Firebase account creation failure in verification step

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_firebase_creation():
    """Debug why Firebase account creation is failing"""
    
    print("🔍 DEBUGGING FIREBASE ACCOUNT CREATION")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Load page and go through registration flow
        print("1. 🌐 Loading and starting registration...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(8)
        
        test_email = f"firebase_debug_{int(time.time())}@example.com"
        test_password = "testpass123"
        
        # Fill and submit registration form
        driver.find_element(By.ID, "fullName").send_keys("Firebase Debug User")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(5)
        
        # Check if we reached verification step
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        if not verification_visible:
            print("❌ Could not reach verification step")
            return False
            
        print(f"   ✅ Reached verification step with email: {test_email}")
        
        # Check registration manager state
        print("\n2. 🔍 Checking Registration Manager State...")
        
        manager_state = driver.execute_script("""
            try {
                return {
                    registrationManager: typeof window.registrationManager !== 'undefined',
                    googleAuth: typeof window.googleAuth !== 'undefined',
                    firebaseAuth: typeof window.firebaseAuth !== 'undefined',
                    createUserFunction: typeof window.createUserWithEmailAndPassword,
                    pendingUserData: window.registrationManager ? 
                        (window.registrationManager.pendingUserData ? 'exists' : 'null') : 'no manager',
                    userData: window.userRegistrationData ? 'exists' : 'null'
                };
            } catch (error) {
                return { error: error.message };
            }
        """)
        
        print("   Registration Manager State:")
        for key, value in manager_state.items():
            status = "✅" if value in [True, "function", "exists"] else "❌"
            print(f"   {key}: {value} {status}")
        
        # Test the verification code submission with detailed logging
        print("\n3. 🔑 Testing Verification Code with Detailed Logging...")
        
        code_input = driver.find_element(By.ID, "verificationCode")
        code_input.send_keys("123ABC")
        
        # Clear console and add comprehensive monitoring
        driver.get_log('browser')
        
        driver.execute_script("""
            console.log('=== FIREBASE DEBUG START ===');
            
            // Check all Firebase components
            console.log('firebaseAuth available:', typeof window.firebaseAuth !== 'undefined');
            console.log('createUserWithEmailAndPassword available:', typeof window.createUserWithEmailAndPassword);
            console.log('registrationManager available:', typeof window.registrationManager !== 'undefined');
            
            if (window.registrationManager) {
                console.log('pendingUserData exists:', window.registrationManager.pendingUserData ? 'yes' : 'no');
                if (window.registrationManager.pendingUserData) {
                    console.log('pending email:', window.registrationManager.pendingUserData.email);
                }
            }
            
            // Override the completeEmailRegistration to debug
            if (window.registrationManager && window.registrationManager.completeEmailRegistration) {
                const originalComplete = window.registrationManager.completeEmailRegistration.bind(window.registrationManager);
                window.registrationManager.completeEmailRegistration = async function(code) {
                    console.log('🔧 completeEmailRegistration called with code:', code);
                    
                    try {
                        console.log('🔧 Calling original completeEmailRegistration...');
                        const result = await originalComplete(code);
                        console.log('🔧 completeEmailRegistration result:', result);
                        return result;
                    } catch (error) {
                        console.log('🔧 completeEmailRegistration error:', error.message);
                        console.log('🔧 Error stack:', error.stack);
                        throw error;
                    }
                };
            }
            
            // Override verifyEmailCode to see what happens
            const originalVerify = window.verifyEmailCode;
            if (originalVerify) {
                window.verifyEmailCode = async function(event) {
                    console.log('🔧 verifyEmailCode called');
                    try {
                        const result = await originalVerify(event);
                        console.log('🔧 verifyEmailCode completed successfully');
                        return result;
                    } catch (error) {
                        console.log('🔧 verifyEmailCode error:', error.message);
                        throw error;
                    }
                };
            }
        """)
        
        # Submit verification code
        verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
        verify_button.click()
        time.sleep(10)
        
        # Get detailed console output
        verification_logs = driver.get_log('browser')
        
        print("\n4. 📝 Detailed Verification Logs:")
        
        firebase_calls = []
        errors = []
        success_indicators = []
        
        for log in verification_logs:
            message = log['message']
            level = log['level']
            
            if '🔧' in message:
                print(f"   DEBUG: {message}")
            elif 'firebase' in message.lower():
                firebase_calls.append(message)
                print(f"   FIREBASE: {message}")
            elif level == 'SEVERE':
                errors.append(message)
                print(f"   ERROR: {message}")
            elif 'success' in message.lower() or 'complete' in message.lower():
                success_indicators.append(message)
                print(f"   SUCCESS: {message}")
        
        # Check final page state
        success_visible = driver.execute_script("""
            return document.getElementById('success-step').classList.contains('active');
        """)
        
        print(f"\n5. 🎯 Analysis Results:")
        print(f"   Firebase calls detected: {len(firebase_calls)}")
        print(f"   Errors found: {len(errors)}")
        print(f"   Success indicators: {len(success_indicators)}")
        print(f"   Success page reached: {'✅' if success_visible else '❌'}")
        
        # Specific issue identification
        if success_visible and len(firebase_calls) == 0:
            print("\n🚨 ISSUE IDENTIFIED:")
            print("   - Success page is reached without Firebase account creation")
            print("   - This suggests verification is bypassed or mocked")
            print("   - No actual Firebase createUserWithEmailAndPassword calls")
            
        elif len(errors) > 0:
            print("\n🚨 ERRORS FOUND:")
            for error in errors[:3]:
                print(f"   - {error}")
                
        return success_visible
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_firebase_creation()
    print("\n💡 This debug shows exactly what's happening in the verification step")