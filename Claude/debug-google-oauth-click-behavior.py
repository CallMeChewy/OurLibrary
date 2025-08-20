#!/usr/bin/env python3
# File: debug-google-oauth-click-behavior.py
# Path: /home/herb/Desktop/OurLibrary/debug-google-oauth-click-behavior.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:40PM
# DEBUG GOOGLE OAUTH CLICK BEHAVIOR

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_google_oauth_click():
    """Debug what happens when Google OAuth button is clicked"""
    
    print("🔍 DEBUGGING: Google OAuth Button Click Behavior")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    
    try:
        print("\\n1. 🌐 Loading page and setting up monitoring...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&debug=oauth"
        driver.get(url)
        time.sleep(15)
        
        # Set up comprehensive monitoring
        driver.execute_script("""
            window.oauthDebugData = {
                functionCalled: false,
                functionExists: typeof signInWithGoogle === 'function',
                functionSource: typeof signInWithGoogle === 'function' ? signInWithGoogle.toString().substring(0, 500) : 'N/A',
                errors: [],
                logs: [],
                popupAttempted: false,
                popupBlocked: false,
                domainError: false,
                firebaseResult: null,
                currentUser: null
            };
            
            // Override console methods to capture logs
            const originalLog = console.log;
            const originalError = console.error;
            
            console.log = function(...args) {
                const message = args.join(' ');
                window.oauthDebugData.logs.push({type: 'log', message: message, time: Date.now()});
                originalLog.apply(console, args);
            };
            
            console.error = function(...args) {
                const message = args.join(' ');
                window.oauthDebugData.errors.push({type: 'error', message: message, time: Date.now()});
                originalError.apply(console, args);
            };
            
            // Override signInWithGoogle to monitor execution
            if (typeof signInWithGoogle === 'function') {
                const originalSignIn = signInWithGoogle;
                window.signInWithGoogle = async function() {
                    console.log('🔍 DEBUG: signInWithGoogle function called');
                    window.oauthDebugData.functionCalled = true;
                    
                    try {
                        const result = await originalSignIn();
                        console.log('🔍 DEBUG: signInWithGoogle result:', result);
                        window.oauthDebugData.firebaseResult = result;
                        
                        // Check current user after authentication
                        if (window.firebaseAuth && window.firebaseAuth.currentUser) {
                            window.oauthDebugData.currentUser = {
                                uid: window.firebaseAuth.currentUser.uid,
                                email: window.firebaseAuth.currentUser.email,
                                displayName: window.firebaseAuth.currentUser.displayName,
                                providerData: window.firebaseAuth.currentUser.providerData.map(p => ({
                                    providerId: p.providerId,
                                    uid: p.uid
                                }))
                            };
                        }
                        
                        return result;
                    } catch (error) {
                        console.log('🔍 DEBUG: signInWithGoogle error:', error);
                        window.oauthDebugData.errors.push({type: 'oauth_error', message: error.message, code: error.code});
                        
                        if (error.code === 'auth/popup-blocked') {
                            window.oauthDebugData.popupBlocked = true;
                        } else if (error.code === 'auth/unauthorized-domain') {
                            window.oauthDebugData.domainError = true;
                        }
                        
                        throw error;
                    }
                };
            }
            
            // Monitor popup attempts
            const originalOpen = window.open;
            window.open = function(...args) {
                console.log('🔍 DEBUG: Popup attempt detected');
                window.oauthDebugData.popupAttempted = true;
                return originalOpen.apply(window, args);
            };
            
            console.log('🔍 DEBUG: Monitoring setup complete');
        """)
        
        print("   ✅ Monitoring setup complete")
        
        print("\\n2. 🔍 Pre-click analysis...")
        
        # Check function availability
        function_status = driver.execute_script("""
            return {
                signInWithGoogle: typeof signInWithGoogle,
                showStatus: typeof showStatus,
                showStep: typeof showStep,
                firebaseAuth: typeof window.firebaseAuth,
                GoogleAuthProvider: typeof window.GoogleAuthProvider,
                signInWithPopup: typeof window.signInWithPopup
            };
        """)
        
        print("   📋 Function Availability:")
        for func, status in function_status.items():
            icon = "✅" if status == "function" or status == "object" else "❌"
            print(f"      {func}: {status} {icon}")
        
        print("\\n3. 🖱️ Clicking Google OAuth button...")
        
        # Find and click the button
        google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
        print(f"   ✅ Found button: '{google_button.text}'")
        
        # Clear any existing status
        driver.execute_script("document.getElementById('statusContainer').innerHTML = '';")
        
        # Click the button
        google_button.click()
        
        print("   ⏳ Waiting for OAuth process (15 seconds)...")
        time.sleep(15)
        
        print("\\n4. 📊 Post-click analysis...")
        
        # Get debug data
        debug_data = driver.execute_script("return window.oauthDebugData || {};")
        
        print("   🔍 OAuth Function Execution:")
        print(f"      Function Called: {'✅' if debug_data.get('functionCalled') else '❌'} {debug_data.get('functionCalled')}")
        print(f"      Function Exists: {'✅' if debug_data.get('functionExists') else '❌'} {debug_data.get('functionExists')}")
        
        if debug_data.get('functionSource'):
            print(f"      Function Preview: {debug_data['functionSource'][:200]}...")
        
        print("   🔍 OAuth Process Results:")
        print(f"      Popup Attempted: {'✅' if debug_data.get('popupAttempted') else '❌'} {debug_data.get('popupAttempted')}")
        print(f"      Popup Blocked: {'⚠️ YES' if debug_data.get('popupBlocked') else '✅ NO'} {debug_data.get('popupBlocked')}")
        print(f"      Domain Error: {'⚠️ YES' if debug_data.get('domainError') else '✅ NO'} {debug_data.get('domainError')}")
        
        if debug_data.get('firebaseResult'):
            print(f"      Firebase Result: ✅ Received")
            print(f"         Type: {type(debug_data['firebaseResult'])}")
        else:
            print(f"      Firebase Result: ❌ None")
        
        if debug_data.get('currentUser'):
            user = debug_data['currentUser']
            print(f"      Current Firebase User: ✅ Found")
            print(f"         UID: {user.get('uid')}")
            print(f"         Email: {user.get('email')}")
            print(f"         Providers: {[p['providerId'] for p in user.get('providerData', [])]}")
        else:
            print(f"      Current Firebase User: ❌ None")
        
        # Show console logs
        if debug_data.get('logs'):
            print("\\n   📝 Console Logs:")
            for log in debug_data['logs'][-5:]:  # Show last 5 logs
                print(f"      {log['message']}")
        
        # Show errors
        if debug_data.get('errors'):
            print("\\n   🚨 Errors:")
            for error in debug_data['errors']:
                print(f"      {error['message']}")
                if 'code' in error:
                    print(f"         Code: {error['code']}")
        
        # Check page status
        status_text = driver.find_element(By.ID, "statusContainer").text.strip()
        success_visible = driver.execute_script("""
            const successStep = document.getElementById('success-step');
            return successStep && successStep.classList.contains('active');
        """)
        
        print(f"\\n   📋 Page Status After Click:")
        print(f"      Status Message: '{status_text}'")
        print(f"      Success Page Visible: {'✅' if success_visible else '❌'} {success_visible}")
        
        # Get browser console logs
        browser_logs = driver.get_log('browser')
        relevant_logs = [log for log in browser_logs if 'GOOGLE' in log['message'] or 'OAuth' in log['message'] or 'auth' in log['message']]
        
        if relevant_logs:
            print("\\n   🌐 Browser Console Logs:")
            for log in relevant_logs[-3:]:  # Show last 3 relevant logs
                print(f"      [{log['level']}] {log['message']}")
        
        # Determine success
        oauth_successful = (
            debug_data.get('functionCalled', False) and
            debug_data.get('currentUser') is not None and
            any(p['providerId'] == 'google.com' for p in debug_data.get('currentUser', {}).get('providerData', []))
        )
        
        print("\\n5. 🎯 DIAGNOSIS:")
        if oauth_successful:
            print("   ✅ SUCCESS: Google OAuth created Firebase account")
            print(f"      Firebase UID: {debug_data['currentUser']['uid']}")
            print("      🔥 CHECK FIREBASE CONSOLE FOR GOOGLE.COM PROVIDER")
            return True
        elif debug_data.get('popupBlocked'):
            print("   ⚠️ POPUP BLOCKED: Browser blocked OAuth popup")
            print("      💡 This is a browser security setting")
            return False
        elif debug_data.get('domainError'):
            print("   ⚠️ DOMAIN ERROR: callmechewy.github.io not authorized")
            print("      💡 Need to add domain to Google Cloud Console")
            return False
        elif not debug_data.get('functionCalled'):
            print("   ❌ FUNCTION NOT CALLED: signInWithGoogle not executing")
            print("      💡 JavaScript error or function not bound to button")
            return False
        else:
            print("   ❌ OAUTH FAILED: Unknown issue")
            print("      💡 Check console logs and Firebase configuration")
            return False
        
    except Exception as e:
        print(f"\\n❌ DEBUG FAILED: {str(e)}")
        return False
        
    finally:
        try:
            screenshot_path = "/home/herb/Desktop/OurLibrary/google_oauth_click_debug.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 Debug Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

if __name__ == "__main__":
    print("🎯 DEBUGGING GOOGLE OAUTH CLICK BEHAVIOR")
    print("Finding out exactly what happens when Google OAuth is clicked\\n")
    
    success = debug_google_oauth_click()
    
    print("\\n" + "=" * 60)
    print("🔍 GOOGLE OAUTH CLICK DEBUG RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS: Google OAuth is working and creates Firebase accounts!")
        print("   💯 The issue was resolved - check Firebase Console")
    else:
        print("🚨 ISSUE IDENTIFIED: Google OAuth has specific problems")
        print("   🔧 Need to fix the identified issues")
        
    print("\\n💡 This debug shows exactly what happens during OAuth click")