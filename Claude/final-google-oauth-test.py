#!/usr/bin/env python3
# File: final-google-oauth-test.py
# Path: /home/herb/Desktop/OurLibrary/final-google-oauth-test.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:45PM
# FINAL GOOGLE OAUTH TEST WITH RELIABLE BUTTON DETECTION

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def final_google_oauth_test():
    """Final test with reliable Google OAuth button detection"""
    
    print("🔥 FINAL GOOGLE OAUTH TEST - RELIABLE DETECTION")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        print("\\n1. 🌐 Loading page with extended wait...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&final=true"
        driver.get(url)
        
        # Wait for page to fully load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        
        print("   ✅ Page loaded, waiting for JavaScript initialization...")
        time.sleep(10)  # Extra time for JavaScript
        
        print("\\n2. 🔍 Comprehensive button search...")
        
        # Try multiple strategies to find Google OAuth button
        button_selectors = [
            "//button[contains(text(), 'Continue with Google')]",
            "//button[contains(text(), 'Sign in with Google')]",
            "//button[contains(@class, 'btn-google')]",
            "//button[contains(@onclick, 'signInWithGoogle')]"
        ]
        
        google_button = None
        for i, selector in enumerate(button_selectors):
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    for button in buttons:
                        if button.is_displayed():
                            google_button = button
                            print(f"   ✅ Found Google button using selector {i+1}: '{button.text}'")
                            break
                if google_button:
                    break
            except Exception as e:
                print(f"   ⚠️ Selector {i+1} failed: {str(e)}")
        
        if not google_button:
            print("   ❌ Google button not found with any selector")
            
            # Debug: show all visible buttons
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            visible_buttons = [b for b in all_buttons if b.is_displayed()]
            print(f"   📋 Found {len(visible_buttons)} visible buttons:")
            for i, btn in enumerate(visible_buttons):
                print(f"      {i+1}. '{btn.text}' (class: {btn.get_attribute('class')})")
            
            return False
        
        print("\\n3. 🧪 Testing Google OAuth with comprehensive monitoring...")
        
        # Set up detailed monitoring
        monitor_setup = driver.execute_script("""
            window.finalOAuthTest = {
                buttonClicked: false,
                functionCalled: false,
                popupAttempted: false,
                firebaseAccountCreated: false,
                firebaseUID: null,
                providerID: null,
                userEmail: null,
                errors: [],
                logs: []
            };
            
            // Monitor console
            const originalLog = console.log;
            const originalError = console.error;
            
            console.log = function(...args) {
                const msg = args.join(' ');
                window.finalOAuthTest.logs.push(msg);
                if (msg.includes('REAL GOOGLE OAUTH')) {
                    window.finalOAuthTest.functionCalled = true;
                }
                originalLog.apply(console, args);
            };
            
            console.error = function(...args) {
                const msg = args.join(' ');
                window.finalOAuthTest.errors.push(msg);
                originalError.apply(console, args);
            };
            
            // Override Firebase signInWithPopup to monitor calls
            if (window.signInWithPopup) {
                const originalSignIn = window.signInWithPopup;
                window.signInWithPopup = async function(auth, provider) {
                    console.log('🔥 FINAL TEST: signInWithPopup called with provider:', provider);
                    window.finalOAuthTest.popupAttempted = true;
                    
                    try {
                        const result = await originalSignIn(auth, provider);
                        console.log('🔥 FINAL TEST: signInWithPopup success:', result.user.uid);
                        
                        window.finalOAuthTest.firebaseAccountCreated = true;
                        window.finalOAuthTest.firebaseUID = result.user.uid;
                        window.finalOAuthTest.userEmail = result.user.email;
                        window.finalOAuthTest.providerID = result.user.providerData[0]?.providerId;
                        
                        return result;
                    } catch (error) {
                        console.log('🔥 FINAL TEST: signInWithPopup error:', error);
                        window.finalOAuthTest.errors.push('signInWithPopup error: ' + error.message);
                        throw error;
                    }
                };
            }
            
            return true;
        """)
        
        if not monitor_setup:
            print("   ❌ Failed to set up monitoring")
            return False
        
        print("   ✅ Monitoring setup complete")
        
        # Clear status and click button
        driver.execute_script("document.getElementById('statusContainer').innerHTML = '';")
        
        print(f"   🖱️ Clicking Google OAuth button: '{google_button.text}'")
        google_button.click()
        
        # Mark button as clicked
        driver.execute_script("window.finalOAuthTest.buttonClicked = true;")
        
        print("   ⏳ Waiting for OAuth process (20 seconds)...")
        time.sleep(20)
        
        print("\\n4. 📊 Final test results...")
        
        # Get comprehensive results
        test_results = driver.execute_script("return window.finalOAuthTest || {};")
        
        # Check Firebase Auth state
        firebase_user = driver.execute_script("""
            return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                uid: window.firebaseAuth.currentUser.uid,
                email: window.firebaseAuth.currentUser.email,
                displayName: window.firebaseAuth.currentUser.displayName,
                providerData: window.firebaseAuth.currentUser.providerData.map(p => p.providerId)
            } : null;
        """)
        
        # Check success page
        success_page = driver.execute_script("""
            const successStep = document.getElementById('success-step');
            return successStep && successStep.classList.contains('active');
        """)
        
        status_message = driver.find_element(By.ID, "statusContainer").text.strip()
        
        print("   📊 FINAL GOOGLE OAUTH RESULTS:")
        print(f"      Button Clicked: {'✅' if test_results.get('buttonClicked') else '❌'} {test_results.get('buttonClicked')}")
        print(f"      Function Called: {'✅' if test_results.get('functionCalled') else '❌'} {test_results.get('functionCalled')}")
        print(f"      Popup Attempted: {'✅' if test_results.get('popupAttempted') else '❌'} {test_results.get('popupAttempted')}")
        print(f"      Firebase Account Created: {'✅' if test_results.get('firebaseAccountCreated') else '❌'} {test_results.get('firebaseAccountCreated')}")
        print(f"      Success Page Shown: {'✅' if success_page else '❌'} {success_page}")
        print(f"      Status Message: '{status_message}'")
        
        if test_results.get('firebaseUID'):
            print(f"      🔥 FIREBASE DETAILS:")
            print(f"         UID: {test_results.get('firebaseUID')}")
            print(f"         Email: {test_results.get('userEmail')}")
            print(f"         Provider: {test_results.get('providerID')}")
        
        if firebase_user:
            print(f"      🔥 CURRENT FIREBASE USER:")
            print(f"         UID: {firebase_user.get('uid')}")
            print(f"         Email: {firebase_user.get('email')}")
            print(f"         Providers: {firebase_user.get('providerData')}")
        
        # Show recent logs
        if test_results.get('logs'):
            print("\\n   📝 Recent Logs:")
            for log in test_results['logs'][-3:]:
                if 'GOOGLE' in log or 'OAuth' in log:
                    print(f"      {log}")
        
        # Show errors
        if test_results.get('errors'):
            print("\\n   🚨 Errors:")
            for error in test_results['errors'][-3:]:
                print(f"      {error}")
        
        # Final determination
        oauth_working = (
            test_results.get('firebaseAccountCreated') and 
            test_results.get('firebaseUID') and
            test_results.get('providerID') == 'google.com'
        )
        
        if oauth_working:
            print("\\n🎉 SUCCESS: Google OAuth creates REAL Firebase accounts!")
            print(f"   🔥 Firebase UID: {test_results.get('firebaseUID')}")
            print(f"   🔥 Provider: google.com")
            print("   💯 CHECK FIREBASE CONSOLE FOR NEW GOOGLE USER")
            return True
        else:
            print("\\n❌ GOOGLE OAUTH NOT CREATING FIREBASE ACCOUNTS")
            if not test_results.get('popupAttempted'):
                print("   💡 OAuth popup was not attempted - check implementation")
            elif test_results.get('errors'):
                print("   💡 OAuth failed due to errors - check error messages")
            else:
                print("   💡 OAuth attempted but Firebase account not created")
            return False
        
    except Exception as e:
        print(f"\\n❌ FINAL TEST FAILED: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
        
    finally:
        try:
            screenshot_path = "/home/herb/Desktop/OurLibrary/final_oauth_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 Final Test Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

if __name__ == "__main__":
    print("🎯 FINAL COMPREHENSIVE GOOGLE OAUTH TEST")
    print("This is the definitive test to determine if Google OAuth works\\n")
    
    success = final_google_oauth_test()
    
    print("\\n" + "=" * 60)
    print("🔥 FINAL GOOGLE OAUTH VERDICT")
    print("=" * 60)
    
    if success:
        print("✅ CONFIRMED: Google OAuth creates real Firebase accounts")
        print("   🔥 Provider: google.com")
        print("   🔥 Firebase Console will show Google-authenticated users")
        print("   💯 System is fully functional")
    else:
        print("❌ CONFIRMED: Google OAuth does NOT create Firebase accounts")
        print("   🚨 Only email registration creates Firebase accounts")
        print("   🔧 Google OAuth needs to be fixed to work with Firebase")
        print("   💡 Current implementation has issues")
    
    print("\\n🎯 This is the definitive answer to your question")