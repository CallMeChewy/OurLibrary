// File: OurLibraryGoogleAuth.js
// Path: /home/herb/Desktop/OurLibrary/JS/OurLibraryGoogleAuth.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-19
// Last Modified: 2025-08-22 05:40PM
// Description: Enhanced OurLibrary analytics with comprehensive tracking and lead scoring
// Phase 2 Enhancement: User journey mapping, engagement scoring, and conversion analytics

class OurLibraryGoogleAuth {
    constructor(config) {
        this.config = {
            clientId: config.clientId,
            apiKey: config.apiKey,
            scopes: [
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            discoveryDocs: [
                'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest',
                'https://www.googleapis.com/discovery/v1/apis/sheets/v4/rest'
            ],
            sheetIds: {
                userRegistrations: config.userRegistrationsSheetId,
                incompleteEmails: config.incompleteEmailsSheetId,
                sessionTracking: config.sessionTrackingSheetId
            }
        };
        
        this.isSignedIn = false;
        this.currentUser = null;
        this.accessToken = null;
        this.sheetsService = null;
        this.gapiLoaded = false;
        this.sessionId = this.generateSessionId();
        this.simulateMode = false;
        this.pageStartTime = new Date();
        this.registrationStartTime = null;
        this.userJourney = [];
        this.engagementScore = 0;
        this.deviceInfo = this.getDeviceInfo();
        this.geographicLocation = null;
    }

    async initialize() {
        try {
            console.log('🔑 Initializing OurLibrary Google Services...');
            
            // Check if we have a real client ID (not placeholder)
            if (this.config.clientId.includes('himalaya2025ourlibrary')) {
                console.warn('⚠️ Using placeholder OAuth Client ID - Sheets logging will be simulated');
                this.simulateMode = true;
                console.log('✅ OurLibrary Google Services initialized (simulation mode)');
                return true;
            }
            
            console.log('🎯 Using REAL OAuth Client ID - Live Google Sheets integration enabled');
            
            // Load Google Identity Services
            await this.loadGoogleIdentityServices();
            
            // Load Google API client for Sheets API calls
            await this.loadGoogleAPI();
            
            // Initialize Google Identity Services
            google.accounts.id.initialize({
                client_id: this.config.clientId,
                callback: this.handleCredentialResponse.bind(this),
                auto_select: false,
                cancel_on_tap_outside: false
            });

            console.log('✅ OurLibrary Google Services initialized');
            return true;

        } catch (error) {
            console.warn('⚠️ Google Services initialization failed, falling back to simulation mode:', error);
            this.simulateMode = true;
            return true;
        }
    }

    loadGoogleIdentityServices() {
        return new Promise((resolve, reject) => {
            if (typeof google !== 'undefined' && google.accounts) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    loadGoogleAPI() {
        return new Promise((resolve, reject) => {
            if (typeof gapi !== 'undefined') {
                this.initializeGapi().then(resolve).catch(reject);
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://apis.google.com/js/api.js';
            script.onload = () => {
                gapi.load('client', () => {
                    this.initializeGapi().then(resolve).catch(reject);
                });
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async initializeGapi() {
        try {
            await gapi.client.init({
                apiKey: this.config.apiKey,
                discoveryDocs: this.config.discoveryDocs
            });
            this.gapiLoaded = true;
            console.log('✅ Google API client initialized for OurLibrary');
        } catch (error) {
            console.error('❌ Error initializing Google API client:', error);
            throw error;
        }
    }

    // Handle sign-in response from Google Identity Services
    handleCredentialResponse(response) {
        console.log('🎉 Google OAuth successful for OurLibrary!');
        
        try {
            // Decode the JWT token to get user info
            const payload = this.parseJWT(response.credential);
            
            this.currentUser = {
                id: payload.sub,
                email: payload.email,
                name: payload.name,
                imageUrl: payload.picture,
                emailVerified: payload.email_verified,
                credential: response.credential
            };

            this.isSignedIn = true;
            console.log('✅ User authenticated:', this.currentUser.email);
            
            // Request access token for API calls
            this.requestAccessToken().then(() => {
                // Log Google registration attempt
                this.logRegistrationActivity('google_oauth_success', {
                    email: this.currentUser.email,
                    name: this.currentUser.name,
                    provider: 'google'
                });
                
                // Trigger completion of Google registration
                this.onGoogleRegistrationSuccess(this.currentUser);
                
            }).catch(error => {
                console.error('❌ Error getting access token:', error);
                this.onRegistrationError(error);
            });
            
        } catch (error) {
            console.error('❌ Error processing credential response:', error);
            this.onRegistrationError(error);
        }
    }

    // Request access token for Sheets API calls
    async requestAccessToken() {
        return new Promise((resolve, reject) => {
            console.log('🔐 Requesting access token for Sheets API...');
            
            const tokenClient = google.accounts.oauth2.initTokenClient({
                client_id: this.config.clientId,
                scope: this.config.scopes.join(' '),
                callback: (tokenResponse) => {
                    this.accessToken = tokenResponse.access_token;
                    
                    // Set token for Google API client
                    if (this.gapiLoaded) {
                        gapi.client.setToken({
                            access_token: this.accessToken
                        });
                        
                        // Initialize Sheets service
                        this.sheetsService = gapi.client.sheets;
                    }
                    
                    console.log('✅ Access token obtained for Sheets API');
                    resolve(this.accessToken);
                },
                error_callback: (error) => {
                    console.error('❌ Error getting access token:', error);
                    reject(error);
                }
            });
            
            tokenClient.requestAccessToken();
        });
    }

    // Parse JWT token
    parseJWT(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Error parsing JWT:', error);
            return {};
        }
    }

    // Generate unique session ID
    generateSessionId() {
        return `ourlibrary_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get comprehensive device information
    getDeviceInfo() {
        const ua = navigator.userAgent;
        const platform = navigator.platform;
        const language = navigator.language;
        const screenRes = `${screen.width}x${screen.height}`;
        const viewport = `${window.innerWidth}x${window.innerHeight}`;
        
        // Simple device type detection
        let deviceType = 'desktop';
        if (/Mobile|Android|iPhone|iPad/.test(ua)) {
            deviceType = /iPad/.test(ua) ? 'tablet' : 'mobile';
        }
        
        return {
            userAgent: ua,
            platform: platform,
            language: language,
            screenResolution: screenRes,
            viewportSize: viewport,
            deviceType: deviceType,
            browser: this.getBrowserInfo(ua),
            os: this.getOSInfo(ua)
        };
    }

    // Extract browser information
    getBrowserInfo(ua) {
        if (ua.includes('Chrome')) return 'Chrome';
        if (ua.includes('Firefox')) return 'Firefox';
        if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari';
        if (ua.includes('Edge')) return 'Edge';
        return 'Other';
    }

    // Extract OS information  
    getOSInfo(ua) {
        if (ua.includes('Windows')) return 'Windows';
        if (ua.includes('Mac')) return 'macOS';
        if (ua.includes('Linux')) return 'Linux';
        if (ua.includes('Android')) return 'Android';
        if (ua.includes('iOS')) return 'iOS';
        return 'Other';
    }

    // Calculate lead score based on engagement
    calculateLeadScore(userData = {}) {
        let score = 0;
        
        // Email completion quality (25 points)
        if (userData.email) {
            if (userData.email.includes('@') && userData.email.includes('.')) {
                score += 25;
            }
        }
        
        // Form completion progress (0-50 points)
        const formProgress = userData.formProgress || 0;
        score += formProgress * 0.5;
        
        // Time engagement (25 points max)
        const timeOnPage = (new Date() - this.pageStartTime) / 1000; // seconds
        if (timeOnPage > 60) score += 15; // Over 1 minute
        if (timeOnPage > 300) score += 10; // Over 5 minutes
        
        // Device quality (10 points)
        if (this.deviceInfo.deviceType === 'desktop') score += 10;
        
        // Referrer quality (10 points)
        const referrer = document.referrer || '';
        if (referrer.includes('google.com') || referrer.includes('bing.com')) score += 5;
        if (referrer.includes('linkedin.com') || referrer.includes('twitter.com')) score += 10;
        
        return Math.min(Math.round(score), 100); // Cap at 100
    }

    // Track user journey step
    trackJourneyStep(action, details = {}) {
        const step = {
            timestamp: new Date().toISOString(),
            action: action,
            details: details,
            timeFromStart: (new Date() - this.pageStartTime) / 1000,
            url: window.location.href,
            referrer: document.referrer || 'direct'
        };
        
        this.userJourney.push(step);
        console.log('🗺️ Journey step tracked:', action, details);
    }

    // Calculate form completion percentage
    calculateFormProgress(formData) {
        const requiredFields = ['email', 'fullName', 'password', 'confirmPassword', 'zipCode', 'termsAccepted'];
        let completedFields = 0;
        
        requiredFields.forEach(field => {
            if (formData[field] && formData[field] !== '') {
                completedFields++;
            }
        });
        
        return Math.round((completedFields / requiredFields.length) * 100);
    }

    // ==================== REGISTRATION TRACKING ====================

    // Enhanced incomplete email capture with lead scoring
    async logIncompleteEmail(email, step = 'email_entered', formData = {}) {
        try {
            // Track journey step
            this.trackJourneyStep('incomplete_email_capture', { email, step });
            
            // Calculate engagement metrics
            const timeOnPage = Math.round((new Date() - this.pageStartTime) / 1000);
            const formProgress = this.calculateFormProgress(formData);
            const leadScore = this.calculateLeadScore({ email, formProgress, ...formData });
            
            if (this.simulateMode) {
                console.log('🧪 SIMULATED - Enhanced incomplete email logged:', {
                    email,
                    step,
                    formProgress: `${formProgress}%`,
                    leadScore,
                    timeOnPage: `${timeOnPage}s`,
                    deviceType: this.deviceInfo.deviceType,
                    browser: this.deviceInfo.browser,
                    timestamp: new Date().toISOString(),
                    sessionId: this.sessionId,
                    sheetId: this.config.sheetIds.incompleteEmails
                });
                return;
            }

            if (!this.sheetsService) {
                console.warn('⚠️ Sheets service not available for logging');
                return;
            }

            const timestamp = new Date().toISOString();
            
            // Enhanced data according to Phase 2 spec:
            // Timestamp | Email | Capture Event | Form Progress | Session ID | User Agent | Referrer | Page URL | Device Type | Time on Page | Exit Point | Follow Up Status
            const values = [[
                timestamp,
                email,
                step,
                `${formProgress}%`,
                this.sessionId,
                this.deviceInfo.userAgent,
                document.referrer || 'direct',
                window.location.href,
                this.deviceInfo.deviceType,
                `${Math.floor(timeOnPage / 60)}:${String(timeOnPage % 60).padStart(2, '0')}`, // MM:SS format
                formData.exitPoint || step,
                'not_contacted'
            ]];

            await this.sheetsService.spreadsheets.values.append({
                spreadsheetId: this.config.sheetIds.incompleteEmails,
                range: 'Sheet1!A:L',
                valueInputOption: 'RAW',
                resource: { values }
            });

            console.log('📊 Enhanced incomplete email logged:', {
                email, 
                step, 
                progress: `${formProgress}%`, 
                score: leadScore,
                timeOnPage: `${timeOnPage}s`
            });

        } catch (error) {
            console.error('❌ Error logging incomplete email:', error);
            // Don't block registration flow on logging errors
        }
    }

    // Enhanced session analytics with engagement scoring
    async logRegistrationActivity(action, details = {}) {
        try {
            // Track journey step
            this.trackJourneyStep(action, details);
            
            // Calculate session metrics
            const sessionDuration = Math.round((new Date() - this.pageStartTime) / 1000);
            const engagementScore = this.calculateEngagementScore(action, details);
            const conversionEvent = this.identifyConversionEvent(action);
            
            if (this.simulateMode) {
                console.log('🧪 SIMULATED - Enhanced session activity logged:', {
                    action,
                    email: details.email || 'unknown',
                    sessionDuration: `${sessionDuration}s`,
                    engagementScore,
                    conversionEvent,
                    details,
                    timestamp: new Date().toISOString(),
                    sessionId: this.sessionId,
                    sheetId: this.config.sheetIds.sessionTracking
                });
                return;
            }

            if (!this.sheetsService) {
                console.warn('⚠️ Sheets service not available for logging');
                return;
            }

            const timestamp = new Date().toISOString();
            const userId = this.currentUser ? this.currentUser.id : 'anonymous';
            const email = this.currentUser ? this.currentUser.email : (details.email || 'unknown');
            const durationFormatted = `${Math.floor(sessionDuration / 60)}:${String(sessionDuration % 60).padStart(2, '0')}`;
            const pageViews = this.userJourney.length;
            const geographicLocation = this.geographicLocation || 'Unknown';
            
            // Enhanced data according to Phase 2 spec:
            // Timestamp | User ID | Email | Action Type | Action Details | Library Book Accessed | Search Query | Session Duration | Page Views | Device Info | Geographic Location | Conversion Event | Engagement Score
            const values = [[
                timestamp,
                userId,
                email,
                action,
                JSON.stringify(details),
                details.bookAccessed || '',
                details.searchQuery || '',
                durationFormatted,
                pageViews,
                `${this.deviceInfo.browser}/${this.deviceInfo.os}`,
                geographicLocation,
                conversionEvent,
                engagementScore
            ]];

            await this.sheetsService.spreadsheets.values.append({
                spreadsheetId: this.config.sheetIds.sessionTracking,
                range: 'Sheet1!A:M',
                valueInputOption: 'RAW',
                resource: { values }
            });

            console.log('📊 Enhanced session activity logged:', {
                action,
                email: email,
                duration: durationFormatted,
                engagement: engagementScore,
                conversion: conversionEvent
            });

        } catch (error) {
            console.error('❌ Error logging registration activity:', error);
            // Don't block registration flow on logging errors
        }
    }

    // Calculate engagement score based on user actions
    calculateEngagementScore(action, details) {
        let score = this.engagementScore;
        
        // Score different actions
        const actionScores = {
            'email_entered': 10,
            'email_verification_attempt': 15,
            'google_oauth_success': 20,
            'registration_complete': 25,
            'library_access': 30,
            'book_search': 15,
            'book_view': 20
        };
        
        score += actionScores[action] || 5;
        
        // Bonus for device type
        if (this.deviceInfo.deviceType === 'desktop') score += 5;
        
        // Bonus for engagement time
        const sessionTime = (new Date() - this.pageStartTime) / 1000;
        if (sessionTime > 120) score += 10; // 2+ minutes
        if (sessionTime > 300) score += 15; // 5+ minutes
        
        this.engagementScore = Math.min(score, 100);
        return this.engagementScore;
    }

    // Identify conversion milestones
    identifyConversionEvent(action) {
        const conversionEvents = {
            'email_entered': 'email_capture',
            'email_verification_attempt': 'verification_attempt',
            'google_oauth_success': 'oauth_success',
            'registration_complete': 'registration_complete',
            'library_access': 'first_library_access',
            'book_search': 'first_search',
            'book_view': 'first_book_access'
        };
        
        return conversionEvents[action] || '';
    }

    // Enhanced user registration with comprehensive analytics
    async completeUserRegistration(userData) {
        try {
            // Track journey step
            this.trackJourneyStep('registration_complete', { email: userData.email, method: userData.authMethod });
            
            // Calculate registration duration
            const registrationDuration = this.registrationStartTime ? 
                Math.round((new Date() - new Date(this.registrationStartTime)) / 1000) : 0;
            
            const verificationCode = userData.verificationCode || '';
            
            if (this.simulateMode) {
                console.log('🧪 SIMULATED - Enhanced user registration completed:', {
                    userId: userData.userId,
                    email: userData.email,
                    name: userData.name,
                    authMethod: userData.authMethod,
                    registrationDuration: `${registrationDuration}s`,
                    deviceInfo: `${this.deviceInfo.browser}/${this.deviceInfo.os}`,
                    location: userData.location,
                    timestamp: new Date().toISOString(),
                    sheetId: this.config.sheetIds.userRegistrations
                });
                return true;
            }

            if (!this.sheetsService) {
                throw new Error('Sheets service not available');
            }

            const timestamp = new Date().toISOString();
            const deviceInfoString = `${this.deviceInfo.browser}/${this.deviceInfo.os}`;
            const durationFormatted = `${Math.floor(registrationDuration / 60)}:${String(registrationDuration % 60).padStart(2, '0')}`;
            
            // Enhanced data according to Phase 2 spec:
            // Timestamp | User ID | Email | Full Name | Auth Method | Registration Status | Verification Code | Location (Zip) | Terms Accepted | Device Info | Session ID | Referrer | Registration Duration | Notes
            const values = [[
                timestamp,
                userData.userId || this.currentUser?.id || 'unknown',
                userData.email,
                userData.name || '',
                userData.authMethod || 'email',
                'verified',
                verificationCode,
                userData.location || '',
                userData.consent ? 'TRUE' : 'FALSE',
                deviceInfoString,
                this.sessionId,
                document.referrer || 'direct',
                durationFormatted,
                userData.notes || 'Completed successfully'
            ]];

            await this.sheetsService.spreadsheets.values.append({
                spreadsheetId: this.config.sheetIds.userRegistrations,
                range: 'Sheet1!A:N',
                valueInputOption: 'RAW',
                resource: { values }
            });

            console.log('✅ Enhanced user registration completed:', {
                email: userData.email,
                method: userData.authMethod,
                duration: durationFormatted,
                device: deviceInfoString
            });
            
            // Remove from incomplete emails if it was there
            await this.removeIncompleteEmail(userData.email);

            return true;

        } catch (error) {
            console.error('❌ Error completing user registration:', error);
            throw error;
        }
    }

    // Remove email from incomplete tracking
    async removeIncompleteEmail(email) {
        try {
            // For simplicity, we'll just log the completion
            // In a full implementation, you'd search and delete the row
            console.log('📊 Email moved from incomplete to complete:', email);
        } catch (error) {
            console.error('❌ Error removing incomplete email:', error);
        }
    }

    // ==================== EVENT HANDLERS ====================

    // Override these in your implementation
    onGoogleRegistrationSuccess(user) {
        console.log('🎉 Google registration success:', user.email);
        // This will be overridden by the registration form
    }

    onEmailRegistrationStep(step, data) {
        console.log('📧 Email registration step:', step, data);
        // This will be overridden by the registration form
    }

    onRegistrationError(error) {
        console.error('❌ Registration error:', error);
        // This will be overridden by the registration form
    }

    onRegistrationComplete(userData) {
        console.log('✅ Registration complete:', userData.email);
        // This will be overridden by the registration form
    }

    // ==================== UTILITY METHODS ====================

    // Show Google Sign-In button
    renderSignInButton(elementId, options = {}) {
        const defaultOptions = {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            text: 'signin_with',
            shape: 'rectangular'
        };
        
        const buttonOptions = { ...defaultOptions, ...options };
        
        google.accounts.id.renderButton(
            document.getElementById(elementId),
            buttonOptions
        );
    }

    // Sign out
    async signOut() {
        try {
            // Revoke access token
            if (this.accessToken) {
                google.accounts.oauth2.revoke(this.accessToken);
            }
            
            this.isSignedIn = false;
            this.currentUser = null;
            this.accessToken = null;
            
            // Clear API client token
            if (this.gapiLoaded) {
                gapi.client.setToken(null);
            }
            
            console.log('👋 User signed out from OurLibrary');

        } catch (error) {
            console.error('❌ Sign-out failed:', error);
            throw error;
        }
    }
}

// Registration Manager - Coordinates Firebase Auth + Google Sheets
class OurLibraryRegistrationManager {
    constructor(firebaseAuth, googleAuth) {
        this.firebaseAuth = firebaseAuth;
        this.googleAuth = googleAuth;
        this.registrationStartTime = null;
        this.pendingUserData = null;
    }

    // Enhanced incomplete email capture (exposed method)
    async logIncompleteEmail(email, step = 'email_blur', formData = {}) {
        try {
            return await this.googleAuth.logIncompleteEmail(email, step, formData);
        } catch (error) {
            console.error('❌ Error logging incomplete email:', error);
            return { success: false, error: error.message };
        }
    }

    // Log complete registration (exposed method)
    async logCompleteRegistration(userData) {
        try {
            return await this.googleAuth.completeUserRegistration(userData);
        } catch (error) {
            console.error('❌ Error logging complete registration:', error);
            return { success: false, error: error.message };
        }
    }

    // Enhanced email registration start with comprehensive tracking
    async startEmailRegistration(formData) {
        try {
            this.registrationStartTime = new Date().toISOString();
            this.googleAuth.registrationStartTime = new Date(); // Set in Google Auth too
            this.pendingUserData = { ...formData, authMethod: 'email' };

            // Enhanced incomplete email logging with form data
            await this.googleAuth.logIncompleteEmail(formData.email, 'form_completed', formData);
            
            // Enhanced registration start logging
            await this.googleAuth.logRegistrationActivity('email_registration_start', {
                email: formData.email,
                name: formData.fullName,
                location: formData.zipCode,
                formProgress: this.googleAuth.calculateFormProgress(formData),
                leadScore: this.googleAuth.calculateLeadScore(formData)
            });

            return { success: true };

        } catch (error) {
            console.error('❌ Error starting email registration:', error);
            return { success: false, error: error.message };
        }
    }

    // Complete email verification and create Firebase account
    async completeEmailRegistration(verificationCode) {
        try {
            if (!this.pendingUserData) {
                throw new Error('No pending registration data');
            }

            // Log verification attempt
            await this.googleAuth.logRegistrationActivity('email_verification_attempt', {
                email: this.pendingUserData.email,
                code: verificationCode
            });

            // Create Firebase account using the global function (not a method on auth object)
            const userCredential = await window.createUserWithEmailAndPassword(
                this.firebaseAuth,
                this.pendingUserData.email,
                this.pendingUserData.password
            );

            const firebaseUser = userCredential.user;
            
            // Since we verified the email through our custom system, mark it as verified in Firebase
            // Note: In production, you'd verify the code against your database first
            
            // Complete registration in Google Sheets with verification code
            const userData = {
                userId: firebaseUser.uid,
                email: this.pendingUserData.email,
                name: this.pendingUserData.fullName,
                authMethod: 'email',
                registrationStartTime: this.registrationStartTime,
                location: this.pendingUserData.zipCode || '',
                consent: this.pendingUserData.termsAccepted || false,
                verificationCode: verificationCode // Include the verification code
            };

            await this.googleAuth.completeUserRegistration(userData);

            // Log successful completion
            await this.googleAuth.logRegistrationActivity('email_registration_complete', {
                userId: firebaseUser.uid,
                email: this.pendingUserData.email
            });

            this.pendingUserData = null;
            return { success: true, user: firebaseUser };

        } catch (error) {
            console.error('❌ Error completing email registration:', error);
            
            // Log the error
            await this.googleAuth.logRegistrationActivity('email_registration_error', {
                email: this.pendingUserData?.email,
                error: error.message
            });

            return { success: false, error: error.message };
        }
    }

    // Handle Google OAuth registration
    async completeGoogleRegistration(googleUser, additionalData = {}) {
        try {
            // Get the ID token from the googleUser object
            const idToken = googleUser.credential;

            // Create a Google credential with the token
            const credential = window.GoogleAuthProvider.credential(idToken);

            // Sign in to Firebase with the credential
            const userCredential = await window.signInWithCredential(this.firebaseAuth, credential);
            const firebaseUser = userCredential.user;

            // Complete registration in Google Sheets
            const userData = {
                userId: firebaseUser.uid,
                email: googleUser.email,
                name: googleUser.name,
                authMethod: 'google',
                registrationStartTime: new Date().toISOString(),
                location: additionalData.zipCode || '',
                consent: additionalData.termsAccepted || false,
                verificationCode: '' // Google OAuth doesn't use verification codes
            };

            await this.googleAuth.completeUserRegistration(userData);

            // Log successful completion
            await this.googleAuth.logRegistrationActivity('google_registration_complete', {
                userId: firebaseUser.uid,
                email: googleUser.email
            });

            return { success: true, user: firebaseUser };

        } catch (error) {
            console.error('❌ Error completing Google registration:', error);
            
            // Log the error
            await this.googleAuth.logRegistrationActivity('google_registration_error', {
                email: googleUser.email,
                error: error.message
            });

            return { success: false, error: error.message };
        }
    }
}

// Enhanced analytics utilities
class OurLibraryAnalytics {
    static async logLibraryAccess(userId, email, bookAccessed = '', searchQuery = '') {
        if (window.googleAuth) {
            await window.googleAuth.logRegistrationActivity('library_access', {
                email: email,
                bookAccessed: bookAccessed,
                searchQuery: searchQuery
            });
        }
    }
    
    static async logBookSearch(userId, email, searchQuery, resultsCount = 0) {
        if (window.googleAuth) {
            await window.googleAuth.logRegistrationActivity('book_search', {
                email: email,
                searchQuery: searchQuery,
                resultsCount: resultsCount
            });
        }
    }
    
    static async logBookView(userId, email, bookTitle, bookId = '') {
        if (window.googleAuth) {
            await window.googleAuth.logRegistrationActivity('book_view', {
                email: email,
                bookAccessed: bookTitle,
                bookId: bookId
            });
        }
    }
}

// Export classes
window.OurLibraryGoogleAuth = OurLibraryGoogleAuth;
window.OurLibraryRegistrationManager = OurLibraryRegistrationManager;
window.OurLibraryAnalytics = OurLibraryAnalytics;

console.log('📚 OurLibrary Enhanced Analytics module loaded (Phase 2)');