#!/usr/bin/env python3
# Test if simulation mode is working

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_simulation_mode():
    """Test if simulation mode is working"""
    
    print("🧪 Testing Simulation Mode")
    print("=" * 40)
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Go to landing page
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(5)  # Wait for all scripts to load
        
        print("1. 🔍 Checking console for simulation mode messages...")
        
        # Get all console logs
        console_logs = driver.get_log('browser')
        
        # Print ALL console messages for debugging
        print("🔍 ALL Console Messages:")
        for i, log in enumerate(console_logs):
            print(f"   {i+1}. [{log['level']}] {log['message'][:120]}...")
        
        # Look for simulation mode indicators
        simulation_messages = [log for log in console_logs if 'simulation' in log['message'].lower()]
        oauth_errors = [log for log in console_logs if 'oauth' in log['message'].lower() and log['level'] == 'SEVERE']
        warning_messages = [log for log in console_logs if 'placeholder' in log['message'].lower()]
        
        print(f"\nFound {len(simulation_messages)} simulation mode messages")
        print(f"Found {len(oauth_errors)} OAuth errors")
        print(f"Found {len(warning_messages)} placeholder warnings")
        
        if simulation_messages:
            print("✅ Simulation mode messages found:")
            for msg in simulation_messages[:3]:
                print(f"   - {msg['message'][:100]}...")
        
        if oauth_errors:
            print("❌ OAuth errors still present:")
            for error in oauth_errors[:2]:
                print(f"   - {error['message'][:100]}...")
        
        # Test email capture
        print("\n2. 🧪 Testing email capture...")
        
        # Open modal
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        join_button.click()
        time.sleep(2)
        
        # Get email input and trigger blur
        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys("test@simulation.com")
        driver.execute_script("arguments[0].blur();", email_input)
        time.sleep(3)
        
        # Check for new logs after email interaction
        all_new_logs = driver.get_log('browser')
        
        print(f"\n🔍 ALL Console Messages After Email Input ({len(all_new_logs)} total):")
        for i, log in enumerate(all_new_logs):
            print(f"   {i+1}. [{log['level']}] {log['message'][:120]}...")
        
        simulation_activity = [log for log in all_new_logs if 'simulated' in log['message'].lower()]
        email_activity = [log for log in all_new_logs if 'email' in log['message'].lower()]
        sheets_activity = [log for log in all_new_logs if 'sheets' in log['message'].lower()]
        
        print(f"\nActivity Analysis:")
        print(f"   Simulation messages: {len(simulation_activity)}")
        print(f"   Email-related messages: {len(email_activity)}")
        print(f"   Sheets-related messages: {len(sheets_activity)}")
        
        if simulation_activity:
            print("✅ Simulation activity detected:")
            for activity in simulation_activity[:2]:
                print(f"   - {activity['message'][:100]}...")
            return True
        elif email_activity or sheets_activity:
            print("⚠️ Email/Sheets activity detected but not simulation:")
            for activity in (email_activity + sheets_activity)[:3]:
                print(f"   - {activity['message'][:100]}...")
            return True
        else:
            print("❌ No relevant activity detected")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_simulation_mode()
    print(f"\n🏁 Simulation mode test: {'✅ PASSED' if success else '❌ FAILED'}")