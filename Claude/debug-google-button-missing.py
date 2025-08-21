#!/usr/bin/env python3
# File: debug-google-button-missing.py
# Path: /home/herb/Desktop/OurLibrary/debug-google-button-missing.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:35PM
# DEBUG WHY GOOGLE OAUTH BUTTON IS MISSING

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_google_button_missing():
    """Debug why Google OAuth button is not appearing"""
    
    print("🔍 DEBUGGING: Why Google OAuth Button is Missing")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)
    driver.maximize_window()
    
    try:
        print("\\n1. 🌐 Loading page...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&debug=button"
        driver.get(url)
        time.sleep(15)
        
        print("\\n2. 🔍 Analyzing ALL buttons on page...")
        
        # Get all buttons with detailed analysis
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   Found {len(all_buttons)} total buttons:")
        
        google_button_found = False
        for i, button in enumerate(all_buttons):
            try:
                text = button.text.strip()
                visible = button.is_displayed()
                enabled = button.is_enabled()
                classes = button.get_attribute("class")
                onclick = button.get_attribute("onclick")
                parent_id = button.find_element(By.XPATH, "..").get_attribute("id")
                
                print(f"\\n   Button {i+1}:")
                print(f"      Text: '{text}'")
                print(f"      Visible: {visible}")
                print(f"      Enabled: {enabled}")
                print(f"      Classes: {classes}")
                print(f"      OnClick: {onclick}")
                print(f"      Parent ID: {parent_id}")
                
                if 'google' in text.lower():
                    google_button_found = True
                    print(f"      🎯 GOOGLE BUTTON FOUND!")
                    
                    # Try to click it
                    if visible and enabled:
                        print(f"      🖱️ Attempting to click...")
                        button.click()
                        time.sleep(5)
                        
                        # Check what happened
                        status_text = driver.find_element(By.ID, "statusContainer").text.strip()
                        success_visible = driver.execute_script("""
                            const successStep = document.getElementById('success-step');
                            return successStep && successStep.classList.contains('active');
                        """)
                        
                        print(f"      📊 Click Result: Status='{status_text}', Success={success_visible}")
                    else:
                        print(f"      ❌ Button not clickable (visible={visible}, enabled={enabled})")
                        
            except Exception as e:
                print(f"   Button {i+1}: Error analyzing - {str(e)}")
        
        if not google_button_found:
            print("\\n❌ NO GOOGLE OAUTH BUTTON FOUND")
            
            print("\\n3. 🔍 Checking page structure...")
            
            # Check if auth steps are visible
            auth_steps = driver.execute_script("""
                return {
                    registrationStep: {
                        exists: !!document.getElementById('registration-step'),
                        active: document.getElementById('registration-step')?.classList.contains('active')
                    },
                    loginStep: {
                        exists: !!document.getElementById('login-step'),
                        active: document.getElementById('login-step')?.classList.contains('active')
                    },
                    verificationStep: {
                        exists: !!document.getElementById('verification-step'),
                        active: document.getElementById('verification-step')?.classList.contains('active')
                    },
                    successStep: {
                        exists: !!document.getElementById('success-step'),
                        active: document.getElementById('success-step')?.classList.contains('active')
                    }
                };
            """)
            
            print("   📋 Page Structure Analysis:")
            for step_name, step_data in auth_steps.items():
                print(f"      {step_name}: exists={step_data['exists']}, active={step_data['active']}")
            
            # Check for elements with 'google' in them
            google_elements = driver.execute_script("""
                const allElements = document.getElementsByTagName('*');
                const googleElements = [];
                
                for (let i = 0; i < allElements.length; i++) {
                    const element = allElements[i];
                    const text = element.textContent || '';
                    const innerHTML = element.innerHTML || '';
                    
                    if (text.toLowerCase().includes('google') || innerHTML.toLowerCase().includes('google')) {
                        googleElements.push({
                            tagName: element.tagName,
                            text: text.substring(0, 100),
                            innerHTML: innerHTML.substring(0, 200),
                            visible: element.offsetWidth > 0 && element.offsetHeight > 0,
                            id: element.id,
                            className: element.className
                        });
                    }
                }
                
                return googleElements;
            """)
            
            print(f"\\n   📋 Elements containing 'google': {len(google_elements)}")
            for i, elem in enumerate(google_elements):
                print(f"      {i+1}. {elem['tagName']} - '{elem['text'][:50]}...' (visible: {elem['visible']})")
        
        # Check if page is on wrong step
        current_step = driver.execute_script("""
            const activeStep = document.querySelector('.auth-step.active');
            return activeStep ? activeStep.id : 'none';
        """)
        
        print(f"\\n   📋 Current Active Step: {current_step}")
        
        if current_step != 'registration-step':
            print("   💡 Page might not be on registration step - Google button only shows there")
            
            # Try to go to registration step
            try:
                driver.execute_script("showStep('registration');")
                time.sleep(2)
                
                print("   🔄 Switched to registration step, rechecking...")
                
                google_buttons_after_switch = driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
                
                if google_buttons_after_switch:
                    print(f"   ✅ Found {len(google_buttons_after_switch)} Google button(s) after switching!")
                    return True
                else:
                    print("   ❌ Still no Google button after switching steps")
                    
            except Exception as e:
                print(f"   ❌ Error switching steps: {str(e)}")
        
        return google_button_found
        
    except Exception as e:
        print(f"\\n❌ DEBUG FAILED: {str(e)}")
        return False
        
    finally:
        try:
            screenshot_path = "/home/herb/Desktop/OurLibrary/debug_button_missing.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 Debug Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

if __name__ == "__main__":
    print("🎯 DEBUGGING GOOGLE OAUTH BUTTON VISIBILITY")
    print("Finding out why the Google OAuth button is not appearing\\n")
    
    found = debug_google_button_missing()
    
    print("\\n" + "=" * 60)
    print("🔍 DEBUG RESULTS")
    print("=" * 60)
    
    if found:
        print("✅ Google OAuth button was found")
        print("   Issue may be timing or page state related")
    else:
        print("❌ Google OAuth button is missing from the deployed page")
        print("   This explains why Google OAuth is not working")
        print("   Need to investigate HTML deployment issues")
    
    print("\\n🔧 Next steps:")
    print("   1. Check if HTML deployment is complete")
    print("   2. Verify button HTML is actually in deployed page")
    print("   3. Fix button visibility/rendering issues")