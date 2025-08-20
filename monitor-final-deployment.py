#!/usr/bin/env python3
# File: monitor-final-deployment.py
# Path: /home/herb/Desktop/OurLibrary/monitor-final-deployment.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:35PM
# MONITOR: Final deployment until verification codes are visible

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_code_visibility():
    """Test if verification codes are now visible to users"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&final_test=true"
        
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(5)
        
        # Fill registration
        test_email = f"final_test_{timestamp}@example.com"
        driver.find_element(By.ID, "fullName").send_keys("Final Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("finaltest123")
        driver.find_element(By.ID, "confirmPassword").send_keys("finaltest123")
        
        # Submit
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        time.sleep(8)
        
        # Check verification step
        verification_active = driver.execute_script("""
            const verifyStep = document.getElementById('verification-step');
            return verifyStep && verifyStep.classList.contains('active');
        """)
        
        if verification_active:
            # Check for code visibility
            real_code = driver.execute_script("return window.pendingVerificationCode || null;")
            status_text = driver.find_element(By.ID, "statusContainer").text.strip()
            email_display = driver.execute_script("return document.getElementById('verificationEmail').innerHTML;")
            
            return {
                "status": "SUCCESS",
                "generated_code": real_code,
                "status_message": status_text,
                "email_display": email_display,
                "code_in_status": real_code and real_code in status_text,
                "code_in_email": real_code and real_code in email_display,
                "visible_to_user": (real_code and real_code in status_text) or (real_code and real_code in email_display)
            }
        else:
            return {"status": "FAILED", "error": "Never reached verification step"}
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/final_visibility_test.png")
        driver.quit()

def monitor_final_deployment():
    """Monitor final deployment until code visibility is fixed"""
    
    print("🎯 MONITORING FINAL DEPLOYMENT - CODE VISIBILITY FIX")
    print("=" * 70)
    print("OBJECTIVE: Ensure verification codes are visible to users")
    print("LATEST FIX: Always display codes, enhanced styling")
    print("=" * 70)
    
    attempt = 0
    max_attempts = 15
    
    while attempt < max_attempts:
        attempt += 1
        current_time = time.strftime('%H:%M:%S')
        
        print(f"\n🔍 VISIBILITY TEST {attempt}/15 - {current_time}")
        
        result = test_code_visibility()
        
        if result["status"] == "SUCCESS":
            print("   📊 TEST RESULTS:")
            print(f"      Generated code: {result['generated_code']}")
            print(f"      Status message: '{result['status_message'][:100]}...'")
            print(f"      Email display contains HTML: {len(result['email_display']) > 50}")
            print(f"      Code visible in status: {result['code_in_status']}")
            print(f"      Code visible in email: {result['code_in_email']}")
            print(f"      Overall visible to user: {result['visible_to_user']}")
            
            if result['visible_to_user']:
                print("\n   ✅ SUCCESS! VERIFICATION CODES ARE NOW VISIBLE!")
                print("      Users can see the verification code")
                return "FIXED"
            else:
                print("\n   ⏳ Still not visible, waiting for deployment...")
        else:
            print(f"   ❌ Test failed: {result.get('error', 'Unknown error')}")
        
        if attempt < max_attempts:
            print(f"   ⏳ Waiting 30 seconds before next test...")
            time.sleep(30)
    
    print("\n❌ MONITORING TIMEOUT")
    return "TIMEOUT"

if __name__ == "__main__":
    result = monitor_final_deployment()
    
    print(f"\n🎯 FINAL DEPLOYMENT RESULT: {result}")
    
    if result == "FIXED":
        print("\n🏆 MISSION ACCOMPLISHED!")
        print("   ✅ Verification codes are now visible to users")
        print("   ✅ User should be able to see and enter correct codes")
        print("   ✅ Registration system fully functional")
    else:
        print(f"\n🚨 Need additional intervention: {result}")