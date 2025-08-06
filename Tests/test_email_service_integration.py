# File: test_email_service_integration.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_email_service_integration.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 05:15AM

"""
Email Service Integration Tests for AndyLibrary
Tests production email providers and fallback mechanisms
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add source directory to path and change to project root
TestDir = Path(__file__).parent
ProjectRoot = TestDir.parent
SourceDir = ProjectRoot / "Source"
sys.path.insert(0, str(SourceDir))

# Change to project root so relative paths work correctly
OriginalDir = os.getcwd()
os.chdir(str(ProjectRoot))

from Core.EmailManager import EmailManager, BOTO3_AVAILABLE

class TestEmailServiceIntegration(unittest.TestCase):
    """Test email service integration and fallback mechanisms"""
    
    def setUp(self):
        """Set up each test"""
        # Create temporary config directory
        self.TestDir = tempfile.mkdtemp(prefix="email_test_")
        self.ConfigPath = os.path.join(self.TestDir, "email_config.json")
        
        # Initialize EmailManager with test config
        self.EmailManager = EmailManager(self.ConfigPath)
        
        # Test email data
        self.TestEmailData = {
            "to_email": "test@example.com",
            "to_name": "Test User",
            "template_type": "verification_email",
            "template_data": {
                "username": "testuser",
                "verification_url": "https://bowersworld.com/verify?token=test123",
                "verification_token": "test123",
                "expires_hours": 24
            }
        }
    
    def tearDown(self):
        """Clean up after each test"""
        import shutil
        if os.path.exists(self.TestDir):
            shutil.rmtree(self.TestDir)
    
    def test_email_manager_initialization(self):
        """Test EmailManager initializes with default configuration"""
        self.assertIsNotNone(self.EmailManager)
        self.assertIsNotNone(self.EmailManager.Config)
        self.assertIn("providers", self.EmailManager.Config)
        self.assertIn("templates", self.EmailManager.Config)
        
        # Check default providers are configured
        Providers = self.EmailManager.Config["providers"]
        self.assertIn("sendgrid", Providers)
        self.assertIn("aws_ses", Providers)
        self.assertIn("mailgun", Providers)
        self.assertIn("smtp", Providers)
        
        print("✅ EmailManager initialization successful")
    
    def test_configuration_security(self):
        """Test that sensitive data is not saved to configuration file"""
        # Save configuration (should strip sensitive data)
        self.EmailManager.SaveConfiguration(self.EmailManager.Config)
        
        # Reload configuration from file
        with open(self.ConfigPath, 'r') as f:
            import json
            SavedConfig = json.load(f)
        
        # Verify sensitive keys are empty
        for Provider in SavedConfig["providers"].values():
            SensitiveKeys = ["api_key", "secret_access_key", "access_key_id", "username", "password"]
            for Key in SensitiveKeys:
                if Key in Provider:
                    self.assertEqual(Provider[Key], "", f"Sensitive key {Key} should be empty in saved config")
        
        print("✅ Configuration security validated")
    
    def test_environment_variable_override(self):
        """Test that environment variables override configuration"""
        # Set environment variables
        os.environ["SENDGRID_API_KEY"] = "test_sendgrid_key"
        os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key" 
        os.environ["MAILGUN_API_KEY"] = "test_mailgun_key"
        os.environ["EMAIL_FROM"] = "test@andylibrary.org"
        
        try:
            # Reinitialize EmailManager
            TestEmailManager = EmailManager(self.ConfigPath)
            
            # Verify environment variables are loaded
            self.assertEqual(TestEmailManager.Config["providers"]["sendgrid"]["api_key"], "test_sendgrid_key")
            self.assertEqual(TestEmailManager.Config["providers"]["aws_ses"]["access_key_id"], "test_aws_key")
            self.assertEqual(TestEmailManager.Config["providers"]["mailgun"]["api_key"], "test_mailgun_key")
            self.assertEqual(TestEmailManager.Config["from_email"], "test@andylibrary.org")
            
            # Verify providers are enabled when API keys are provided
            self.assertTrue(TestEmailManager.Config["providers"]["sendgrid"]["enabled"])
            # AWS SES might not be enabled if boto3 is missing - check conditionally
            if BOTO3_AVAILABLE:
                self.assertTrue(TestEmailManager.Config["providers"]["aws_ses"]["enabled"])
            self.assertTrue(TestEmailManager.Config["providers"]["mailgun"]["enabled"])
            
            print("✅ Environment variable override successful")
            
        finally:
            # Clean up environment variables
            for Key in ["SENDGRID_API_KEY", "AWS_ACCESS_KEY_ID", "MAILGUN_API_KEY", "EMAIL_FROM"]:
                if Key in os.environ:
                    del os.environ[Key]
    
    def test_html_template_generation(self):
        """Test HTML email template generation"""
        # Test verification email template
        VerificationHTML = self.EmailManager.GenerateHTMLContent(self.TestEmailData)
        
        self.assertIn("AndyLibrary", VerificationHTML)
        self.assertIn("testuser", VerificationHTML)
        self.assertIn("https://bowersworld.com/verify?token=test123", VerificationHTML)
        self.assertIn("24 hours", VerificationHTML)
        self.assertIn("Project Himalaya", VerificationHTML)
        
        # Test welcome email template
        WelcomeData = {
            "template_type": "welcome",
            "template_data": {
                "username": "newuser",
                "library_url": "https://bowersworld.com",
                "support_email": "support@andylibrary.org"
            }
        }
        
        WelcomeHTML = self.EmailManager.GenerateHTMLContent(WelcomeData)
        self.assertIn("Welcome to AndyLibrary", WelcomeHTML)
        self.assertIn("newuser", WelcomeHTML)
        self.assertIn("support@andylibrary.org", WelcomeHTML)
        
        # Test password reset template
        ResetData = {
            "template_type": "password_reset",
            "template_data": {
                "username": "resetuser",
                "reset_url": "https://bowersworld.com/reset?token=reset123",
                "expires_hours": 2
            }
        }
        
        ResetHTML = self.EmailManager.GenerateHTMLContent(ResetData)
        self.assertIn("Password Reset", ResetHTML)
        self.assertIn("resetuser", ResetHTML)
        self.assertIn("2 hours", ResetHTML)
        
        print("✅ HTML template generation successful")
    
    @patch('requests.post')
    def test_sendgrid_integration(self, MockPost):
        """Test SendGrid email sending integration"""
        # Configure SendGrid
        self.EmailManager.Config["providers"]["sendgrid"]["enabled"] = True
        self.EmailManager.Config["providers"]["sendgrid"]["api_key"] = "test_api_key"
        
        # Mock successful response
        MockResponse = MagicMock()
        MockResponse.status_code = 202
        MockResponse.headers = {"X-Message-Id": "test_message_id"}
        MockPost.return_value = MockResponse
        
        # Send email
        Result = self.EmailManager.SendViaSendGrid(self.TestEmailData)
        
        # Verify result
        self.assertTrue(Result["success"])
        self.assertEqual(Result["provider"], "sendgrid")
        self.assertEqual(Result["message_id"], "test_message_id")
        
        # Verify API call
        MockPost.assert_called_once()
        CallArgs = MockPost.call_args
        
        # Check URL (access via args or kwargs)
        if "url" in CallArgs[1]:
            self.assertEqual(CallArgs[1]["url"], "https://api.sendgrid.com/v3/mail/send")
        else:
            # Check first positional argument for URL
            self.assertEqual(CallArgs[0][0] if CallArgs[0] else "", "https://api.sendgrid.com/v3/mail/send")
        
        # Check headers
        self.assertIn("Authorization", CallArgs[1]["headers"])
        self.assertEqual(CallArgs[1]["headers"]["Authorization"], "Bearer test_api_key")
        
        # Check payload
        Payload = CallArgs[1]["json"]
        self.assertIn("personalizations", Payload)
        self.assertEqual(Payload["personalizations"][0]["to"][0]["email"], "test@example.com")
        
        print("✅ SendGrid integration test successful")
    
    @unittest.skipIf(not BOTO3_AVAILABLE, "boto3 not available")
    @patch('boto3.client') 
    def test_aws_ses_integration(self, MockBoto3Client):
        """Test AWS SES email sending integration"""
        # Configure AWS SES
        self.EmailManager.Config["providers"]["aws_ses"]["enabled"] = True
        self.EmailManager.Config["providers"]["aws_ses"]["access_key_id"] = "test_key"
        self.EmailManager.Config["providers"]["aws_ses"]["secret_access_key"] = "test_secret"
        
        # Mock SES client
        MockSESClient = MagicMock()
        MockSESClient.send_email.return_value = {"MessageId": "aws_message_id"}
        MockBoto3Client.return_value = MockSESClient
        
        # Initialize SES client
        self.EmailManager.InitializeProviders()
        self.EmailManager.SESClient = MockSESClient
        
        # Send email
        Result = self.EmailManager.SendViaAWSSES(self.TestEmailData)
        
        # Verify result
        self.assertTrue(Result["success"])
        self.assertEqual(Result["provider"], "aws_ses")
        self.assertEqual(Result["message_id"], "aws_message_id")
        
        # Verify SES call
        MockSESClient.send_email.assert_called_once()
        CallArgs = MockSESClient.send_email.call_args[1]
        
        self.assertEqual(CallArgs["Destination"]["ToAddresses"], ["test@example.com"])
        self.assertIn("Welcome to AndyLibrary", CallArgs["Message"]["Subject"]["Data"])
        
        print("✅ AWS SES integration test successful")
    
    @patch('requests.post')
    def test_mailgun_integration(self, MockPost):
        """Test Mailgun email sending integration"""
        # Configure Mailgun
        self.EmailManager.Config["providers"]["mailgun"]["enabled"] = True
        self.EmailManager.Config["providers"]["mailgun"]["api_key"] = "test_mailgun_key"
        self.EmailManager.Config["providers"]["mailgun"]["domain"] = "mg.andylibrary.org"
        
        # Mock successful response
        MockResponse = MagicMock()
        MockResponse.status_code = 200
        MockResponse.json.return_value = {"id": "mailgun_message_id"}
        MockPost.return_value = MockResponse
        
        # Send email
        Result = self.EmailManager.SendViaMailgun(self.TestEmailData)
        
        # Verify result
        self.assertTrue(Result["success"])
        self.assertEqual(Result["provider"], "mailgun")
        self.assertEqual(Result["message_id"], "mailgun_message_id")
        
        # Verify API call
        MockPost.assert_called_once()
        CallArgs = MockPost.call_args
        
        # Check URL (access via args or kwargs)
        ExpectedUrl = "https://api.mailgun.net/v3/mg.andylibrary.org/messages"
        if "url" in CallArgs[1]:
            self.assertEqual(CallArgs[1]["url"], ExpectedUrl)
        else:
            # Check first positional argument for URL
            self.assertEqual(CallArgs[0][0] if CallArgs[0] else "", ExpectedUrl)
        
        # Check auth
        self.assertEqual(CallArgs[1]["auth"], ("api", "test_mailgun_key"))
        
        # Check payload
        self.assertEqual(CallArgs[1]["data"]["to"], "test@example.com")
        
        print("✅ Mailgun integration test successful")
    
    @patch('smtplib.SMTP')
    def test_smtp_fallback(self, MockSMTP):
        """Test SMTP fallback email sending"""
        # Configure SMTP
        self.EmailManager.Config["providers"]["smtp"]["enabled"] = True
        self.EmailManager.Config["providers"]["smtp"]["username"] = "test@gmail.com"
        self.EmailManager.Config["providers"]["smtp"]["password"] = "test_password"
        
        # Mock SMTP server
        MockSMTPInstance = MagicMock()
        MockSMTP.return_value.__enter__.return_value = MockSMTPInstance
        
        # Send email
        Result = self.EmailManager.SendViaSMTP(self.TestEmailData)
        
        # Verify result
        self.assertTrue(Result["success"])
        self.assertEqual(Result["provider"], "smtp")
        
        # Verify SMTP calls
        MockSMTPInstance.starttls.assert_called_once()
        MockSMTPInstance.login.assert_called_once_with("test@gmail.com", "test_password")
        MockSMTPInstance.send_message.assert_called_once()
        
        print("✅ SMTP fallback test successful")
    
    def test_provider_fallback_mechanism(self):
        """Test fallback to multiple providers when primary fails"""
        # Disable all providers initially
        for Provider in self.EmailManager.Config["providers"].values():
            Provider["enabled"] = False
        
        # Test fallback with no providers enabled
        Result = self.EmailManager.SendWithFallback(self.TestEmailData)
        self.assertFalse(Result["success"])
        self.assertIn("All providers failed", Result["error"])
        
        print("✅ Provider fallback mechanism test successful")
    
    @patch('smtplib.SMTP')
    def test_verification_email_workflow(self, MockSMTP):
        """Test complete verification email workflow"""
        # Enable mock provider for testing
        self.EmailManager.Config["providers"]["smtp"]["enabled"] = True
        self.EmailManager.Config["providers"]["smtp"]["username"] = "test@example.com"
        self.EmailManager.Config["providers"]["smtp"]["password"] = "test_password"
        self.EmailManager.Provider = "smtp"  # Set active provider
        
        # Mock SMTP server
        MockSMTPInstance = MagicMock()
        MockSMTP.return_value.__enter__.return_value = MockSMTPInstance
        
        Result = self.EmailManager.SendVerificationEmail(
            Email="student@university.edu",
            VerificationToken="secure_token_123",
            Username="student"
        )
        
        # Should succeed with mock configuration
        self.assertTrue(Result["success"])
        
        print("✅ Verification email workflow test successful")
    
    @patch('smtplib.SMTP')
    def test_welcome_email_workflow(self, MockSMTP):
        """Test welcome email sending workflow"""
        # Enable mock provider for testing
        self.EmailManager.Config["providers"]["smtp"]["enabled"] = True
        self.EmailManager.Config["providers"]["smtp"]["username"] = "test@example.com"
        self.EmailManager.Config["providers"]["smtp"]["password"] = "test_password"
        self.EmailManager.Provider = "smtp"  # Set active provider
        
        # Mock SMTP server
        MockSMTPInstance = MagicMock()
        MockSMTP.return_value.__enter__.return_value = MockSMTPInstance
        
        Result = self.EmailManager.SendWelcomeEmail(
            Email="newuser@example.com",
            Username="newuser"
        )
        
        # Should succeed with mock
        self.assertTrue(Result["success"])
        
        print("✅ Welcome email workflow test successful")
    
    @patch('smtplib.SMTP')
    def test_password_reset_workflow(self, MockSMTP):
        """Test password reset email workflow"""
        # Enable mock provider for testing
        self.EmailManager.Config["providers"]["smtp"]["enabled"] = True
        self.EmailManager.Config["providers"]["smtp"]["username"] = "test@example.com"
        self.EmailManager.Config["providers"]["smtp"]["password"] = "test_password"
        self.EmailManager.Provider = "smtp"  # Set active provider
        
        # Mock SMTP server
        MockSMTPInstance = MagicMock()
        MockSMTP.return_value.__enter__.return_value = MockSMTPInstance
        
        Result = self.EmailManager.SendPasswordResetEmail(
            Email="user@example.com",
            ResetToken="reset_token_456",
            Username="user"
        )
        
        # Should succeed with mock
        self.assertTrue(Result["success"])
        
        print("✅ Password reset workflow test successful")
    
    def test_configuration_validation(self):
        """Test email configuration validation"""
        TestResult = self.EmailManager.TestEmailConfiguration()
        
        # Should return test results for all providers
        self.assertIn("providers", TestResult)
        self.assertIn("sendgrid", TestResult["providers"])
        self.assertIn("aws_ses", TestResult["providers"])
        self.assertIn("mailgun", TestResult["providers"])
        self.assertIn("smtp", TestResult["providers"])
        
        # All should be disabled by default (no API keys)
        for ProviderName, ProviderResult in TestResult["providers"].items():
            # Check if enabled key exists before accessing
            if "enabled" in ProviderResult and ProviderResult["enabled"]:
                self.assertIn("status", ProviderResult)
            else:
                self.assertEqual(ProviderResult.get("status", "disabled"), "disabled")
        
        print("✅ Configuration validation test successful")

def RunEmailServiceTests():
    """Run email service integration tests with detailed output"""
    print("🔍 STARTING EMAIL SERVICE INTEGRATION TESTS")
    print("=" * 65)
    
    # Create test suite
    TestSuite = unittest.TestLoader().loadTestsFromTestCase(TestEmailServiceIntegration)
    
    # Run tests with verbose output
    TestRunner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    TestResult = TestRunner.run(TestSuite)
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 EMAIL SERVICE TEST SUMMARY")
    print(f"   Tests Run: {TestResult.testsRun}")
    print(f"   Failures: {len(TestResult.failures)}")
    print(f"   Errors: {len(TestResult.errors)}")
    print(f"   Skipped: {len(TestResult.skipped) if hasattr(TestResult, 'skipped') else 0}")
    
    if TestResult.wasSuccessful():
        print("   Status: ✅ ALL EMAIL SERVICE TESTS PASSED")
        print("\n🎉 EmailManager is ready for production deployment!")
        print("\n📧 Next Steps:")
        print("   1. Configure production email service (SendGrid/AWS SES/Mailgun)")
        print("   2. Set environment variables with real API keys")
        print("   3. Test with real email delivery")
        print("   4. Monitor email delivery rates and failures")
    else:
        print("   Status: ❌ SOME TESTS FAILED")
        
        if TestResult.failures:
            print("\n🔥 FAILURES:")
            for test, traceback in TestResult.failures:
                print(f"   {test}: {traceback}")
        
        if TestResult.errors:
            print("\n💥 ERRORS:")  
            for test, traceback in TestResult.errors:
                print(f"   {test}: {traceback}")
    
    return TestResult.wasSuccessful()

if __name__ == "__main__":
    RunEmailServiceTests()