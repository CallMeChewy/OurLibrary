# Manual Testing Checklist for OurLibrary Authentication

**Date**: 2025-08-20  
**Tester**: _______________  
**Version**: Phase 1 Complete

---

## 🧪 Required Test Accounts

### New Email Account
- [ ] Create brand new email account (Gmail/Yahoo/Outlook)
- [ ] Email address: _______________________
- [ ] Password: ___________________________

### Google Account  
- [ ] Use existing Google account OR create new one
- [ ] Google email: _______________________

---

## 📧 EMAIL REGISTRATION FLOW

### Test 1: Basic Registration
- [ ] Navigate to: https://callmechewy.github.io/OurLibrary/
- [ ] Click "Get Started" button
- [ ] Verify redirect to auth-demo.html
- [ ] Enter new email address
- [ ] Enter password (minimum 6 characters)
- [ ] Click "Register with Email"
- [ ] Verify "Please check your email" message appears

### Test 2: Email Verification
- [ ] Check email inbox (including spam folder)
- [ ] Find verification email from OurLibrary
- [ ] Subject line: "Verify your email for OurLibrary"
- [ ] Click verification link
- [ ] Verify successful verification page loads
- [ ] Return to auth-demo.html
- [ ] Try logging in with verified email

### Test 3: Email Edge Cases
- [ ] Try registering same email again (should fail)
- [ ] Try invalid email format: `notanemail`
- [ ] Try email with spaces: ` test@gmail.com `
- [ ] Try empty email field
- [ ] Verify appropriate error messages

---

## 🔐 GOOGLE OAUTH FLOW

### Test 4: Google Authentication
- [ ] Navigate to: https://callmechewy.github.io/OurLibrary/auth-demo.html
- [ ] Click "Sign in with Google" button
- [ ] Verify Google OAuth popup opens
- [ ] Select Google account
- [ ] Grant permissions to OurLibrary
- [ ] Verify successful authentication
- [ ] Check user is logged in

### Test 5: Google Edge Cases
- [ ] Try Google auth with popup blocked
- [ ] Try canceling Google OAuth flow
- [ ] Try Google auth with existing email account
- [ ] Test Google auth on mobile device

---

## 🔍 FIREBASE VALIDATION

### Test 6: Firebase Console Check
- [ ] Open: https://console.firebase.google.com/project/our-library-d7b60
- [ ] Navigate to Authentication > Users
- [ ] Verify new email user appears in list
- [ ] Verify Google user appears in list
- [ ] Check user creation timestamps
- [ ] Verify user UIDs are unique

---

## ⚠️ STUPID HUMAN ERRORS

### Test 7: Common Mistakes
- [ ] Register with CAPS LOCK email: `TEST@GMAIL.COM`
- [ ] Use password with only numbers: `123456`
- [ ] Copy/paste email with trailing spaces
- [ ] Try to register without internet connection
- [ ] Rapidly click register button multiple times
- [ ] Try using special characters in password: `P@ssw0rd!`
- [ ] Test with browser back button during registration

### Test 8: Browser Compatibility
- [ ] Test on Chrome (desktop)
- [ ] Test on Firefox (desktop)
- [ ] Test on Safari (if available)
- [ ] Test on mobile Chrome
- [ ] Test on mobile Safari
- [ ] Test with ad blocker enabled
- [ ] Test with JavaScript disabled (should show error)

---

## 🖥️ TECHNICAL VALIDATION

### Test 9: Network Conditions
- [ ] Test with slow internet (throttle connection)
- [ ] Test with intermittent connection
- [ ] Check for proper loading states
- [ ] Verify timeout handling

### Test 10: Security Testing
- [ ] Check HTTPS is used throughout
- [ ] Verify no credentials appear in browser console
- [ ] Check Firebase security rules prevent unauthorized access
- [ ] Verify password is not visible in network requests

---

## 📊 RESULTS TRACKING

### Email Registration Results
- Registration Success: ⬜ PASS ⬜ FAIL
- Email Delivery: ⬜ PASS ⬜ FAIL  
- Verification Link: ⬜ PASS ⬜ FAIL
- Login After Verification: ⬜ PASS ⬜ FAIL

### Google OAuth Results
- OAuth Popup: ⬜ PASS ⬜ FAIL
- Permission Grant: ⬜ PASS ⬜ FAIL
- Successful Auth: ⬜ PASS ⬜ FAIL
- User Creation: ⬜ PASS ⬜ FAIL

### Firebase Validation
- Email User in Console: ⬜ PASS ⬜ FAIL
- Google User in Console: ⬜ PASS ⬜ FAIL
- Proper User Data: ⬜ PASS ⬜ FAIL

### Edge Cases
- Error Handling: ⬜ PASS ⬜ FAIL
- Browser Compatibility: ⬜ PASS ⬜ FAIL
- Security Measures: ⬜ PASS ⬜ FAIL

---

## 🚨 ISSUES FOUND

**Issue 1**: ________________________________  
**Severity**: ⬜ Critical ⬜ High ⬜ Medium ⬜ Low  
**Description**: ____________________________

**Issue 2**: ________________________________  
**Severity**: ⬜ Critical ⬜ High ⬜ Medium ⬜ Low  
**Description**: ____________________________

**Issue 3**: ________________________________  
**Severity**: ⬜ Critical ⬜ High ⬜ Medium ⬜ Low  
**Description**: ____________________________

---

## ✅ SIGN-OFF

**All Tests Completed**: ⬜ YES ⬜ NO  
**Critical Issues Found**: ⬜ YES ⬜ NO  
**Ready for Production**: ⬜ YES ⬜ NO  

**Tester Signature**: _____________________  
**Date Completed**: ______________________