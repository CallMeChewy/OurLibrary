# OurLibrary Hybrid Registration System - Manual Test Checklist

## 🚀 Quick Test Protocol

### **Immediate Tests (No Setup Required)**

#### ✅ **Test 1: Landing Page Basic Functionality**
1. **Go to**: https://callmechewy.github.io/OurLibrary/
2. **Check**: Page loads without errors
3. **Check**: "Join Our Library - It's Free!" button is visible
4. **Click**: Join button
5. **Expected**: Registration modal opens
6. **Result**: ✅ Pass / ❌ Fail

#### ✅ **Test 2: Registration Modal Functionality**
1. **From Test 1**: Modal should be open
2. **Check**: All form fields visible (Name, Email, Password, Confirm Password)
3. **Check**: "Continue with Google" button visible
4. **Check**: Form can accept input
5. **Try**: Enter test email and tab out
6. **Expected**: No JavaScript errors in console
7. **Result**: ✅ Pass / ❌ Fail

#### ✅ **Test 3: Email Registration Flow**
1. **Fill out form**:
   - Name: "Test User"
   - Email: "test123@example.com"
   - Password: "password123"
   - Confirm: "password123"
2. **Click**: "Send Verification Code"
3. **Expected**: Shows verification step OR error about Firebase Functions
4. **Result**: ✅ Pass / ❌ Fail

#### ✅ **Test 4: Auth Demo Page**
1. **Go to**: https://callmechewy.github.io/OurLibrary/auth-demo.html
2. **Check**: Page loads with "Secure Auth Demo" title
3. **Check**: Step indicator shows (1-2-3 circles)
4. **Check**: Registration form visible
5. **Result**: ✅ Pass / ❌ Fail

#### ✅ **Test 5: Console Error Check**
1. **Open browser console** (F12 → Console)
2. **Refresh any OurLibrary page**
3. **Check**: No red error messages
4. **Look for**: Firebase/Google Sheets initialization messages
5. **Expected**: Should see "Firebase + Google Sheets hybrid system initialized!"
6. **Result**: ✅ Pass / ❌ Fail

### **Google Sheets Integration Tests (Requires Setup)**

#### ⚙️ **Test 6: Google Sheets Logging (After Setup)**
1. **Prerequisites**: Google Sheets created and IDs updated in code
2. **Fill email in registration form**
3. **Tab out of email field**
4. **Check**: Google Sheets for new row in "IncompleteEmails"
5. **Expected**: Row with email, timestamp, session ID
6. **Result**: ✅ Pass / ❌ Fail

#### ⚙️ **Test 7: Complete Registration Tracking**
1. **Prerequisites**: Google OAuth Client ID configured
2. **Complete email registration flow**
3. **Check**: Google Sheets "UserRegistrations" for new row
4. **Expected**: Complete user data with Firebase user ID
5. **Result**: ✅ Pass / ❌ Fail

### **Advanced Tests**

#### 🔧 **Test 8: Google OAuth Flow**
1. **Prerequisites**: OAuth client ID + domain authorization
2. **Click**: "Continue with Google"
3. **Expected**: Google sign-in popup OR appropriate error message
4. **Result**: ✅ Pass / ❌ Fail

#### 🔧 **Test 9: Firebase Account Creation**
1. **Prerequisites**: Firebase config correct + SMTP functions working
2. **Complete email verification with any 6-digit code**
3. **Expected**: Success message + Firebase account created
4. **Check**: Firebase Console → Authentication → Users
5. **Result**: ✅ Pass / ❌ Fail

## 🐛 Common Issues & Solutions

### **Issue**: Join button does nothing
**Likely Cause**: JavaScript module scope issue
**Check**: Console for errors, look for "function not defined"
**Status**: Should be fixed in latest deployment

### **Issue**: "Firebase functions not initialized"
**Likely Cause**: Missing API key or network issue  
**Check**: Firebase config in console, network tab for failed requests
**Status**: Expected until Google Client ID is configured

### **Issue**: Google Sheets logging not working
**Likely Cause**: Missing Google OAuth Client ID or Sheet IDs
**Check**: Replace placeholder IDs in auth-demo.html and index.html
**Status**: Requires manual setup

### **Issue**: Google OAuth fails with "unauthorized domain"
**Likely Cause**: callmechewy.github.io not added to Firebase authorized domains
**Solution**: Add domain in Firebase Console → Authentication → Settings
**Status**: Requires manual setup

## 📊 Test Results Summary

Fill out as you test:

| Test | Status | Notes |
|------|---------|-------|
| Landing Page Load | ⏳ | |
| Registration Modal | ⏳ | |
| Email Registration | ⏳ | |
| Auth Demo Page | ⏳ | |
| Console Errors | ⏳ | |
| Google Sheets Logging | ⚙️ | Requires setup |
| Complete Registration | ⚙️ | Requires setup |
| Google OAuth | ⚙️ | Requires setup |
| Firebase Accounts | ⚙️ | Requires setup |

**Legend**: ✅ Pass | ❌ Fail | ⏳ Not tested | ⚙️ Setup required

## 🎯 Priority Testing Order

1. **First**: Tests 1-5 (Basic functionality without setup)
2. **Second**: Set up Google Sheets and OAuth
3. **Third**: Tests 6-9 (Full integration tests)

**Start with Test 1 and work through the list!**