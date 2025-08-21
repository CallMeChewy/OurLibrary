#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_bypass_verification():
    """Debug what's happening with bypass verification"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Simulate the bypass URL
        test_email = f"debug_{int(time.time())}@example.com"
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?email={test_email}&name=Debug%20Test&password=debug123"
        
        print(f"🧪 DEBUGGING BYPASS VERIFICATION")
        print(f"URL: {url}")
        
        driver.get(url)
        time.sleep(8)  # Wait for bypass to execute
        
        # Check current state
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
        
        # Check verification details
        verification_details = driver.execute_script("""
            return {
                pendingCode: window.pendingVerificationCode,
                pendingEmail: window.pendingVerificationEmail,
                userRegistrationData: window.userRegistrationData,
                bypassExecuted: window.bypassToVerification,
                currentStep: document.querySelector('.step.active')?.textContent || 'none'
            };
        """)
        
        print(f"Current step: {current_step}")
        print(f"Pending code: {verification_details['pendingCode']}")
        print(f"Pending email: {verification_details['pendingEmail']}")
        print(f"User data: {verification_details['userRegistrationData']}")
        print(f"Bypass executed: {verification_details['bypassExecuted']}")
        
        if current_step == 'verification' and verification_details['pendingCode']:
            print(f"✅ Bypass worked - testing verification with real code")
            
            # Enter the real code
            code_input = driver.find_element(By.ID, "verificationCode")
            code_input.clear()
            code_input.send_keys(verification_details['pendingCode'])
            
            # Submit
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
            verify_button.click()
            
            time.sleep(5)
            
            # Check result
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
            
            status_message = driver.find_element(By.ID, "statusContainer").text
            
            print(f"Result step: {result_step}")
            print(f"Status: {status_message}")
            
            if 'failed' in status_message.lower():
                print("🚨 SAME VERIFICATION FAILURE!")
                return "VERIFICATION_FAILED"
            elif result_step == 'success':
                print("✅ Verification worked!")
                return "SUCCESS"
                
        else:
            print("❌ Bypass didn't work properly")
            return "BYPASS_FAILED"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return "ERROR"
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/bypass_debug.png")
        driver.quit()

if __name__ == "__main__":
    result = debug_bypass_verification()
    print(f"\n🎯 DEBUG RESULT: {result}")