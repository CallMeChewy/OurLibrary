# AndyLibrary Complete User Flow Diagram

## From First Visit to Book Access - All Paths and Failure Points

```mermaid
flowchart TD
    %% Start Point
    START([👤 User Opens Browser]) --> VISIT_URL{Visit andylibrary.com}

    %% Initial Page Load
    VISIT_URL --> |First Time| LANDING[📄 Landing Page Loads<br/>- Static assets load<br/>- Service worker registers<br/>- Auth status checked]
    VISIT_URL --> |Returning User| CHECK_SESSION{Check Session Token}

    %% Landing Page Decision
    LANDING --> AUTH_STATUS{User Authenticated?}
    AUTH_STATUS --> |No| SHOW_AUTH[🔐 Show Authentication Options<br/>- Email/Password Form<br/>- OAuth Providers<br/>- Register Link]
    AUTH_STATUS --> |Yes| DASHBOARD[📚 Library Dashboard]

    %% Registration Flow Start
    SHOW_AUTH --> REG_CHOICE{User Choice}
    REG_CHOICE --> |Click Register| REG_FORM[📝 Registration Form<br/>Fields:<br/>- Email: user@example.com<br/>- Username: johndoe<br/>- Password: ••••••••<br/>- Mission Acknowledgment ☑️]
    REG_CHOICE --> |Login Existing| LOGIN_FORM[🔑 Login Form<br/>Fields:<br/>- Email: user@example.com<br/>- Password: ••••••••]
    REG_CHOICE --> |OAuth Login| OAUTH_FLOW[🌐 OAuth Provider Selection]

    %% Registration Submission
    REG_FORM --> REG_SUBMIT[📤 Submit Registration<br/>POST /api/auth/register<br/>Data: {email, username, password, mission_acknowledgment}]

    %% Registration Validation
    REG_SUBMIT --> REG_VALIDATE{Server Validation}
    REG_VALIDATE --> |✅ Valid| CHECK_DUPLICATE{Check Duplicates}
    REG_VALIDATE --> |❌ Invalid Data| REG_ERROR_VALIDATION[❌ Validation Error<br/>- Missing fields<br/>- Invalid email format<br/>- Weak password<br/>- Mission not acknowledged]
    REG_ERROR_VALIDATION --> REG_FORM

    %% Duplicate Check
    CHECK_DUPLICATE --> |No Duplicates| CREATE_USER[✅ Create User Account<br/>- Hash password with bcrypt<br/>- Generate verification token<br/>- Set EmailVerified=FALSE<br/>- Set IsActive=FALSE<br/>- Insert into Users table]
    CHECK_DUPLICATE --> |Email Exists| REG_ERROR_EMAIL[❌ Email Already Registered<br/>Status: 409 Conflict<br/>Message: "Email already in use"]
    CHECK_DUPLICATE --> |Username Exists| REG_ERROR_USERNAME[❌ Username Taken<br/>Status: 409 Conflict<br/>Message: "Username already taken"]
    REG_ERROR_EMAIL --> REG_FORM
    REG_ERROR_USERNAME --> REG_FORM

    %% User Creation Success
    CREATE_USER --> SEND_VERIFICATION[📧 Send Verification Email<br/>To: user@example.com<br/>From: HimalayaProject1@gmail.com<br/>Subject: "Welcome to AndyLibrary - Verify Your Email"<br/>Body: Contains verification link with token]

    %% Email Sending Process
    SEND_VERIFICATION --> EMAIL_SMTP{SMTP Connection}
    EMAIL_SMTP --> |✅ Success| EMAIL_SENT[✅ Email Sent Successfully<br/>SMTP: smtp.gmail.com:465<br/>SSL: Enabled<br/>Status: 250 OK]
    EMAIL_SMTP --> |❌ Failed| EMAIL_ERROR[❌ Email Send Failed<br/>- SMTP server down<br/>- Invalid credentials<br/>- Network timeout<br/>- Rate limit exceeded]

    EMAIL_SENT --> REG_SUCCESS[🎉 Registration Success<br/>Message: "Registration successful!<br/>Please check your email to verify account"<br/>User ID: 30 assigned]
    EMAIL_ERROR --> REG_SUCCESS_NO_EMAIL[⚠️ Registration Success<br/>Warning: "Account created but<br/>verification email failed to send"]

    REG_SUCCESS --> AWAIT_VERIFICATION[⏳ User Checks Email<br/>Action Required:<br/>- Check inbox/spam<br/>- Click verification link]
    REG_SUCCESS_NO_EMAIL --> AWAIT_VERIFICATION

    %% Email Verification Flow
    AWAIT_VERIFICATION --> EMAIL_RECEIVED{User Receives Email?}
    EMAIL_RECEIVED --> |Yes| CLICK_VERIFY[👆 Click Verification Link<br/>URL: /api/auth/verify-email?token=xyz123<br/>GET request with token parameter]
    EMAIL_RECEIVED --> |No - Lost/Spam| REQUEST_RESEND[🔄 Request Resend<br/>User clicks "Resend Email"<br/>POST /api/auth/resend-verification]
    EMAIL_RECEIVED --> |No - Never Arrives| EMAIL_ISSUES[📧 Email Delivery Issues<br/>- Spam folder<br/>- Email provider blocking<br/>- Incorrect email address<br/>- SMTP server issues]

    %% Verification Link Processing
    CLICK_VERIFY --> VERIFY_TOKEN{Validate Token}
    VERIFY_TOKEN --> |✅ Valid| ACTIVATE_ACCOUNT[✅ Activate Account<br/>- Set EmailVerified=TRUE<br/>- Set IsActive=TRUE<br/>- Set AccessLevel=basic<br/>- Clear verification token]
    VERIFY_TOKEN --> |❌ Invalid| VERIFY_ERROR[❌ Verification Failed<br/>- Token expired<br/>- Token not found<br/>- Already verified<br/>- Malformed token]

    ACTIVATE_ACCOUNT --> VERIFY_SUCCESS[🎉 Account Verified<br/>Redirect to login page<br/>Message: "Email verified successfully!<br/>You can now log in"]
    VERIFY_ERROR --> VERIFY_ERROR_PAGE[❌ Verification Error Page<br/>Options:<br/>- Request new verification<br/>- Contact support<br/>- Try login (if already verified)]

    %% Login Flow (New or Returning Users)
    LOGIN_FORM --> LOGIN_SUBMIT[📤 Submit Login<br/>POST /api/auth/login<br/>Data: {email, password}]
    VERIFY_SUCCESS --> LOGIN_FORM
    CHECK_SESSION --> |Valid Session| DASHBOARD
    CHECK_SESSION --> |Invalid/Expired| LOGIN_FORM

    %% Login Validation
    LOGIN_SUBMIT --> LOGIN_VALIDATE{Server Validation}
    LOGIN_VALIDATE --> |❌ Missing Fields| LOGIN_ERROR_FIELDS[❌ Missing Required Fields<br/>Status: 422<br/>Message: Field required errors]
    LOGIN_VALIDATE --> |✅ Fields Present| AUTH_USER{Authenticate User}
    LOGIN_ERROR_FIELDS --> LOGIN_FORM

    %% User Authentication Process
    AUTH_USER --> FIND_USER{Find User by Email}
    FIND_USER --> |Not Found| LOGIN_ERROR_INVALID[❌ Invalid Credentials<br/>Status: 401<br/>Message: "Invalid email or password"<br/>Security: Don't reveal if email exists]
    FIND_USER --> |Found| CHECK_LOCKOUT{Account Locked?}

    %% Account Security Checks
    CHECK_LOCKOUT --> |Yes - Locked| LOGIN_ERROR_LOCKED[❌ Account Locked<br/>Status: 423<br/>Message: "Account temporarily locked<br/>due to failed login attempts"<br/>Lockout: 15 minutes]
    CHECK_LOCKOUT --> |No| CHECK_EMAIL_VERIFIED{Email Verified?}

    CHECK_EMAIL_VERIFIED --> |No| LOGIN_ERROR_UNVERIFIED[❌ Email Not Verified<br/>Status: 401<br/>Message: "Email verification required<br/>Please check your email and verify"<br/>Options: Resend verification]
    CHECK_EMAIL_VERIFIED --> |Yes| CHECK_ACTIVE{Account Active?}

    CHECK_ACTIVE --> |No| LOGIN_ERROR_INACTIVE[❌ Account Deactivated<br/>Status: 401<br/>Message: "Account is deactivated<br/>Contact support for assistance"]
    CHECK_ACTIVE --> |Yes| VERIFY_PASSWORD{Verify Password}

    %% Password Verification
    VERIFY_PASSWORD --> PASSWORD_CHECK[🔐 bcrypt.checkpw<br/>Compare entered password with<br/>stored hash from database]
    PASSWORD_CHECK --> |✅ Match| RESET_ATTEMPTS[✅ Reset Login Attempts<br/>- Set LoginAttempts=0<br/>- Clear LockoutUntil<br/>- Update LastLoginAt]
    PASSWORD_CHECK --> |❌ No Match| INCREMENT_ATTEMPTS[❌ Increment Failed Attempts<br/>- LoginAttempts++<br/>- If attempts >= 5: Lock for 15min<br/>- Save to database]

    INCREMENT_ATTEMPTS --> LOGIN_ERROR_INVALID
    RESET_ATTEMPTS --> CREATE_SESSION[✅ Create User Session<br/>- Generate session token<br/>- Generate refresh token<br/>- Set expiration (24 hours)<br/>- Store in UserSessions table<br/>- Include user info in response]

    CREATE_SESSION --> LOGIN_SUCCESS[🎉 Login Successful<br/>Response includes:<br/>- User info (ID, email, username)<br/>- Session token<br/>- Refresh token<br/>- Expires at timestamp<br/>- Welcome message]

    %% Post-Login Dashboard Access
    LOGIN_SUCCESS --> DASHBOARD
    DASHBOARD --> LIBRARY_INTERFACE[📚 Library Dashboard Loads<br/>Features Available:<br/>- Search 1,219 books<br/>- Browse 26 categories<br/>- View 118 subjects<br/>- User profile menu<br/>- Book recommendations]

    %% Book Search and Browse
    LIBRARY_INTERFACE --> USER_ACTION{User Action}
    USER_ACTION --> |Search Books| SEARCH_FLOW[🔍 Search Books<br/>Query: "python programming"<br/>GET /api/books?search=python<br/>Returns: Book metadata from database]
    USER_ACTION --> |Browse Category| BROWSE_FLOW[📂 Browse Category<br/>Category: "Programming Languages"<br/>GET /api/books?category=21<br/>Returns: Filtered book list]
    USER_ACTION --> |Click Book| BOOK_ACCESS[📖 Access Book<br/>Book ID: 893<br/>Title: "Algorithmic Problem Solving with Python"<br/>Request: GET /api/books/893/url]

    %% Book Search Results
    SEARCH_FLOW --> SEARCH_RESULTS[📋 Search Results Displayed<br/>- Book titles and metadata<br/>- Author information<br/>- Subject categories<br/>- Availability status<br/>- Click to access options]
    BROWSE_FLOW --> BROWSE_RESULTS[📂 Category Results<br/>- Filtered book list<br/>- Pagination controls<br/>- Sort options<br/>- Filter by subject]

    SEARCH_RESULTS --> BOOK_SELECT{User Selects Book}
    BROWSE_RESULTS --> BOOK_SELECT
    BOOK_SELECT --> BOOK_ACCESS

    %% Book Access Flow - Critical Google Drive Integration
    BOOK_ACCESS --> GDRIVE_CHECK{Google Drive Configured?}
    GDRIVE_CHECK --> |No| GDRIVE_SETUP[⚙️ Google Drive Setup Required<br/>Redirect to: /setup.html<br/>Message: "To access books, configure<br/>Google Drive integration"]
    GDRIVE_CHECK --> |Yes| GDRIVE_AUTH{Google Auth Valid?}

    %% Google Drive Setup Process
    GDRIVE_SETUP --> OAUTH_START[🌐 Start OAuth Flow<br/>Redirect to Google:<br/>https://accounts.google.com/o/oauth2/auth<br/>Scopes: drive.readonly, drive.metadata.readonly<br/>Client ID: From config]

    OAUTH_START --> OAUTH_USER_ACTION{User Action at Google}
    OAUTH_USER_ACTION --> |Grants Permission| OAUTH_CALLBACK[✅ OAuth Callback<br/>GET /api/auth/oauth/callback<br/>Parameters: code, state<br/>Exchange code for tokens]
    OAUTH_USER_ACTION --> |Denies Permission| OAUTH_DENIED[❌ OAuth Denied<br/>Error: access_denied<br/>Message: "Google Drive access required<br/>to download books"]
    OAUTH_USER_ACTION --> |Timeout/Error| OAUTH_ERROR[❌ OAuth Error<br/>- Network timeout<br/>- Invalid client config<br/>- Google service down]

    OAUTH_CALLBACK --> SAVE_TOKENS[💾 Save Google Tokens<br/>- Access token<br/>- Refresh token<br/>- Expiration time<br/>- User association]
    OAUTH_DENIED --> GDRIVE_SETUP
    OAUTH_ERROR --> GDRIVE_SETUP

    SAVE_TOKENS --> GDRIVE_READY[✅ Google Drive Ready<br/>User can now access books<br/>from their Google Drive]
    GDRIVE_READY --> FIND_LIBRARY_FOLDER

    %% Google Drive Authentication Check
    GDRIVE_AUTH --> |Valid| FIND_LIBRARY_FOLDER[🔍 Find Library Folder<br/>Search Google Drive for:<br/>Folder name: "AndyLibrary"<br/>Type: application/vnd.google-apps.folder]
    GDRIVE_AUTH --> |Invalid/Expired| REFRESH_TOKENS{Refresh Tokens}

    REFRESH_TOKENS --> |Success| FIND_LIBRARY_FOLDER
    REFRESH_TOKENS --> |Failed| GDRIVE_SETUP

    %% Library Folder Discovery
    FIND_LIBRARY_FOLDER --> FOLDER_CHECK{Folder Exists?}
    FOLDER_CHECK --> |Not Found| FOLDER_MISSING[❌ Library Folder Missing<br/>Message: "Create 'AndyLibrary' folder<br/>in your Google Drive and<br/>upload book files to it"<br/>Instructions provided]
    FOLDER_CHECK --> |Found| SEARCH_BOOK_FILE[🔍 Search for Book File<br/>In folder: AndyLibrary<br/>Search for: "Algorithmic Problem Solving with Python"<br/>Extensions: .pdf, .epub, .mobi, .txt, .doc, .docx]

    %% Book File Search
    SEARCH_BOOK_FILE --> FILE_FOUND{Book File Found?}
    FILE_FOUND --> |Yes| GENERATE_DOWNLOAD_LINK[🔗 Generate Download Link<br/>Create temporary signed URL<br/>Valid for: 1 hour<br/>Direct download from Google Drive]
    FILE_FOUND --> |No| FILE_NOT_FOUND[❌ Book File Not Available<br/>Message: "Book not found in your<br/>Google Drive. Please upload:<br/>'Algorithmic Problem Solving with Python.pdf'<br/>to your AndyLibrary folder"]

    %% Successful Book Access
    GENERATE_DOWNLOAD_LINK --> BOOK_DELIVERY[📖 Book Delivered<br/>Options:<br/>- Direct download<br/>- Stream in browser<br/>- Open in PDF reader<br/>- Download progress tracking]

    %% Error Recovery Paths
    FOLDER_MISSING --> CREATE_FOLDER_HELP[📋 Folder Creation Help<br/>Step-by-step instructions:<br/>1. Go to drive.google.com<br/>2. Create "AndyLibrary" folder<br/>3. Upload book files<br/>4. Return to AndyLibrary<br/>5. Try accessing book again]

    FILE_NOT_FOUND --> UPLOAD_HELP[📋 File Upload Help<br/>Instructions:<br/>1. Download book from legitimate source<br/>2. Upload to AndyLibrary folder<br/>3. Ensure exact filename match<br/>4. Supported formats listed<br/>5. Retry book access]

    %% All Error Paths Lead Back to Recovery
    LOGIN_ERROR_INVALID --> LOGIN_FORM
    LOGIN_ERROR_LOCKED --> LOCKOUT_WAIT[⏰ Wait for Lockout Expiry<br/>Time remaining displayed<br/>Option to reset password<br/>Contact support link]
    LOGIN_ERROR_UNVERIFIED --> RESEND_VERIFICATION[📧 Resend Verification<br/>POST /api/auth/resend-verification<br/>New email sent with fresh token]
    LOGIN_ERROR_INACTIVE --> CONTACT_SUPPORT[📞 Contact Support<br/>Support channels provided<br/>Account reactivation process<br/>Appeal procedure]

    LOCKOUT_WAIT --> |After 15 min| LOGIN_FORM
    RESEND_VERIFICATION --> AWAIT_VERIFICATION

    %% Subsequent Visits Flow
    DASHBOARD --> |Return Visit| LIBRARY_INTERFACE
    BOOK_DELIVERY --> |User Returns| CHECK_SESSION

    %% Failure Recovery Summary
    OAUTH_DENIED --> GDRIVE_MANUAL[📖 Manual Instructions<br/>Alternative access methods<br/>Download books independently<br/>Support contact information]
    FOLDER_MISSING --> GDRIVE_MANUAL
    FILE_NOT_FOUND --> GDRIVE_MANUAL

    %% Success Path Summary
    BOOK_DELIVERY --> SUCCESS_END[🎉 SUCCESS<br/>User successfully accesses books<br/>Full functionality achieved<br/>Return visits streamlined]

    %% Style the flowchart
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px

    class START,SUCCESS_END startEnd
    class REG_FORM,LOGIN_FORM,SEND_VERIFICATION,CREATE_USER,BOOK_DELIVERY process
    class AUTH_STATUS,REG_CHOICE,CHECK_DUPLICATE,EMAIL_RECEIVED decision
    class REG_ERROR_VALIDATION,LOGIN_ERROR_INVALID,FOLDER_MISSING,FILE_NOT_FOUND error
    class LOGIN_SUCCESS,REG_SUCCESS,BOOK_DELIVERY success
```

