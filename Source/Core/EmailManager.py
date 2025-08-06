# File: EmailManager.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/EmailManager.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-08-04 02:21AM

"""
Email Manager for AndyLibrary
Handles production email verification, notifications, and communications
Supports multiple email service providers (SendGrid, AWS SES, Mailgun)
"""

import os
import json
import logging
import smtplib
import requests
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# Optional dependencies - gracefully handle missing packages
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    ClientError = Exception  # Fallback for type hints

class EmailManager:
    """
    Production-ready email management system for AndyLibrary
    Supports SendGrid, AWS SES, Mailgun, and SMTP fallback
    """
    
    def __init__(self, ConfigPath: str = "Config/email_config.json"):
        """
        Initialize EmailManager with configuration
        
        Args:
            ConfigPath: Path to email configuration file
        """
        self.ConfigPath = ConfigPath
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.Config = self.LoadConfiguration()
        self.Provider = self.Config.get("active_provider", "sendgrid")
        
        # Initialize provider-specific clients
        self.InitializeProviders()
        
        self.Logger.info(f"EmailManager initialized with provider: {self.Provider}")
    
    def LoadConfiguration(self) -> Dict[str, Any]:
        """Load email configuration from file and environment"""
        try:
            # Load base configuration
            if os.path.exists(self.ConfigPath):
                with open(self.ConfigPath, 'r') as f:
                    Config = json.load(f)
            else:
                Config = self.GetDefaultConfiguration()
                self.SaveConfiguration(Config)
            
            # Override with environment variables for security
            Config = self.OverrideWithEnvironment(Config)
            
            return Config
            
        except Exception as e:
            self.Logger.error(f"Failed to load email configuration: {e}")
            return self.GetDefaultConfiguration()
    
    def GetDefaultConfiguration(self) -> Dict[str, Any]:
        """Get default email configuration"""
        return {
            "active_provider": "sendgrid",
            "from_email": "noreply@andylibrary.org",
            "from_name": "AndyLibrary",
            "reply_to": "support@andylibrary.org",
            
            "providers": {
                "sendgrid": {
                    "api_key": "",
                    "api_url": "https://api.sendgrid.com/v3/mail/send",
                    "enabled": True
                },
                "aws_ses": {
                    "access_key_id": "",
                    "secret_access_key": "",
                    "region": "us-east-1",
                    "enabled": False
                },
                "mailgun": {
                    "api_key": "",
                    "domain": "",
                    "api_url": "https://api.mailgun.net/v3",
                    "enabled": False
                },
                "smtp": {
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True,
                    "enabled": False
                }
            },
            
            "templates": {
                "verification_email": {
                    "subject": "Welcome to AndyLibrary - Verify Your Email",
                    "template_id": "d-verification-template-id"
                },
                "password_reset": {
                    "subject": "AndyLibrary - Password Reset Request",
                    "template_id": "d-password-reset-template-id"
                },
                "welcome": {
                    "subject": "Welcome to AndyLibrary - Your Educational Library Awaits",
                    "template_id": "d-welcome-template-id"
                }
            },
            
            "settings": {
                "max_retries": 3,
                "retry_delay": 5,
                "timeout": 30,
                "rate_limit": 100  # emails per hour
            }
        }
    
    def OverrideWithEnvironment(self, Config: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables for security"""
        
        # SendGrid
        if os.getenv("SENDGRID_API_KEY"):
            Config["providers"]["sendgrid"]["api_key"] = os.getenv("SENDGRID_API_KEY")
            Config["providers"]["sendgrid"]["enabled"] = True
        
        # AWS SES
        if os.getenv("AWS_ACCESS_KEY_ID"):
            Config["providers"]["aws_ses"]["access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            Config["providers"]["aws_ses"]["secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
            Config["providers"]["aws_ses"]["region"] = os.getenv("AWS_REGION", "us-east-1")
            Config["providers"]["aws_ses"]["enabled"] = True
        
        # Mailgun
        if os.getenv("MAILGUN_API_KEY"):
            Config["providers"]["mailgun"]["api_key"] = os.getenv("MAILGUN_API_KEY")
            Config["providers"]["mailgun"]["domain"] = os.getenv("MAILGUN_DOMAIN")
            Config["providers"]["mailgun"]["enabled"] = True
        
        # SMTP
        if os.getenv("SMTP_USERNAME"):
            Config["providers"]["smtp"]["username"] = os.getenv("SMTP_USERNAME")
            Config["providers"]["smtp"]["password"] = os.getenv("SMTP_PASSWORD")
            Config["providers"]["smtp"]["host"] = os.getenv("SMTP_HOST", "smtp.gmail.com")
            Config["providers"]["smtp"]["port"] = int(os.getenv("SMTP_PORT", "587"))
            Config["providers"]["smtp"]["enabled"] = True
        
        # General settings
        if os.getenv("EMAIL_FROM"):
            Config["from_email"] = os.getenv("EMAIL_FROM")
        
        return Config
    
    def SaveConfiguration(self, Config: Dict[str, Any]) -> None:
        """Save configuration to file (without sensitive data)"""
        try:
            # Create config directory if it doesn't exist
            ConfigDir = Path(self.ConfigPath).parent
            ConfigDir.mkdir(parents=True, exist_ok=True)
            
            # Remove sensitive data before saving
            SafeConfig = self.RemoveSensitiveData(Config.copy())
            
            with open(self.ConfigPath, 'w') as f:
                json.dump(SafeConfig, f, indent=2)
                
        except Exception as e:
            self.Logger.error(f"Failed to save email configuration: {e}")
    
    def RemoveSensitiveData(self, Config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from configuration before saving"""
        SensitiveKeys = [
            "api_key", "secret_access_key", "access_key_id", 
            "username", "password"
        ]
        
        for Provider in Config.get("providers", {}).values():
            for Key in SensitiveKeys:
                if Key in Provider:
                    Provider[Key] = ""
        
        return Config
    
    def InitializeProviders(self) -> None:
        """Initialize provider-specific clients"""
        try:
            # Initialize AWS SES client (if boto3 is available)
            if self.Config["providers"]["aws_ses"]["enabled"] and BOTO3_AVAILABLE:
                self.SESClient = boto3.client(
                    'ses',
                    aws_access_key_id=self.Config["providers"]["aws_ses"]["access_key_id"],
                    aws_secret_access_key=self.Config["providers"]["aws_ses"]["secret_access_key"],
                    region_name=self.Config["providers"]["aws_ses"]["region"]
                )
            elif self.Config["providers"]["aws_ses"]["enabled"] and not BOTO3_AVAILABLE:
                self.Logger.warning("AWS SES enabled but boto3 not available. Install boto3 for AWS SES support.")
                self.Config["providers"]["aws_ses"]["enabled"] = False
            
        except Exception as e:
            self.Logger.error(f"Failed to initialize email providers: {e}")
    
    def SendVerificationEmail(self, Email: str, VerificationToken: str, Username: str = None) -> Dict[str, Any]:
        """
        Send email verification email
        
        Args:
            Email: Recipient email address
            VerificationToken: Secure verification token
            Username: Optional username for personalization
            
        Returns:
            Dict with success status and details
        """
        try:
            # Generate verification URL
            BaseUrl = os.getenv("BASE_URL", "https://bowersworld.com")
            VerificationUrl = f"{BaseUrl}/api/auth/verify-email?token={VerificationToken}"
            
            # Prepare email data
            EmailData = {
                "to_email": Email,
                "to_name": Username or Email.split('@')[0],
                "template_type": "verification_email",
                "template_data": {
                    "username": Username or "Student",
                    "verification_url": VerificationUrl,
                    "verification_token": VerificationToken,
                    "expires_hours": 24
                }
            }
            
            # Send verification email to user
            VerificationResult = self.SendTemplatedEmail(EmailData)
            
            # Send admin notification
            if VerificationResult.get("success"):
                self.SendAdminNotification(Email, Username)
            
            return VerificationResult
            
        except Exception as e:
            self.Logger.error(f"Failed to send verification email: {e}")
            return {"success": False, "error": str(e)}
    
    def SendWelcomeEmail(self, Email: str, Username: str = None) -> Dict[str, Any]:
        """
        Send welcome email after successful verification
        
        Args:
            Email: Recipient email address
            Username: Optional username for personalization
            
        Returns:
            Dict with success status and details
        """
        try:
            EmailData = {
                "to_email": Email,
                "to_name": Username or Email.split('@')[0],
                "template_type": "welcome",
                "template_data": {
                    "username": Username or "Student",
                    "library_url": os.getenv("BASE_URL", "https://bowersworld.com"),
                    "support_email": self.Config["reply_to"]
                }
            }
            
            return self.SendTemplatedEmail(EmailData)
            
        except Exception as e:
            self.Logger.error(f"Failed to send welcome email: {e}")
            return {"success": False, "error": str(e)}
    
    def SendPasswordResetEmail(self, Email: str, ResetToken: str, Username: str = None) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            Email: Recipient email address
            ResetToken: Secure reset token
            Username: Optional username for personalization
            
        Returns:
            Dict with success status and details
        """
        try:
            # Generate reset URL
            BaseUrl = os.getenv("BASE_URL", "https://bowersworld.com")
            ResetUrl = f"{BaseUrl}/reset-password?token={ResetToken}"
            
            EmailData = {
                "to_email": Email,
                "to_name": Username or Email.split('@')[0],
                "template_type": "password_reset",
                "template_data": {
                    "username": Username or "Student",
                    "reset_url": ResetUrl,
                    "reset_token": ResetToken,
                    "expires_hours": 2
                }
            }
            
            return self.SendTemplatedEmail(EmailData)
            
        except Exception as e:
            self.Logger.error(f"Failed to send password reset email: {e}")
            return {"success": False, "error": str(e)}
    
    def SendTemplatedEmail(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send templated email using configured provider
        
        Args:
            EmailData: Email data including recipient, template, and variables
            
        Returns:
            Dict with success status and details
        """
        try:
            Provider = self.Provider
            
            # Try primary provider first
            if Provider == "sendgrid":
                return self.SendViaSendGrid(EmailData)
            elif Provider == "aws_ses":
                return self.SendViaAWSSES(EmailData)
            elif Provider == "mailgun":
                return self.SendViaMailgun(EmailData)
            elif Provider == "smtp":
                return self.SendViaSMTP(EmailData)
            else:
                # Fallback to first available provider
                return self.SendWithFallback(EmailData)
                
        except Exception as e:
            self.Logger.error(f"Failed to send templated email: {e}")
            return {"success": False, "error": str(e)}
    
    def SendWithFallback(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """Try multiple providers in order until one succeeds"""
        Providers = ["sendgrid", "aws_ses", "mailgun", "smtp"]
        LastError = None
        
        for Provider in Providers:
            if not self.Config["providers"][Provider]["enabled"]:
                continue
                
            try:
                if Provider == "sendgrid":
                    Result = self.SendViaSendGrid(EmailData)
                elif Provider == "aws_ses":
                    Result = self.SendViaAWSSES(EmailData)
                elif Provider == "mailgun":
                    Result = self.SendViaMailgun(EmailData)
                elif Provider == "smtp":
                    Result = self.SendViaSMTP(EmailData)
                
                if Result["success"]:
                    self.Logger.info(f"Email sent successfully via {Provider}")
                    return Result
                else:
                    LastError = Result["error"]
                    
            except Exception as e:
                LastError = str(e)
                self.Logger.warning(f"Provider {Provider} failed: {e}")
                continue
        
        return {"success": False, "error": f"All providers failed. Last error: {LastError}"}
    
    def SendViaSendGrid(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        try:
            Config = self.Config["providers"]["sendgrid"]
            if not Config["enabled"] or not Config["api_key"]:
                return {"success": False, "error": "SendGrid not configured"}
            
            # Get template info
            TemplateInfo = self.Config["templates"][EmailData["template_type"]]
            
            # Prepare SendGrid payload
            Payload = {
                "personalizations": [{
                    "to": [{"email": EmailData["to_email"], "name": EmailData["to_name"]}],
                    "dynamic_template_data": EmailData["template_data"]
                }],
                "from": {
                    "email": self.Config["from_email"],
                    "name": self.Config["from_name"]
                },
                "reply_to": {
                    "email": self.Config["reply_to"]
                },
                "template_id": TemplateInfo["template_id"]
            }
            
            # If no template ID, send with HTML content
            if not TemplateInfo.get("template_id"):
                Payload["subject"] = TemplateInfo["subject"]
                Payload["content"] = [{
                    "type": "text/html",
                    "value": self.GenerateHTMLContent(EmailData)
                }]
                del Payload["template_id"]
            
            Headers = {
                "Authorization": f"Bearer {Config['api_key']}",
                "Content-Type": "application/json"
            }
            
            Response = requests.post(Config["api_url"], json=Payload, headers=Headers, timeout=30)
            
            if Response.status_code == 202:
                return {"success": True, "provider": "sendgrid", "message_id": Response.headers.get("X-Message-Id")}
            else:
                return {"success": False, "error": f"SendGrid API error: {Response.status_code} - {Response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"SendGrid error: {str(e)}"}
    
    def SendViaAWSSES(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via AWS SES"""
        try:
            Config = self.Config["providers"]["aws_ses"]
            if not Config["enabled"]:
                return {"success": False, "error": "AWS SES not configured"}
            
            if not BOTO3_AVAILABLE:
                return {"success": False, "error": "boto3 not available for AWS SES"}
            
            if not hasattr(self, 'SESClient'):
                return {"success": False, "error": "AWS SES client not initialized"}
            
            TemplateInfo = self.Config["templates"][EmailData["template_type"]]
            
            Response = self.SESClient.send_email(
                Source=f"{self.Config['from_name']} <{self.Config['from_email']}>",
                Destination={"ToAddresses": [EmailData["to_email"]]},
                Message={
                    "Subject": {"Data": TemplateInfo["subject"], "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": self.GenerateHTMLContent(EmailData), "Charset": "UTF-8"}
                    }
                },
                ReplyToAddresses=[self.Config["reply_to"]]
            )
            
            return {
                "success": True, 
                "provider": "aws_ses", 
                "message_id": Response["MessageId"]
            }
            
        except ClientError as e:
            return {"success": False, "error": f"AWS SES error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"success": False, "error": f"AWS SES error: {str(e)}"}
    
    def SendViaMailgun(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via Mailgun API"""
        try:
            Config = self.Config["providers"]["mailgun"]
            if not Config["enabled"] or not Config["api_key"] or not Config["domain"]:
                return {"success": False, "error": "Mailgun not configured"}
            
            TemplateInfo = self.Config["templates"][EmailData["template_type"]]
            
            Payload = {
                "from": f"{self.Config['from_name']} <{self.Config['from_email']}>",
                "to": EmailData["to_email"],
                "subject": TemplateInfo["subject"],
                "html": self.GenerateHTMLContent(EmailData),
                "h:Reply-To": self.Config["reply_to"]
            }
            
            Response = requests.post(
                f"{Config['api_url']}/{Config['domain']}/messages",
                auth=("api", Config["api_key"]),
                data=Payload,
                timeout=30
            )
            
            if Response.status_code == 200:
                ResponseData = Response.json()
                return {
                    "success": True, 
                    "provider": "mailgun", 
                    "message_id": ResponseData.get("id")
                }
            else:
                return {"success": False, "error": f"Mailgun API error: {Response.status_code} - {Response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Mailgun error: {str(e)}"}
    
    def SendViaSMTP(self, EmailData: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via SMTP (fallback option)"""
        try:
            Config = self.Config["providers"]["smtp"]
            if not Config["enabled"] or not Config["username"]:
                return {"success": False, "error": "SMTP not configured"}
            
            TemplateInfo = self.Config["templates"][EmailData["template_type"]]
            
            # Create message
            Message = MIMEMultipart('alternative')
            Message['Subject'] = TemplateInfo["subject"]
            Message['From'] = f"{self.Config['from_name']} <{self.Config['from_email']}>"
            Message['To'] = EmailData["to_email"]
            Message['Reply-To'] = self.Config["reply_to"]
            
            # Add HTML content
            HTMLPart = MIMEText(self.GenerateHTMLContent(EmailData), 'html')
            Message.attach(HTMLPart)
            
            # Send via SMTP
            if Config.get("use_ssl", False):
                # Use SSL connection (typically port 465)
                with smtplib.SMTP_SSL(Config["host"], Config["port"]) as Server:
                    Server.login(Config["username"], Config["password"])
                    Server.send_message(Message)
            else:
                # Use TLS connection (typically port 587)
                with smtplib.SMTP(Config["host"], Config["port"]) as Server:
                    if Config.get("use_tls", True):
                        Server.starttls()
                    Server.login(Config["username"], Config["password"])
                    Server.send_message(Message)
            
            return {"success": True, "provider": "smtp", "message_id": "smtp_sent"}
            
        except Exception as e:
            return {"success": False, "error": f"SMTP error: {str(e)}"}
    
    def GenerateHTMLContent(self, EmailData: Dict[str, Any]) -> str:
        """Generate HTML content for email templates"""
        TemplateType = EmailData["template_type"]
        Data = EmailData["template_data"]
        
        if TemplateType == "verification_email":
            return self.GetVerificationEmailHTML(Data)
        elif TemplateType == "welcome":
            return self.GetWelcomeEmailHTML(Data)
        elif TemplateType == "password_reset":
            return self.GetPasswordResetEmailHTML(Data)
        elif TemplateType == "admin_notification":
            return self.GetAdminNotificationHTML(Data)
        else:
            return "<p>Email content not available</p>"
    
    def GetVerificationEmailHTML(self, Data: Dict[str, Any]) -> str:
        """Generate HTML for verification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your AndyLibrary Account</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">📚 AndyLibrary</h1>
                    <p style="color: #7f8c8d; font-size: 16px; margin: 0;">Educational Library Platform</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                    <h2 style="color: white; margin: 0;">Welcome to Project Himalaya!</h2>
                    <p style="color: white; margin: 10px 0 0 0; font-style: italic;">"Getting education into the hands of people who can least afford it"</p>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #2c3e50;">Hello {Data['username']}!</h3>
                    <p style="color: #555; font-size: 16px;">Thank you for joining AndyLibrary. To complete your registration and access our educational resources, please verify your email address.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{Data['verification_url']}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 16px;">
                        ✅ Verify Email Address
                    </a>
                </div>
                
                <div style="background-color: #f8f9ff; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea; margin: 30px 0;">
                    <h4 style="color: #2c3e50; margin-top: 0;">🔒 Security Information</h4>
                    <ul style="color: #555; margin: 0;">
                        <li>This verification link expires in {Data['expires_hours']} hours</li>
                        <li>If you didn't create this account, you can safely ignore this email</li>
                        <li>For security, we never ask for passwords via email</li>
                    </ul>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; text-align: center;">
                    <p style="color: #7f8c8d; font-size: 14px; margin: 0;">
                        Can't click the button? Copy and paste this link into your browser:<br>
                        <a href="{Data['verification_url']}" style="color: #667eea; word-break: break-all;">{Data['verification_url']}</a>
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #7f8c8d; font-size: 12px; margin: 0;">
                        © 2025 AndyLibrary - Educational Digital Library<br>
                        <a href="mailto:support@andylibrary.org" style="color: #667eea;">support@andylibrary.org</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def GetWelcomeEmailHTML(self, Data: Dict[str, Any]) -> str:
        """Generate HTML for welcome email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to AndyLibrary!</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">🎉 Welcome to AndyLibrary!</h1>
                    <p style="color: #7f8c8d; font-size: 16px; margin: 0;">Your educational journey begins now</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
                    <h2 style="color: white; margin: 0 0 15px 0;">Hello {Data['username']}! 👋</h2>
                    <p style="color: white; margin: 0; font-size: 18px;">Your email has been verified and your account is now active!</p>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #2c3e50;">🚀 What's Next?</h3>
                    <div style="background-color: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h4 style="color: #2c3e50; margin-top: 0;">📚 Explore Our Library</h4>
                        <p style="color: #555; margin-bottom: 15px;">Access thousands of educational resources across multiple subjects.</p>
                        <a href="{Data['library_url']}" style="display: inline-block; background: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                            Browse Library
                        </a>
                    </div>
                </div>
                
                <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db; margin: 30px 0;">
                    <h4 style="color: #2c3e50; margin-top: 0;">🎯 Our Educational Mission</h4>
                    <p style="color: #555; margin: 0; font-style: italic;">"Getting education into the hands of people who can least afford it"</p>
                    <p style="color: #555; margin: 10px 0 0 0;">You're now part of a global community working to make education accessible to everyone, everywhere.</p>
                </div>
                
                <div style="margin: 30px 0;">
                    <h4 style="color: #2c3e50;">Need Help?</h4>
                    <p style="color: #555;">Our support team is here to help you make the most of AndyLibrary.</p>
                    <p style="color: #555; margin: 0;">
                        📧 Email: <a href="mailto:{Data['support_email']}" style="color: #667eea;">{Data['support_email']}</a>
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #7f8c8d; font-size: 12px; margin: 0;">
                        © 2025 AndyLibrary - Educational Digital Library<br>
                        Making education accessible worldwide
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def GetPasswordResetEmailHTML(self, Data: Dict[str, Any]) -> str:
        """Generate HTML for password reset email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your AndyLibrary Password</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">🔐 Password Reset</h1>
                    <p style="color: #7f8c8d; font-size: 16px; margin: 0;">AndyLibrary Account Security</p>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #2c3e50;">Hello {Data['username']},</h3>
                    <p style="color: #555; font-size: 16px;">We received a request to reset your AndyLibrary password. If you made this request, click the button below to create a new password.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{Data['reset_url']}" style="display: inline-block; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: 600; font-size: 16px;">
                        🔓 Reset Password
                    </a>
                </div>
                
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107; margin: 30px 0;">
                    <h4 style="color: #856404; margin-top: 0;">⚠️ Security Notice</h4>
                    <ul style="color: #856404; margin: 0;">
                        <li>This reset link expires in {Data['expires_hours']} hours</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Your current password remains unchanged until you create a new one</li>
                        <li>For security, we recommend using a strong, unique password</li>
                    </ul>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; text-align: center;">
                    <p style="color: #7f8c8d; font-size: 14px; margin: 0;">
                        Can't click the button? Copy and paste this link into your browser:<br>
                        <a href="{Data['reset_url']}" style="color: #e74c3c; word-break: break-all;">{Data['reset_url']}</a>
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #7f8c8d; font-size: 12px; margin: 0;">
                        © 2025 AndyLibrary - Educational Digital Library<br>
                        <a href="mailto:support@andylibrary.org" style="color: #e74c3c;">support@andylibrary.org</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def GetAdminNotificationHTML(self, Data: Dict[str, Any]) -> str:
        """Generate HTML for admin notification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New AndyLibrary Account Registration</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px;">🆕 New Account Registration</h1>
                    <p style="color: #7f8c8d; font-size: 16px; margin: 0;">AndyLibrary - Project Himalaya</p>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #2c3e50;">New User Registration Alert</h3>
                    <p style="color: #555; font-size: 16px;">A new user has registered for AndyLibrary and is requesting access to educational resources.</p>
                </div>
                
                <div style="background-color: #e8f4fd; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db; margin: 30px 0;">
                    <h4 style="color: #2980b9; margin-top: 0;">📊 Registration Details</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #555; font-weight: 600;">📧 Email:</td>
                            <td style="padding: 8px 0; color: #2c3e50;">{Data['user_email']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #555; font-weight: 600;">👤 Username:</td>
                            <td style="padding: 8px 0; color: #2c3e50;">{Data['username']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #555; font-weight: 600;">⏰ Registration Time:</td>
                            <td style="padding: 8px 0; color: #2c3e50;">{Data['registration_time']}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #fff8e1; padding: 20px; border-radius: 10px; border-left: 4px solid #f39c12; margin: 30px 0;">
                    <h4 style="color: #e67e22; margin-top: 0;">🏔️ Educational Mission</h4>
                    <p style="color: #d68910; margin: 0; font-style: italic;">"Getting education into the hands of people who can least afford it"</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 30px 0;">
                    <h4 style="color: #495057; margin-top: 0;">📋 Next Steps</h4>
                    <ul style="color: #6c757d; margin: 0; padding-left: 20px;">
                        <li style="margin-bottom: 8px;">User will receive email verification link</li>
                        <li style="margin-bottom: 8px;">Account will be activated after email verification</li>
                        <li style="margin-bottom: 8px;">User can then access educational library resources</li>
                        <li>Monitor usage patterns for educational impact assessment</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid #eee;">
                    <p style="color: #7f8c8d; font-size: 14px; margin: 0;">
                        AndyLibrary - Project Himalaya<br>
                        Making education accessible worldwide
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def TestEmailConfiguration(self) -> Dict[str, Any]:
        """Test email configuration and provider connectivity"""
        Results = {"success": True, "providers": {}}
        
        for ProviderName, ProviderConfig in self.Config["providers"].items():
            if not ProviderConfig["enabled"]:
                Results["providers"][ProviderName] = {"enabled": False, "status": "disabled"}
                continue
            
            try:
                # Test basic configuration
                if ProviderName == "sendgrid":
                    TestResult = self.TestSendGrid()
                elif ProviderName == "aws_ses":
                    TestResult = self.TestAWSSES()
                elif ProviderName == "mailgun":
                    TestResult = self.TestMailgun()
                elif ProviderName == "smtp":
                    TestResult = self.TestSMTP()
                else:
                    TestResult = {"success": False, "error": "Unknown provider"}
                
                Results["providers"][ProviderName] = TestResult
                
                if not TestResult["success"]:
                    Results["success"] = False
                    
            except Exception as e:
                Results["providers"][ProviderName] = {"success": False, "error": str(e)}
                Results["success"] = False
        
        return Results
    
    def TestSendGrid(self) -> Dict[str, Any]:
        """Test SendGrid configuration"""
        try:
            Config = self.Config["providers"]["sendgrid"]
            if not Config["api_key"]:
                return {"success": False, "error": "API key not configured"}
            
            # Test API key validity
            Headers = {"Authorization": f"Bearer {Config['api_key']}"}
            Response = requests.get("https://api.sendgrid.com/v3/user/profile", headers=Headers, timeout=10)
            
            if Response.status_code == 200:
                return {"success": True, "status": "configured", "provider": "sendgrid"}
            else:
                return {"success": False, "error": f"API key invalid: {Response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def TestAWSSES(self) -> Dict[str, Any]:
        """Test AWS SES configuration"""
        try:
            if not BOTO3_AVAILABLE:
                return {"success": False, "error": "boto3 not available"}
            
            if hasattr(self, 'SESClient'):
                # Test by getting send quota
                Response = self.SESClient.get_send_quota()
                return {"success": True, "status": "configured", "provider": "aws_ses", "quota": Response}
            else:
                return {"success": False, "error": "SES client not initialized"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def TestMailgun(self) -> Dict[str, Any]:
        """Test Mailgun configuration"""
        try:
            Config = self.Config["providers"]["mailgun"]
            if not Config["api_key"] or not Config["domain"]:
                return {"success": False, "error": "API key or domain not configured"}
            
            # Test domain validation
            Response = requests.get(
                f"{Config['api_url']}/{Config['domain']}",
                auth=("api", Config["api_key"]),
                timeout=10
            )
            
            if Response.status_code == 200:
                return {"success": True, "status": "configured", "provider": "mailgun"}
            else:
                return {"success": False, "error": f"Domain validation failed: {Response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def TestSMTP(self) -> Dict[str, Any]:
        """Test SMTP configuration"""
        try:
            Config = self.Config["providers"]["smtp"]
            if not Config["username"] or not Config["password"]:
                return {"success": False, "error": "SMTP credentials not configured"}
            
            # Test SMTP connection
            if Config.get("use_ssl", False):
                # Use SSL connection (typically port 465)
                with smtplib.SMTP_SSL(Config["host"], Config["port"]) as Server:
                    Server.login(Config["username"], Config["password"])
            else:
                # Use TLS connection (typically port 587)
                with smtplib.SMTP(Config["host"], Config["port"]) as Server:
                    if Config.get("use_tls", True):
                        Server.starttls()
                    Server.login(Config["username"], Config["password"])
            
            return {"success": True, "status": "configured", "provider": "smtp"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def SendAdminNotification(self, UserEmail: str, Username: str = None) -> Dict[str, Any]:
        """
        Send notification to admin about new account registration
        
        Args:
            UserEmail: New user's email address
            Username: New user's username
            
        Returns:
            Dict with success status
        """
        try:
            AdminEmailData = {
                "to_email": "HimalayaProject1@gmail.com",
                "template_type": "admin_notification", 
                "template_data": {
                    "user_email": UserEmail,
                    "username": Username or "No username provided",
                    "registration_time": self.GetCurrentTimestamp()
                }
            }
            
            return self.SendTemplatedEmail(AdminEmailData)
            
        except Exception as e:
            self.Logger.error(f"Failed to send admin notification: {e}")
            return {"success": False, "error": str(e)}
    
    def GetCurrentTimestamp(self) -> str:
        """Get current timestamp in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")