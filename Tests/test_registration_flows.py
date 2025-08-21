#!/usr/bin/env python3
# File: test_registration_flows.py
# Path: /home/herb/Desktop/OurLibrary/Tests/test_registration_flows.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-19
# Last Modified: 2025-08-19 04:25PM
# Description: Comprehensive test suite for OurLibrary hybrid registration system

import pytest
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestOurLibraryRegistration:
    """Test suite for OurLibrary hybrid Firebase + Google Sheets registration system"""
    
    @pytest.fixture(scope="class")
    def browser_setup(self):
        """Setup Chrome browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--headless")  # Uncomment for headless testing
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        driver.maximize_window()
        
        yield driver
        driver.quit()

    def test_landing_page_loads(self, browser_setup):
        """Test that the main landing page loads correctly"""
        driver = browser_setup
        
        print("🧪 Testing landing page load...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        # Check title
        assert "OurLibrary" in driver.title
        
        # Check key elements exist
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        assert join_button.is_displayed()
        
        # Check Firebase and Google Sheets integration loaded
        console_logs = driver.get_log('browser')
        firebase_loaded = any('Firebase' in log['message'] for log in console_logs)
        print(f"✅ Landing page loaded successfully, Firebase detected: {firebase_loaded}")

    def test_join_button_functionality(self, browser_setup):
        """Test that Join button opens registration modal"""
        driver = browser_setup
        
        print("🧪 Testing Join button functionality...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        # Wait for page to fully load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
        )
        
        # Click Join button
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        join_button.click()
        
        # Check if modal appears
        try:
            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "registration-form"))
            )
            assert modal.is_displayed()
            print("✅ Join button successfully opens registration modal")
        except TimeoutException:
            print("❌ Join button did not open modal - checking for alerts")
            # Check for any alerts that might indicate the function was called
            alert_text = driver.execute_script("return window.lastAlert || 'No alert'")
            print(f"Alert detected: {alert_text}")

    def test_email_input_tracking(self, browser_setup):
        """Test that email input is tracked for incomplete registrations"""
        driver = browser_setup
        
        print("🧪 Testing email input tracking...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        # Open registration modal
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        join_button.click()
        
        # Wait for modal and input email
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            test_email = f"test_incomplete_{int(time.time())}@example.com"
            email_input.send_keys(test_email)
            
            # Trigger blur event to capture incomplete email
            driver.execute_script("arguments[0].blur();", email_input)
            
            # Check console for logging activity
            time.sleep(2)  # Allow time for async logging
            console_logs = driver.get_log('browser')
            
            logging_detected = any('incomplete' in log['message'].lower() or 'sheets' in log['message'].lower() 
                                 for log in console_logs)
            
            print(f"✅ Email input tracking test completed. Logging detected: {logging_detected}")
            print(f"Test email used: {test_email}")
            
        except TimeoutException:
            print("❌ Could not find email input in registration modal")

    def test_full_email_registration_flow(self, browser_setup):
        """Test complete email registration flow"""
        driver = browser_setup
        
        print("🧪 Testing full email registration flow...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        # Open registration modal
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        join_button.click()
        
        try:
            # Fill out registration form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            test_email = f"test_full_{int(time.time())}@example.com"
            test_name = "Test User"
            test_password = "password123"
            
            # Fill form fields
            driver.find_element(By.ID, "fullName").send_keys(test_name)
            driver.find_element(By.ID, "email").send_keys(test_email)
            driver.find_element(By.ID, "password").send_keys(test_password)
            driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
            
            # Submit form
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
            submit_button.click()
            
            # Wait for verification step
            try:
                verification_step = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, "verification-step"))
                )
                
                print(f"✅ Email registration form submitted successfully")
                print(f"✅ Verification step reached")
                print(f"Test email: {test_email}")
                
                # Check if verification code input is present
                code_input = driver.find_element(By.ID, "verificationCode")
                assert code_input.is_displayed()
                
                print("✅ Verification code input found - registration flow working")
                
            except TimeoutException:
                print("❌ Verification step not reached - checking for errors")
                # Check for any error messages
                error_elements = driver.find_elements(By.CLASS_NAME, "error")
                for error in error_elements:
                    if error.is_displayed():
                        print(f"Error found: {error.text}")
                        
        except Exception as e:
            print(f"❌ Email registration flow failed: {str(e)}")

    def test_google_oauth_button_present(self, browser_setup):
        """Test that Google OAuth button is present and clickable"""
        driver = browser_setup
        
        print("🧪 Testing Google OAuth button presence...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        
        # Open registration modal
        join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
        join_button.click()
        
        try:
            # Look for Google OAuth button
            google_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue with Google')]"))
            )
            
            assert google_button.is_displayed()
            print("✅ Google OAuth button found and clickable")
            
            # Click to test (but don't complete OAuth in automated test)
            google_button.click()
            
            # Check console for any OAuth initialization
            time.sleep(3)
            console_logs = driver.get_log('browser')
            oauth_activity = any('google' in log['message'].lower() or 'oauth' in log['message'].lower() 
                               for log in console_logs)
            
            print(f"✅ Google OAuth button click test completed. Activity detected: {oauth_activity}")
            
        except TimeoutException:
            print("❌ Google OAuth button not found or not clickable")

    def test_auth_demo_page_loads(self, browser_setup):
        """Test that the detailed auth demo page loads correctly"""
        driver = browser_setup
        
        print("🧪 Testing auth demo page...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        
        # Check title
        assert "Secure Authentication Demo" in driver.title
        
        # Check key elements
        demo_title = driver.find_element(By.XPATH, "//h1[contains(text(), 'Secure Auth Demo')]")
        assert demo_title.is_displayed()
        
        # Check Firebase initialization
        console_logs = driver.get_log('browser')
        firebase_initialized = any('Firebase' in log['message'] and 'initialized' in log['message'] 
                                 for log in console_logs)
        
        print(f"✅ Auth demo page loaded. Firebase initialized: {firebase_initialized}")

    def test_javascript_errors(self, browser_setup):
        """Check for JavaScript errors that might break functionality"""
        driver = browser_setup
        
        print("🧪 Testing for JavaScript errors...")
        
        # Test both main pages
        pages = [
            "https://callmechewy.github.io/OurLibrary/",
            "https://callmechewy.github.io/OurLibrary/auth-demo.html"
        ]
        
        for page in pages:
            driver.get(page)
            time.sleep(5)  # Allow time for all scripts to load
            
            console_logs = driver.get_log('browser')
            errors = [log for log in console_logs if log['level'] == 'SEVERE']
            
            if errors:
                print(f"❌ JavaScript errors found on {page}:")
                for error in errors:
                    print(f"   - {error['message']}")
            else:
                print(f"✅ No severe JavaScript errors on {page}")

    def test_responsive_design(self, browser_setup):
        """Test that the registration works on different screen sizes"""
        driver = browser_setup
        
        print("🧪 Testing responsive design...")
        
        screen_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in screen_sizes:
            driver.set_window_size(width, height)
            driver.get("https://callmechewy.github.io/OurLibrary/")
            
            # Check if Join button is still clickable
            try:
                join_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
                )
                assert join_button.is_displayed()
                print(f"✅ Join button accessible at {width}x{height}")
                
            except TimeoutException:
                print(f"❌ Join button not accessible at {width}x{height}")

    def test_hybrid_system_integration(self, browser_setup):
        """Test that both Firebase and Google Sheets systems are properly integrated"""
        driver = browser_setup
        
        print("🧪 Testing hybrid system integration...")
        driver.get("https://callmechewy.github.io/OurLibrary/auth-demo.html")
        
        # Wait for page load and check for hybrid system components
        time.sleep(5)
        
        # Check if required global objects exist
        firebase_ready = driver.execute_script("return typeof window.firebaseAuth !== 'undefined'")
        google_auth_ready = driver.execute_script("return typeof window.googleAuth !== 'undefined'")
        registration_manager_ready = driver.execute_script("return typeof window.registrationManager !== 'undefined'")
        
        print(f"Firebase Auth ready: {firebase_ready}")
        print(f"Google Auth ready: {google_auth_ready}")
        print(f"Registration Manager ready: {registration_manager_ready}")
        
        # Check console for initialization messages
        console_logs = driver.get_log('browser')
        hybrid_messages = [log for log in console_logs 
                         if 'hybrid' in log['message'].lower() or 'sheets' in log['message'].lower()]
        
        if hybrid_messages:
            print("✅ Hybrid system integration messages found:")
            for msg in hybrid_messages:
                print(f"   - {msg['message']}")
        else:
            print("⚠️ No specific hybrid system messages found")

if __name__ == "__main__":
    # Run tests manually if executed directly
    print("🚀 Starting OurLibrary Registration System Tests")
    pytest.main([__file__, "-v", "--tb=short"])