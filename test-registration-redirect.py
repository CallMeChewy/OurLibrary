#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_registration_redirect():
    """Test the registration redirect flow"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")  # Fresh session
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        print("🧪 TESTING REGISTRATION REDIRECT FLOW")
        print("=" * 50)
        
        # Load main site
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(5)
        
        # Find and click registration
        try:
            reg_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join Our Library')]")
            reg_button.click()
            time.sleep(2)
            print("✅ Registration modal opened")
        except Exception as e:
            print(f"❌ Could not find registration button: {e}")
            # Try alternative selector
            try:
                reg_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join')]")
                reg_button.click()
                time.sleep(2)
                print("✅ Registration modal opened (alternative selector)")
            except:
                print("❌ No registration button found with any selector")
                return False
        
        # Fill form
        test_email = f"redirect_test_{int(time.time())}@example.com"
        
        driver.find_element(By.ID, "email").send_keys(test_email)
        driver.find_element(By.ID, "fullName").send_keys("Redirect Test User")
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirmPassword").send_keys("testpass123")
        
        print(f"✅ Form filled with email: {test_email}")
        
        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        submit_button.click()
        
        print("✅ Form submitted, waiting for response...")
        
        # Wait and check what happens
        for i in range(10):
            time.sleep(1)
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"[{i+1}s] URL: {current_url}")
            
            if "auth-demo.html" in current_url:
                print("✅ SUCCESS: Redirected to auth-demo.html!")
                
                # Check if form is pre-filled
                try:
                    email_field = driver.find_element(By.ID, "email").get_attribute("value")
                    name_field = driver.find_element(By.ID, "fullName").get_attribute("value")
                    
                    print(f"   Pre-filled email: {email_field}")
                    print(f"   Pre-filled name: {name_field}")
                    
                    if email_field == test_email:
                        print("✅ Form correctly pre-filled!")
                        return True
                    else:
                        print("⚠️ Form not pre-filled correctly")
                        return True  # Still redirected
                        
                except Exception as e:
                    print(f"   Error checking pre-fill: {e}")
                    return True  # Still redirected
                    
        print("❌ No redirect occurred within 10 seconds")
        
        # Check for alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   Alert found: {alert_text}")
            alert.accept()
            
            if "Redirecting to verification" in alert_text:
                print("✅ Found redirect alert - waiting longer...")
                time.sleep(3)
                
                if "auth-demo.html" in driver.current_url:
                    print("✅ Redirect successful after alert!")
                    return True
                    
        except:
            print("   No alert found")
            
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
        
    finally:
        driver.save_screenshot("/home/herb/Desktop/OurLibrary/registration_test.png")
        driver.quit()

if __name__ == "__main__":
    success = test_registration_redirect()
    print(f"\n🎯 REDIRECT TEST RESULT: {'SUCCESS' if success else 'FAILED'}")