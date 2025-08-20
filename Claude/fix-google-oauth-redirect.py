#!/usr/bin/env python3
# File: fix-google-oauth-redirect.py
# Path: /home/herb/Desktop/OurLibrary/fix-google-oauth-redirect.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 12:15PM
# Diagnose and fix Google OAuth redirect_uri_mismatch

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def diagnose_google_oauth():
    """Diagnose Google OAuth redirect_uri_mismatch issue"""
    
    print("🔍 DIAGNOSING GOOGLE OAUTH REDIRECT_URI_MISMATCH")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Load the auth demo page
        print("1. 🌐 Loading auth demo page...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(8)
        
        # Get current URL and domain info
        current_url = driver.current_url
        print(f"   Current URL: {current_url}")
        
        # Extract domain information
        from urllib.parse import urlparse
        parsed = urlparse(current_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        print(f"   Domain: {domain}")
        
        # Check Google OAuth configuration
        print("\n2. 🔑 Checking Google OAuth Configuration...")
        
        oauth_config = driver.execute_script("""
            return {
                clientId: window.googleAuth ? window.googleAuth.config.clientId : 'not found',
                currentOrigin: window.location.origin,
                currentHost: window.location.host,
                currentProtocol: window.location.protocol
            };
        """)
        
        print(f"   Client ID: {oauth_config['clientId']}")
        print(f"   Current origin: {oauth_config['currentOrigin']}")
        print(f"   Current host: {oauth_config['currentHost']}")
        print(f"   Current protocol: {oauth_config['currentProtocol']}")
        
        # Try to click Google OAuth and capture the exact error
        print("\n3. 🧪 Testing Google OAuth Button Click...")
        
        try:
            # Find the Google OAuth button
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
            print("   ✅ Google OAuth button found")
            
            # Click and capture what happens
            print("   🖱️ Clicking Google OAuth button...")
            google_button.click()
            time.sleep(5)
            
            # Check current URL after click
            new_url = driver.current_url
            page_source = driver.page_source
            
            print(f"   New URL: {new_url}")
            
            if "redirect_uri_mismatch" in page_source:
                print("   ❌ Confirmed: redirect_uri_mismatch error")
                
                # Extract error details from page
                if "Error 400" in page_source:
                    print("   📋 Error 400: redirect_uri_mismatch details:")
                    # Try to find specific error text
                    error_elements = driver.find_elements(By.TAG_NAME, "p")
                    for element in error_elements:
                        text = element.text
                        if "redirect_uri" in text.lower() or "authorized" in text.lower():
                            print(f"      {text}")
                            
            elif "accounts.google.com" in new_url:
                print("   ✅ Google OAuth opened successfully (no redirect_uri error)")
            else:
                print("   ⚠️ Unexpected behavior after OAuth click")
                
        except Exception as e:
            print(f"   ❌ Error testing Google OAuth: {str(e)}")
        
        # Provide fix recommendations
        print("\n4. 🔧 REDIRECT_URI_MISMATCH FIX REQUIRED:")
        print("   The Google OAuth Client ID needs to be configured with the correct redirect URIs.")
        print("   ")
        print("   Required redirect URIs for Google Cloud Console:")
        print(f"   ✅ {oauth_config['currentOrigin']}")
        print("   ✅ https://callmechewy.github.io")
        print("   ✅ https://callmechewy.github.io/OurLibrary")
        print("   ✅ https://callmechewy.github.io/OurLibrary/auth-demo.html")
        print("   ")
        print("   Steps to fix:")
        print("   1. Go to Google Cloud Console")
        print("   2. Navigate to APIs & Services > Credentials") 
        print("   3. Edit the OAuth 2.0 Client ID")
        print("   4. Add the above URIs to 'Authorized redirect URIs'")
        print("   5. Save the configuration")
        
        # Also check if we can temporarily disable Google OAuth
        print("\n5. 🛠️ TEMPORARY WORKAROUND:")
        print("   While fixing OAuth config, we can:")
        print("   - Hide Google OAuth button until fixed")
        print("   - Focus testing on email registration")
        print("   - Ensure email verification works perfectly")
        
        return oauth_config
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    config = diagnose_google_oauth()
    if config:
        print(f"\n🎯 OAuth Client ID: {config['clientId']}")
        print(f"🎯 Required Domain: {config['currentOrigin']}")
        print("\n💡 This diagnosis shows exactly what needs to be configured in Google Cloud Console")