## Critical Failure Points Analysis

### 🔥 **High-Risk Failure Points**

1. **Email Delivery Failure** (Lines 47-52)
   
   - SMTP server issues
   - User's email provider blocking
   - Spam folder filtering
   - **Impact**: User cannot verify account

2. **Google Drive OAuth Denial** (Lines 158-161)
   
   - User refuses permission
   - Invalid OAuth configuration
   - **Impact**: Cannot access any books

3. **Missing Library Folder** (Lines 184-186)
   
   - User hasn't created "AndyLibrary" folder
   - **Impact**: No books accessible despite working authentication

4. **Account Security Lockouts** (Lines 100-103)
   
   - 5 failed login attempts = 15-minute lockout
   - **Impact**: Legitimate users locked out

### 📊 **Data Flow Summary**

**Registration Data Captured:**

- Email: `user@example.com`
- Username: `johndoe`
- Password: `••••••••` (bcrypt hashed)
- Mission Acknowledgment: `true`
- Timestamps: Creation, verification, last login

**Email Communications:**

- **From**: `HimalayaProject1@gmail.com`
- **SMTP**: `smtp.gmail.com:465` (SSL)
- **Types**: Verification, password reset, welcome messages
- **Failure Handling**: Graceful degradation with manual verification options

**Session Management:**

- **Tokens**: Session + Refresh tokens
- **Expiration**: 24 hours default
- **Storage**: Database + HTTP-only cookies
- **Security**: CSRF protection, secure headers

This flowchart reveals that while the basic authentication flow is robust, the Google Drive dependency creates significant user experience friction points that need careful UX design and clear user guidance.