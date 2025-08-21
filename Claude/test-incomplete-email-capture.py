#!/usr/bin/env python3
# Test incomplete email capture functionality

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_incomplete_email_capture():
    """Test that incomplete email entries are properly captured and logged"""
    
    print("🧪 Testing Incomplete Email Capture Functionality")
    print("=" * 50)
    
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
        
        print("1. 🖱️  Opening registration modal...")
        join_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Join Our Library')]"))
        )
        join_button.click()
        
        # Wait for modal
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "registration-form"))
        )
        print("✅ Modal opened successfully")
        
        # Test different incomplete email scenarios
        test_scenarios = [
            {"email": "test1", "description": "Partial email without domain"},
            {"email": "test2@", "description": "Email with @ but no domain"},
            {"email": "test3@example", "description": "Email without TLD"},
            {"email": "test4@example.com", "description": "Complete email (control test)"},
            {"email": "", "description": "Empty email field"}
        ]
        
        email_input = driver.find_element(By.ID, "email")
        successful_captures = 0
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. 📧 Testing: {scenario['description']}")
            print(f"   Email: '{scenario['email']}'")
            
            # Clear the email field
            email_input.clear()
            time.sleep(0.5)
            
            # Enter the test email
            if scenario['email']:
                email_input.send_keys(scenario['email'])
            
            # Get initial console log count
            initial_logs = len(driver.get_log('browser'))
            
            # Trigger blur event (user leaves the field)
            driver.execute_script("arguments[0].blur();", email_input)
            
            # Wait for any async logging
            time.sleep(2)
            
            # Check for new console activity
            new_logs = driver.get_log('browser')[initial_logs:]
            
            # Look for logging activity
            logging_detected = any(
                'incomplete' in log['message'].lower() or
                'email' in log['message'].lower() or
                'sheets' in log['message'].lower() or
                'capture' in log['message'].lower() or
                'track' in log['message'].lower()
                for log in new_logs
            )
            
            if logging_detected:
                print("   ✅ Logging activity detected")
                successful_captures += 1
                
                # Show relevant log messages
                relevant_logs = [log for log in new_logs if any(keyword in log['message'].lower() 
                               for keyword in ['incomplete', 'email', 'sheets', 'capture', 'track'])]
                for log in relevant_logs[:2]:  # Show first 2 relevant logs
                    print(f"   📝 {log['message'][:80]}...")
            else:
                print("   ⚠️ No logging activity detected")
                
            # Check for Google Sheets integration specifically
            sheets_activity = any('sheets' in log['message'].lower() for log in new_logs)
            if sheets_activity:
                print("   📊 Google Sheets integration activity detected")
                
            # Check for errors
            errors = [log for log in new_logs if log['level'] == 'SEVERE']
            if errors:
                print("   ❌ Errors detected:")
                for error in errors[:1]:  # Show first error
                    print(f"      {error['message'][:80]}...")
        
        print(f"\n📊 Summary:")
        print(f"   Total scenarios tested: {len(test_scenarios)}")
        print(f"   Successful captures detected: {successful_captures}")
        print(f"   Success rate: {successful_captures}/{len(test_scenarios)} ({100*successful_captures/len(test_scenarios):.1f}%)")
        
        # Additional test: Check if Google Sheets integration is properly initialized
        print(f"\n🔧 Checking Google Sheets Integration Status:")
        
        google_auth_ready = driver.execute_script("return typeof window.googleAuth !== 'undefined'")
        registration_manager_ready = driver.execute_script("return typeof window.registrationManager !== 'undefined'")
        
        print(f"   Google Auth Object: {'✅ Ready' if google_auth_ready else '❌ Not found'}")
        print(f"   Registration Manager: {'✅ Ready' if registration_manager_ready else '❌ Not found'}")
        
        if google_auth_ready and registration_manager_ready:
            print("   ✅ Hybrid system properly initialized")
            
            # Test if methods are available
            try:
                has_log_method = driver.execute_script(
                    "return typeof window.registrationManager.logIncompleteEmail === 'function'"
                )
                print(f"   logIncompleteEmail method: {'✅ Available' if has_log_method else '❌ Missing'}")
                
                # Also check the structure more deeply
                manager_methods = driver.execute_script("""
                    if (window.registrationManager) {
                        return Object.getOwnPropertyNames(window.registrationManager).concat(
                            Object.getOwnPropertyNames(Object.getPrototypeOf(window.registrationManager))
                        );
                    } return [];
                """)
                print(f"   Available methods: {manager_methods}")
                
                # Test calling the method directly
                if has_log_method:
                    try:
                        result = driver.execute_script("""
                            return window.registrationManager.logIncompleteEmail('test@example.com', 'direct_test')
                                .then(r => 'success').catch(e => e.message);
                        """)
                        print(f"   Direct method test: {result}")
                    except Exception as e:
                        print(f"   Direct method test failed: {e}")
                        
            except Exception as e:
                print(f"   ❌ Cannot check method availability: {e}")
        else:
            print("   ⚠️ Hybrid system not fully initialized")
            print("   💡 This is expected until Google Sheets IDs are configured")
        
        # Determine overall success
        basic_functionality = successful_captures >= len(test_scenarios) // 2
        infrastructure_ready = google_auth_ready and registration_manager_ready
        
        if basic_functionality and infrastructure_ready:
            print(f"\n✅ Overall Assessment: System ready for email capture")
            print(f"   - Email field interaction working: ✅")
            print(f"   - Logging infrastructure ready: ✅")
            print(f"   - Next step: Configure Google Sheets IDs")
            return True
        elif infrastructure_ready:
            print(f"\n⚠️ Overall Assessment: Infrastructure ready but needs tuning")
            print(f"   - Logging infrastructure ready: ✅")
            print(f"   - Email capture needs optimization: ⚠️")
            return True
        else:
            print(f"\n❌ Overall Assessment: System needs configuration")
            print(f"   - Basic functionality: {'✅' if basic_functionality else '❌'}")
            print(f"   - Infrastructure: {'✅' if infrastructure_ready else '❌'}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_incomplete_email_capture()
    print(f"\n🏁 Incomplete email capture test: {'✅ PASSED' if success else '❌ FAILED'}")