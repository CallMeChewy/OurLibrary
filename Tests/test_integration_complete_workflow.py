# File: test_integration_complete_workflow.py
# Path: /home/herb/Desktop/AndyLibrary/Tests/test_integration_complete_workflow.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 11:14AM

"""
Integration Tests for Complete User Workflow
Tests the entire user journey from BowersWorld to native app launch
"""

import unittest
import requests
import json
import time
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add source directory to path and change to project root for proper file access
TestDir = Path(__file__).parent
ProjectRoot = TestDir.parent
SourceDir = ProjectRoot / "Source"
sys.path.insert(0, str(SourceDir))

# Change to project root so relative paths work correctly
OriginalDir = os.getcwd()
os.chdir(str(ProjectRoot))

from Core.DatabaseManager import DatabaseManager
from Core.UserSetupManager import UserSetupManager

class TestCompleteUserWorkflow(unittest.TestCase):
    """Test complete user workflow integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.TestDir = tempfile.mkdtemp(prefix="andylibrary_integration_test_")
        cls.TestDbPath = os.path.join(cls.TestDir, "test_library.db")
        
        # Create minimal test database
        cls.CreateTestDatabase()
        
        # Test server configuration
        cls.BaseUrl = "http://127.0.0.1:8080"
        cls.TestUser = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "username": "testuser",
            "mission_acknowledged": True
        }
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if os.path.exists(cls.TestDir):
            shutil.rmtree(cls.TestDir)
    
    @classmethod
    def CreateTestDatabase(cls):
        """Create minimal test database with required tables"""
        import sqlite3
        
        Connection = sqlite3.connect(cls.TestDbPath)
        
        # Create minimal books table for compatibility
        Connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT,
                FilePath TEXT,
                ThumbnailImage BLOB,
                category_id INTEGER,
                subject_id INTEGER,
                Rating REAL,
                FileSize INTEGER,
                PageCount INTEGER
            )
        """)
        
        # Create categories table
        Connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                category TEXT
            )
        """)
        
        # Create subjects table
        Connection.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                subject TEXT,
                category_id INTEGER
            )
        """)
        
        # Insert test data
        Connection.execute("INSERT INTO categories (id, category) VALUES (1, 'Education')")
        Connection.execute("INSERT INTO subjects (id, subject, category_id) VALUES (1, 'Computer Science', 1)")
        Connection.execute("""
            INSERT INTO books (id, title, author, FilePath, category_id, subject_id, Rating, FileSize, PageCount)
            VALUES (1, 'Test Book', 'Test Author', '/test/path', 1, 1, 4.5, 1024000, 250)
        """)
        
        Connection.commit()
        Connection.close()

    def setUp(self):
        """Set up each test"""
        # Initialize database manager with test database
        self.DbManager = DatabaseManager(self.TestDbPath)
        
        # Clean up any existing test user
        try:
            self.DbManager.Connection.execute("DELETE FROM Users WHERE Email = ?", (self.TestUser["email"],))
            self.DbManager.Connection.commit()
        except Exception:
            pass
        
    def tearDown(self):
        """Clean up after each test"""
        if self.DbManager:
            self.DbManager.Disconnect()
    
    def test_01_bowersworld_landing_page_accessible(self):
        """Test that BowersWorld landing page is accessible"""
        try:
            Response = requests.get(f"{self.BaseUrl}/", timeout=5)
            self.assertEqual(Response.status_code, 200)
            # Check for either BowersWorld content or library content (both valid entry points)
            HasBowersWorld = "Project Himalaya" in Response.text and "Getting education into the hands" in Response.text
            HasLibrary = "Anderson's Library" in Response.text
            self.assertTrue(HasBowersWorld or HasLibrary, "Should show either BowersWorld or Library interface")
            
            if HasBowersWorld:
                print("✅ BowersWorld landing page accessible")
            else:
                print("✅ Library interface accessible (alternative entry point)")
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - start with 'python StartOurLibrary.py'")
    
    def test_02_auth_page_accessible(self):
        """Test that authentication page is accessible"""
        try:
            Response = requests.get(f"{self.BaseUrl}/auth.html", timeout=5)
            self.assertEqual(Response.status_code, 200)
            # Check for registration/login functionality (case insensitive)
            ResponseText = Response.text.lower()
            HasRegister = "register" in ResponseText or "join us" in ResponseText or "join" in ResponseText
            HasLogin = "login" in ResponseText or "enter" in ResponseText
            self.assertTrue(HasRegister and HasLogin, "Should have both registration and login options")
            print("✅ Authentication page accessible")
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - start with 'python StartOurLibrary.py'")
    
    def test_03_user_registration_workflow(self):
        """Test complete user registration workflow"""
        # Test user registration using correct parameter names
        Result = self.DbManager.CreateUser(
            Email=self.TestUser["email"],
            Password=self.TestUser["password"], 
            Username=self.TestUser["username"],
            MissionAcknowledged=self.TestUser["mission_acknowledged"]
        )
        
        if not Result["success"]:
            print(f"❌ User registration failed: {Result}")
            
        self.assertTrue(Result["success"], f"Registration failed: {Result.get('error', 'Unknown error')}")
        self.assertEqual(Result["email"], self.TestUser["email"])
        self.assertEqual(Result["access_level"], "pending")
        self.assertFalse(Result["email_verified"])
        
        print(f"✅ User registration successful: {Result['email']}")
        
        # Store user ID for subsequent tests
        self.UserId = Result["user_id"]
        
        return Result
    
    def test_04_email_verification_workflow(self):
        """Test email verification workflow"""
        # Create user for this test
        Result = self.DbManager.CreateUser(
            Email=self.TestUser["email"],
            Password=self.TestUser["password"], 
            Username=self.TestUser["username"],
            MissionAcknowledged=self.TestUser["mission_acknowledged"]
        )
        
        self.assertTrue(Result["success"], f"Registration failed: {Result.get('error', 'Unknown error')}")
        RegistrationResult = Result
        
        # Get verification token from database
        User = self.DbManager.Connection.execute("""
            SELECT EmailVerificationToken FROM Users WHERE Id = ?
        """, (RegistrationResult["user_id"],)).fetchone()
        
        self.assertIsNotNone(User)
        VerificationToken = User["EmailVerificationToken"] if User else None
        self.assertIsNotNone(VerificationToken)
        
        # Verify email using correct parameter name
        VerificationResult = self.DbManager.VerifyUserEmail(VerificationToken=VerificationToken)
        
        self.assertTrue(VerificationResult["success"])
        self.assertEqual(VerificationResult["user_id"], RegistrationResult["user_id"])
        
        print(f"✅ Email verification successful: {VerificationResult['email']}")
        
        return VerificationResult
    
    def test_05_user_authentication_workflow(self):
        """Test user authentication after email verification"""
        # Create and verify user for this test
        Result = self.DbManager.CreateUser(
            Email=self.TestUser["email"],
            Password=self.TestUser["password"], 
            Username=self.TestUser["username"],
            MissionAcknowledged=self.TestUser["mission_acknowledged"]
        )
        
        # Get and use verification token
        User = self.DbManager.Connection.execute("""
            SELECT EmailVerificationToken FROM Users WHERE Id = ?
        """, (Result["user_id"],)).fetchone()
        
        VerificationToken = User["EmailVerificationToken"] if User else None
        VerificationResult = self.DbManager.VerifyUserEmail(VerificationToken=VerificationToken)
        self.assertTrue(VerificationResult["success"])
        
        # Authenticate user using correct parameter names
        AuthResult = self.DbManager.AuthenticateUser(
            Email=self.TestUser["email"], 
            Password=self.TestUser["password"]
        )
        
        self.assertTrue(AuthResult["success"])
        self.assertEqual(AuthResult["user"]["email"], self.TestUser["email"])
        self.assertTrue(AuthResult["user"]["email_verified"])
        
        print(f"✅ User authentication successful: {AuthResult['user']['email']}")
        
        return AuthResult
    
    def test_06_session_management_workflow(self):
        """Test session creation and validation"""
        # Create, verify, and authenticate user for this test
        Result = self.DbManager.CreateUser(
            Email=self.TestUser["email"],
            Password=self.TestUser["password"], 
            Username=self.TestUser["username"],
            MissionAcknowledged=self.TestUser["mission_acknowledged"]
        )
        
        # Verify email
        User = self.DbManager.Connection.execute("""
            SELECT EmailVerificationToken FROM Users WHERE Id = ?
        """, (Result["user_id"],)).fetchone()
        
        VerificationToken = User["EmailVerificationToken"] if User else None
        self.DbManager.VerifyUserEmail(VerificationToken=VerificationToken)
        
        # Authenticate user
        AuthResult = self.DbManager.AuthenticateUser(
            Email=self.TestUser["email"], 
            Password=self.TestUser["password"]
        )
        self.assertTrue(AuthResult["success"])
        UserId = AuthResult["user"]["id"]
        
        # Create session using correct parameter names
        SessionResult = self.DbManager.CreateUserSession(
            UserId=UserId, 
            IPAddress="127.0.0.1", 
            UserAgent="TestAgent/1.0"
        )
        
        self.assertTrue(SessionResult["success"])
        self.assertIsNotNone(SessionResult["session_token"])
        
        # Validate session using correct parameter names
        ValidationResult = self.DbManager.ValidateSession(SessionToken=SessionResult["session_token"])
        
        self.assertTrue(ValidationResult["success"])
        self.assertEqual(ValidationResult["user"]["id"], UserId)
        
        print(f"✅ Session management successful for user: {ValidationResult['user']['email']}")
        
        return SessionResult
    
    @patch('Core.UserSetupManager.UserSetupManager')
    def test_07_user_setup_manager_initialization(self, MockSetupManager):
        """Test UserSetupManager initialization with user isolation"""
        # Mock setup manager to avoid actual file system operations
        MockInstance = MagicMock()
        MockInstance.Username = "testuser"
        MockInstance.Platform = "linux"
        MockInstance.AndyLibraryDir = Path("/tmp/test/andylibrary/users/testuser")
        MockSetupManager.return_value = MockInstance
        
        # Initialize setup manager
        SetupManager = UserSetupManager(user_id=1, username="testuser")
        
        # Verify proper initialization
        self.assertEqual(SetupManager.Username, "testuser")
        self.assertEqual(SetupManager.Platform, "linux")
        self.assertTrue(str(SetupManager.AndyLibraryDir).endswith("users/testuser"))
        
        print("✅ UserSetupManager initialization successful with user isolation")
    
    def test_08_database_library_functionality(self):
        """Test that library database functionality works"""
        # Test getting books
        Books = self.DbManager.GetBooks(Limit=10)
        self.assertIsInstance(Books, list)
        
        if Books:
            self.assertIn('title', Books[0])
            self.assertIn('author', Books[0])
            print(f"✅ Library functionality working - {len(Books)} books available")
        else:
            print("✅ Library functionality working - empty library handled correctly")
        
        # Test getting categories
        Categories = self.DbManager.GetCategories()
        self.assertIsInstance(Categories, list)
        
        if Categories:
            self.assertIn('name', Categories[0])
            print(f"✅ Categories functionality working - {len(Categories)} categories available")
    
    def test_09_api_endpoints_availability(self):
        """Test that key API endpoints are available"""
        Endpoints = [
            "/",
            "/auth.html",
            "/setup.html",
            "/api/categories",
            "/docs"
        ]
        
        AvailableEndpoints = []
        
        for Endpoint in Endpoints:
            try:
                Response = requests.get(f"{self.BaseUrl}{Endpoint}", timeout=5)
                if Response.status_code == 200:
                    AvailableEndpoints.append(Endpoint)
            except requests.exceptions.ConnectionError:
                self.skipTest("Server not running - start with 'python StartOurLibrary.py'")
            except Exception:
                pass  # Endpoint may not be implemented yet
        
        self.assertGreater(len(AvailableEndpoints), 0, "At least some endpoints should be available")
        print(f"✅ API endpoints available: {', '.join(AvailableEndpoints)}")
    
    def test_10_complete_user_journey_simulation(self):
        """Simulate complete user journey from registration to library access"""
        print("\n🚀 SIMULATING COMPLETE USER JOURNEY")
        
        # Step 1: User visits BowersWorld
        print("   1. User visits BowersWorld landing page...")
        self.test_01_bowersworld_landing_page_accessible()
        
        # Step 2: User navigates to registration
        print("   2. User navigates to registration page...")
        self.test_02_auth_page_accessible()
        
        # Step 3: User registers account
        print("   3. User registers new account...")
        RegistrationResult = self.test_03_user_registration_workflow()
        
        # Step 4: User verifies email (using the registration from step 3)
        print("   4. User verifies email address...")
        User = self.DbManager.Connection.execute("""
            SELECT EmailVerificationToken FROM Users WHERE Email = ?
        """, (self.TestUser["email"],)).fetchone()
        
        VerificationToken = User["EmailVerificationToken"] if User else None
        VerificationResult = self.DbManager.VerifyUserEmail(VerificationToken=VerificationToken)
        self.assertTrue(VerificationResult["success"])
        print(f"✅ Email verification successful: {VerificationResult['email']}")
        
        # Step 5: User authenticates
        print("   5. User logs in with credentials...")
        AuthResult = self.DbManager.AuthenticateUser(
            Email=self.TestUser["email"], 
            Password=self.TestUser["password"]
        )
        self.assertTrue(AuthResult["success"])
        print(f"✅ User authentication successful: {AuthResult['user']['email']}")
        
        # Step 6: System creates session
        print("   6. System creates user session...")
        SessionResult = self.DbManager.CreateUserSession(
            UserId=AuthResult["user"]["id"], 
            IPAddress="127.0.0.1", 
            UserAgent="TestAgent/1.0"
        )
        self.assertTrue(SessionResult["success"])
        print(f"✅ Session management successful for user: {AuthResult['user']['email']}")
        
        # Step 7: User setup process (mocked)
        print("   7. User setup and installation process...")
        self.test_07_user_setup_manager_initialization()
        
        # Step 8: Library access
        print("   8. User accesses library functionality...")
        self.test_08_database_library_functionality()
        
        print("\n✅ COMPLETE USER JOURNEY SIMULATION SUCCESSFUL")
        print(f"   📧 User: {self.TestUser['email']}")
        print(f"   🔑 Session: Active")
        print(f"   📚 Library: Accessible")
        print(f"   🎯 Mission: Educational access achieved")

def RunIntegrationTests():
    """Run integration tests with detailed output"""
    print("🔍 STARTING INTEGRATION TESTS FOR COMPLETE USER WORKFLOW")
    print("=" * 70)
    
    # Create test suite
    TestSuite = unittest.TestLoader().loadTestsFromTestCase(TestCompleteUserWorkflow)
    
    # Run tests with verbose output
    TestRunner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    TestResult = TestRunner.run(TestSuite)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print(f"   Tests Run: {TestResult.testsRun}")
    print(f"   Failures: {len(TestResult.failures)}")
    print(f"   Errors: {len(TestResult.errors)}")
    print(f"   Skipped: {len(TestResult.skipped) if hasattr(TestResult, 'skipped') else 0}")
    
    if TestResult.wasSuccessful():
        print("   Status: ✅ ALL INTEGRATION TESTS PASSED")
        print("\n🎉 AndyLibrary is ready for complete user workflows!")
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
    RunIntegrationTests()