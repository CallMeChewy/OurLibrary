#!/usr/bin/env python3
# File: check-oauth-button-exists.py
# Path: /home/herb/Desktop/OurLibrary/check-oauth-button-exists.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 01:35PM
# Check if Google OAuth button exists and get its exact text

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def check_oauth_button_exists():
    """Check if Google OAuth button exists and show all buttons"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        print("🔍 CHECKING FOR GOOGLE OAUTH BUTTON")
        print("=" * 40)
        
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(8)
        
        # Get all buttons on the page
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        print(f"Found {len(all_buttons)} total buttons:")
        
        for i, button in enumerate(all_buttons, 1):
            try:
                text = button.text.strip()
                visible = button.is_displayed()
                enabled = button.is_enabled()
                print(f"  {i}. Text: '{text}' | Visible: {visible} | Enabled: {enabled}")
                
                if 'google' in text.lower():
                    print(f"     🎯 This is a Google OAuth button!")
                    
                    # Try clicking it
                    if visible and enabled:
                        print(f"     🖱️ Attempting to click...")
                        original_url = driver.current_url
                        button.click()
                        time.sleep(5)
                        
                        new_url = driver.current_url
                        page_source = driver.page_source
                        
                        if "redirect_uri_mismatch" in page_source:
                            print(f"     ❌ CONFIRMED: redirect_uri_mismatch error!")
                            return True
                        elif new_url != original_url:
                            print(f"     ✅ Redirected to: {new_url}")
                        else:
                            print(f"     ⚠️ No redirect occurred")
                    else:
                        print(f"     ❌ Button not clickable")
            except Exception as e:
                print(f"  {i}. Error reading button: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"❌ Check failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    found_error = check_oauth_button_exists()
    if found_error:
        print("\n❌ CONFIRMED: Google OAuth redirect_uri_mismatch error exists")
    else:
        print("\n⚠️ Could not reproduce the redirect_uri_mismatch error")