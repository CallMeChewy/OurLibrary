#!/usr/bin/env python3
# File: comprehensive-firebase-verification-test.py
# Path: /home/herb/Desktop/OurLibrary/comprehensive-firebase-verification-test.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:25PM
# COMPREHENSIVE FIREBASE VERIFICATION TEST - BOTH EMAIL AND GOOGLE

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def comprehensive_firebase_test():
    """Comprehensive test of both email and Google OAuth Firebase account creation"""
    
    print("🔥 COMPREHENSIVE FIREBASE ACCOUNT VERIFICATION TEST")
    print("=" * 80)
    print("Testing BOTH email registration AND Google OAuth with Firebase")
    print("Verifying actual Firebase Console account creation")
    print("=" * 80)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)
    driver.maximize_window()
    
    test_results = {
        'email_registration': {
            'attempted': False,
            'firebase_account_created': False,
            'firebase_uid': None,
            'provider': None,
            'email': None
        },
        'google_oauth': {
            'attempted': False,
            'firebase_account_created': False,
            'firebase_uid': None,
            'provider': None,
            'email': None,
            'popup_blocked': False,
            'domain_error': False
        }
    }
    
    try:
        print("\\n🧪 PART 1: EMAIL REGISTRATION FIREBASE TEST")
        print("-" * 60)
        
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&test=comprehensive"
        driver.get(url)
        time.sleep(15)
        
        # Test email registration
        test_email = f"firebase_email_test_{timestamp}@example.com"
        test_password = "testpass123"
        
        print(f"1. 📧 Testing email registration with: {test_email}")
        
        # Fill registration form
        driver.find_element(By.ID, "fullName").clear()
        driver.find_element(By.ID, "fullName").send_keys("Email Test User")
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(test_password)
        driver.find_element(By.ID, "confirmPassword").clear()
        driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
        
        # Monitor Firebase account creation for email
        driver.execute_script(f"""
            window.emailTestData = {{
                email: '{test_email}',
                accountCreated: false,
                uid: null,
                provider: null,
                error: null
            }};
            
            if (window.createUserWithEmailAndPassword) {{
                const original = window.createUserWithEmailAndPassword;
                window.createUserWithEmailAndPassword = async function(auth, email, password) {{
                    console.log('🔥 EMAIL TEST: createUserWithEmailAndPassword called');
                    console.log('🔥 EMAIL TEST: Email:', email);
                    
                    try {{
                        const result = await original(auth, email, password);
                        console.log('🔥 EMAIL TEST: Firebase account created successfully');
                        console.log('🔥 EMAIL TEST: UID:', result.user.uid);
                        console.log('🔥 EMAIL TEST: Provider data:', result.user.providerData);
                        
                        window.emailTestData.accountCreated = true;
                        window.emailTestData.uid = result.user.uid;
                        window.emailTestData.provider = result.user.providerData[0]?.providerId || 'password';
                        
                        return result;
                    }} catch (error) {{
                        console.log('🔥 EMAIL TEST: Error:', error);
                        window.emailTestData.error = error.message;
                        throw error;
                    }}
                }};
            }}
        """)
        
        # Submit email registration
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(8)
        
        # Check if verification step appeared
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("   ✅ Reached verification step - proceeding to create Firebase account")
            
            # Enter verification code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.send_keys("TEST99")
            
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(10)
            
            # Check email registration results
            email_results = driver.execute_script("return window.emailTestData || {};")
            
            print("   📊 EMAIL REGISTRATION RESULTS:")
            print(f"      Account Created: {'✅' if email_results.get('accountCreated') else '❌'} {email_results.get('accountCreated')}")
            print(f"      Firebase UID: {email_results.get('uid', 'None')}")
            print(f"      Provider: {email_results.get('provider', 'None')}")
            print(f"      Error: {email_results.get('error', 'None')}")
            
            test_results['email_registration']['attempted'] = True
            test_results['email_registration']['firebase_account_created'] = email_results.get('accountCreated', False)
            test_results['email_registration']['firebase_uid'] = email_results.get('uid')
            test_results['email_registration']['provider'] = email_results.get('provider')
            test_results['email_registration']['email'] = test_email
        else:
            print("   ❌ Did not reach verification step - email registration failed")
        
        print("\\n🧪 PART 2: GOOGLE OAUTH FIREBASE TEST")
        print("-" * 60)
        
        # Refresh page for clean Google OAuth test
        driver.refresh()
        time.sleep(10)
        
        print("2. 🔍 Testing Google OAuth Firebase account creation")
        
        # Check Google OAuth implementation
        oauth_check = driver.execute_script("""
            console.log('🔍 CHECKING: Google OAuth implementation');
            
            if (typeof signInWithGoogle !== 'function') {
                return { exists: false };
            }
            
            const source = signInWithGoogle.toString();
            return {
                exists: true,
                usesRealFirebase: source.includes('signInWithPopup') && source.includes('GoogleAuthProvider'),
                hasScopes: source.includes('addScope'),
                isSimulation: source.includes('simulation') || source.includes('simulatedGoogleUser')
            };
        """)
        
        print(f"   📋 Google OAuth Implementation:")
        print(f"      Function exists: {'✅' if oauth_check.get('exists') else '❌'}")
        print(f"      Uses real Firebase: {'✅' if oauth_check.get('usesRealFirebase') else '❌'}")
        print(f"      Has scopes: {'✅' if oauth_check.get('hasScopes') else '❌'}")
        print(f"      Is simulation: {'❌' if not oauth_check.get('isSimulation') else '⚠️ YES'}")
        
        if not oauth_check.get('usesRealFirebase'):
            print("   ❌ Google OAuth is not using real Firebase - skipping test")
            test_results['google_oauth']['attempted'] = False
        else:
            # Monitor Google OAuth Firebase creation
            driver.execute_script("""
                window.googleOAuthTestData = {
                    attempted: false,
                    accountCreated: false,
                    uid: null,
                    email: null,
                    displayName: null,
                    provider: null,
                    error: null,
                    popupBlocked: false,
                    domainError: false
                };
                
                // Override signInWithGoogle to monitor results
                if (typeof signInWithGoogle === 'function') {
                    const original = signInWithGoogle;
                    window.signInWithGoogle = async function() {
                        console.log('🔥 GOOGLE TEST: signInWithGoogle called');
                        window.googleOAuthTestData.attempted = true;
                        
                        try {
                            const result = await original();
                            
                            if (result && result.user) {
                                console.log('🔥 GOOGLE TEST: Real Firebase user created/signed in');
                                console.log('🔥 GOOGLE TEST: UID:', result.user.uid);
                                console.log('🔥 GOOGLE TEST: Email:', result.user.email);
                                console.log('🔥 GOOGLE TEST: Provider data:', result.user.providerData);
                                
                                window.googleOAuthTestData.accountCreated = true;
                                window.googleOAuthTestData.uid = result.user.uid;
                                window.googleOAuthTestData.email = result.user.email;
                                window.googleOAuthTestData.displayName = result.user.displayName;
                                window.googleOAuthTestData.provider = result.user.providerData[0]?.providerId;
                            }
                            
                            return result;
                        } catch (error) {
                            console.log('🔥 GOOGLE TEST: Error:', error);
                            window.googleOAuthTestData.error = error.message;
                            
                            if (error.code === 'auth/popup-blocked') {
                                window.googleOAuthTestData.popupBlocked = true;
                            } else if (error.code === 'auth/unauthorized-domain') {
                                window.googleOAuthTestData.domainError = true;
                            }
                            
                            throw error;
                        }
                    };
                }
            """)
            
            # Find and click Google OAuth button
            try:
                google_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
                
                if google_buttons:
                    google_button = google_buttons[0]
                    print(f"   ✅ Found Google button: '{google_button.text}'")
                    
                    print("   🖱️ Clicking Google OAuth button...")
                    google_button.click()
                    
                    print("   ⏳ Waiting for OAuth process (20 seconds)...")
                    time.sleep(20)
                    
                    # Get Google OAuth results
                    oauth_results = driver.execute_script("return window.googleOAuthTestData || {};")
                    
                    # Check current Firebase user
                    current_user = driver.execute_script("""
                        return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                            uid: window.firebaseAuth.currentUser.uid,
                            email: window.firebaseAuth.currentUser.email,
                            displayName: window.firebaseAuth.currentUser.displayName,
                            providerData: window.firebaseAuth.currentUser.providerData.map(p => ({
                                providerId: p.providerId,
                                uid: p.uid,
                                email: p.email
                            }))
                        } : null;
                    """)
                    
                    print("   📊 GOOGLE OAUTH RESULTS:")
                    print(f"      OAuth Attempted: {'✅' if oauth_results.get('attempted') else '❌'} {oauth_results.get('attempted')}")
                    print(f"      Account Created: {'✅' if oauth_results.get('accountCreated') else '❌'} {oauth_results.get('accountCreated')}")
                    print(f"      Firebase UID: {oauth_results.get('uid', 'None')}")
                    print(f"      Email: {oauth_results.get('email', 'None')}")
                    print(f"      Provider: {oauth_results.get('provider', 'None')}")
                    print(f"      Popup Blocked: {'⚠️ YES' if oauth_results.get('popupBlocked') else '✅ NO'} {oauth_results.get('popupBlocked')}")
                    print(f"      Domain Error: {'⚠️ YES' if oauth_results.get('domainError') else '✅ NO'} {oauth_results.get('domainError')}")
                    print(f"      Error: {oauth_results.get('error', 'None')}")
                    
                    if current_user:
                        print("   🔥 CURRENT FIREBASE USER:")
                        print(f"      UID: {current_user.get('uid')}")
                        print(f"      Email: {current_user.get('email')}")
                        print(f"      Name: {current_user.get('displayName')}")
                        print(f"      Providers: {[p['providerId'] for p in current_user.get('providerData', [])]}")
                    
                    test_results['google_oauth']['attempted'] = oauth_results.get('attempted', False)
                    test_results['google_oauth']['firebase_account_created'] = oauth_results.get('accountCreated', False)
                    test_results['google_oauth']['firebase_uid'] = oauth_results.get('uid')
                    test_results['google_oauth']['provider'] = oauth_results.get('provider')
                    test_results['google_oauth']['email'] = oauth_results.get('email')
                    test_results['google_oauth']['popup_blocked'] = oauth_results.get('popupBlocked', False)
                    test_results['google_oauth']['domain_error'] = oauth_results.get('domainError', False)
                    
                else:
                    print("   ❌ Google OAuth button not found")
                    
            except Exception as e:
                print(f"   ❌ Error testing Google OAuth: {str(e)}")
        
        return test_results
        
    except Exception as e:
        print(f"\\n❌ COMPREHENSIVE TEST FAILED: {str(e)}")
        return test_results
        
    finally:
        try:
            # Save test results
            results_path = "/home/herb/Desktop/OurLibrary/comprehensive_firebase_test_results.json"
            with open(results_path, 'w') as f:
                json.dump(test_results, f, indent=2)
            print(f"\\n📊 Test Results Saved: {results_path}")
            
            # Take screenshot
            screenshot_path = "/home/herb/Desktop/OurLibrary/comprehensive_firebase_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot Saved: {screenshot_path}")
            
        except:
            pass
            
        driver.quit()

