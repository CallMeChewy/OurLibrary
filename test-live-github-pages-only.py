#!/usr/bin/env python3
# File: test-live-github-pages-only.py
# Path: /home/herb/Desktop/OurLibrary/test-live-github-pages-only.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:10PM
# TEST: ONLY live GitHub Pages - NO LOCAL TESTING ALLOWED

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_live_github_pages_only():
    """Test ONLY the live GitHub Pages deployment - NO LOCAL TESTING"""
    
    print("🌐 TESTING LIVE GITHUB PAGES ONLY")
    print("=" * 60)
    print("RULE: NO LOCAL TESTING - ONLY REAL DEPLOYED SYSTEM")
    print("TESTING: https://callmechewy.github.io/OurLibrary/auth-demo.html")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-offline-load-stale-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        # FORCE fresh load from GitHub Pages
        timestamp = int(time.time())
        live_url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&live_test=true&no_cache={timestamp}"
        
        print(f"1. 🌐 Loading LIVE GitHub Pages: {live_url}")
        driver.get(live_url)
        
        # Clear all caches
        driver.execute_script("window.location.reload(true);")
        time.sleep(3)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(8)
        
        print("2. 📝 Filling registration on LIVE site...")
        test_email = f"live_github_test_{timestamp}@example.com"
        
        driver.find_element(By.ID, "fullName").send_keys("Live GitHub Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("live123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("live123456")
        
        print(f"   Test email: {test_email}")
        
        # Check what version of code is deployed
        deployment_check = driver.execute_script("""
            // Check if the fix is deployed by looking for the new verification logic
            const scriptContent = document.documentElement.innerHTML;
            return {
                hasOldFakeVerification: scriptContent.includes('For demo purposes, we\\'ll simulate verification'),
                hasNewRealVerification: scriptContent.includes('CRITICAL FIX: Real verification code check'),
                hasGenerateCode: scriptContent.includes('Math.random().toString(36).substr(2, 6)'),
                hasCodeValidation: scriptContent.includes('window.pendingVerificationCode')
            };
        """)
        
        print("\\n📊 DEPLOYMENT STATUS CHECK:")
        print(f"   Old fake verification present: {deployment_check['hasOldFakeVerification']}")
        print(f"   New real verification present: {deployment_check['hasNewRealVerification']}")
        print(f"   Code generation present: {deployment_check['hasGenerateCode']}")
        print(f"   Code validation present: {deployment_check['hasCodeValidation']}")
        
        if deployment_check['hasOldFakeVerification'] and not deployment_check['hasNewRealVerification']:
            print("\\n🚨 DEPLOYMENT NOT UPDATED YET")
            print("   GitHub Pages still serving old broken version")
            print("   Fix is not live - testing current deployed version")
        elif deployment_check['hasNewRealVerification']:
            print("\\n✅ FIX IS DEPLOYED")
            print("   GitHub Pages serving updated version with real verification")
        
        print("\\n3. 🚀 Submitting registration on LIVE site...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Monitor what happens
        time.sleep(10)
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            print("4. ✅ Reached verification step on LIVE site")
            
            # Check if real verification code was generated (if fix is deployed)
            real_code = driver.execute_script("return window.pendingVerificationCode || null;")
            if real_code:
                print(f"   🎉 FIX IS LIVE: Real verification code generated: {real_code}")
                fix_deployed = True
            else:
                print("   ⚠️ Fix not deployed yet - testing current broken version")
                fix_deployed = False
            
            # Test the LIVE system behavior
            print("\\n5. 🧪 Testing LIVE system behavior...")
            
            # Try fake code first
            print("   Testing fake code '999999'...")
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.clear()
            code_input.send_keys("999999")
            
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            time.sleep(8)
            
            # Check result
            firebase_user = driver.execute_script("""
                return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                    uid: window.firebaseAuth.currentUser.uid,
                    email: window.firebaseAuth.currentUser.email
                } : null;
            """)
            
            current_step = driver.execute_script("""
                const steps = ['registration', 'verification', 'success'];
                for (let step of steps) {
                    const element = document.getElementById(step + '-step');
                    if (element && element.classList.contains('active')) {
                        return step;
                    }
                }
                return 'unknown';
            """)
            
            status_message = driver.find_element(By.ID, "statusContainer").text.strip()
            
            print(f"      Current step: {current_step}")
            print(f"      Status: '{status_message}'")
            print(f"      Firebase account created: {bool(firebase_user)}")
            
            if firebase_user:
                print(f"      🚨 BROKEN: Firebase UID {firebase_user['uid']} created with fake code!")
                security_broken = True
            else:
                print(f"      ✅ FIXED: Fake code rejected!")
                security_broken = False
            
            # If we have a real code and the fix is deployed, test it
            if fix_deployed and real_code and not security_broken:
                print(f"\\n   Testing real code '{real_code}'...")
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys(real_code)
                
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                time.sleep(8)
                
                firebase_user_real = driver.execute_script("""
                    return window.firebaseAuth && window.firebaseAuth.currentUser ? {
                        uid: window.firebaseAuth.currentUser.uid,
                        email: window.firebaseAuth.currentUser.email
                    } : null;
                """)
                
                if firebase_user_real:
                    print(f"      ✅ SUCCESS: Real code created Firebase account {firebase_user_real['uid']}")
                    return "FIXED"
                else:
                    print(f"      ❌ ISSUE: Real code didn't work")
                    return "PARTIAL"
            
            if security_broken:
                return "BROKEN"
            elif fix_deployed:
                return "FIXED"
            else:
                return "AWAITING_DEPLOYMENT"
        
        else:
            print("❌ Never reached verification step on LIVE site")
            return "BROKEN"
        
    except Exception as e:
        print(f"\\n❌ LIVE test error: {e}")
        return "ERROR"
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/live_github_test.png")
        driver.quit()

if __name__ == "__main__":
    print("🌐 TESTING LIVE GITHUB PAGES DEPLOYMENT ONLY")
    print("NO LOCAL TESTING - NO CHEATING - REAL SOURCES ONLY\\n")
    
    result = test_live_github_pages_only()
    
    print(f"\\n🎯 LIVE GITHUB PAGES TEST RESULT: {result}")
    
    if result == "BROKEN":
        print("🚨 LIVE SYSTEM IS BROKEN - Security vulnerability confirmed")
    elif result == "AWAITING_DEPLOYMENT":
        print("⏳ Fix implemented but GitHub Pages not updated yet")
    elif result == "FIXED":
        print("✅ LIVE SYSTEM FIXED - Security vulnerability patched")
    elif result == "PARTIAL":
        print("⚠️ Partially working - needs more investigation")
    else:
        print("❌ Unable to test live system")