#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_google_oauth_console():
    """Test Google OAuth with console error monitoring"""
    
    print("🔍 TESTING GOOGLE OAUTH WITH CONSOLE MONITORING")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(5)
        
        # Open registration modal
        reg_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        reg_button.click()
        time.sleep(2)
        
        # Check Google Auth availability before clicking
        google_auth_status = driver.execute_script("""
            return {
                googleAuthExists: !!window.googleAuth,
                googleAuthType: typeof window.googleAuth,
                googleAuthReady: window.googleAuth ? window.googleAuth.isReady : false,
                registrationManagerExists: !!window.registrationManager,
                registerWithGoogleExists: !!window.registerWithGoogle,
                registerWithGoogleType: typeof window.registerWithGoogle
            };
        """)
        
        print("📊 GOOGLE AUTH STATUS:")
        for key, value in google_auth_status.items():
            print(f"   {key}: {value}")
        
        # Click Google OAuth button and monitor console
        google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register with Google')]")
        
        print("\n🚀 Clicking Google OAuth button...")
        google_button.click()
        
        # Wait and check for any changes
        time.sleep(3)
        
        # Check console logs
        console_logs = driver.get_log('browser')
        
        print("\n📋 CONSOLE LOGS AFTER CLICK:")
        for log in console_logs[-10:]:  # Show last 10 logs
            level = log['level']
            message = log['message']
            print(f"   [{level}] {message}")
        
        # Check if any OAuth functions were called
        oauth_debug = driver.execute_script("""
            return {
                currentURL: window.location.href,
                googleAuthCalled: window.googleAuthWasCalled || false,
                anyErrors: window.lastError || null,
                popupBlocked: window.popupBlocked || false
            };
        """)
        
        print("\n🔍 OAUTH DEBUG INFO:")
        for key, value in oauth_debug.items():
            print(f"   {key}: {value}")
            
        return google_auth_status
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/google_oauth_console_test.png")
        driver.quit()

if __name__ == "__main__":
    result = test_google_oauth_console()
    
    if result:
        print(f"\n🎯 DIAGNOSIS:")
        if not result['googleAuthExists']:
            print("   ❌ window.googleAuth does not exist")
            print("   CAUSE: Google Auth module not loaded or initialized")
        elif not result['googleAuthReady']:
            print("   ❌ window.googleAuth exists but not ready")
            print("   CAUSE: Google Auth initialization failed")
        elif not result['registrationManagerExists']:
            print("   ❌ window.registrationManager does not exist")
            print("   CAUSE: Registration manager not initialized")
        else:
            print("   ✅ All dependencies exist - investigating deeper...")