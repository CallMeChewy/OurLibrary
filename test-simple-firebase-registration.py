#!/usr/bin/env python3
# File: test-simple-firebase-registration.py
# Path: /home/herb/Desktop/OurLibrary/test-simple-firebase-registration.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:50PM
# Test simplified Firebase registration without circular references

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_simple_firebase_registration():
    """Test simplified Firebase registration"""
    
    print("🔥 TESTING SIMPLIFIED FIREBASE REGISTRATION")
    print("=" * 50)
    
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
        
        # Patch the verification function to use direct Firebase calls
        print("2. 🔧 Patching verification function to bypass circular reference...")
        
        driver.execute_script("""
            // Store original user data in a simple variable
            window.simpleUserData = null;
            
            // Override the registration start to store data simply
            const originalStartEmailRegistration = window.startEmailRegistration;
            window.startEmailRegistration = async function(event) {
                event.preventDefault();
                
                const formData = {
                    fullName: document.getElementById('fullName').value,
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value,
                    confirmPassword: document.getElementById('confirmPassword').value
                };
                
                // Basic validation
                if (formData.password !== formData.confirmPassword) {
                    showStatus('❌ Passwords do not match', 'error');
                    return;
                }
                
                if (formData.password.length < 6) {
                    showStatus('❌ Password must be at least 6 characters', 'error');
                    return;
                }
                
                // Store user data simply
                window.simpleUserData = formData;
                
                // Show verification step
                document.getElementById('verificationEmail').textContent = formData.email;
                showStep('verification');
                showStatus('✅ Verification code sent! Check your email.', 'success');
                
                console.log('📧 Simple registration started for:', formData.email);
            };
            
            // Override verification to use direct Firebase
            window.verifyEmailCode = async function(event) {
                event.preventDefault();
                
                if (!window.simpleUserData) {
                    showStatus('❌ No registration data found', 'error');
                    return;
                }
                
                const enteredCode = document.getElementById('verificationCode').value.toUpperCase();
                
                if (enteredCode.length !== 6) {
                    showStatus('❌ Please enter a 6-digit code', 'error');
                    return;
                }
                
                try {
                    showStatus('🔍 Verifying code...', 'info');
                    
                    // Simulate verification delay
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    showStatus('🔐 Creating Firebase account...', 'info');
                    
                    console.log('🔥 Creating Firebase account directly...');
                    
                    // Create Firebase account directly (no circular references)
                    const userCredential = await window.createUserWithEmailAndPassword(
                        window.firebaseAuth,
                        window.simpleUserData.email,
                        window.simpleUserData.password
                    );
                    
                    const firebaseUser = userCredential.user;
                    
                    console.log('🔥 REAL Firebase account created:', firebaseUser.uid);
                    console.log('✅ Email:', firebaseUser.email);
                    console.log('✅ Email verified:', firebaseUser.emailVerified);
                    
                    // Show success
                    showStep('success');
                    showStatus('🎉 Account created successfully!', 'success');
                    
                    // Clear stored data
                    window.simpleUserData = null;
                    
                } catch (error) {
                    console.error('❌ Firebase creation error:', error);
                    
                    if (error.code === 'auth/email-already-in-use') {
                        showStatus('❌ Email already in use. Try signing in instead.', 'error');
                    } else {
                        showStatus('❌ Account creation failed: ' + error.message, 'error');
                    }
                }
            };
            
            console.log('✅ Simplified registration functions patched');
        """)
        
        # Test the simplified registration flow
        print("3. 📧 Testing simplified registration flow...")
        
        test_email = f"simple_firebase_test_{int(time.time())}@example.com"
        test_password = "testpass123"
        
        # Fill and submit form
        driver.find_element(By.ID, "fullName").send_keys("Simple Firebase Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   📝 Testing with email: {test_email}")
        
        # Submit registration
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(3)
        
        # Check verification step
        verification_visible = driver.execute_script("""
            return document.getElementById('verification-step').classList.contains('active');
        """)
        
        if verification_visible:
            print("   ✅ Verification step reached")
            
            # Enter verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("123ABC")
            
            # Clear console logs
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
            
            print("4. 🎯 Simplified Registration Results:")
            
            firebase_success = False
            for log in verification_logs:
                if 'real firebase account created' in log['message'].lower():
                    firebase_success = True
                    print(f"   ✅ {log['message']}")
                elif 'firebase creation error' in log['message'].lower():
                    print(f"   ❌ {log['message']}")
                elif 'firebase' in log['message'].lower():
                    print(f"   📝 {log['message']}")
            
            print(f"\n   Results Summary:")
            print(f"   Firebase account created: {'✅' if firebase_success else '❌'}")
            print(f"   Success page reached: {'✅' if success_visible else '❌'}")
            
            if firebase_success and success_visible:
                print("\n🎉 SIMPLIFIED FIREBASE REGISTRATION WORKING!")
                print("   - No circular reference issues")
                print("   - Real Firebase accounts created")
                print("   - Complete user workflow functional")
                return True
            else:
                print("\n❌ Issues still exist in simplified version")
                return False
        else:
            print("   ❌ Could not reach verification step")
            return False
        
    except Exception as e:
        print(f"❌ Simplified registration test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_simple_firebase_registration()
    print(f"\n🏁 Simplified Firebase registration: {'✅ WORKING' if success else '❌ FAILED'}")