#!/usr/bin/env python3
# File: monitor-github-deployment-complete.py
# Path: /home/herb/Desktop/OurLibrary/monitor-github-deployment-complete.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 06:35PM
# MONITOR: GitHub deployment until complete and verify correct page

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def check_github_deployment_status():
    """Check GitHub deployment status and verify correct page content"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&deployment_monitor=true"
        
        driver.get(url)
        time.sleep(5)
        
        # Check page content and deployment status
        page_info = driver.execute_script("""
            const html = document.documentElement.innerHTML;
            return {
                pageTitle: document.title,
                hasOldFakeCode: html.includes('For demo purposes, we\\'ll simulate verification'),
                hasNewRealCode: html.includes('CRITICAL FIX: Real verification code check'),
                hasCodeGeneration: html.includes('Math.random().toString(36).substr(2, 6)'),
                hasVisibilityFix: html.includes('🔑 YOUR VERIFICATION CODE:'),
                hasEmailDisplayFix: html.includes('emailDisplay.innerHTML'),
                lastModified: document.lastModified,
                currentTime: new Date().toISOString(),
                pageSize: html.length,
                hasBackToSMTP: html.includes('Back to SMTP Test'),
                hasSecureAuthDemo: html.includes('Secure Auth Demo'),
                registrationStepExists: !!document.getElementById('registration-step'),
                verificationStepExists: !!document.getElementById('verification-step'),
                successStepExists: !!document.getElementById('success-step')
            };
        """)
        
        # Take screenshot for comparison
        screenshot_path = f"/home/herb/Desktop/OurLibrary/deployment_check_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        
        return page_info, screenshot_path
        
    except Exception as e:
        return {"error": str(e)}, None
        
    finally:
        driver.quit()

def test_registration_screen_appearance():
    """Test what the registration screen actually looks like"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    try:
        url = "https://callmechewy.github.io/OurLibrary/auth-demo.html"
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "registration-step"))
        )
        time.sleep(5)
        
        # Check registration screen elements
        screen_info = driver.execute_script("""
            return {
                title: document.title,
                registrationVisible: document.getElementById('registration-step').classList.contains('active'),
                hasGoogleButton: !!document.querySelector('button[onclick*="signInWithGoogle"]'),
                hasEmailForm: !!document.getElementById('email'),
                hasFullNameField: !!document.getElementById('fullName'),
                hasPasswordField: !!document.getElementById('password'),
                hasConfirmPasswordField: !!document.getElementById('confirmPassword'),
                hasSubmitButton: !!document.querySelector('button[type="submit"]'),
                pageStructure: {
                    steps: Array.from(document.querySelectorAll('.step')).map(s => s.textContent),
                    activeStep: document.querySelector('.step.active')?.textContent,
                    formFields: Array.from(document.querySelectorAll('input')).map(i => i.id)
                }
            };
        """)
        
        # Fill form to test progression
        driver.find_element(By.ID, "fullName").send_keys("Screen Test")
        driver.find_element(By.ID, "email").send_keys("screentest@example.com")
        driver.find_element(By.ID, "password").send_keys("test123")
        driver.find_element(By.ID, "confirmPassword").send_keys("test123")
        
        # Take screenshot of registration screen
        reg_screenshot = "/home/herb/Desktop/OurLibrary/registration_screen_check.png"
        driver.save_screenshot(reg_screenshot)
        
        # Submit to see verification screen
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
        submit_button.click()
        
        time.sleep(8)
        
        # Check verification screen
        verification_info = driver.execute_script("""
            return {
                verificationActive: document.getElementById('verification-step').classList.contains('active'),
                emailDisplay: document.getElementById('verificationEmail').textContent,
                statusMessage: document.getElementById('statusContainer').textContent,
                generatedCode: window.pendingVerificationCode,
                hasCodeInput: !!document.getElementById('verificationCode'),
                hasVerifyButton: !!document.querySelector('button[onclick*="verifyEmailCode"]')
            };
        """)
        
        # Take screenshot of verification screen
        verify_screenshot = "/home/herb/Desktop/OurLibrary/verification_screen_check.png"
        driver.save_screenshot(verify_screenshot)
        
        return {
            "registration": screen_info,
            "verification": verification_info,
            "screenshots": {
                "registration": reg_screenshot,
                "verification": verify_screenshot
            }
        }
        
    except Exception as e:
        return {"error": str(e)}
        
    finally:
        driver.quit()

