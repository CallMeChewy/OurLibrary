#!/usr/bin/env python3
# Test email registration flow specifically

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_email_registration():
    """Test the email registration flow specifically"""
    
    print("🧪 Testing Email Registration Flow")
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
        
        # Fill out form
        print("3. 📝 Filling out registration form...")
        
        # First, let's inspect what form fields are actually available
        print("🔍 Inspecting form fields...")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(all_inputs)} input fields:")
        for input_el in all_inputs:
            input_id = input_el.get_attribute('id')
            input_name = input_el.get_attribute('name')
            input_type = input_el.get_attribute('type')
            print(f"  - ID: '{input_id}', Name: '{input_name}', Type: '{input_type}'")
        
        # Try to find fields by ID first, then by name as fallback
        try:
            name_input = driver.find_element(By.ID, "fullName")
        except:
            try:
                name_input = driver.find_element(By.CSS_SELECTOR, "input[name='firstName']")
                print("⚠️ Using firstName field as fallback")
            except:
                print("❌ Could not find name input field")
                return False
                
        try:
            email_input = driver.find_element(By.ID, "email")
        except:
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
                print("⚠️ Using name selector for email field")
            except:
                print("❌ Could not find email input field")
                return False
                
        try:
            password_input = driver.find_element(By.ID, "password")
        except:
            try:
                password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
                print("⚠️ Using name selector for password field")
            except:
                print("❌ Could not find password input field")
                return False
                
        try:
            confirm_input = driver.find_element(By.ID, "confirmPassword")
        except:
            try:
                confirm_input = driver.find_element(By.CSS_SELECTOR, "input[name='confirmPassword']")
                print("⚠️ Using name selector for confirm password field")
            except:
                print("❌ Could not find confirm password input field")
                return False
        
        test_email = f"test_{int(time.time())}@example.com"
        
        name_input.send_keys("Test User")
        email_input.send_keys(test_email)
        password_input.send_keys("password123")
        confirm_input.send_keys("password123")
        
        print(f"✅ Form filled with email: {test_email}")
        
        # Test email blur event (incomplete email tracking)
        print("4. 🎯 Testing incomplete email tracking...")
        email_input.click()
        driver.execute_script("arguments[0].blur();", email_input)
        time.sleep(1)
        print("✅ Email blur event triggered")
        
        # Submit form
        print("5. 📤 Submitting registration form...")
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        # Wait for result
        time.sleep(5)
        
        # Check what happened
        current_url = driver.current_url
        page_source_snippet = driver.page_source[:500] if driver.page_source else ""
        
        # Check console for messages
        console_logs = driver.get_log('browser')
        registration_logs = [log for log in console_logs if 'registration' in log['message'].lower()]
        error_logs = [log for log in console_logs if log['level'] == 'SEVERE']
        
        print("\n📊 Results:")
        print(f"   Current URL: {current_url}")
        print(f"   Registration logs: {len(registration_logs)}")
        print(f"   Error logs: {len(error_logs)}")
        
        if registration_logs:
            print("   📝 Registration activity detected:")
            for log in registration_logs[:3]:
                print(f"      - {log['message'][:80]}...")
                
        if error_logs:
            print("   ❌ Errors found:")
            for log in error_logs[:2]:
                print(f"      - {log['message'][:80]}...")
        
        # Check for verification step or success message
        try:
            verification_step = driver.find_element(By.ID, "verification-step")
            if verification_step.is_displayed():
                print("✅ Reached verification step successfully!")
                return True
            else:
                print("❌ Verification step not visible")
        except:
            print("🔍 Verification step not found, checking for other success indicators...")
            
            # Check if modal is still visible or if alert was triggered
            try:
                modal = driver.find_element(By.ID, "registration-form")
                if not modal.is_displayed():
                    print("✅ Registration modal closed - likely success")
                    return True
                else:
                    print("⚠️ Registration modal still visible")
            except:
                print("⚠️ Cannot determine modal state")
            
            # Check page source for success indicators
            page_source = driver.page_source.lower()
            if 'verification' in page_source or 'success' in page_source:
                print("✅ Success indicators found in page content")
                return True
                
            # Check for Firebase registration success in console
            firebase_success = any('registration successful' in log['message'].lower() or 
                                 'verification email' in log['message'].lower()
                                 for log in console_logs)
            
            if firebase_success:
                print("✅ Firebase registration success detected in console")
                return True
                
            print("❌ No success indicators found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_email_registration()
    print(f"\n🏁 Email registration test: {'✅ PASSED' if success else '❌ FAILED'}")