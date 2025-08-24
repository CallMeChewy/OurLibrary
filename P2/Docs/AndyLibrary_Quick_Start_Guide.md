# AndyLibrary Quick Start Guide

## Complete User Journey - Shortest Path to Library Access

**"Getting education into the hands of people who can least afford it"**

This guide provides exact step-by-step instructions to get from zero to a fully functional AndyLibrary in the shortest possible path.

---

## Prerequisites

- Computer with internet connection
- Web browser (Chrome, Firefox, Safari, Edge)
- Email address for account creation

---

## Step-by-Step Instructions

### Step 1: Access the Landing Page

**User Action:**

```
Open web browser and navigate to: http://127.0.0.1:8080
```

**System Response:**

- Loads bowersworld.html (Project Himalaya landing page)
- Shows purple gradient background
- Displays "Project Himalaya" branding
- Shows mission statement: "Getting education into the hands of people who can least afford it"
- Renders three feature cards: AI-Powered Curation, Human Expertise, Global Access
- Displays three action buttons

---

### Step 2: Click Access AndyLibrary Now

**User Action:**

```
Click the orange button labeled: "🚀 Access AndyLibrary Now"
```

**System Response:**

- Redirects to /auth.html
- Loads authentication page with purple gradient background
- Shows "AndyLibrary" branding
- Displays mission statement
- Shows two tabs: "Login" (active) and "📝 Join Us"
- Login form is visible by default
- Social login options may appear (Google, GitHub, Facebook if configured)

---

### Step 3: Switch to Registration

**User Action:**

```
Click the tab labeled: "📝 Join Us"
```

**System Response:**

- JavaScript switchTab('register') function executes
- Console log: "🔄 Switching to tab: register"
- Login form fades out (display: none)
- Registration form slides in with animation
- Blue info banner appears: "💡 New to AndyLibrary? Fill out the form below..."
- Email field automatically receives focus
- Console log: "✅ Showing form: register-form"
- Console log: "🎯 Focused on first input: register-email"

---

### Step 4: Fill Registration Form - Email

**User Action:**

```
Type in email field: your.email@example.com
```

*(Replace with your actual email address)*

**System Response:**

- Text appears in email input field
- Real-time validation may trigger on blur
- Field border changes to blue on focus
- Form validation state updates

---

### Step 5: Fill Registration Form - Username (Optional)

**User Action:**

```
Type in username field: myusername
```

*(Replace with your preferred username, or leave blank)*

**System Response:**

- Text appears in username input field
- Availability check may trigger on keyup
- Field styling updates on focus

---

### Step 6: Fill Registration Form - Password

**User Action:**

```
Type in password field: MySecurePass123!
```

*(Use a password with at least 8 characters, including uppercase, lowercase, and numbers)*

**System Response:**

- Password text appears as dots/asterisks
- Password strength meter may update
- Field validation occurs in real-time
- Form button enablement state may change

---

### Step 7: Select Subscription Tier

**User Action:**

```
Click on: "Free Explorer" tier (should be pre-selected)
```

**System Response:**

- Tier option highlights with blue background and white text
- Other tier options return to default styling
- Hidden input field value updates to "free"
- selectedSubscriptionTier variable updates

---

### Step 8: Accept Mission Acknowledgment

**User Action:**

```
Click the checkbox next to: "I understand and support AndyLibrary's educational mission"
```

**System Response:**

- Checkbox becomes checked (✓)
- Form validation state updates
- Submit button may become enabled
- Required field validation passes

---

### Step 9: Submit Registration

**User Action:**

```
Click the button: "Join AndyLibrary"
```

**System Response:**

- Button becomes disabled

- Button text changes to show loading spinner: "Creating Account..."

- handleRegistration(event) JavaScript function executes

- Form fields become disabled

