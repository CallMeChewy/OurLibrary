#!/usr/bin/env python3
# File: test-fresh-browser-simulation.py
# Path: /home/herb/Desktop/OurLibrary/test-fresh-browser-simulation.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:30PM
# TEST: Simulate fresh browser like user's Edge browser

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_fresh_browser_simulation():
    """Simulate exactly what user experienced in fresh Edge browser"""
    
    print("🌐 SIMULATING FRESH EDGE BROWSER EXPERIENCE")
    print("=" * 60)
    print("Testing: auth-demo.html with completely fresh session")
    print("Expected: Should see verification code clearly or reproduce user's error")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # Simulate fresh browser - no cache, no history
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-offline-load-stale-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        # Load the exact URL - auth-demo.html
        url = "https://callmechewy.github.io/OurLibrary/auth-demo.html"
        
        print(f"1. 🌐 Loading auth-demo.html (fresh browser): {url}")
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(8)
        
        # Verify we're on the right page
        page_title = driver.title
        back_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'Back to SMTP Test')]")
        
        print(f"   Page title: {page_title}")
        print(f"   Has 'Back to SMTP Test' link: {len(back_link) > 0}")
        
        print("2. 📝 Filling registration form...")
        test_email = "FayBowers@gmail.com"  # Use similar email format as user
        
        driver.find_element(By.ID, "fullName").send_keys("Fresh Browser Test")
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "password").send_keys("test123456")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123456")
        
        print(f"   Email: {test_email}")
        
        print("3. 🚀 Submitting registration...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Wait longer to see all status messages
        print("4. 👀 Monitoring status messages and code display...")
        for i in range(15):
            time.sleep(1)
            
            # Check current step
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
            
            # Check status message
            status_text = driver.find_element(By.ID, "statusContainer").text.strip()
            
            # Check email display area
            email_display = driver.find_element(By.ID, "verificationEmail").text.strip()
            
            # Check for generated code
            real_code = driver.execute_script("return window.pendingVerificationCode || null;")
            
            print(f"   [{i+1}s] Step: {current_step}")
            print(f"   [{i+1}s] Status: '{status_text}'")
            print(f"   [{i+1}s] Email display: '{email_display}'")
            print(f"   [{i+1}s] Generated code: {real_code}")
            
            if current_step == 'verification':
                print(f"   ✅ Reached verification step")
                break
        
        # Take screenshot of verification step
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/fresh_browser_verification.png")
        
        if current_step == 'verification':
            print("\\n5. 🧪 Testing verification...")
            
            # Check what code is actually available
            final_code = driver.execute_script("return window.pendingVerificationCode || null;")
            final_status = driver.find_element(By.ID, "statusContainer").text.strip()
            final_email_display = driver.find_element(By.ID, "verificationEmail").text.strip()
            
            print(f"   Final generated code: {final_code}")
            print(f"   Final status message: '{final_status}'")
            print(f"   Final email display: '{final_email_display}'")
            
            # Check if user can see the code anywhere
            code_visible_in_status = final_code and final_code in final_status
            code_visible_in_email = final_code and final_code in final_email_display
            
            print(f"   Code visible in status: {code_visible_in_status}")
            print(f"   Code visible in email display: {code_visible_in_email}")
            
            if final_code and (code_visible_in_status or code_visible_in_email):
                print(f"\\n   🧪 Testing REAL code '{final_code}'...")
                
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.clear()
                code_input.send_keys(final_code)
                
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                time.sleep(8)
                
                result_step = driver.execute_script("""
                    const steps = ['registration', 'verification', 'success'];
                    for (let step of steps) {
                        const element = document.getElementById(step + '-step');
                        if (element && element.classList.contains('active')) {
                            return step;
                        }
                    }
                    return 'unknown';
                """)
                
                result_status = driver.find_element(By.ID, "statusContainer").text.strip()
                
                print(f"   Result step: {result_step}")
                print(f"   Result status: '{result_status}'")
                
                if 'failed' in result_status.lower():
                    print("   🚨 REPRODUCED USER'S ERROR: Verification failed with real code!")
                    return "USER_ERROR_REPRODUCED"
                elif result_step == 'success':
                    print("   ✅ Real code worked")
                    return "WORKING"
                else:
                    print("   🤔 Unclear result")
                    return "UNCLEAR"
            else:
                print("   🚨 CODE NOT VISIBLE TO USER!")
                print("   This explains why user entered random code '9LX98W'")
                return "CODE_NOT_VISIBLE"
        
        return "DID_NOT_REACH_VERIFICATION"
        
    except Exception as e:
        print(f"\\n❌ Test error: {e}")
        return "TEST_ERROR"
        
    finally:
        driver.quit()

if __name__ == "__main__":
    result = test_fresh_browser_simulation()
    
    print(f"\\n🎯 FRESH BROWSER TEST RESULT: {result}")
    
    if result == "USER_ERROR_REPRODUCED":
        print("\\n🚨 CONFIRMED: Real verification codes are being rejected")
        print("   The system is still broken even for correct codes")
    elif result == "CODE_NOT_VISIBLE":
        print("\\n🚨 CONFIRMED: Users cannot see the verification code")
        print("   This is why user entered random code '9LX98W'")
    elif result == "WORKING":
        print("\\n🤔 System appears to work in automated test")
        print("   But user experienced failure - environment difference")
    else:
        print(f"\\n🔍 Other issue detected: {result}")