#!/usr/bin/env python3
# File: test-both-auth-methods-final.py
# Path: /home/herb/Desktop/OurLibrary/test-both-auth-methods-final.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 05:10PM
# FINAL TEST: BOTH EMAIL AND GOOGLE OAUTH MUST CREATE FIREBASE ACCOUNTS

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_both_auth_methods_final():
    """Final test: SUCCESS = Firebase has both email and Google entries"""
    
    print("🔥 FINAL AUTHENTICATION TEST - BOTH METHODS MUST WORK")
    print("=" * 80)
    print("SUCCESS CRITERIA: Firebase Console shows BOTH email and Google accounts")
    print("=" * 80)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    results = {
        'email_auth': {
            'attempted': False,
            'firebase_account_created': False,
            'firebase_uid': None,
            'provider': None,
            'test_email': None
        },
        'google_auth': {
            'attempted': False,
            'firebase_account_created': False,
            'firebase_uid': None,
            'provider': None,
            'google_user_email': None,
            'credential_used': False
        }
    }
    
    try:
        print("\\n🧪 PART 1: EMAIL AUTHENTICATION TEST")
        print("-" * 60)
        
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&final_test=true"
        driver.get(url)
        
        # Wait for full page load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(10)
        
        test_email = f"final_email_test_{timestamp}@example.com"
        test_password = "finaltest123"
        
        print(f"1. 📧 Testing email registration: {test_email}")
        
        # Set up email authentication monitoring
        driver.execute_script(f"""
            window.finalTestResults = {{
                emailAuth: {{
                    attempted: false,
                    accountCreated: false,
                    uid: null,
                    provider: null,
                    email: '{test_email}'
                }},
                googleAuth: {{
                    attempted: false,
                    credentialUsed: false,
                    accountCreated: false,
                    uid: null,
                    provider: null,
                    email: null
                }}
            }};
            
            // Monitor email authentication
            if (window.createUserWithEmailAndPassword) {{
                const original = window.createUserWithEmailAndPassword;
                window.createUserWithEmailAndPassword = async function(auth, email, password) {{
                    console.log('🔥 FINAL TEST: Email createUser called for', email);
                    window.finalTestResults.emailAuth.attempted = true;
                    
                    try {{
                        const result = await original(auth, email, password);
                        console.log('🔥 FINAL TEST: Email Firebase account created:', result.user.uid);
                        
                        window.finalTestResults.emailAuth.accountCreated = true;
                        window.finalTestResults.emailAuth.uid = result.user.uid;
                        window.finalTestResults.emailAuth.provider = 'password';
                        
                        return result;
                    }} catch (error) {{
                        console.log('🔥 FINAL TEST: Email Firebase error:', error);
                        throw error;
                    }}
                }};
            }}
        """)
        
        # Fill and submit email registration
        driver.find_element(By.ID, "fullName").send_keys("Final Test User")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(8)
        
        # Complete email verification
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("   ✅ Reached verification step")
            
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("FINAL9")
            
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(10)
            
            # Check email authentication results
            email_results = driver.execute_script("return window.finalTestResults.emailAuth;")
            
            print("   📊 EMAIL AUTHENTICATION RESULTS:")
            print(f"      Attempted: {'✅' if email_results.get('attempted') else '❌'} {email_results.get('attempted')}")
            print(f"      Firebase Account Created: {'✅' if email_results.get('accountCreated') else '❌'} {email_results.get('accountCreated')}")
            print(f"      Firebase UID: {email_results.get('uid', 'None')}")
            print(f"      Provider: {email_results.get('provider', 'None')}")
            
            results['email_auth']['attempted'] = email_results.get('attempted', False)
            results['email_auth']['firebase_account_created'] = email_results.get('accountCreated', False)
            results['email_auth']['firebase_uid'] = email_results.get('uid')
            results['email_auth']['provider'] = email_results.get('provider')
            results['email_auth']['test_email'] = test_email
        else:
            print("   ❌ Email authentication failed - no verification step")
        
        print("\\n🧪 PART 2: GOOGLE OAUTH TEST (WITH USER FIXES)")
        print("-" * 60)
        
        # Refresh page for clean Google OAuth test
        driver.refresh()
        time.sleep(10)
        
        print("2. 🔍 Testing Google OAuth with improved implementation")
        
        # Set up Google OAuth monitoring with credential detection
        driver.execute_script("""
            window.finalTestResults = {
                googleAuth: {
                    attempted: false,
                    credentialUsed: false,
                    accountCreated: false,
                    uid: null,
                    provider: null,
                    email: null
                }
            };
            
            // Monitor signInWithCredential (the user's fix)
            if (window.signInWithCredential) {
                const original = window.signInWithCredential;
                window.signInWithCredential = async function(auth, credential) {
                    console.log('🔥 FINAL TEST: signInWithCredential called (USER FIX)');
                    window.finalTestResults.googleAuth.attempted = true;
                    window.finalTestResults.googleAuth.credentialUsed = true;
                    
                    try {
                        const result = await original(auth, credential);
                        console.log('🔥 FINAL TEST: Google Firebase account created via credential:', result.user.uid);
                        
                        window.finalTestResults.googleAuth.accountCreated = true;
                        window.finalTestResults.googleAuth.uid = result.user.uid;
                        window.finalTestResults.googleAuth.provider = result.user.providerData[0]?.providerId || 'google.com';
                        window.finalTestResults.googleAuth.email = result.user.email;
                        
                        return result;
                    } catch (error) {
                        console.log('🔥 FINAL TEST: Google credential error:', error);
                        throw error;
                    }
                };
            }
            
            // Also monitor signInWithPopup as fallback
            if (window.signInWithPopup) {
                const original = window.signInWithPopup;
                window.signInWithPopup = async function(auth, provider) {
                    console.log('🔥 FINAL TEST: signInWithPopup called (fallback)');
                    window.finalTestResults.googleAuth.attempted = true;
                    
                    try {
                        const result = await original(auth, provider);
                        console.log('🔥 FINAL TEST: Google Firebase account created via popup:', result.user.uid);
                        
                        window.finalTestResults.googleAuth.accountCreated = true;
                        window.finalTestResults.googleAuth.uid = result.user.uid;
                        window.finalTestResults.googleAuth.provider = result.user.providerData[0]?.providerId || 'google.com';
                        window.finalTestResults.googleAuth.email = result.user.email;
                        
                        return result;
                    } catch (error) {
                        console.log('🔥 FINAL TEST: Google popup error:', error);
                        throw error;
                    }
                };
            }
            
            console.log('🔍 FINAL TEST: Google OAuth monitoring setup complete');
        """)
        
        # Find and click Google OAuth button
        try:
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue with Google')]"))
            )
            
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
            print(f"   ✅ Found Google OAuth button: '{google_button.text}'")
            
            # Clear status and click
            driver.execute_script("document.getElementById('statusContainer').innerHTML = '';")
            
            print("   🖱️ Clicking Google OAuth button...")
            google_button.click()
            
            print("   ⏳ Waiting for OAuth process with credential flow (20 seconds)...")
            time.sleep(20)
            
            # Get Google OAuth results
            google_results = driver.execute_script("return window.finalTestResults.googleAuth;")
            
            # Check current Firebase user
            current_user = driver.execute_script("""
                return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                    uid: window.firebaseAuth.currentUser.uid,
                    email: window.firebaseAuth.currentUser.email,
                    displayName: window.firebaseAuth.currentUser.displayName,
                    providerData: window.firebaseAuth.currentUser.providerData.map(p => p.providerId)
                } : null;
            """)
            
            success_page = driver.execute_script("""
                const successStep = document.getElementById('success-step');
                return successStep && successStep.classList.contains('active');
            """)
            
            status_message = driver.find_element(By.ID, "statusContainer").text.strip()
            
            print("   📊 GOOGLE OAUTH RESULTS:")
            print(f"      Attempted: {'✅' if google_results.get('attempted') else '❌'} {google_results.get('attempted')}")
            print(f"      Credential Used (User Fix): {'✅' if google_results.get('credentialUsed') else '❌'} {google_results.get('credentialUsed')}")
            print(f"      Firebase Account Created: {'✅' if google_results.get('accountCreated') else '❌'} {google_results.get('accountCreated')}")
            print(f"      Firebase UID: {google_results.get('uid', 'None')}")
            print(f"      Provider: {google_results.get('provider', 'None')}")
            print(f"      Email: {google_results.get('email', 'None')}")
            print(f"      Success Page: {'✅' if success_page else '❌'} {success_page}")
            print(f"      Status: '{status_message}'")
            
            if current_user:
                print(f"      🔥 Current Firebase User:")
                print(f"         UID: {current_user.get('uid')}")
                print(f"         Email: {current_user.get('email')}")
                print(f"         Providers: {current_user.get('providerData')}")
            
            results['google_auth']['attempted'] = google_results.get('attempted', False)
            results['google_auth']['firebase_account_created'] = google_results.get('accountCreated', False)
            results['google_auth']['firebase_uid'] = google_results.get('uid')
            results['google_auth']['provider'] = google_results.get('provider')
            results['google_auth']['google_user_email'] = google_results.get('email')
            results['google_auth']['credential_used'] = google_results.get('credentialUsed', False)
            
        except Exception as e:
            print(f"   ❌ Google OAuth test failed: {str(e)}")
        
        return results
        
    except Exception as e:
        print(f"\\n❌ FINAL TEST FAILED: {str(e)}")
        return results
        
    finally:
        try:
            # Save test results
            results_path = "/home/herb/Desktop/OurLibrary/final_auth_test_results.json"
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Take screenshot
            screenshot_path = "/home/herb/Desktop/OurLibrary/final_auth_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📊 Results: {results_path}")
            print(f"📸 Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

def analyze_final_results(results):
    """Analyze final test results against success criteria"""
    
    print("\\n" + "=" * 80)
    print("🏁 FINAL RESULTS ANALYSIS - SUCCESS CRITERIA CHECK")
    print("=" * 80)
    
    email_working = results['email_auth']['firebase_account_created']
    google_working = results['google_auth']['firebase_account_created']
    
    print("\\n📊 AUTHENTICATION METHOD RESULTS:")
    
    # Email Authentication Analysis
    print("\\n   📧 EMAIL AUTHENTICATION:")
    if email_working:
        print("   ✅ SUCCESS: Creates Firebase accounts")
        print(f"      🔥 Firebase UID: {results['email_auth']['firebase_uid']}")
        print(f"      🔥 Provider: {results['email_auth']['provider']}")
        print(f"      🔥 Test Email: {results['email_auth']['test_email']}")
    else:
        print("   ❌ FAILURE: Does not create Firebase accounts")
    
    # Google OAuth Analysis
    print("\\n   🔍 GOOGLE OAUTH:")
    if google_working:
        print("   ✅ SUCCESS: Creates Firebase accounts")
        print(f"      🔥 Firebase UID: {results['google_auth']['firebase_uid']}")
        print(f"      🔥 Provider: {results['google_auth']['provider']}")
        print(f"      🔥 User Email: {results['google_auth']['google_user_email']}")
        if results['google_auth']['credential_used']:
            print("      🎯 User's signInWithCredential fix was used!")
        else:
            print("      💡 Fallback method was used")
    else:
        print("   ❌ FAILURE: Does not create Firebase accounts")
        if results['google_auth']['attempted']:
            print("      💡 OAuth was attempted but failed to create Firebase account")
        else:
            print("      💡 OAuth was not attempted")
    
    # Success criteria evaluation
    print("\\n🎯 SUCCESS CRITERIA EVALUATION:")
    print("   Requirement: Firebase Console must show BOTH email and Google accounts")
    
    if email_working and google_working:
        print("\\n🎉 ✅ SUCCESS CRITERIA MET!")
        print("   🔥 Firebase Console will show:")
        print(f"      • Email user: {results['email_auth']['test_email']} (provider: password)")
        print(f"        UID: {results['email_auth']['firebase_uid']}")
        print(f"      • Google user: {results['google_auth']['google_user_email']} (provider: {results['google_auth']['provider']})")
        print(f"        UID: {results['google_auth']['firebase_uid']}")
        print("\\n💯 BOTH AUTHENTICATION METHODS CREATE FIREBASE ACCOUNTS")
        return "SUCCESS"
    elif email_working:
        print("\\n⚠️ ❌ PARTIAL SUCCESS - EMAIL ONLY")
        print("   ✅ Email authentication works")
        print("   ❌ Google OAuth still broken")
        print("   🔧 Google OAuth needs more fixes")
        return "EMAIL_ONLY"
    elif google_working:
        print("\\n⚠️ ❌ PARTIAL SUCCESS - GOOGLE ONLY") 
        print("   ❌ Email authentication broken")
        print("   ✅ Google OAuth works")
        print("   🔧 Email authentication needs fixes")
        return "GOOGLE_ONLY"
    else:
        print("\\n🚨 ❌ COMPLETE FAILURE")
        print("   ❌ Neither authentication method works")
        print("   🔧 Both methods need fixes")
        return "FAILURE"

if __name__ == "__main__":
    print("🎯 FINAL AUTHENTICATION TEST")
    print("SUCCESS = Firebase Console shows BOTH email AND Google accounts\\n")
    
    results = test_both_auth_methods_final()
    status = analyze_final_results(results)
    
    print(f"\\n{'='*80}")
    print("🔥 FINAL VERDICT")
    print(f"{'='*80}")
    
    if status == "SUCCESS":
        print("🏆 SUCCESS: BOTH authentication methods create Firebase accounts!")
        print("   💯 User's fixes worked!")
        print("   🔥 Firebase Console will show both email and Google users")
    elif status == "EMAIL_ONLY":
        print("⚠️ PARTIAL: Only email authentication works")
        print("   🔧 Google OAuth still needs fixing")
    elif status == "GOOGLE_ONLY":
        print("⚠️ PARTIAL: Only Google OAuth works") 
        print("   🔧 Email authentication still needs fixing")
    else:
        print("🚨 FAILURE: Neither authentication method works")
        print("   🔧 Both methods need immediate attention")
    
    print(f"\\n🎯 Test Result: {status}")
    print("Check Firebase Console > Authentication > Users for verification")