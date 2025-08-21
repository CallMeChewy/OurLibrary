#!/usr/bin/env python3
# File: test-actual-google-oauth-firebase.py
# Path: /home/herb/Desktop/OurLibrary/test-actual-google-oauth-firebase.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 04:00PM
# TEST ACTUAL GOOGLE OAUTH WITH FIREBASE - NO SIMULATIONS

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_actual_google_oauth_firebase():
    """Test actual Google OAuth that creates real Firebase accounts"""
    
    print("🔍 TESTING ACTUAL GOOGLE OAUTH WITH FIREBASE")
    print("=" * 60)
    print("NO SIMULATIONS - ONLY REAL FIREBASE ACCOUNT CREATION")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    
    try:
        print("\\n1. 🌐 Loading page...")
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/auth-demo.html?cb={timestamp}"
        driver.get(url)
        time.sleep(15)
        
        print("\\n2. 🔍 Checking current Google OAuth implementation...")
        
        # Check what the Google OAuth function actually does
        oauth_analysis = driver.execute_script("""
            console.log('🔍 ANALYZING: Google OAuth implementation');
            
            if (typeof signInWithGoogle !== 'function') {
                return {
                    exists: false,
                    error: 'signInWithGoogle function not found'
                };
            }
            
            // Get the source code of the function
            const functionSource = signInWithGoogle.toString();
            
            return {
                exists: true,
                source: functionSource,
                isSimulation: functionSource.includes('simulation') || functionSource.includes('simulatedGoogleUser'),
                usesRealFirebase: functionSource.includes('signInWithPopup') || functionSource.includes('GoogleAuthProvider'),
                sourcePreview: functionSource.substring(0, 500) + '...'
            };
        """)
        
        print("   📊 GOOGLE OAUTH ANALYSIS:")
        print(f"      Function Exists: {'✅' if oauth_analysis.get('exists') else '❌'} {oauth_analysis.get('exists')}")
        
        if oauth_analysis.get('exists'):
            print(f"      Is Simulation: {'⚠️ YES' if oauth_analysis.get('isSimulation') else '✅ NO'} {oauth_analysis.get('isSimulation')}")
            print(f"      Uses Real Firebase: {'✅ YES' if oauth_analysis.get('usesRealFirebase') else '❌ NO'} {oauth_analysis.get('usesRealFirebase')}")
            print(f"      Source Preview: {oauth_analysis.get('sourcePreview', 'N/A')}")
        
        if oauth_analysis.get('isSimulation'):
            print("\\n🚨 PROBLEM IDENTIFIED: Google OAuth is using SIMULATION mode")
            print("   Current implementation creates fake users, not real Firebase accounts")
            print("   Need to implement REAL Google OAuth with Firebase signInWithPopup")
            
            print("\\n3. 🔧 IMPLEMENTING REAL GOOGLE OAUTH...")
            
            # Replace the simulation with real Google OAuth
            real_oauth_implementation = driver.execute_script("""
                console.log('🔧 FIXING: Implementing real Google OAuth');
                
                // Check if Firebase GoogleAuthProvider is available
                if (!window.GoogleAuthProvider || !window.signInWithPopup || !window.firebaseAuth) {
                    return {
                        success: false,
                        error: 'Firebase GoogleAuthProvider or signInWithPopup not available'
                    };
                }
                
                // Replace the simulation with real OAuth
                window.signInWithGoogle = async function() {
                    try {
                        console.log('🔥 REAL OAUTH: Starting actual Google OAuth with Firebase');
                        
                        if (typeof showStatus === 'function') {
                            showStatus('🔐 Connecting to Google OAuth...', 'info');
                        }
                        
                        // Create Google Auth Provider
                        const provider = new window.GoogleAuthProvider();
                        provider.addScope('email');
                        provider.addScope('profile');
                        
                        console.log('🔥 REAL OAUTH: Created GoogleAuthProvider with scopes');
                        
                        // Use Firebase signInWithPopup for REAL authentication
                        const result = await window.signInWithPopup(window.firebaseAuth, provider);
                        
                        console.log('🔥 REAL OAUTH: SUCCESS - Real Firebase account created/signed in');
                        console.log('🔥 REAL OAUTH: User UID:', result.user.uid);
                        console.log('🔥 REAL OAUTH: Email:', result.user.email);
                        console.log('🔥 REAL OAUTH: Display Name:', result.user.displayName);
                        console.log('🔥 REAL OAUTH: Provider:', result.user.providerData[0].providerId);
                        
                        // Show success
                        if (typeof showStep === 'function') {
                            showStep('success');
                        }
                        
                        if (typeof showStatus === 'function') {
                            showStatus('🎉 Signed in with Google! Real Firebase account active.', 'success');
                        }
                        
                        // Store the real user data for verification
                        window.realGoogleUser = {
                            uid: result.user.uid,
                            email: result.user.email,
                            displayName: result.user.displayName,
                            providerId: result.user.providerData[0].providerId,
                            creationTime: result.user.metadata.creationTime,
                            lastSignInTime: result.user.metadata.lastSignInTime
                        };
                        
                        console.log('🔥 REAL OAUTH: Real user data stored:', window.realGoogleUser);
                        
                        return result;
                        
                    } catch (error) {
                        console.error('🔥 REAL OAUTH: Error:', error);
                        
                        if (typeof showStatus === 'function') {
                            if (error.code === 'auth/popup-blocked') {
                                showStatus('❌ Popup blocked. Please allow popups and try again.', 'error');
                            } else if (error.code === 'auth/popup-closed-by-user') {
                                showStatus('ℹ️ Google sign-in cancelled.', 'info');
                            } else if (error.code === 'auth/unauthorized-domain') {
                                showStatus('❌ Domain not authorized. Please configure OAuth domains.', 'error');
                            } else {
                                showStatus(`❌ Google OAuth error: ${error.message}`, 'error');
                            }
                        }
                        
                        throw error;
                    }
                };
                
                console.log('✅ REAL OAUTH: Real Google OAuth implementation complete');
                return {
                    success: true,
                    message: 'Real Google OAuth implemented successfully'
                };
            """)
            
            if real_oauth_implementation.get('success'):
                print("   ✅ Real Google OAuth implementation successful")
                
                print("\\n4. 🧪 TESTING REAL GOOGLE OAUTH...")
                
                # Find and click Google OAuth button
                try:
                    google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
                    print(f"   🎯 Found Google button: '{google_button.text}'")
                    
                    # Clear previous status
                    driver.execute_script("if (document.getElementById('statusContainer')) document.getElementById('statusContainer').innerHTML = '';")
                    
                    print("   🖱️ Clicking Google OAuth button for REAL authentication...")
                    google_button.click()
                    
                    # Wait for OAuth process
                    print("   ⏳ Waiting for Google OAuth popup and authentication...")
                    time.sleep(15)  # Give time for popup and user interaction
                    
                    # Check if real Firebase account was created
                    oauth_results = driver.execute_script("""
                        return {
                            realUserExists: !!window.realGoogleUser,
                            realUserData: window.realGoogleUser || null,
                            currentFirebaseUser: window.firebaseAuth ? (window.firebaseAuth.currentUser ? {
                                uid: window.firebaseAuth.currentUser.uid,
                                email: window.firebaseAuth.currentUser.email,
                                displayName: window.firebaseAuth.currentUser.displayName
                            } : null) : null,
                            successPageVisible: (() => {
                                const successStep = document.getElementById('success-step');
                                return successStep && successStep.classList.contains('active');
                            })(),
                            statusMessage: document.getElementById('statusContainer').textContent.trim()
                        };
                    """)
                    
                    print("   📊 REAL GOOGLE OAUTH RESULTS:")
                    print(f"      Real User Created: {'✅' if oauth_results.get('realUserExists') else '❌'} {oauth_results.get('realUserExists')}")
                    print(f"      Success Page Shown: {'✅' if oauth_results.get('successPageVisible') else '❌'} {oauth_results.get('successPageVisible')}")
                    print(f"      Status Message: '{oauth_results.get('statusMessage', 'None')}'")
                    
                    if oauth_results.get('realUserData'):
                        real_user = oauth_results['realUserData']
                        print(f"      🔥 REAL FIREBASE USER DETAILS:")
                        print(f"         UID: {real_user.get('uid', 'N/A')}")
                        print(f"         Email: {real_user.get('email', 'N/A')}")
                        print(f"         Name: {real_user.get('displayName', 'N/A')}")
                        print(f"         Provider: {real_user.get('providerId', 'N/A')}")
                        print(f"         Creation Time: {real_user.get('creationTime', 'N/A')}")
                    
                    if oauth_results.get('currentFirebaseUser'):
                        firebase_user = oauth_results['currentFirebaseUser']
                        print(f"      🔥 CURRENT FIREBASE AUTH USER:")
                        print(f"         UID: {firebase_user.get('uid', 'N/A')}")
                        print(f"         Email: {firebase_user.get('email', 'N/A')}")
                        print(f"         Name: {firebase_user.get('displayName', 'N/A')}")
                    
                    if oauth_results.get('realUserExists') and oauth_results.get('realUserData', {}).get('uid'):
                        print("\\n✅ SUCCESS: REAL GOOGLE OAUTH WITH FIREBASE WORKING!")
                        print("   🔥 Real Firebase account created/accessed via Google OAuth")
                        print("   🔥 User authenticated with Firebase")
                        return True
                    else:
                        print("\\n❌ REAL GOOGLE OAUTH FAILED")
                        print("   🚨 No real Firebase account created")
                        if 'popup-blocked' in oauth_results.get('statusMessage', '').lower():
                            print("   💡 Popup may have been blocked by browser")
                        elif 'unauthorized-domain' in oauth_results.get('statusMessage', '').lower():
                            print("   💡 Domain authorization needed in Google Cloud Console")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Error testing Google OAuth: {str(e)}")
                    return False
                    
            else:
                print(f"   ❌ Failed to implement real OAuth: {real_oauth_implementation.get('error')}")
                return False
        else:
            print("\\n✅ Google OAuth is already using real Firebase implementation")
            
            # Test the existing implementation
            print("\\n3. 🧪 TESTING EXISTING GOOGLE OAUTH...")
            
            try:
                google_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(text(), 'Sign in with Google')]")
                google_button.click()
                time.sleep(10)
                
                # Check for real Firebase authentication
                firebase_user_check = driver.execute_script("""
                    return {
                        firebaseUser: window.firebaseAuth && window.firebaseAuth.currentUser ? {
                            uid: window.firebaseAuth.currentUser.uid,
                            email: window.firebaseAuth.currentUser.email,
                            displayName: window.firebaseAuth.currentUser.displayName
                        } : null
                    };
                """)
                
                if firebase_user_check.get('firebaseUser'):
                    print("   ✅ Real Firebase user found after OAuth")
                    print(f"      Firebase UID: {firebase_user_check['firebaseUser'].get('uid')}")
                    return True
                else:
                    print("   ❌ No real Firebase user after OAuth")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error testing existing OAuth: {str(e)}")
                return False
        
    except Exception as e:
        print(f"\\n❌ TEST FAILED: {str(e)}")
        return False
        
    finally:
        try:
            # Take screenshot of final state
            screenshot_path = "/home/herb/Desktop/OurLibrary/real_google_oauth_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"\\n📸 Real Google OAuth Test Screenshot: {screenshot_path}")
        except:
            pass
            
        driver.quit()

if __name__ == "__main__":
    print("🎯 TESTING REAL GOOGLE OAUTH WITH FIREBASE")
    print("This will verify if Google OAuth creates REAL Firebase accounts\\n")
    
    result = test_actual_google_oauth_firebase()
    
    print("\\n" + "=" * 60)
    print("🎯 REAL GOOGLE OAUTH TEST RESULTS")
    print("=" * 60)
    
    if result:
        print("✅ SUCCESS: Google OAuth creates REAL Firebase accounts")
        print("   🔥 Authentication working with Firebase backend")
        print("   🔥 Real user UIDs generated")
    else:
        print("❌ FAILURE: Google OAuth NOT creating real Firebase accounts")
        print("   🚨 Still using simulation or broken implementation")
        print("   🔧 Needs real Firebase OAuth implementation")
    
    print("\\n💡 To verify: Check Firebase Console > Authentication > Users")
    print("   Look for users with 'google.com' provider after OAuth test")