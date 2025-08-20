#!/usr/bin/env python3
# File: monitor-deployment-and-fix.py
# Path: /home/herb/Desktop/OurLibrary/monitor-deployment-and-fix.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:15PM
# MONITOR: GitHub Pages deployment and fix until working

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def check_deployment_status():
    """Check if GitHub Pages has deployed the fix"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&deployment_check=true"
        
        driver.get(url)
        time.sleep(5)
        
        # Check deployment status
        deployment_status = driver.execute_script("""
            const html = document.documentElement.innerHTML;
            return {
                oldFakeCode: html.includes('For demo purposes, we\\'ll simulate verification'),
                newRealCode: html.includes('CRITICAL FIX: Real verification code check'),
                codeGeneration: html.includes('Math.random().toString(36).substr(2, 6)'),
                timestamp: new Date().toISOString()
            };
        """)
        
        return deployment_status
        
    except Exception as e:
        print(f"Deployment check error: {e}")
        return None
        
    finally:
        driver.quit()

def test_security_vulnerability():
    """Test if the security vulnerability still exists"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&security_test=true"
        
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(5)
        
        # Fill registration
        test_email = f"security_test_{timestamp}@example.com"
        driver.find_element(By.ID, "fullName").send_keys("Security Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("test123")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123")
        
        # Submit
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(8)
        
        # Check verification step
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if not verification_active:
            return {"status": "FAILED", "error": "Never reached verification step"}
        
        # Try fake code "999999"
        code_input = driver.find_element(By.ID, "verificationCode")
        code_input.clear()
        code_input.send_keys("999999")
        
        verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
        verify_button.click()
        time.sleep(8)
        
        # Check if Firebase account was created
        firebase_result = driver.execute_script("""
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
        
        return {
            "status": "COMPLETED",
            "firebase_created": bool(firebase_result),
            "firebase_uid": firebase_result["uid"] if firebase_result else None,
            "current_step": current_step,
            "vulnerability_exists": bool(firebase_result),
            "test_email": test_email
        }
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
        
    finally:
        driver.quit()

def monitor_and_fix():
    """Monitor deployment and fix until working"""
    
    print("🔄 MONITORING GITHUB PAGES DEPLOYMENT AND FIXING UNTIL WORKING")
    print("=" * 80)
    print("OBJECTIVE: Fix the security vulnerability completely")
    print("RULE: No stopping until verification system works correctly")
    print("=" * 80)
    
    attempt = 0
    max_attempts = 60  # 30 minutes of monitoring
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\\n🔍 ATTEMPT {attempt}/60 - {time.strftime('%H:%M:%S')}")
        
        # Check deployment status
        print("   Checking GitHub Pages deployment...")
        deployment = check_deployment_status()
        
        if deployment:
            print(f"   Old fake code present: {deployment['oldFakeCode']}")
            print(f"   New real code present: {deployment['newRealCode']}")
            print(f"   Code generation present: {deployment['codeGeneration']}")
            
            if deployment['newRealCode'] and deployment['codeGeneration']:
                print("   ✅ FIX APPEARS TO BE DEPLOYED!")
            else:
                print("   ⏳ Fix not deployed yet...")
        
        # Test security vulnerability
        print("   Testing security vulnerability...")
        security_test = test_security_vulnerability()
        
        if security_test["status"] == "COMPLETED":
            if security_test["vulnerability_exists"]:
                print(f"   🚨 VULNERABILITY STILL EXISTS:")
                print(f"      Firebase UID created: {security_test['firebase_uid']}")
                print(f"      With fake code '999999'")
                print(f"      Current step: {security_test['current_step']}")
            else:
                print(f"   ✅ VULNERABILITY FIXED!")
                print(f"      Fake code '999999' was rejected")
                print(f"      No Firebase account created")
                print(f"      Current step: {security_test['current_step']}")
                
                print("\\n🎉 SUCCESS! SECURITY VULNERABILITY FIXED!")
                print("   ✅ Fake verification codes are rejected")
                print("   ✅ Firebase accounts not created without real verification")
                return True
        else:
            print(f"   ❌ Test failed: {security_test.get('error', 'Unknown error')}")
        
        # Wait before next attempt
        if attempt < max_attempts:
            print(f"   ⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("\\n❌ MONITORING TIMEOUT")
    print("   Reached maximum attempts without fixing the vulnerability")
    return False

if __name__ == "__main__":
    success = monitor_and_fix()
    
    if success:
        print("\\n🏆 MISSION ACCOMPLISHED!")
        print("   Security vulnerability has been fixed")
        print("   System now requires real email verification")
    else:
        print("\\n🚨 MISSION FAILED")
        print("   Unable to fix security vulnerability within time limit")
        print("   Manual intervention required")