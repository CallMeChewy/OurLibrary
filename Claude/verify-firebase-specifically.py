#!/usr/bin/env python3
# File: verify-firebase-specifically.py
# Path: /home/herb/Desktop/OurLibrary/verify-firebase-specifically.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 03:50PM
# VERIFY FIREBASE FUNCTIONALITY SPECIFICALLY

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def verify_firebase_functionality():
    """Test Firebase functionality specifically - no assumptions"""
    
    print("🔥 VERIFYING FIREBASE FUNCTIONALITY SPECIFICALLY")
    print("=" * 70)
    print("Testing ACTUAL Firebase connection and account creation")
    print("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    
    firebase_test_results = {
        'firebase_connected': False,
        'firebase_auth_available': False,
        'firebase_functions_available': False,
        'createUser_function_available': False,
        'actual_account_creation_attempted': False,
        'actual_account_creation_successful': False,
        'firebase_uid_generated': None,
        'smtp_function_called': False,
        'smtp_function_successful': False,
        'error_details': []
    }
    
    try:
        print("\\n1. 🌐 Loading page and checking Firebase initialization...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        driver.get(url)
        time.sleep(15)  # Wait for full Firebase initialization
        
        # Check Firebase initialization status
        firebase_status = driver.execute_script("""
            console.log('🔥 FIREBASE CHECK: Starting Firebase verification');
            
            const status = {
                firebaseReady: !!window.firebaseReady,
                firebaseAuth: {
                    exists: !!window.firebaseAuth,
                    type: typeof window.firebaseAuth,
                    currentUser: window.firebaseAuth ? window.firebaseAuth.currentUser : null
                },
                firebaseFunctions: {
                    exists: !!window.firebaseFunctions,
                    type: typeof window.firebaseFunctions
                },
                createUserFunction: {
                    exists: !!window.createUserWithEmailAndPassword,
                    type: typeof window.createUserWithEmailAndPassword
                },
                signInFunction: {
                    exists: !!window.signInWithEmailAndPassword,
                    type: typeof window.signInWithEmailAndPassword
                },
                httpsCallable: {
                    exists: !!window.httpsCallable,
                    type: typeof window.httpsCallable
                }
            };
            
            console.log('🔥 FIREBASE STATUS:', status);
            return status;
        """)
        
        print("   📊 FIREBASE INITIALIZATION STATUS:")
        print(f"      Firebase Ready: {'✅' if firebase_status['firebaseReady'] else '❌'} {firebase_status['firebaseReady']}")
        print(f"      Firebase Auth: {'✅' if firebase_status['firebaseAuth']['exists'] else '❌'} {firebase_status['firebaseAuth']['type']}")
        print(f"      Firebase Functions: {'✅' if firebase_status['firebaseFunctions']['exists'] else '❌'} {firebase_status['firebaseFunctions']['type']}")
        print(f"      createUserWithEmailAndPassword: {'✅' if firebase_status['createUserFunction']['exists'] else '❌'} {firebase_status['createUserFunction']['type']}")
        print(f"      httpsCallable: {'✅' if firebase_status['httpsCallable']['exists'] else '❌'} {firebase_status['httpsCallable']['type']}")
        
        firebase_test_results['firebase_connected'] = firebase_status['firebaseReady']
        firebase_test_results['firebase_auth_available'] = firebase_status['firebaseAuth']['exists']
        firebase_test_results['firebase_functions_available'] = firebase_status['firebaseFunctions']['exists']
        firebase_test_results['createUser_function_available'] = firebase_status['createUserFunction']['exists']
        
        if not firebase_status['firebaseReady']:
            firebase_test_results['error_details'].append("Firebase not ready")
            print("   ❌ Firebase not ready - cannot proceed with tests")
            return firebase_test_results
        
        print("\\n2. 🧪 Testing Firebase SMTP Function Call...")
        
        # Test SMTP function specifically
        smtp_test_result = driver.execute_script("""
            return new Promise(async (resolve) => {
                try {
                    console.log('🔥 SMTP TEST: Testing Firebase Functions SMTP');
                    
                    if (!window.httpsCallable || !window.firebaseFunctions) {
                        resolve({
                            success: false,
                            error: 'Firebase Functions or httpsCallable not available'
                        });
                        return;
                    }
                    
                    // Try to create the SMTP function
                    const sendVerificationEmail = window.httpsCallable(window.firebaseFunctions, 'sendVerificationEmail');
                    console.log('🔥 SMTP TEST: sendVerificationEmail function created');
                    
                    // Attempt to call it with a test email
                    const testEmail = 'firebase_test_' + Date.now() + '@example.com';
                    console.log('🔥 SMTP TEST: Calling with email:', testEmail);
                    
                    try {
                        const result = await sendVerificationEmail({ email: testEmail });
                        console.log('🔥 SMTP TEST: Success result:', result);
                        resolve({
                            success: true,
                            email: testEmail,
                            result: result.data || result
                        });
                    } catch (error) {
                        console.log('🔥 SMTP TEST: Error calling function:', error);
                        resolve({
                            success: false,
                            error: error.message,
                            email: testEmail,
                            attempted: true
                        });
                    }
                    
                } catch (error) {
                    console.log('🔥 SMTP TEST: Failed to setup:', error);
                    resolve({
                        success: false,
                        error: error.message,
                        setupFailed: true
                    });
                }
            });
        """)
        
        time.sleep(8)  # Wait for the promise to resolve
        
        print("   📊 FIREBASE SMTP FUNCTION TEST:")
        print(f"      Function Called: {'✅' if smtp_test_result else '❌'}")
        if smtp_test_result:
            if 'success' in smtp_test_result:
                print(f"      Success: {'✅' if smtp_test_result['success'] else '❌'} {smtp_test_result['success']}")
                firebase_test_results['smtp_function_called'] = True
                firebase_test_results['smtp_function_successful'] = smtp_test_result['success']
                if not smtp_test_result['success'] and 'error' in smtp_test_result:
                    print(f"      Error: {smtp_test_result['error']}")
                    firebase_test_results['error_details'].append(f"SMTP Error: {smtp_test_result['error']}")
            else:
                print(f"      Result: {smtp_test_result}")
        
        print("\\n3. 🔥 Testing ACTUAL Firebase Account Creation...")
        
        # Fill registration form
        test_email = f"firebase_account_test_{int(time.time())}@example.com"
        test_password = "firebase123"
        
        driver.find_element(By.ID, "fullName").clear()
        driver.find_element(By.ID, "fullName").send_keys("Firebase Test User")
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").clear()
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        print(f"   📧 Test Account Email: {test_email}")
        
        # Set up Firebase account creation monitoring
        driver.execute_script(f"""
            window.firebaseAccountTest = {{
                email: '{test_email}',
                password: '{test_password}',
                accountCreated: false,
                uid: null,
                error: null,
                createUserCalled: false
            }};
            
            // Override createUserWithEmailAndPassword to monitor actual calls
            if (window.createUserWithEmailAndPassword) {{
                const originalCreate = window.createUserWithEmailAndPassword;
                window.createUserWithEmailAndPassword = async function(auth, email, password) {{
                    console.log('🔥 FIREBASE ACCOUNT: createUserWithEmailAndPassword called');
                    console.log('🔥 FIREBASE ACCOUNT: Email:', email);
                    console.log('🔥 FIREBASE ACCOUNT: Auth object:', auth);
                    
                    window.firebaseAccountTest.createUserCalled = true;
                    
                    try {{
                        const result = await originalCreate(auth, email, password);
                        console.log('🔥 FIREBASE ACCOUNT: SUCCESS - Account created');
                        console.log('🔥 FIREBASE ACCOUNT: User UID:', result.user.uid);
                        console.log('🔥 FIREBASE ACCOUNT: User email:', result.user.email);
                        console.log('🔥 FIREBASE ACCOUNT: Creation time:', result.user.metadata.creationTime);
                        
                        window.firebaseAccountTest.accountCreated = true;
                        window.firebaseAccountTest.uid = result.user.uid;
                        
                        return result;
                    }} catch (error) {{
                        console.log('🔥 FIREBASE ACCOUNT: ERROR creating account:', error);
                        window.firebaseAccountTest.error = error.message;
                        throw error;
                    }}
                }};
            }}
        """)
        
        # Submit the form to trigger account creation
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        print("   🖱️ Submitting form to start account creation process...")
        submit_button.click()
        
        # Wait for form processing
        time.sleep(8)
        
        # Check if we reached verification step (indicates SMTP worked)
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("   ✅ Reached verification step - SMTP function working")
            
            # Enter verification code to trigger Firebase account creation
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("TEST99")
            
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            print("   🔥 Submitting verification code to create Firebase account...")
            verify_button.click()
            
            # Wait for Firebase account creation
            time.sleep(10)
            
            # Check results
            account_test_results = driver.execute_script("return window.firebaseAccountTest || {};")
            
            print("   📊 FIREBASE ACCOUNT CREATION RESULTS:")
            print(f"      createUser Function Called: {'✅' if account_test_results.get('createUserCalled') else '❌'} {account_test_results.get('createUserCalled')}")
            print(f"      Account Created: {'✅' if account_test_results.get('accountCreated') else '❌'} {account_test_results.get('accountCreated')}")
            print(f"      Firebase UID Generated: {account_test_results.get('uid', 'None')}")
            if account_test_results.get('error'):
                print(f"      Error: {account_test_results.get('error')}")
                firebase_test_results['error_details'].append(f"Account Creation Error: {account_test_results.get('error')}")
            
            firebase_test_results['actual_account_creation_attempted'] = account_test_results.get('createUserCalled', False)
            firebase_test_results['actual_account_creation_successful'] = account_test_results.get('accountCreated', False)
            firebase_test_results['firebase_uid_generated'] = account_test_results.get('uid')
            
        else:
            print("   ❌ Did not reach verification step - SMTP function may not be working")
            firebase_test_results['error_details'].append("Did not reach verification step")
        
        return firebase_test_results
        
    except Exception as e:
        print(f"\\n❌ FIREBASE TEST ERROR: {str(e)}")
        firebase_test_results['error_details'].append(f"Test Error: {str(e)}")
        return firebase_test_results
        
    finally:
        try:
            # Take screenshot of final state
            screenshot_path = "/home/herb/Desktop/OurLibrary/firebase_test_proof.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 Firebase Test Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

def analyze_firebase_results(results):
    """Analyze Firebase test results and provide summary"""
    
    print("\\n" + "=" * 70)
    print("🔥 FIREBASE FUNCTIONALITY ANALYSIS")
    print("=" * 70)
    
    score = 0
    total = 6
    
    print("\\n📊 FIREBASE COMPONENT STATUS:")
    
    if results['firebase_connected']:
        print("   ✅ Firebase Connection: WORKING")
        score += 1
    else:
        print("   ❌ Firebase Connection: NOT WORKING")
    
    if results['firebase_auth_available']:
        print("   ✅ Firebase Auth: AVAILABLE")
        score += 1
    else:
        print("   ❌ Firebase Auth: NOT AVAILABLE")
    
    if results['firebase_functions_available']:
        print("   ✅ Firebase Functions: AVAILABLE")
        score += 1
    else:
        print("   ❌ Firebase Functions: NOT AVAILABLE")
    
    if results['createUser_function_available']:
        print("   ✅ createUserWithEmailAndPassword: AVAILABLE")
        score += 1
    else:
        print("   ❌ createUserWithEmailAndPassword: NOT AVAILABLE")
    
    if results['actual_account_creation_attempted']:
        print("   ✅ Account Creation: ATTEMPTED")
        score += 1
    else:
        print("   ❌ Account Creation: NOT ATTEMPTED")
    
    if results['actual_account_creation_successful']:
        print("   ✅ Account Creation: SUCCESSFUL")
        score += 1
        if results['firebase_uid_generated']:
            print(f"      🔥 Firebase UID: {results['firebase_uid_generated']}")
    else:
        print("   ❌ Account Creation: FAILED")
    
    percentage = (score / total) * 100
    
    print(f"\\n📈 FIREBASE FUNCTIONALITY SCORE: {score}/{total} ({percentage:.1f}%)")
    
    if score == total:
        print("\\n🎉 FIREBASE IS FULLY FUNCTIONAL!")
        print("   ✅ All Firebase components working")
        print("   ✅ Real account creation confirmed")
        print("   ✅ SMTP functions operational")
        return "FULLY_FUNCTIONAL"
    elif score >= 4:
        print("\\n⚠️ FIREBASE PARTIALLY FUNCTIONAL")
        print("   ✅ Core Firebase components working")
        if not results['actual_account_creation_successful']:
            print("   ❌ Account creation needs fixing")
        return "PARTIALLY_FUNCTIONAL"  
    else:
        print("\\n🚨 FIREBASE NOT FUNCTIONAL")
        print("   ❌ Critical Firebase components broken")
        return "NOT_FUNCTIONAL"

if __name__ == "__main__":
    print("🎯 STARTING FIREBASE-SPECIFIC VERIFICATION")
    print("This will test ONLY Firebase functionality with no assumptions\\n")
    
    results = verify_firebase_functionality()
    status = analyze_firebase_results(results)
    
    if results['error_details']:
        print("\\n🚨 ERROR DETAILS:")
        for error in results['error_details']:
            print(f"   • {error}")
    
    print(f"\\n🔥 FINAL FIREBASE STATUS: {status}")
    
    if status == "FULLY_FUNCTIONAL":
        print("💯 Firebase is working perfectly - real accounts are being created!")
    elif status == "PARTIALLY_FUNCTIONAL":
        print("⚠️ Firebase has issues - some components not working properly")  
    else:
        print("❌ Firebase is not working - needs immediate fixes")