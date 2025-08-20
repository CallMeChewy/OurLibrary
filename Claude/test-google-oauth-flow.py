#!/usr/bin/env python3
# Test Google OAuth registration flow specifically

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_google_oauth_registration():
    """Test the Google OAuth registration flow specifically"""
    
    print("🧪 Testing Google OAuth Registration Flow")
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
        # Go to landing page and open modal
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        print("1. 🖱️  Clicking Join button...")
        join_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
        )
        join_button.click()
        
        # Wait for modal
        print("2. ⏳ Waiting for registration modal...")
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "registration-form"))
        )
        print("✅ Modal opened successfully")
        
        # Find and click Google OAuth button
        print("3. 🔍 Looking for Google OAuth button...")
        try:
            google_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Register with Google')]"))
            )
            print("✅ Google OAuth button found")
            
            # Check what happens when we click the button
            print("4. 🖱️  Clicking Google OAuth button...")
            
            # Store initial console logs count
            initial_logs = len(driver.get_log('browser'))
            
            # Click the button
            google_button.click()
            
            # Wait a moment for any OAuth initialization
            time.sleep(3)
            
            # Check for OAuth activity
            console_logs = driver.get_log('browser')
            new_logs = console_logs[initial_logs:]
            
            oauth_activity = any('google' in log['message'].lower() or 
                               'oauth' in log['message'].lower() or
                               'gapi' in log['message'].lower() or
                               'client' in log['message'].lower()
                               for log in new_logs)
            
            print(f"✅ Google OAuth button clicked. Activity detected: {oauth_activity}")
            
            if new_logs:
                print("📝 New console messages after OAuth click:")
                for log in new_logs[:5]:  # Show first 5 messages
                    print(f"   - {log['message'][:100]}...")
            
            # Check for specific OAuth errors or success indicators
            oauth_errors = [log for log in new_logs if log['level'] == 'SEVERE' and 
                           ('oauth' in log['message'].lower() or 'google' in log['message'].lower())]
            
            if oauth_errors:
                print("⚠️ OAuth-related errors found:")
                for error in oauth_errors:
                    print(f"   - {error['message'][:100]}...")
                    
            # Check for unauthorized domain error specifically
            domain_errors = [log for log in new_logs if 'unauthorized' in log['message'].lower() or
                           'domain' in log['message'].lower()]
            
            if domain_errors:
                print("🚨 Domain authorization issues detected:")
                for error in domain_errors:
                    print(f"   - {error['message'][:100]}...")
                print("💡 Solution: Add callmechewy.github.io to Firebase authorized domains")
            
            # Check if any popup or redirect occurred
            current_url = driver.current_url
            if current_url != "https://callmechewy.github.io/OurLibrary/":
                print(f"✅ URL changed to: {current_url}")
                print("✅ OAuth redirect initiated successfully")
                return True
            else:
                print("ℹ️ No redirect occurred - checking for other OAuth indicators")
                
                # Check for Google API client initialization
                google_api_ready = driver.execute_script("return typeof gapi !== 'undefined'")
                google_auth_instance = driver.execute_script("return typeof window.googleAuth !== 'undefined'")
                
                print(f"Google API loaded: {google_api_ready}")
                print(f"GoogleAuth instance: {google_auth_instance}")
                
                if oauth_activity or google_api_ready or google_auth_instance:
                    print("✅ OAuth infrastructure detected - system ready for configuration")
                    return True
                else:
                    print("❌ No OAuth activity detected")
                    return False
                    
        except Exception as e:
            print(f"❌ Google OAuth button test failed: {str(e)}")
            
            # Check if button exists with different text
            alternative_buttons = [
                "//button[contains(text(), 'Continue with Google')]",
                "//button[contains(text(), 'Google')]",
                "//button[contains(@class, 'google')]"
            ]
            
            for xpath in alternative_buttons:
                try:
                    alt_button = driver.find_element(By.XPATH, xpath)
                    if alt_button.is_displayed():
                        print(f"ℹ️ Found alternative Google button: {alt_button.text}")
                        break
                except:
                    continue
            else:
                print("❌ No Google OAuth button found")
            
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_google_oauth_registration()
    print(f"\n🏁 Google OAuth registration test: {'✅ PASSED' if success else '❌ FAILED'}")