#!/usr/bin/env python3
# File: google-oauth-button-test.py
# Path: /home/herb/Desktop/OurLibrary/google-oauth-button-test.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 03:45PM
# Test specifically for Google OAuth button

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_google_oauth_button():
    """Test specifically for Google OAuth button and functionality"""
    
    print("🔍 TESTING GOOGLE OAUTH BUTTON SPECIFICALLY")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    
    try:
        print("1. 🌐 Loading page...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        driver.get(url)
        time.sleep(10)
        
        print("2. 🔍 Finding ALL buttons...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   Found {len(all_buttons)} total buttons")
        
        for i, button in enumerate(all_buttons):
            try:
                text = button.text.strip()
                visible = button.is_displayed()
                enabled = button.is_enabled()
                print(f"   Button {i+1}: '{text}' | Visible: {visible} | Enabled: {enabled}")
                
                if 'google' in text.lower():
                    print(f"      🎯 GOOGLE BUTTON FOUND!")
                    
                    # Try clicking it
                    print("      🖱️ CLICKING GOOGLE BUTTON...")
                    button.click()
                    time.sleep(8)
                    
                    # Check result
                    success_visible = driver.execute_script("""
                        const successStep = document.getElementById('success-step');
                        return successStep && successStep.classList.contains('active');
                    """)
                    
                    status_text = driver.find_element(By.ID, "statusContainer").text.strip()
                    
                    print(f"      📊 Result: Success page={success_visible}, Status='{status_text}'")
                    
                    if success_visible or 'success' in status_text.lower():
                        print("      ✅ GOOGLE OAUTH IS WORKING!")
                        return True
                    else:
                        print("      ❌ Google OAuth not working properly")
                        return False
                        
            except Exception as e:
                print(f"   Button {i+1}: Error - {str(e)}")
        
        print("❌ No Google OAuth button found")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    result = test_google_oauth_button()
    print(f"\\n🎯 GOOGLE OAUTH TEST RESULT: {'✅ WORKING' if result else '❌ NOT WORKING'}")