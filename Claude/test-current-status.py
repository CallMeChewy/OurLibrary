#!/usr/bin/env python3
# Quick test script to check current OurLibrary system status

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_current_system():
    """Test current system status and report findings"""
    
    print("🚀 OurLibrary System Status Test")
    print("=" * 50)
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        # Test 1: Landing Page
        print("\n📋 Test 1: Landing Page Load")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(3)
        
        if "OurLibrary" in driver.title:
            print("✅ Landing page loads successfully")
        else:
            print("❌ Landing page title incorrect")
            
        # Test 2: Join Button
        print("\n📋 Test 2: Join Button Functionality")
        try:
            join_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
            )
            print("✅ Join button found and clickable")
            
            # Click the button
            join_button.click()
            time.sleep(2)
            
            # Check if modal appeared
            try:
                modal = driver.find_element(By.ID, "registration-form")
                if modal.is_displayed():
                    print("✅ Registration modal opens successfully")
                else:
                    print("❌ Registration modal not visible")
            except:
                print("❌ Registration modal not found")
                
        except TimeoutException:
            print("❌ Join button not found or not clickable")
        
        # Test 3: Console Messages
        print("\n📋 Test 3: JavaScript Console Analysis")
        console_logs = driver.get_log('browser')
        
        errors = [log for log in console_logs if log['level'] == 'SEVERE']
        if errors:
            print("❌ JavaScript errors found:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   - {error['message'][:100]}...")
        else:
            print("✅ No severe JavaScript errors")
            
        # Check for specific messages
        firebase_messages = [log for log in console_logs if 'firebase' in log['message'].lower()]
        sheets_messages = [log for log in console_logs if 'sheets' in log['message'].lower()]
        hybrid_messages = [log for log in console_logs if 'hybrid' in log['message'].lower()]
        
        print(f"   📊 Firebase messages: {len(firebase_messages)}")
        print(f"   📊 Sheets messages: {len(sheets_messages)}")
        print(f"   📊 Hybrid messages: {len(hybrid_messages)}")
        
        # Test 4: Form Elements
        print("\n📋 Test 4: Registration Form Elements")
        try:
            email_input = driver.find_element(By.ID, "email")
            name_input = driver.find_element(By.ID, "fullName")
            password_input = driver.find_element(By.ID, "password")
            google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google')]")
            
            elements_found = sum([
                email_input.is_displayed(),
                name_input.is_displayed(), 
                password_input.is_displayed(),
                google_button.is_displayed()
            ])
            
            print(f"✅ Form elements visible: {elements_found}/4")
            
        except Exception as e:
            print(f"❌ Form elements check failed: {str(e)[:50]}...")
        
        # Test 5: Auth Demo Page
        print("\n📋 Test 5: Auth Demo Page")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        time.sleep(3)
        
        if "Secure Authentication Demo" in driver.title:
            print("✅ Auth demo page loads successfully")
        else:
            print("❌ Auth demo page title incorrect")
            
        # Check for step indicators
        try:
            steps = driver.find_elements(By.CLASS_NAME, "step")
            print(f"✅ Step indicators found: {len(steps)}/3")
        except:
            print("❌ Step indicators not found")
        
        # Test 6: Global Objects Check
        print("\n📋 Test 6: JavaScript Integration Check")
        firebase_ready = driver.execute_script("return typeof window.firebaseAuth !== 'undefined'")
        google_auth_ready = driver.execute_script("return typeof window.googleAuth !== 'undefined'")
        registration_manager_ready = driver.execute_script("return typeof window.registrationManager !== 'undefined'")
        
        print(f"   🔥 Firebase Auth: {'✅' if firebase_ready else '❌'}")
        print(f"   📊 Google Auth: {'✅' if google_auth_ready else '❌'}")
        print(f"   🔧 Registration Manager: {'✅' if registration_manager_ready else '❌'}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SYSTEM STATUS SUMMARY")
        print("=" * 50)
        
        basic_functionality = all([
            "OurLibrary" in driver.title,
            firebase_ready
        ])
        
        if basic_functionality:
            print("✅ BASIC SYSTEM: Working")
        else:
            print("❌ BASIC SYSTEM: Issues found")
            
        if google_auth_ready and registration_manager_ready:
            print("✅ HYBRID INTEGRATION: Ready (needs Google Sheets setup)")
        else:
            print("❌ HYBRID INTEGRATION: Not properly initialized")
            
        print("\n🎯 NEXT STEPS:")
        if basic_functionality:
            print("1. ✅ Basic functionality confirmed")
            print("2. 🔧 Set up Google Sheets IDs in code")
            print("3. 🔧 Configure Google OAuth Client ID")
            print("4. 🔧 Add domain to Firebase authorized domains")
            print("5. 🧪 Test complete registration flow")
        else:
            print("1. 🐛 Fix basic JavaScript initialization issues")
            print("2. 🔧 Check Firebase configuration")
            print("3. 🧪 Re-test basic functionality")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        
    finally:
        driver.quit()
        print("\n🏁 Test completed")

if __name__ == "__main__":
    test_current_system()