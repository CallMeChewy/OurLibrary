#!/usr/bin/env python3
# File: detailed-console-debug.py
# Path: /home/herb/Desktop/OurLibrary/detailed-console-debug.py
# Standard: AIDEV-PascalCase-2.3  
# Created: 2025-08-20
# Last Modified: 2025-08-20 03:10PM
# Detailed console debugging to find JavaScript issues

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def detailed_console_debug():
    """Get detailed console information from the live system"""
    
    print("🔍 DETAILED CONSOLE DEBUGGING")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        print("1. 🌐 Loading live page...")
        cache_buster = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={cache_buster}"
        driver.get(url)
        time.sleep(15)
        
        print("2. 📋 Getting ALL console logs...")
        
        # Get all browser logs
        logs = driver.get_log('browser')
        
        print(f"   Total console entries: {len(logs)}")
        
        if logs:
            print("   📝 ALL CONSOLE MESSAGES:")
            for i, log in enumerate(logs):
                level = log['level']
                message = log['message']
                timestamp = log['timestamp']
                
                if level == 'SEVERE':
                    icon = "🚨"
                elif level == 'WARNING': 
                    icon = "⚠️"
                elif level == 'INFO':
                    icon = "ℹ️"
                else:
                    icon = "📝"
                
                print(f"      {i+1}. {icon} [{level}] {message}")
        
        print("\\n3. 🧪 Testing function definitions...")
        
        # Test individual function existence
        function_check = driver.execute_script("""
            const results = {
                windowKeys: Object.keys(window).filter(key => 
                    key.includes('sign') || 
                    key.includes('show') || 
                    key.includes('start') ||
                    key.includes('firebase') ||
                    key.includes('google')
                ),
                signInWithGoogle: {
                    exists: typeof window.signInWithGoogle,
                    callable: typeof window.signInWithGoogle === 'function'
                },
                startEmailRegistration: {
                    exists: typeof window.startEmailRegistration,
                    callable: typeof window.startEmailRegistration === 'function'
                },
                showStatus: {
                    exists: typeof window.showStatus,
                    callable: typeof window.showStatus === 'function'  
                },
                showStep: {
                    exists: typeof window.showStep,
                    callable: typeof window.showStep === 'function'
                },
                firebaseReady: window.firebaseReady || false,
                firebaseAuth: typeof window.firebaseAuth,
                scriptErrors: window.scriptErrors || []
            };
            
            // Try to get the source of signInWithGoogle if it exists
            if (typeof window.signInWithGoogle === 'function') {
                try {
                    results.signInWithGoogleSource = window.signInWithGoogle.toString().substring(0, 200) + '...';
                } catch(e) {
                    results.signInWithGoogleSource = 'Error getting source: ' + e.message;
                }
            }
            
            return results;
        """)
        
        print("   🔍 Function Analysis Results:")
        print(f"      Window keys with auth/show/firebase: {function_check['windowKeys']}")
        print(f"      signInWithGoogle: exists={function_check['signInWithGoogle']['exists']}, callable={function_check['signInWithGoogle']['callable']}")
        print(f"      startEmailRegistration: exists={function_check['startEmailRegistration']['exists']}, callable={function_check['startEmailRegistration']['callable']}")
        print(f"      showStatus: exists={function_check['showStatus']['exists']}, callable={function_check['showStatus']['callable']}")
        print(f"      showStep: exists={function_check['showStep']['exists']}, callable={function_check['showStep']['callable']}")
        print(f"      firebaseReady: {function_check['firebaseReady']}")
        print(f"      firebaseAuth type: {function_check['firebaseAuth']}")
        
        if 'signInWithGoogleSource' in function_check:
            print(f"      signInWithGoogle source preview: {function_check['signInWithGoogleSource']}")
        
        print("\\n4. 🎯 Manual function call test...")
        
        # Try to call signInWithGoogle manually
        manual_call_result = driver.execute_script("""
            try {
                if (typeof window.signInWithGoogle === 'function') {
                    console.log('🧪 MANUAL TEST: Calling signInWithGoogle...');
                    
                    // Try to call it
                    const result = window.signInWithGoogle();
                    
                    return {
                        success: true,
                        result: typeof result,
                        message: 'Function called successfully'
                    };
                } else {
                    return {
                        success: false,
                        result: null,
                        message: 'signInWithGoogle function not found'
                    };
                }
            } catch (error) {
                return {
                    success: false,
                    result: null,
                    message: 'Error calling function: ' + error.message
                };
            }
        """)
        
        print(f"   Manual call result: {manual_call_result}")
        
        # Check page elements
        print("\\n5. 🔍 Page element check...")
        
        try:
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
            print(f"   ✅ Google button found: '{google_button.text}'")
            print(f"      Visible: {google_button.is_displayed()}")
            print(f"      Enabled: {google_button.is_enabled()}")
            print(f"      onclick attribute: {google_button.get_attribute('onclick')}")
            
        except Exception as e:
            print(f"   ❌ Google button not found: {e}")
        
        print("\\n6. 🚨 FINAL DIAGNOSIS:")
        
        severe_errors = [log for log in logs if log['level'] == 'SEVERE']
        if severe_errors:
            print("   🚨 CRITICAL JAVASCRIPT ERRORS BLOCKING EXECUTION:")
            for error in severe_errors:
                print(f"      - {error['message']}")
        else:
            print("   ✅ No critical JavaScript errors found")
            
        if not function_check['signInWithGoogle']['callable']:
            print("   ❌ signInWithGoogle function is not available/callable")
        else:
            print("   ✅ signInWithGoogle function is available and callable")
            
        if not function_check['showStatus']['callable']:
            print("   ❌ showStatus function is not available - UI updates will fail")
        else:
            print("   ✅ showStatus function is available")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    detailed_console_debug()