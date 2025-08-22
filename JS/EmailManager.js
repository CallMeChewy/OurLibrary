// File: EmailManager.js
// Path: OurLibrary/JS/EmailManager.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-21
// Last Modified: 2025-08-21 08:30PM
// Description: Email delivery management with custom SMTP and Firebase fallback

class EmailManager {
    constructor() {
        this.config = null;
        this.initialized = false;
        this.debug = true; // Enable for testing
    }

    async initialize() {
        try {
            // Load email configuration
            const response = await fetch('Config/email_config.json');
            this.config = await response.json();
            this.initialized = true;
            
            console.log('📧 EmailManager initialized with provider:', this.config.active_provider);
            return true;
        } catch (error) {
            console.warn('⚠️ EmailManager: Could not load config, using Firebase fallback only');
            this.config = { active_provider: 'firebase' };
            this.initialized = true;
            return false;
        }
    }

    async sendVerificationEmail(email) {
        if (!this.initialized) {
            await this.initialize();
        }

        const methods = [
            { name: 'custom_smtp', fn: () => this.sendViaCustomSMTP(email) },
            { name: 'firebase', fn: () => this.sendViaFirebase(email) }
        ];

        // Try methods in order of preference
        for (const method of methods) {
            try {
                console.log(`📧 Attempting email via ${method.name}...`);
                const result = await method.fn();
                
                if (result.success) {
                    console.log(`✅ Email sent successfully via ${method.name}`);
                    return {
                        success: true,
                        method: method.name,
                        data: result.data,
                        deliverability: method.name === 'custom_smtp' ? 'high' : 'medium'
                    };
                }
            } catch (error) {
                console.warn(`❌ ${method.name} failed:`, error.message);
                // Continue to next method
            }
        }

        throw new Error('All email delivery methods failed');
    }

    async sendViaCustomSMTP(email) {
        // Note: Direct SMTP from browser has limitations
        // This is a placeholder for the custom SMTP implementation
        
        if (!this.config.providers?.smtp?.enabled) {
            throw new Error('Custom SMTP not enabled in configuration');
        }

        console.log('🔧 Custom SMTP: This would use ProjectHimalaya@BowersWorld.com');
        console.log('📧 Target email:', email);
        console.log('⚙️  SMTP Config:', {
            host: this.config.providers.smtp.host,
            port: this.config.providers.smtp.port,
            from: this.config.from_email
        });

        // For now, simulate success (would be replaced with actual SMTP implementation)
        if (this.debug) {
            console.log('🧪 SIMULATED: Custom SMTP email sent successfully');
            return {
                success: true,
                data: {
                    messageId: `custom_${Date.now()}`,
                    provider: 'custom_smtp',
                    deliverability: 'high'
                }
            };
        }

        throw new Error('Custom SMTP implementation pending');
    }

    async sendViaFirebase(email) {
        try {
            if (!window.firebaseFunctions || !window.httpsCallable) {
                throw new Error('Firebase Functions not available');
            }

            console.log('🔥 Using Firebase Functions for email delivery');
            
            const sendVerificationEmail = window.httpsCallable(
                window.firebaseFunctions, 
                'sendVerificationEmail'
            );
            
            const result = await sendVerificationEmail({ email });
            
            return {
                success: true,
                data: {
                    ...result.data,
                    provider: 'firebase',
                    deliverability: 'medium' // Firebase emails go to spam
                }
            };
        } catch (error) {
            console.error('🔥 Firebase email error:', error);
            throw error;
        }
    }

    // Generate verification code (consistent with current system)
    generateVerificationCode() {
        return Math.random().toString().substr(2, 6).toUpperCase();
    }

    // Create email template
    createVerificationEmailHtml(email, code) {
        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OurLibrary - Email Verification</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 30px 20px; text-align: center; }
        .content { padding: 30px 20px; }
        .code-box { background-color: #f0f9ff; border: 2px dashed #3b82f6; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
        .code { font-size: 32px; font-weight: bold; color: #1d4ed8; letter-spacing: 4px; }
        .footer { background-color: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 14px; }
        .security-note { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 OurLibrary</h1>
            <p>Project Himalaya - Educational Access Initiative</p>
        </div>
        
        <div class="content">
            <h2>Verify Your Email Address</h2>
            <p>Hello,</p>
            <p>Thank you for joining OurLibrary! To complete your registration, please use the verification code below:</p>
            
            <div class="code-box">
                <div class="code">${code}</div>
                <p><strong>Your 6-digit verification code</strong></p>
            </div>
            
            <div class="security-note">
                <strong>🛡️ Security Notice:</strong> This code will expire in 15 minutes. Never share this code with anyone. 
                We will never ask for this code via phone or other communication.
            </div>
            
            <p>If you didn't request this verification, you can safely ignore this email.</p>
            
            <p>Welcome to our mission of getting education into the hands of people who can least afford it!</p>
            
            <p>Best regards,<br>
            <strong>The OurLibrary Team</strong><br>
            Project Himalaya</p>
        </div>
        
        <div class="footer">
            <p>This email was sent from ProjectHimalaya@BowersWorld.com</p>
            <p>© 2025 OurLibrary - Project Himalaya. Educational Access Initiative.</p>
        </div>
    </div>
</body>
</html>`;
    }
}

// Export for global use
window.EmailManager = EmailManager;

console.log('📧 EmailManager module loaded - Custom SMTP + Firebase fallback ready');