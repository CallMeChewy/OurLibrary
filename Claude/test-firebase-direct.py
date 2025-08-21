#!/usr/bin/env python3
# File: test-firebase-direct.py
# Path: /home/herb/Desktop/OurLibrary/test-firebase-direct.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:40PM
# Test Firebase functions directly to see what's failing

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_firebase_direct():
    """Test Firebase functions directly"""
    
    print("🔥 TESTING FIREBASE FUNCTIONS DIRECTLY")
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
        time.sleep(10)
        
        # Test Firebase directly via console
        print("2. 🧪 Testing Firebase createUserWithEmailAndPassword directly...")
        
        test_email = f"firebase_direct_test_{int(time.time())}@example.com"
        test_password = "testpass123"
        
        # Try to create Firebase account directly
        firebase_test = driver.execute_script(f"""
            return new Promise(async (resolve) => {{
                try {{
                    console.log('🧪 Testing Firebase createUser directly...');
                    console.log('Auth object:', window.firebaseAuth);
                    console.log('CreateUser function:', typeof window.createUserWithEmailAndPassword);
                    
                    if (!window.firebaseAuth) {{
                        resolve({{ error: 'firebaseAuth not available' }});
                        return;
                    }}
                    
                    if (typeof window.createUserWithEmailAndPassword !== 'function') {{
                        resolve({{ error: 'createUserWithEmailAndPassword not a function' }});
                        return;
                    }}
                    
                    console.log('🧪 Attempting to create Firebase account...');
                    const userCredential = await window.createUserWithEmailAndPassword(
                        window.firebaseAuth,
                        '{test_email}',
                        '{test_password}'
                    );
                    
                    console.log('🔥 Firebase account created:', userCredential.user);
                    resolve({{
                        success: true,
                        uid: userCredential.user.uid,
                        email: userCredential.user.email,
                        emailVerified: userCredential.user.emailVerified
                    }});
                    
                }} catch (error) {{
                    console.log('❌ Firebase creation error:', error.message);
                    console.log('❌ Error code:', error.code);
                    resolve({{
                        error: error.message,
                        code: error.code
                    }});
                }}
            }});
        """)
        
        print(f"3. 🎯 Firebase Direct Test Results:")
        print(f"   Test email: {test_email}")
        
        if 'success' in firebase_test and firebase_test['success']:
            print(f"   ✅ Firebase account created successfully!")
            print(f"   User ID: {firebase_test['uid']}")
            print(f"   Email: {firebase_test['email']}")
            print(f"   Email verified: {firebase_test['emailVerified']}")
        else:
            print(f"   ❌ Firebase creation failed:")
            print(f"   Error: {firebase_test.get('error', 'Unknown error')}")
            if 'code' in firebase_test:
                print(f"   Error code: {firebase_test['code']}")
        
        # Test registration manager method specifically
        print("\n4. 🔧 Testing Registration Manager Method...")
        
        # Set up registration data
        registration_test = driver.execute_script(f"""
            return new Promise(async (resolve) => {{
                try {{
                    console.log('🧪 Testing registration manager...');
                    
                    if (!window.registrationManager) {{
                        resolve({{ error: 'registrationManager not available' }});
                        return;
                    }}
                    
                    // Set up pending user data manually
                    window.registrationManager.pendingUserData = {{
                        email: '{test_email}2',
                        password: '{test_password}',
                        fullName: 'Direct Test User'
                    }};
                    
                    console.log('🧪 Calling completeEmailRegistration...');
                    const result = await window.registrationManager.completeEmailRegistration('123ABC');
                    
                    console.log('🧪 Registration manager result:', result);
                    resolve(result);
                    
                }} catch (error) {{
                    console.log('❌ Registration manager error:', error.message);
                    console.log('❌ Error stack:', error.stack);
                    resolve({{
                        error: error.message,
                        stack: error.stack
                    }});
                }}
            }});
        """)
        
        print(f"   Registration Manager Test:")
        if 'success' in registration_test and registration_test['success']:
            print(f"   ✅ Registration manager worked!")
            if 'user' in registration_test:
                print(f"   User created: {registration_test['user']}")
        else:
            print(f"   ❌ Registration manager failed:")
            print(f"   Error: {registration_test.get('error', 'Unknown error')}")
        
        # Get console logs to see any additional output
        console_logs = driver.get_log('browser')
        
        print("\n5. 📝 Recent Console Activity:")
        for log in console_logs[-10:]:  # Last 10 logs
            if 'firebase' in log['message'].lower() or '🧪' in log['message'] or '🔥' in log['message']:
                print(f"   {log['message']}")
        
        return firebase_test.get('success', False)
        
    except Exception as e:
        print(f"❌ Direct Firebase test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_firebase_direct()
    print(f"\n🏁 Firebase direct test: {'✅ WORKING' if success else '❌ BROKEN'}")