# Google Sheets Setup Guide - OurLibrary Analytics

## ✅ Sheet IDs Updated in Code

Your actual Google Sheets have been configured in the system:

| Sheet Purpose | Your Sheet ID | Status |
|---------------|---------------|--------|
| **User Registrations** | `1lhdKnjyltHHQaDSfAfQ9Vcog40vsnFTqzDFxa9sEBFE` | ✅ Updated |
| **Incomplete Emails** | `197Qu-GeIYaL2CyiFArhgM9GJbuyGCUK4JZjxWXsAHaI` | ✅ Updated |
| **Session Analytics** | `1KZPSyXCqkWKHzaM8Y45BmoZqHpzU-VWOpQq0W8UELxg` | ✅ Updated |

---

## 📊 **Sheet 1: User Registrations**
**URL**: https://docs.google.com/spreadsheets/d/1lhdKnjyltHHQaDSfAfQ9Vcog40vsnFTqzDFxa9sEBFE/edit

### **Column Headers (Row 1):**
Copy and paste these headers into **Row 1** of your first sheet:

```
userId	email	name	authMethod	status	startTime	completionTime	location	consent	notes
```

### **What Each Column Tracks:**
- **userId**: Firebase User ID (auto-generated)
- **email**: User's email address
- **name**: User's full name
- **authMethod**: `email`, `google`, `facebook`, etc.
- **status**: `complete`, `pending`, `verified`
- **startTime**: When registration started
- **completionTime**: When registration completed
- **location**: User's location (if provided)
- **consent**: Terms acceptance (true/false)
- **notes**: Additional registration notes

---

## 📧 **Sheet 2: Incomplete Emails**
**URL**: https://docs.google.com/spreadsheets/d/197Qu-GeIYaL2CyiFArhgM9GJbuyGCUK4JZjxWXsAHaI/edit

### **Column Headers (Row 1):**
Copy and paste these headers into **Row 1** of your second sheet:

```
email	timestamp	step	sessionId	userAgent	referrer	hostname
```

### **What Each Column Tracks:**
- **email**: Email address entered (even if incomplete)
- **timestamp**: When the email was entered
- **step**: `email_blur`, `email_entered`, `form_started`
- **sessionId**: Unique session identifier
- **userAgent**: Browser/device information
- **referrer**: Where the user came from
- **hostname**: Domain where the action occurred

---

## 📈 **Sheet 3: Session Analytics**
**URL**: https://docs.google.com/spreadsheets/d/1KZPSyXCqkWKHzaM8Y45BmoZqHpzU-VWOpQq0W8UELxg/edit

### **Column Headers (Row 1):**
Copy and paste these headers into **Row 1** of your third sheet:

```
userId	email	action	details	sessionId	timestamp	userAgent	hostname
```

### **What Each Column Tracks:**
- **userId**: Firebase User ID (if available)
- **email**: User's email address
- **action**: `registration_start`, `google_oauth_success`, `email_verification_attempt`
- **details**: JSON data with additional context
- **sessionId**: Unique session identifier
- **timestamp**: When the action occurred
- **userAgent**: Browser/device information
- **hostname**: Domain where the action occurred

---

## 🔧 **Quick Setup Instructions:**

1. **Open each sheet** using the URLs above
2. **Click on cell A1** (first cell)
3. **Paste the headers** from this guide
4. **Press Tab or Enter** to separate columns
5. **Save the sheet** (Ctrl+S or auto-saves)

---

## 🎯 **What Happens Next:**

Once you add these headers, your OurLibrary system will automatically start logging:

- ✅ **Complete user registrations** → Sheet 1
- ✅ **Incomplete email captures** → Sheet 2  
- ✅ **Detailed user journey analytics** → Sheet 3

---

## 🚀 **Testing Your Setup:**

After adding headers, go to https://callmechewy.github.io/OurLibrary/ and:

1. **Click "Join Our Library"**
2. **Enter an email and tab out** → Should log to Sheet 2
3. **Complete registration** → Should log to Sheets 1 & 3

---

**Need help with the headers? Just let me know which sheet you're working on!**