- POST request sent to /api/auth/register with JSON payload:
  
  ```json
  {
  "email": "your.email@example.com",
  "username": "myusername",
  "password": "MySecurePass123!",
  "subscription_tier": "free",
  "mission_acknowledgment": true,
  "data_sharing_consent": false,
  "anonymous_usage_consent": false
  }
  ```

---

### Step 10: Server Processing

**System Response:**

- Server validates all input fields
- Checks for duplicate email/username in database
- Generates bcrypt password hash (cost 12)
- Creates new user record in SQLite database
- Generates UUID verification token
- Sets email_verified to FALSE initially
- Attempts to send verification email via SMTP

**If successful:**

- HTTP 200/201 response returned
- User ID assigned (auto-increment)
- Green success message appears: "✅ Registration successful! 📧 Please check your email..."

**If email verification is required:**

- Form automatically switches back to Login tab after 3 seconds
- Email field pre-filled with registered email
- Additional message about email verification

---

### Step 11: Check Email (If Required)

**User Action:**

```
1. Open your email client
2. Look for email from "AndyLibrary noreply"
3. Subject: "Welcome - Verify Your Email"
4. Click the "Verify Email" button in the email
```

**System Response:**

- Email client opens verification link: /verify-email?token=abc123
- GET request sent to server with verification token
- Server validates token and expiration (24 hours)
- If valid: Updates email_verified to TRUE and is_active to TRUE
- Success page shown with green checkmark
- Auto-redirect to library after 10 seconds

---

### Step 12: Login to Library

**User Action:**

```
If redirected back to auth page, fill login form:
Email: your.email@example.com
Password: MySecurePass123!
Click: "Enter Library"
```

**System Response:**

- handleLogin(event) JavaScript function executes
- POST request to /api/auth/login
- Server validates credentials
- If successful:
  - Session token generated and returned
  - localStorage.setItem('auth_token', token)
  - localStorage.setItem('refresh_token', refresh_token)
  - localStorage.setItem('user_info', JSON.stringify(user))
  - Success message: "Login successful!"
  - Automatic redirect to /library after 1 second

---

### Step 13: Access Main Library

**System Response:**

- Browser navigates to /library
- desktop-library.html loads
- Main AndyLibrary interface appears
- User authentication verified
- Full library functionality available:
  - Search educational materials
  - Browse categories
  - Download resources
  - Access Google Drive integration
  - Use intelligent search features

---

## Alternative: Guest Access (Fastest Path)

If you want the absolute fastest access without registration:

**User Action:**

```
From the auth page, click: "Continue as Guest (Limited Access)"
```

**System Response:**

- Immediate redirect to /library
- Guest mode activated
- Limited functionality:
  - Browse available content
  - Limited search results (first 10)
  - No downloads
  - Registration prompts throughout interface
  - Sample pages only

---

## Summary

**Shortest Path with Full Access:**

1. Navigate to landing page
2. Click "Access AndyLibrary Now"
3. Click "📝 Join Us" tab
4. Enter email, username, password
5. Accept mission acknowledgment
6. Click "Join AndyLibrary"
7. Verify email (if required)
8. Login with credentials
9. Access full library

**Total Time:** 3-5 minutes depending on email verification

**Shortest Path with Limited Access:**

1. Navigate to landing page
2. Click "Access AndyLibrary Now"
3. Click "Continue as Guest"
4. Access limited library

**Total Time:** 30 seconds

---

## Troubleshooting

**Registration Issues:**

- Ensure email format is valid
- Password must be at least 8 characters
- Check spam folder for verification email
- Mission acknowledgment checkbox must be checked

**Login Issues:**

- Verify email address spelling
- Ensure password is correct (case-sensitive)
- Complete email verification if required
- Clear browser cache if persistent issues

**Setup/Installation:**

- Authentication required for setup process
- Complete registration and login first
- Setup page will guide you through installation
- Installation creates local shortcuts and configuration

---

**🎯 Result:** You now have full access to AndyLibrary's educational resources, supporting the mission of "getting education into the hands of people who can least afford it."