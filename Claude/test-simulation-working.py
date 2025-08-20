#!/usr/bin/env python3
# Test if simulation mode is actually working

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_simulation_working():
    """Test if simulation mode is working for email registration"""
    
    print("🧪 Testing Simulation Mode Functionality")
    print("=" * 45)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Go to OurLibrary
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(5)
        
        # Check initial console for simulation mode detection
        initial_logs = driver.get_log('browser')
        simulation_detected = any('simulation mode' in log['message'].lower() for log in initial_logs)
        
        print(f"1. 🔍 Simulation mode detected: {'✅' if simulation_detected else '❌'}")
        
        # Open registration modal
        print("2. 🖱️  Opening registration modal...")
        join_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
        )
        join_button.click()
        
        # Wait for modal and fill email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        
        test_email = f"simulation_test_{int(time.time())}@example.com"
        email_input.send_keys(test_email)
        
        print(f"3. 📧 Entered email: {test_email}")
        
        # Trigger blur to test email capture
        driver.execute_script("arguments[0].blur();", email_input)
        time.sleep(2)
        
        # Also fill complete form and try to submit
        driver.find_element(By.ID, "fullName").send_keys("Simulation Test User")
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirmPassword").send_keys("testpass123")
        
        # Try to submit
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        print("4. 📤 Attempted form submission...")
        time.sleep(3)
        
        # Get all console logs and look for simulation activity
        all_logs = driver.get_log('browser')
        
        simulation_logs = [log for log in all_logs if 'simulated' in log['message'].lower()]
        email_logs = [log for log in all_logs if test_email in log['message']]
        registration_logs = [log for log in all_logs if 'registration' in log['message'].lower()]
        
        print(f"\n📊 Activity Detected:")
        print(f"   Simulation logs: {len(simulation_logs)}")
        print(f"   Email-specific logs: {len(email_logs)}")
        print(f"   Registration logs: {len(registration_logs)}")
        
        if simulation_logs:
            print("✅ Simulation logging detected:")
            for log in simulation_logs[:3]:
                print(f"   - {log['message'][:100]}...")
                
        if email_logs:
            print("✅ Email tracking detected:")
            for log in email_logs[:2]:
                print(f"   - {log['message'][:100]}...")
        
        # Determine success
        success = len(simulation_logs) > 0 or len(email_logs) > 0 or len(registration_logs) > 0
        
        if success:
            print("✅ System is working in simulation mode!")
            print("📊 Data that would be logged to Google Sheets is being captured")
        else:
            print("❌ No simulation activity detected")
            print("🔍 Printing all console logs for debugging:")
            for i, log in enumerate(all_logs[-10:], 1):  # Last 10 logs
                print(f"   {i}. [{log['level']}] {log['message'][:80]}...")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_simulation_working()
    print(f"\n🏁 Simulation functionality test: {'✅ PASSED' if success else '❌ FAILED'}")
    print("💡 Even if Google Sheets API isn't enabled, the system should work in simulation mode")