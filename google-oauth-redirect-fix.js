
/* Google OAuth Redirect Fix Patch
 * Apply this fix to resolve redirect_uri_mismatch errors
 * This implements proper redirect URI handling for GitHub Pages
 */

(function() {
    'use strict';
    
    console.log('🔧 Applying Google OAuth redirect fix patch...');
    
    // Wait for page to load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyOAuthFix);
    } else {
        applyOAuthFix();
    }
    
    function applyOAuthFix() {
        // Override the Google OAuth function with proper redirect handling
        if (typeof window.signInWithGoogle === 'function') {
            const originalSignIn = window.signInWithGoogle;
            
            window.signInWithGoogle = async function() {
                try {
                    console.log('🔧 Using patched Google OAuth with redirect fix');
                    
                    // Show loading status
                    if (typeof showStatus === 'function') {
                        showStatus('🔐 Connecting to Google (fixed redirect)...', 'info');
                    }
                    
                    // Use Google Identity Services with popup mode (no redirect needed)
                    if (typeof google !== 'undefined' && google.accounts) {
                        
                        google.accounts.id.initialize({
                            client_id: '71206584632-kocta4ifm4a1fm3ejmpkmvjc212jhnjs.apps.googleusercontent.com',
                            callback: function(response) {
                                console.log('🎉 Google OAuth successful with patch!');
                                
                                // Parse the credential response
                                try {
                                    const payload = JSON.parse(atob(response.credential.split('.')[1]));
                                    
                                    if (typeof showStep === 'function') {
                                        showStep('success');
                                    }
                                    
                                    if (typeof showStatus === 'function') {
                                        showStatus('🎉 Google sign-in successful! (Redirect fix applied)', 'success');
                                    }
                                    
                                    console.log('✅ User:', payload.email);
                                    
                                } catch (error) {
                                    console.error('Error processing Google response:', error);
                                    if (typeof showStatus === 'function') {
                                        showStatus('❌ Google sign-in processing failed', 'error');
                                    }
                                }
                            },
                            auto_select: false,
                            ux_mode: 'popup'  // This avoids redirect issues
                        });
                        
                        // Trigger the sign-in
                        google.accounts.id.prompt();
                        
                    } else {
                        throw new Error('Google Identity Services not loaded');
                    }
                    
                } catch (error) {
                    console.error('Patched Google OAuth error:', error);
                    if (typeof showStatus === 'function') {
                        showStatus('❌ Google OAuth patch failed. Using email registration instead.', 'error');
                    }
                }
            };
            
            console.log('✅ Google OAuth redirect fix patch applied');
            
            // Show notification that fix is active
            if (typeof showStatus === 'function') {
                setTimeout(() => {
                    showStatus('🔧 Google OAuth redirect fix active', 'info');
                }, 1000);
            }
        }
    }
})();
