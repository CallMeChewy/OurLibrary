#!/usr/bin/env python3
# File: diagnose-oauth-error.py
# Path: /home/herb/Desktop/OurLibrary/diagnose-oauth-error.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:55PM
# DIAGNOSE EXACT OAUTH ERROR

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def diagnose_oauth_error():
    """Diagnose the exact OAuth error"""
    
    print("🔍 DIAGNOSING EXACT GOOGLE OAUTH ERROR")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    
    try:
        print("\\n1. 🌐 Loading page...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&diagnose=true"
        driver.get(url)
        time.sleep(15)
        
        print("\\n2. 🔧 Setting up detailed error capture...")
        
        # Enhanced error capture
        driver.execute_script("""
            window.oauthDiagnosis = {
                errors: [],
                networkErrors: [],
                popupErrors: [],
                detailedLog: []
            };
            
            // Capture all console errors
            const originalError = console.error;
            console.error = function(...args) {
                const message = args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                ).join(' ');
                
                window.oauthDiagnosis.errors.push({
                    message: message,
                    timestamp: Date.now(),
                    stack: args.find(arg => arg && arg.stack) ? arg.stack : null
                });
                
                originalError.apply(console, args);
            };
            
            // Override signInWithPopup to capture detailed errors
            if (window.signInWithPopup) {
                const original = window.signInWithPopup;
                window.signInWithPopup = async function(auth, provider) {
                    window.oauthDiagnosis.detailedLog.push('signInWithPopup called');
                    
                    try {
                        const result = await original(auth, provider);
                        window.oauthDiagnosis.detailedLog.push('signInWithPopup succeeded: ' + result.user.uid);
                        return result;
                    } catch (error) {
                        window.oauthDiagnosis.detailedLog.push('signInWithPopup failed: ' + error.code + ' - ' + error.message);
                        
                        // Capture specific OAuth error details
                        window.oauthDiagnosis.errors.push({
                            type: 'oauth_error',
                            code: error.code,
                            message: error.message,
                            customData: error.customData,
                            timestamp: Date.now()
                        });
                        
                        throw error;
                    }
                };
            }
            
            // Capture popup errors
            const originalOpen = window.open;
            window.open = function(...args) {
                window.oauthDiagnosis.detailedLog.push('Popup attempted: ' + args[0]);
                try {
                    const popup = originalOpen.apply(window, args);
                    if (!popup) {
                        window.oauthDiagnosis.popupErrors.push('Popup blocked by browser');
                    }
                    return popup;
                } catch (error) {
                    window.oauthDiagnosis.popupErrors.push('Popup error: ' + error.message);
                    throw error;
                }
            };
            
            console.log('🔍 Enhanced OAuth error diagnosis setup complete');
        """)
        
        print("   ✅ Error capture setup complete")
        
        print("\\n3. 🖱️ Clicking Google OAuth to capture error...")
        
        # Find and click Google OAuth button
        google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
        google_button.click()
        
        print("   ⏳ Waiting to capture OAuth error details...")
        time.sleep(10)
        
        # Get diagnostic results
        diagnosis = driver.execute_script("return window.oauthDiagnosis || {};")
        
        print("\\n4. 🚨 OAUTH ERROR DIAGNOSIS:")
        
        if diagnosis.get('detailedLog'):
            print("   📋 OAuth Process Log:")
            for log in diagnosis['detailedLog']:
                print(f"      • {log}")
        
        if diagnosis.get('errors'):
            print("   🚨 OAuth Errors Found:")
            for error in diagnosis['errors']:
                print(f"      🔸 Type: {error.get('type', 'general')}")
                print(f"      🔸 Code: {error.get('code', 'N/A')}")
                print(f"      🔸 Message: {error.get('message', 'N/A')}")
                if error.get('customData'):
                    print(f"      🔸 Details: {error.get('customData')}")
                print()
        
        if diagnosis.get('popupErrors'):
            print("   🪟 Popup Errors:")
            for error in diagnosis['popupErrors']:
                print(f"      • {error}")
        
        # Get browser console logs for additional context
        browser_logs = driver.get_log('browser')
        oauth_logs = [log for log in browser_logs if 'auth' in log['message'].lower() or 'oauth' in log['message'].lower()]
        
        if oauth_logs:
            print("   📺 Browser Console OAuth Logs:")
            for log in oauth_logs[-5:]:
                print(f"      [{log['level']}] {log['message']}")
        
        # Provide specific solutions based on errors found
        print("\\n5. 💡 SOLUTION BASED ON ERROR:")
        
        has_domain_error = any('unauthorized-domain' in str(error.get('code', '')) for error in diagnosis.get('errors', []))
        has_popup_error = bool(diagnosis.get('popupErrors'))
        has_network_error = any('network' in str(error.get('message', '')).lower() for error in diagnosis.get('errors', []))
        
        if has_domain_error:
            print("   🎯 DOMAIN AUTHORIZATION ISSUE (Most Likely):")
            print("      1. Go to Google Cloud Console")
            print("      2. APIs & Services > Credentials")
            print("      3. Edit OAuth 2.0 Client ID")
            print("      4. Add 'https://callmechewy.github.io' to Authorized origins")
            print("      5. Add 'https://callmechewy.github.io/OurLibrary/auth-demo.html' to Redirect URIs")
            print("      6. Save and wait 5-10 minutes")
            
        elif has_popup_error:
            print("   🪟 POPUP BLOCKING ISSUE:")
            print("      1. Allow popups for callmechewy.github.io")
            print("      2. Or try incognito mode")
            print("      3. Or use redirect flow instead of popup")
            
        elif has_network_error:
            print("   🌐 NETWORK/CONFIGURATION ISSUE:")
            print("      1. Check Firebase console OAuth configuration")
            print("      2. Verify client ID is correct")
            print("      3. Ensure Google provider is enabled")
            
        else:
            print("   ❓ GENERAL OAUTH CONFIGURATION:")
            print("      1. Check Google Cloud Console OAuth settings")
            print("      2. Verify Firebase Authentication provider")
            print("      3. Ensure domain authorization is complete")
        
        return diagnosis
        
    except Exception as e:
        print(f"\\n❌ DIAGNOSIS FAILED: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🎯 DIAGNOSING GOOGLE OAUTH ERROR")
    print("This will show you the exact error and solution\\n")
    
    diagnosis = diagnose_oauth_error()
    
    print("\\n" + "=" * 60)
    print("🔧 OAUTH FIX SUMMARY")
    print("=" * 60)
    
    if diagnosis and diagnosis.get('errors'):
        print("✅ OAuth error captured and diagnosed")
        print("📋 Follow the solution steps above to fix the issue")
    else:
        print("⚠️  No specific OAuth error captured")
        print("💡 Most likely issue: Domain not authorized in Google Cloud Console")
    
    print("\\n🎯 MOST COMMON SOLUTION:")
    print("   Add callmechewy.github.io to Google Cloud Console OAuth settings")