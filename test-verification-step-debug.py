#!/usr/bin/env python3
# File: test-verification-step-debug.py
# Path: /home/herb/Desktop/OurLibrary/test-verification-step-debug.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 01:00PM
# Debug what happens in verification step with full console monitoring

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_verification_step_debug():
    """Debug verification step with full console monitoring"""
    
    print("🔍 DEBUGGING VERIFICATION STEP")
    print("=" * 40)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        print("1. 🌐 Loading auth demo page...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(8)
        
        # Enable comprehensive console monitoring
        driver.execute_script("""
            // Override console methods to capture everything
            const originalLog = console.log;
            const originalError = console.error;
            const originalWarn = console.warn;
            
            window.debugLogs = [];
            
            console.log = function(...args) {
                window.debugLogs.push({type: 'log', message: args.join(' '), timestamp: Date.now()});
                originalLog.apply(console, args);
            };
            
            console.error = function(...args) {
                window.debugLogs.push({type: 'error', message: args.join(' '), timestamp: Date.now()});
                originalError.apply(console, args);
            };
            
            console.warn = function(...args) {
                window.debugLogs.push({type: 'warn', message: args.join(' '), timestamp: Date.now()});
                originalWarn.apply(console, args);
            };
            
            // Monitor Firebase functions
            if (window.createUserWithEmailAndPassword) {
                const originalCreateUser = window.createUserWithEmailAndPassword;
                window.createUserWithEmailAndPassword = function(...args) {
                    console.log('🔥 FIREBASE CALL: createUserWithEmailAndPassword with email:', args[2]);
                    return originalCreateUser.apply(this, args).then(result => {
                        console.log('🔥 FIREBASE SUCCESS: Account created with UID:', result.user.uid);
                        return result;
                    }).catch(error => {
                        console.log('🔥 FIREBASE ERROR:', error.message);
                        throw error;
                    });
                };
            }
            
            console.log('✅ Debug monitoring enabled');
        """)
        
        # Fill registration form
        test_email = f"verification_debug_{int(time.time())}@example.com"
        test_password = "testpass123"
        
        driver.find_element(By.ID, "fullName").send_keys("Verification Debug User")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"2. 📧 Starting registration with email: {test_email}")
        
        # Submit registration
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(5)
        
        # Check if we reached verification step
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        if verification_visible:
            print("3. ✅ Verification step reached, entering code...")
            
            # Enter verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("123ABC")
            
            # Monitor the verification submission carefully
            driver.execute_script("""
                console.log('=== VERIFICATION SUBMISSION DEBUG START ===');
                
                // Check what verification function exists
                console.log('verifyEmailCode function type:', typeof window.verifyEmailCode);
                
                // Override the function to add debug
                if (window.verifyEmailCode) {
                    const originalVerify = window.verifyEmailCode;
                    window.verifyEmailCode = async function(event) {
                        console.log('🔧 verifyEmailCode called with event:', event);
                        console.log('🔧 Current step before verification:', 
                            document.getElementById('verification-step').classList.contains('active') ? 'verification' : 'other');
                        
                        try {
                            const result = await originalVerify(event);
                            console.log('🔧 verifyEmailCode completed with result:', result);
                            return result;
                        } catch (error) {
                            console.log('🔧 verifyEmailCode threw error:', error.message);
                            console.log('🔧 Error stack:', error.stack);
                            throw error;
                        }
                    };
                }
            """)
            
            # Clear browser logs to get fresh output
            driver.get_log('browser')
            
            # Submit verification
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(10)
            
            # Get all logs from the verification process
            verification_logs = driver.get_log('browser')
            
            # Also get custom debug logs
            custom_logs = driver.execute_script("return window.debugLogs || [];")
            
            print("\n4. 📝 Verification Process Debug Output:")
            print("   Browser Console Logs:")
            for log in verification_logs:
                if any(keyword in log['message'].lower() for keyword in ['firebase', 'verification', 'error', '🔥', '🔧']):
                    print(f"     [{log['level']}] {log['message']}")
            
            print("   Custom Debug Logs:")
            for log in custom_logs[-20:]:  # Last 20 custom logs
                print(f"     [{log['type'].upper()}] {log['message']}")
            
            # Check final state
            success_visible = driver.execute_script("""
                return document.getElementById('success-step').classList.contains('active');
            """)
            
            print(f"\n5. 🎯 Final State:")
            print(f"   Success page visible: {'✅' if success_visible else '❌'}")
            
            # Check for any errors in the status container
            status_text = driver.find_element(By.ID, "statusContainer").text
            if status_text:
                print(f"   Status message: {status_text}")
            
            return success_visible
        else:
            print("❌ Could not reach verification step")
            return False
        
    except Exception as e:
        print(f"❌ Verification debug failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_verification_step_debug()
    print("\n💡 This shows exactly what's happening (or not happening) during verification")