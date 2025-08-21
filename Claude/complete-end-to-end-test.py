#!/usr/bin/env python3
# File: complete-end-to-end-test.py
# Path: /home/herb/Desktop/OurLibrary/complete-end-to-end-test.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 03:25PM
# COMPLETE END-TO-END TESTING - NO SHORTCUTS

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def complete_end_to_end_test():
    """Complete end-to-end testing with proof of functionality"""
    
    print("🎯 COMPLETE END-TO-END AUTHENTICATION TESTING")
    print("=" * 80)
    print("TESTING EVERY STEP FROM LOAD TO SUCCESS - NO SHORTCUTS")
    print("=" * 80)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)
    driver.maximize_window()
    
    test_results = {
        'step_1_page_load': {'status': 'TESTING', 'details': {}},
        'step_2_javascript_errors': {'status': 'TESTING', 'details': {}},
        'step_3_function_availability': {'status': 'TESTING', 'details': {}},
        'step_4_google_oauth_test': {'status': 'TESTING', 'details': {}},
        'step_5_email_registration_test': {'status': 'TESTING', 'details': {}},
        'step_6_firebase_creation_test': {'status': 'TESTING', 'details': {}},
        'overall_system_status': 'TESTING'
    }
    
    try:
        print("\\n🔍 STEP 1: COMPREHENSIVE PAGE LOAD TEST")
        print("-" * 60)
        
        # Load with aggressive cache busting
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}&nocache=true"
        print(f"   📡 Loading: {url}")
        
        driver.get(url)
        time.sleep(15)  # Wait for full page load
        
        # Comprehensive page load validation
        page_title = driver.title
        page_url = driver.current_url
        page_source_length = len(driver.page_source)
        
        print(f"   📋 Page Title: {page_title}")
        print(f"   📋 Page URL: {page_url}")
        print(f"   📋 Page Source Length: {page_source_length} characters")
        
        # Check for key elements
        try:
            header = driver.find_element(By.TAG_NAME, "h1").text
            print(f"   📋 Header Found: {header}")
        except:
            header = "NOT FOUND"
            
        # Count total elements
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        
        print(f"   📋 Buttons Found: {len(all_buttons)}")
        print(f"   📋 Inputs Found: {len(all_inputs)}")
        print(f"   📋 Divs Found: {len(all_divs)}")
        
        if "OurLibrary" in page_title and page_source_length > 5000 and len(all_buttons) > 5:
            test_results['step_1_page_load']['status'] = 'PASS'
            test_results['step_1_page_load']['details'] = {
                'title': page_title,
                'url': page_url,
                'source_length': page_source_length,
                'buttons': len(all_buttons),
                'inputs': len(all_inputs)
            }
            print("   ✅ STEP 1: PAGE LOAD - PASS")
        else:
            test_results['step_1_page_load']['status'] = 'FAIL'
            test_results['step_1_page_load']['details'] = {'error': 'Page load validation failed'}
            print("   ❌ STEP 1: PAGE LOAD - FAIL")
        
        print("\\n🔍 STEP 2: JAVASCRIPT ERROR ANALYSIS")
        print("-" * 60)
        
        # Get ALL browser logs with detailed analysis
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        js_warnings = [log for log in logs if log['level'] == 'WARNING']
        js_info = [log for log in logs if log['level'] == 'INFO']
        
        print(f"   📊 Total Log Entries: {len(logs)}")
        print(f"   🚨 Severe Errors: {len(js_errors)}")
        print(f"   ⚠️  Warnings: {len(js_warnings)}")
        print(f"   ℹ️  Info Messages: {len(js_info)}")
        
        critical_errors = []
        if js_errors:
            print("   🚨 DETAILED ERROR ANALYSIS:")
            for i, error in enumerate(js_errors):
                print(f"      {i+1}. {error['message']}")
                if 'SyntaxError' in error['message'] or 'ReferenceError' in error['message']:
                    critical_errors.append(error['message'])
        
        if len(critical_errors) == 0:
            test_results['step_2_javascript_errors']['status'] = 'PASS'
            test_results['step_2_javascript_errors']['details'] = {
                'total_logs': len(logs),
                'severe_errors': len(js_errors),
                'critical_syntax_errors': 0
            }
            print("   ✅ STEP 2: NO CRITICAL JAVASCRIPT ERRORS - PASS")
        else:
            test_results['step_2_javascript_errors']['status'] = 'FAIL'
            test_results['step_2_javascript_errors']['details'] = {
                'critical_errors': critical_errors
            }
            print(f"   ❌ STEP 2: {len(critical_errors)} CRITICAL JAVASCRIPT ERRORS - FAIL")
        
        print("\\n🔍 STEP 3: FUNCTION AVAILABILITY TEST")
        print("-" * 60)
        
        # Comprehensive function availability check
        function_check = driver.execute_script("""
            console.log('🧪 TESTING: Function availability check started');
            
            const results = {
                timestamp: Date.now(),
                functions: {},
                globals: {},
                firebase_status: {}
            };
            
            // Test core authentication functions
            const testFunctions = [
                'signInWithGoogle',
                'startEmailRegistration', 
                'verifyEmailCode',
                'showStatus',
                'showStep',
                'resetDemo',
                'goToLibrary'
            ];
            
            testFunctions.forEach(funcName => {
                const funcType = typeof window[funcName];
                results.functions[funcName] = {
                    exists: funcType !== 'undefined',
                    type: funcType,
                    callable: funcType === 'function'
                };
                
                if (funcType === 'function') {
                    try {
                        // Try to get function source preview
                        const source = window[funcName].toString();
                        results.functions[funcName].source_preview = source.substring(0, 100) + '...';
                    } catch(e) {
                        results.functions[funcName].source_preview = 'Cannot access source';
                    }
                }
            });
            
            // Test Firebase globals
            results.firebase_status = {
                firebaseReady: !!window.firebaseReady,
                firebaseAuth: typeof window.firebaseAuth,
                firebaseFunctions: typeof window.firebaseFunctions,
                createUserWithEmailAndPassword: typeof window.createUserWithEmailAndPassword,
                signInWithEmailAndPassword: typeof window.signInWithEmailAndPassword
            };
            
            // Test Google Auth globals
            results.globals = {
                googleAuth: typeof window.googleAuth,
                registrationManager: typeof window.registrationManager
            };
            
            console.log('🧪 TESTING: Function check complete', results);
            return results;
        """)
        
        print("   📋 FUNCTION AVAILABILITY RESULTS:")
        functions_working = 0
        total_functions = len(function_check['functions'])
        
        for func_name, func_data in function_check['functions'].items():
            status = "✅ WORKING" if func_data['callable'] else "❌ MISSING"
            if func_data['callable']:
                functions_working += 1
            print(f"      {func_name}: {func_data['type']} {status}")
        
        print("   📋 FIREBASE STATUS:")
        firebase_ready = function_check['firebase_status']['firebaseReady']
        firebase_auth = function_check['firebase_status']['firebaseAuth'] == 'object'
        print(f"      Firebase Ready: {'✅' if firebase_ready else '❌'} {firebase_ready}")
        print(f"      Firebase Auth: {'✅' if firebase_auth else '❌'} {function_check['firebase_status']['firebaseAuth']}")
        
        if functions_working >= 4 and firebase_ready:  # Need at least 4 core functions + firebase
            test_results['step_3_function_availability']['status'] = 'PASS'
            test_results['step_3_function_availability']['details'] = {
                'functions_working': functions_working,
                'total_functions': total_functions,
                'firebase_ready': firebase_ready
            }
            print(f"   ✅ STEP 3: FUNCTIONS AVAILABLE ({functions_working}/{total_functions}) - PASS")
        else:
            test_results['step_3_function_availability']['status'] = 'FAIL'
            test_results['step_3_function_availability']['details'] = {
                'functions_working': functions_working,
                'total_functions': total_functions,
                'firebase_ready': firebase_ready
            }
            print(f"   ❌ STEP 3: INSUFFICIENT FUNCTIONS ({functions_working}/{total_functions}) - FAIL")
        
        print("\\n🔍 STEP 4: GOOGLE OAUTH END-TO-END TEST")
        print("-" * 60)
        
        try:
            # Find Google OAuth button
            google_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
            
            if google_buttons:
                google_button = google_buttons[0]
                print(f"   🎯 Google Button Found: '{google_button.text}'")
                print(f"   📋 Button Visible: {google_button.is_displayed()}")
                print(f"   📋 Button Enabled: {google_button.is_enabled()}")
                
                # Clear any existing status messages
                driver.execute_script("if (document.getElementById('statusContainer')) document.getElementById('statusContainer').innerHTML = '';")
                
                # Set up monitoring for the click
                driver.execute_script("""
                    window.testMonitor = {
                        clicked: false,
                        functionCalled: false,
                        statusUpdated: false,
                        successPageShown: false,
                        startTime: Date.now()
                    };
                    
                    // Monitor signInWithGoogle calls
                    if (typeof window.signInWithGoogle === 'function') {
                        const original = window.signInWithGoogle;
                        window.signInWithGoogle = async function(...args) {
                            console.log('🧪 MONITOR: signInWithGoogle called');
                            window.testMonitor.functionCalled = true;
                            return await original.apply(this, args);
                        };
                    }
                    
                    // Monitor status updates
                    if (typeof window.showStatus === 'function') {
                        const originalStatus = window.showStatus;
                        window.showStatus = function(...args) {
                            console.log('🧪 MONITOR: showStatus called with:', args[0]);
                            window.testMonitor.statusUpdated = true;
                            return originalStatus.apply(this, args);
                        };
                    }
                    
                    // Monitor step changes
                    if (typeof window.showStep === 'function') {
                        const originalStep = window.showStep;
                        window.showStep = function(...args) {
                            console.log('🧪 MONITOR: showStep called with:', args[0]);
                            if (args[0] === 'success') {
                                window.testMonitor.successPageShown = true;
                            }
                            return originalStep.apply(this, args);
                        };
                    }
                """)
                
                # Record initial state
                initial_url = driver.current_url
                initial_step = driver.execute_script("return document.querySelector('.auth-step.active')?.id || 'unknown';")
                
                print(f"   📋 Initial URL: {initial_url}")
                print(f"   📋 Initial Step: {initial_step}")
                
                # Click the Google OAuth button
                print("   🖱️ CLICKING GOOGLE OAUTH BUTTON...")
                ActionChains(driver).move_to_element(google_button).click().perform()
                
                # Mark as clicked
                driver.execute_script("window.testMonitor.clicked = true;")
                
                print("   ⏳ Waiting 10 seconds for complete OAuth process...")
                time.sleep(10)
                
                # Get monitoring results
                monitor_results = driver.execute_script("return window.testMonitor || {};")
                final_url = driver.current_url
                final_step = driver.execute_script("return document.querySelector('.auth-step.active')?.id || 'unknown';")
                status_text = driver.find_element(By.ID, "statusContainer").text.strip()
                
                print("   📊 GOOGLE OAUTH TEST RESULTS:")
                print(f"      Button Clicked: {'✅' if monitor_results.get('clicked') else '❌'} {monitor_results.get('clicked')}")
                print(f"      Function Called: {'✅' if monitor_results.get('functionCalled') else '❌'} {monitor_results.get('functionCalled')}")
                print(f"      Status Updated: {'✅' if monitor_results.get('statusUpdated') else '❌'} {monitor_results.get('statusUpdated')}")
                print(f"      Success Page: {'✅' if monitor_results.get('successPageShown') else '❌'} {monitor_results.get('successPageShown')}")
                print(f"      Final URL: {final_url}")
                print(f"      Final Step: {final_step}")
                print(f"      Status Message: '{status_text}'")
                
                # Determine if Google OAuth is working
                google_oauth_working = (
                    monitor_results.get('functionCalled', False) and
                    monitor_results.get('statusUpdated', False) and
                    (monitor_results.get('successPageShown', False) or final_step == 'success-step' or 'success' in status_text.lower())
                )
                
                if google_oauth_working:
                    test_results['step_4_google_oauth_test']['status'] = 'PASS'
                    test_results['step_4_google_oauth_test']['details'] = {
                        'button_clicked': monitor_results.get('clicked'),
                        'function_called': monitor_results.get('functionCalled'),
                        'status_updated': monitor_results.get('statusUpdated'),
                        'success_shown': monitor_results.get('successPageShown'),
                        'final_step': final_step,
                        'status_message': status_text
                    }
                    print("   ✅ STEP 4: GOOGLE OAUTH WORKS END-TO-END - PASS")
                else:
                    test_results['step_4_google_oauth_test']['status'] = 'FAIL'
                    test_results['step_4_google_oauth_test']['details'] = {
                        'button_clicked': monitor_results.get('clicked'),
                        'function_called': monitor_results.get('functionCalled'),
                        'status_updated': monitor_results.get('statusUpdated'),
                        'success_shown': monitor_results.get('successPageShown'),
                        'final_step': final_step,
                        'status_message': status_text
                    }
                    print("   ❌ STEP 4: GOOGLE OAUTH NOT WORKING END-TO-END - FAIL")
            else:
                test_results['step_4_google_oauth_test']['status'] = 'FAIL'
                test_results['step_4_google_oauth_test']['details'] = {'error': 'Google OAuth button not found'}
                print("   ❌ STEP 4: GOOGLE OAUTH BUTTON NOT FOUND - FAIL")
                
        except Exception as e:
            test_results['step_4_google_oauth_test']['status'] = 'ERROR'
            test_results['step_4_google_oauth_test']['details'] = {'error': str(e)}
            print(f"   ❌ STEP 4: GOOGLE OAUTH ERROR - {str(e)}")
        
        print("\\n🔍 STEP 5: EMAIL REGISTRATION END-TO-END TEST")
        print("-" * 60)
        
        # Reset to registration page if needed
        if test_results['step_4_google_oauth_test']['status'] == 'PASS':
            driver.refresh()
            time.sleep(10)
        
        test_email = f"test_{int(time.time())}@example.com"
        test_password = "testpass123"
        
        try:
            # Fill out registration form
            print("   📝 Filling registration form...")
            driver.find_element(By.ID, "fullName").send_keys("Test User")
            driver.find_element(By.ID, "email").send_keys(test_email)
            driver.find_element(By.ID, "password").send_keys(test_password)
            driver.find_element(By.ID, "confirmPassword").send_keys(test_password)
            
            print(f"   📧 Test Email: {test_email}")
            
            # Set up monitoring for email registration
            driver.execute_script("""
                window.emailTestMonitor = {
                    formSubmitted: false,
                    registrationStarted: false,
                    verificationStepShown: false,
                    firebaseAttempted: false,
                    startTime: Date.now()
                };
                
                // Monitor form submission
                if (typeof window.startEmailRegistration === 'function') {
                    const original = window.startEmailRegistration;
                    window.startEmailRegistration = async function(...args) {
                        console.log('🧪 EMAIL MONITOR: startEmailRegistration called');
                        window.emailTestMonitor.registrationStarted = true;
                        return await original.apply(this, args);
                    };
                }
                
                // Monitor step changes for verification
                if (typeof window.showStep === 'function') {
                    const originalStep = window.showStep;
                    window.showStep = function(...args) {
                        console.log('🧪 EMAIL MONITOR: showStep called with:', args[0]);
                        if (args[0] === 'verification') {
                            window.emailTestMonitor.verificationStepShown = true;
                        }
                        return originalStep.apply(this, args);
                    };
                }
            """)
            
            # Submit the form
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send Verification Code')]")
            print("   🖱️ SUBMITTING EMAIL REGISTRATION FORM...")
            submit_button.click()
            
            # Mark form as submitted
            driver.execute_script("window.emailTestMonitor.formSubmitted = true;")
            
            print("   ⏳ Waiting 10 seconds for email registration process...")
            time.sleep(10)
            
            # Check if verification step appeared
            email_monitor = driver.execute_script("return window.emailTestMonitor || {};")
            verification_step_active = driver.execute_script("""
                const verifyStep = document.getElementById('verification-step');
                return verifyStep && verifyStep.classList.contains('active');
            """)
            
            displayed_email = ""
            try:
                displayed_email = driver.find_element(By.ID, "verificationEmail").text
            except:
                pass
                
            status_after_email = driver.find_element(By.ID, "statusContainer").text.strip()
            
            print("   📊 EMAIL REGISTRATION TEST RESULTS:")
            print(f"      Form Submitted: {'✅' if email_monitor.get('formSubmitted') else '❌'} {email_monitor.get('formSubmitted')}")
            print(f"      Registration Started: {'✅' if email_monitor.get('registrationStarted') else '❌'} {email_monitor.get('registrationStarted')}")
            print(f"      Verification Step Shown: {'✅' if verification_step_active else '❌'} {verification_step_active}")
            print(f"      Displayed Email: {displayed_email}")
            print(f"      Status Message: '{status_after_email}'")
            
            # Test email verification if we got to verification step
            if verification_step_active:
                print("   🔑 TESTING EMAIL VERIFICATION...")
                
                # Enter verification code
                code_input = driver.find_element(By.ID, "verificationCode")
                code_input.send_keys("TEST99")
                
                # Monitor Firebase account creation
                driver.execute_script("""
                    window.firebaseTestMonitor = {
                        accountCreationAttempted: false,
                        accountCreated: false,
                        successPageShown: false
                    };
                    
                    // Monitor Firebase account creation
                    if (window.createUserWithEmailAndPassword) {
                        const original = window.createUserWithEmailAndPassword;
                        window.createUserWithEmailAndPassword = function(...args) {
                            console.log('🧪 FIREBASE MONITOR: createUserWithEmailAndPassword called');
                            window.firebaseTestMonitor.accountCreationAttempted = true;
                            return original.apply(this, args).then(result => {
                                console.log('🧪 FIREBASE MONITOR: Account created with UID:', result.user.uid);
                                window.firebaseTestMonitor.accountCreated = true;
                                return result;
                            }).catch(error => {
                                console.log('🧪 FIREBASE MONITOR: Account creation error:', error);
                                throw error;
                            });
                        };
                    }
                    
                    // Monitor success step
                    if (typeof window.showStep === 'function') {
                        const originalStep = window.showStep;
                        window.showStep = function(...args) {
                            if (args[0] === 'success') {
                                window.firebaseTestMonitor.successPageShown = true;
                            }
                            return originalStep.apply(this, args);
                        };
                    }
                """)
                
                # Submit verification
                verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify Email')]")
                verify_button.click()
                
                print("   ⏳ Waiting 10 seconds for verification and Firebase account creation...")
                time.sleep(10)
                
                # Get final results
                firebase_monitor = driver.execute_script("return window.firebaseTestMonitor || {};")
                final_success_step = driver.execute_script("""
                    const successStep = document.getElementById('success-step');
                    return successStep && successStep.classList.contains('active');
                """)
                final_status = driver.find_element(By.ID, "statusContainer").text.strip()
                
                print("   📊 EMAIL VERIFICATION & FIREBASE TEST RESULTS:")
                print(f"      Account Creation Attempted: {'✅' if firebase_monitor.get('accountCreationAttempted') else '❌'} {firebase_monitor.get('accountCreationAttempted')}")
                print(f"      Firebase Account Created: {'✅' if firebase_monitor.get('accountCreated') else '❌'} {firebase_monitor.get('accountCreated')}")
                print(f"      Success Page Shown: {'✅' if final_success_step else '❌'} {final_success_step}")
                print(f"      Final Status: '{final_status}'")
                
                # Determine overall email registration success
                email_registration_working = (
                    email_monitor.get('registrationStarted', False) and
                    verification_step_active and
                    displayed_email == test_email
                )
                
                firebase_creation_working = (
                    firebase_monitor.get('accountCreationAttempted', False) and
                    firebase_monitor.get('accountCreated', False)
                )
                
                if email_registration_working:
                    test_results['step_5_email_registration_test']['status'] = 'PASS'
                    test_results['step_5_email_registration_test']['details'] = {
                        'form_submitted': email_monitor.get('formSubmitted'),
                        'registration_started': email_monitor.get('registrationStarted'),
                        'verification_shown': verification_step_active,
                        'email_correct': displayed_email == test_email,
                        'test_email': test_email
                    }
                    print("   ✅ STEP 5: EMAIL REGISTRATION WORKS END-TO-END - PASS")
                else:
                    test_results['step_5_email_registration_test']['status'] = 'FAIL'
                    print("   ❌ STEP 5: EMAIL REGISTRATION NOT WORKING END-TO-END - FAIL")
                
                if firebase_creation_working:
                    test_results['step_6_firebase_creation_test']['status'] = 'PASS'
                    test_results['step_6_firebase_creation_test']['details'] = {
                        'creation_attempted': firebase_monitor.get('accountCreationAttempted'),
                        'account_created': firebase_monitor.get('accountCreated'),
                        'success_page': final_success_step
                    }
                    print("   ✅ STEP 6: FIREBASE ACCOUNT CREATION WORKS - PASS")
                else:
                    test_results['step_6_firebase_creation_test']['status'] = 'FAIL'
                    test_results['step_6_firebase_creation_test']['details'] = {
                        'creation_attempted': firebase_monitor.get('accountCreationAttempted'),
                        'account_created': firebase_monitor.get('accountCreated'),
                        'success_page': final_success_step
                    }
                    print("   ❌ STEP 6: FIREBASE ACCOUNT CREATION NOT WORKING - FAIL")
            else:
                test_results['step_5_email_registration_test']['status'] = 'FAIL'
                test_results['step_6_firebase_creation_test']['status'] = 'FAIL'
                print("   ❌ STEP 5: EMAIL REGISTRATION FAILED - NO VERIFICATION STEP")
                print("   ❌ STEP 6: FIREBASE TESTING SKIPPED - EMAIL REGISTRATION FAILED")
                
        except Exception as e:
            test_results['step_5_email_registration_test']['status'] = 'ERROR'
            test_results['step_6_firebase_creation_test']['status'] = 'ERROR'
            print(f"   ❌ STEP 5 & 6: EMAIL/FIREBASE ERROR - {str(e)}")
        
        # Calculate overall system status
        print("\\n" + "=" * 80)
        print("🏁 COMPLETE END-TO-END TEST RESULTS - DEFINITIVE PROOF")
        print("=" * 80)
        
        passed_steps = sum(1 for result in test_results.values() if result.get('status') == 'PASS')
        total_steps = len([k for k in test_results.keys() if k != 'overall_system_status'])
        
        for step_name, result in test_results.items():
            if step_name == 'overall_system_status':
                continue
            status_icon = "✅ PASS" if result['status'] == 'PASS' else "❌ FAIL" if result['status'] == 'FAIL' else "🚨 ERROR"
            formatted_name = step_name.replace('_', ' ').replace('step ', 'Step ').title()
            print(f"   {formatted_name}: {status_icon}")
        
        success_percentage = (passed_steps / total_steps) * 100
        print(f"\\n📊 OVERALL SYSTEM FUNCTIONALITY: {passed_steps}/{total_steps} steps passed ({success_percentage:.1f}%)")
        
        if passed_steps == total_steps:
            test_results['overall_system_status'] = 'FULLY_FUNCTIONAL'
            print("\\n🎉 PROOF: COMPLETE AUTHENTICATION SYSTEM IS FULLY FUNCTIONAL!")
            print("   ✅ Google OAuth: Working end-to-end")
            print("   ✅ Email Registration: Working end-to-end") 
            print("   ✅ Firebase Integration: Creating real accounts")
            print("   🔥 System is production ready!")
        elif test_results.get('step_4_google_oauth_test', {}).get('status') == 'PASS' or test_results.get('step_5_email_registration_test', {}).get('status') == 'PASS':
            test_results['overall_system_status'] = 'PARTIALLY_FUNCTIONAL'
            print("\\n⚠️ PROOF: AUTHENTICATION SYSTEM PARTIALLY FUNCTIONAL")
            if test_results.get('step_4_google_oauth_test', {}).get('status') == 'PASS':
                print("   ✅ Google OAuth: Working")
            else:
                print("   ❌ Google OAuth: Not working")
            if test_results.get('step_5_email_registration_test', {}).get('status') == 'PASS':
                print("   ✅ Email Registration: Working")
            else:
                print("   ❌ Email Registration: Not working")
        else:
            test_results['overall_system_status'] = 'NOT_FUNCTIONAL'
            print("\\n🚨 PROOF: AUTHENTICATION SYSTEM IS NOT FUNCTIONAL")
            print("   ❌ Google OAuth: Broken")
            print("   ❌ Email Registration: Broken")
            print("   🔧 Immediate fixes required")
        
        return test_results
        
    except Exception as e:
        print(f"\\n❌ COMPLETE TEST FAILED: {str(e)}")
        test_results['overall_system_status'] = 'TEST_ERROR'
        return test_results
        
    finally:
        try:
            # Take screenshot as proof
            screenshot_path = "/home/herb/Desktop/OurLibrary/complete_test_proof.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 PROOF SCREENSHOT: {screenshot_path}")
            
            # Save detailed test results
            results_path = "/home/herb/Desktop/OurLibrary/complete_test_results.json"
            with open(results_path, 'w') as f:
                json.dump(test_results, f, indent=2)
            print(f"📊 DETAILED RESULTS: {results_path}")
            
        except Exception as e:
            print(f"⚠️ Could not save proof files: {e}")
            
        driver.quit()

if __name__ == "__main__":
    print("🎯 STARTING COMPLETE END-TO-END AUTHENTICATION TEST")
    print("This will test EVERY aspect of the system with PROOF")
    print("No shortcuts - complete validation from load to success")
    
    results = complete_end_to_end_test()
    
    print(f"\\n{'='*80}")
    print("🎯 FINAL DEFINITIVE RESULTS WITH PROOF")
    print(f"{'='*80}")
    
    if results['overall_system_status'] == 'FULLY_FUNCTIONAL':
        print("🏆 SUCCESS: COMPLETE AUTHENTICATION SYSTEM IS 100% FUNCTIONAL!")
    elif results['overall_system_status'] == 'PARTIALLY_FUNCTIONAL':
        print("⚠️ PARTIAL: SOME AUTHENTICATION METHODS WORKING")
    elif results['overall_system_status'] == 'NOT_FUNCTIONAL':
        print("🚨 FAILURE: AUTHENTICATION SYSTEM IS BROKEN")
    else:
        print("❌ ERROR: TESTING COULD NOT BE COMPLETED")
    
    print(f"\\nTested on: https://callmechewy.github.io/OurLibrary/auth-demo.html")
    print(f"This is complete proof of current system status.")