def monitor_deployment_until_complete():
    """Monitor GitHub deployment until complete"""
    
    print("🔄 MONITORING GITHUB DEPLOYMENT UNTIL COMPLETE")
    print("=" * 70)
    print("OBJECTIVE: Verify deployment and check if we're deploying wrong page")
    print("=" * 70)
    
    attempt = 0
    max_attempts = 20
    
    while attempt < max_attempts:
        attempt += 1
        current_time = time.strftime('%H:%M:%S')
        
        print(f"\\n🔍 DEPLOYMENT CHECK {attempt}/20 - {current_time}")
        
        # Check deployment status
        deployment_info, screenshot_path = check_github_deployment_status()
        
        if "error" not in deployment_info:
            print("   📄 PAGE CONTENT ANALYSIS:")
            print(f"      Page title: {deployment_info['pageTitle']}")
            print(f"      Page size: {deployment_info['pageSize']} characters")
            print(f"      Last modified: {deployment_info['lastModified']}")
            print(f"      Has 'Secure Auth Demo': {deployment_info['hasSecureAuthDemo']}")
            print(f"      Has 'Back to SMTP Test': {deployment_info['hasBackToSMTP']}")
            
            print("   🔧 DEPLOYMENT STATUS:")
            print(f"      Old fake code: {deployment_info['hasOldFakeCode']}")
            print(f"      New real code: {deployment_info['hasNewRealCode']}")
            print(f"      Code generation: {deployment_info['hasCodeGeneration']}")
            print(f"      Visibility fix: {deployment_info['hasVisibilityFix']}")
            print(f"      Email display fix: {deployment_info['hasEmailDisplayFix']}")
            
            print("   🖼️ PAGE STRUCTURE:")
            print(f"      Registration step exists: {deployment_info['registrationStepExists']}")
            print(f"      Verification step exists: {deployment_info['verificationStepExists']}")
            print(f"      Success step exists: {deployment_info['successStepExists']}")
            
            if deployment_info['hasVisibilityFix'] and deployment_info['hasEmailDisplayFix']:
                print("\\n   ✅ LATEST FIXES DEPLOYED!")
                break
            else:
                print("\\n   ⏳ Still waiting for latest fixes...")
        else:
            print(f"   ❌ Error checking deployment: {deployment_info['error']}")
        
        if attempt < max_attempts:
            print(f"   ⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    # Final test of registration screen appearance
    print(f"\\n🖼️ TESTING REGISTRATION SCREEN APPEARANCE...")
    screen_test = test_registration_screen_appearance()
    
    if "error" not in screen_test:
        print("   📱 REGISTRATION SCREEN:")
        reg_info = screen_test["registration"]
        print(f"      Title: {reg_info['title']}")
        print(f"      Registration visible: {reg_info['registrationVisible']}")
        print(f"      Has Google button: {reg_info['hasGoogleButton']}")
        print(f"      Has email form: {reg_info['hasEmailForm']}")
        print(f"      Form fields: {reg_info['pageStructure']['formFields']}")
        print(f"      Steps: {reg_info['pageStructure']['steps']}")
        
        print("   📧 VERIFICATION SCREEN:")
        verify_info = screen_test["verification"]
        print(f"      Verification active: {verify_info['verificationActive']}")
        print(f"      Email display: '{verify_info['emailDisplay']}'")
        print(f"      Status message: '{verify_info['statusMessage']}'")
        print(f"      Generated code: {verify_info['generatedCode']}")
        print(f"      Has code input: {verify_info['hasCodeInput']}")
        
        print(f"\\n📸 SCREENSHOTS SAVED:")
        print(f"      Registration: {screen_test['screenshots']['registration']}")
        print(f"      Verification: {screen_test['screenshots']['verification']}")
        
        if verify_info['generatedCode'] and verify_info['generatedCode'] not in verify_info['statusMessage']:
            print("\\n🚨 PROBLEM IDENTIFIED:")
            print("   Code is generated but NOT visible in status message")
            print("   This confirms user's issue - code is invisible")
            return "CODE_NOT_VISIBLE"
        elif verify_info['generatedCode'] and verify_info['generatedCode'] in verify_info['statusMessage']:
            print("\\n✅ CODE VISIBILITY FIXED:")
            print("   Generated code is now visible in status message")
            return "FIXED"
        else:
            print("\\n❓ UNCLEAR STATUS:")
            print("   Unable to determine code visibility")
            return "UNCLEAR"
    else:
        print(f"   ❌ Error testing screen: {screen_test['error']}")
        return "ERROR"

if __name__ == "__main__":
    result = monitor_deployment_until_complete()
    
    print(f"\\n🎯 DEPLOYMENT MONITORING RESULT: {result}")
    
    if result == "CODE_NOT_VISIBLE":
        print("\\n🚨 CONFIRMED: User's issue reproduced")
        print("   Verification codes are generated but invisible to users")
        print("   Need additional fix to make codes visible")
    elif result == "FIXED":
        print("\\n✅ ISSUE RESOLVED")
        print("   Verification codes are now visible to users")
        print("   User should try again")
    else:
        print(f"\\n🔍 Status unclear: {result}")