def analyze_comprehensive_results(results):
    """Analyze comprehensive test results"""
    
    print("\\n" + "=" * 80)
    print("🔥 COMPREHENSIVE FIREBASE ACCOUNT ANALYSIS")
    print("=" * 80)
    
    email_reg = results['email_registration']
    google_oauth = results['google_oauth']
    
    print("\\n📊 EMAIL REGISTRATION ANALYSIS:")
    if email_reg['attempted']:
        if email_reg['firebase_account_created']:
            print("   ✅ SUCCESS: Email registration creates Firebase accounts")
            print(f"      UID: {email_reg['firebase_uid']}")
            print(f"      Provider: {email_reg['provider']}")
            print(f"      Email: {email_reg['email']}")
        else:
            print("   ❌ FAILURE: Email registration not creating Firebase accounts")
    else:
        print("   ⚠️ NOT TESTED: Email registration was not attempted")
    
    print("\\n📊 GOOGLE OAUTH ANALYSIS:")
    if google_oauth['attempted']:
        if google_oauth['firebase_account_created']:
            print("   ✅ SUCCESS: Google OAuth creates Firebase accounts")
            print(f"      UID: {google_oauth['firebase_uid']}")
            print(f"      Provider: {google_oauth['provider']}")
            print(f"      Email: {google_oauth['email']}")
        else:
            print("   ❌ FAILURE: Google OAuth not creating Firebase accounts")
            if google_oauth['popup_blocked']:
                print("      Issue: Browser blocked OAuth popup")
            elif google_oauth['domain_error']:
                print("      Issue: Domain not authorized in Google Cloud Console")
            else:
                print("      Issue: Unknown OAuth error")
    else:
        print("   ⚠️ NOT TESTED: Google OAuth was not attempted")
    
    print("\\n🎯 FIREBASE CONSOLE VERIFICATION:")
    print("   To verify these accounts in Firebase Console:")
    print("   1. Go to: https://console.firebase.google.com/")
    print("   2. Select project: our-library-d7b60")
    print("   3. Navigate to: Authentication > Users")
    print("   4. Look for:")
    
    if email_reg['firebase_account_created']:
        print(f"      - Email user: {email_reg['email']} (provider: password)")
        print(f"        UID: {email_reg['firebase_uid']}")
    
    if google_oauth['firebase_account_created']:
        print(f"      - Google user: {google_oauth['email']} (provider: google.com)")
        print(f"        UID: {google_oauth['firebase_uid']}")
    
    # Overall status
    email_working = email_reg['firebase_account_created']
    google_working = google_oauth['firebase_account_created']
    
    print("\\n🏁 FINAL VERDICT:")
    if email_working and google_working:
        print("   🎉 BOTH authentication methods create Firebase accounts")
        return "FULLY_FUNCTIONAL"
    elif email_working:
        print("   ⚠️ ONLY email registration creates Firebase accounts")
        print("   🚨 Google OAuth needs fixing")
        return "EMAIL_ONLY"
    elif google_working:
        print("   ⚠️ ONLY Google OAuth creates Firebase accounts")
        print("   🚨 Email registration needs fixing")
        return "GOOGLE_ONLY"
    else:
        print("   🚨 NEITHER authentication method creates Firebase accounts")
        return "NOT_FUNCTIONAL"

if __name__ == "__main__":
    print("🎯 STARTING COMPREHENSIVE FIREBASE VERIFICATION")
    print("Testing BOTH email registration AND Google OAuth")
    print("Verifying which creates actual Firebase Console accounts\\n")
    
    results = comprehensive_firebase_test()
    status = analyze_comprehensive_results(results)
    
    print(f"\\n🔥 SYSTEM STATUS: {status}")
    
    if status == "EMAIL_ONLY":
        print("💡 FINDING: You are correct - only email creates Firebase accounts")
        print("🔧 ACTION NEEDED: Fix Google OAuth to create real Firebase accounts")
    elif status == "FULLY_FUNCTIONAL":
        print("💯 FINDING: Both methods create Firebase accounts as expected")
    else:
        print(f"🚨 FINDING: System has issues - {status}")