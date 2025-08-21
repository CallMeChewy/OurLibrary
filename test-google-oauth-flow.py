#!/usr/bin/env python3
# File: test-google-oauth-flow.py
# Path: /home/herb/Desktop/OurLibrary/test-google-oauth-flow.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 07:05PM
# TEST: Google OAuth registration flow from main site

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_google_oauth_flow():
    """Test the Google OAuth registration flow"""
    
    print("🔍 TESTING GOOGLE OAUTH REGISTRATION FLOW")
    print("=" * 60)
    print("OBJECTIVE: Identify Google OAuth dual-system conflicts")
    print("APPROACH: Same systematic debugging as email verification")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        print("1. 🌐 Loading main OurLibrary site...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(5)
        
        print("2. 🔍 Looking for Google OAuth registration button...")
        
        # Find registration modal trigger
        try:
            reg_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
            reg_button.click()
            time.sleep(2)
            print("   ✅ Registration modal opened")
        except Exception as e:
            print(f"   ❌ Could not open registration modal: {e}")
            return "MODAL_FAILED"
        
        # Look for Google OAuth button
        try:
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register with Google') or contains(text(), 'Google')]")
            print(f"   ✅ Found Google OAuth button: '{google_button.text}'")
            
            # Check what function it calls
            onclick = google_button.get_attribute("onclick")
            print(f"   📋 Button onclick: {onclick}")
            
            print("3. 🚀 Clicking Google OAuth button...")
            google_button.click()
            
            # Monitor what happens for 10 seconds
            print("4. 👀 Monitoring OAuth flow...")
            for i in range(10):
                time.sleep(1)
                current_url = driver.current_url
                page_title = driver.title
                
                print(f"   [{i+1}s] URL: {current_url}")
                
                # Check for Google OAuth popup or redirect
                if "accounts.google.com" in current_url:
                    print("   ✅ Redirected to Google OAuth")
                    return "GOOGLE_OAUTH_REDIRECT"
                elif "auth-demo.html" in current_url:
                    print("   ✅ Redirected to auth-demo.html")
                    return "AUTH_DEMO_REDIRECT"
                
                # Check for error messages or alerts
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print(f"   ⚠️ Alert: {alert_text}")
                    alert.accept()
                    
                    if "will be implemented" in alert_text.lower():
                        print("   ❌ Google OAuth not implemented yet")
                        return "NOT_IMPLEMENTED"
                except:
                    pass
            
            print("   ❓ No clear redirect or popup detected")
            return "UNCLEAR"
            
        except Exception as e:
            print(f"   ❌ Could not find Google OAuth button: {e}")
            
            # List all buttons for debugging
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"   📋 Available buttons ({len(buttons)}):")
            for btn in buttons[:10]:  # Show first 10
                try:
                    text = btn.text.strip()
                    if text:
                        print(f"      - '{text}'")
                except:
                    pass
            
            return "BUTTON_NOT_FOUND"
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return "TEST_ERROR"
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/google_oauth_test.png")
        driver.quit()

if __name__ == "__main__":
    result = test_google_oauth_flow()
    
    print(f"\n🎯 GOOGLE OAUTH TEST RESULT: {result}")
    
    if result == "NOT_IMPLEMENTED":
        print("\n📋 FINDING: Google OAuth shows 'not implemented' message")
        print("   NEXT: Check if button is connected to working OAuth system")
    elif result == "GOOGLE_OAUTH_REDIRECT":
        print("\n📋 FINDING: Google OAuth popup/redirect working")
        print("   NEXT: Test what happens after Google authentication")
    elif result == "AUTH_DEMO_REDIRECT":
        print("\n📋 FINDING: Direct redirect to auth-demo.html")
        print("   NEXT: Check if Google auth state is passed properly")
    else:
        print(f"\n📋 FINDING: Unexpected result - {result}")
        print("   NEXT: Investigate button implementation and error handling")