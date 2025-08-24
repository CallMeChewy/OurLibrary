# File: MANUAL_TESTING_GUIDE.md

# Path: /home/herb/Desktop/AndyLibrary/MANUAL_TESTING_GUIDE.md

# Standard: AIDEV-PascalCase-2.1

# Created: 2025-07-26

# Last Modified: 2025-07-26 05:58AM

# 🧪 MANUAL TESTING GUIDE FOR ANDYLIBRARY

## 🎯 Overview

This guide provides comprehensive manual testing procedures for **AndyLibrary (Project Himalaya)** - the advanced educational platform with sophisticated search, user progress tracking, and production-ready infrastructure.

## 📋 Pre-Testing Checklist

### **System Requirements**

- [ ] Python 3.11+ installed
- [ ] All dependencies from `requirements.txt` installed
- [ ] Database file accessible at `/home/herb/Desktop/AndyLibrary/Data/Databases/MyLibrary.db`
- [ ] WebPages directory with all HTML/CSS/JS files

### **Testing Environment Setup**

```bash
# 1. Navigate to project directory
cd /home/herb/Desktop/AndyLibrary

# 2. Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Start the application
python StartAndyGoogle.py

# 4. Note the server URL (usually http://127.0.0.1:8000)
```

## 🧪 COMPREHENSIVE MANUAL TEST SUITE

### **TEST SUITE 1: Core System Functionality** ⭐ CRITICAL

#### **Test 1.1: Application Startup**

**Objective**: Verify AndyLibrary starts correctly with all components

**Steps**:

1. Run `python StartAndyGoogle.py`
2. Verify startup messages show:
   - ✅ Environment check passed
   - ✅ Database connection established
   - ✅ Advanced Search API integrated successfully
   - ✅ Server running on detected port

**Expected Results**:

- Server starts without errors
- Port detection works (tries 8000, falls back if needed)
- All components initialize successfully
- Access URLs displayed correctly

**Pass Criteria**: ✅ All startup messages successful, server accessible

---

#### **Test 1.2: BowersWorld Landing Page**

**Objective**: Verify the main landing page loads with Project Himalaya branding

**Steps**:

1. Navigate to server URL (e.g., http://127.0.0.1:8000)
2. Verify page loads completely
3. Check for Project Himalaya branding
4. Test navigation links

**Expected Results**:

- Page loads with "BowersWorld.com - Project Himalaya" title
- Educational mission content visible
- Registration/login links functional
- Professional appearance and branding

**Pass Criteria**: ✅ Landing page loads with proper branding and navigation

---

#### **Test 1.3: API Documentation Access**

**Objective**: Verify FastAPI documentation is accessible and complete

**Steps**:

1. Navigate to `/docs` endpoint (e.g., http://127.0.0.1:8000/docs)
2. Verify Swagger UI loads
3. Check for new advanced endpoints
4. Test a simple API call

**Expected Results**:

- Swagger UI loads with complete API documentation
- Advanced search endpoints visible (`/api/search/advanced`, `/api/search/categories`)
- Progress tracking endpoints visible (`/api/progress/*`)
- All endpoints documented with proper schemas

**Pass Criteria**: ✅ API docs accessible with all new advanced endpoints

---

### **TEST SUITE 2: User Authentication & Registration** ⭐ CRITICAL

#### **Test 2.1: New User Registration**

**Objective**: Test complete user registration workflow

**Steps**:

1. Navigate to `/auth.html`
2. Fill out registration form with valid data:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPassword123!`
3. Submit registration
4. Check for email verification requirement
5. Note verification token in server logs

**Expected Results**:

- Registration form accepts valid input
- Email verification message displayed
- Verification token generated and logged
- User record created in database

**Pass Criteria**: ✅ Registration completes with email verification flow

---

#### **Test 2.2: Email Verification Simulation**

**Objective**: Test email verification process

**Steps**:

1. From server logs, copy verification token
2. Navigate to `/api/auth/verify-email?token=YOUR_TOKEN`
3. Verify account activation
4. Attempt login with verified account

**Expected Results**:

- Verification endpoint accepts token
- Account status changes to verified
- Login becomes possible after verification
- Proper success/error messages displayed

**Pass Criteria**: ✅ Email verification process completes successfully

---

#### **Test 2.3: User Login**

**Objective**: Test user authentication process

**Steps**:

1. Navigate to `/auth.html`
2. Switch to login mode
3. Enter verified user credentials
4. Submit login form
5. Verify session creation

**Expected Results**:

- Login form accepts credentials
- Authentication succeeds for verified user
- Session token created and stored
- Redirect to appropriate next page

**Pass Criteria**: ✅ Login process works with session management

---

### **TEST SUITE 3: Advanced Search Functionality** ⭐ NEW FEATURE

#### **Test 3.1: Basic Search API**

**Objective**: Test advanced search with comprehensive mode

**API Test**:

```bash
curl -X POST "http://127.0.0.1:8000/api/search/advanced" \
  -H "Content-Type: application/json" \
  -d '{
    "Query": "python programming",
    "SearchMode": "comprehensive",
    "PageSize": 10
  }'
```

**Expected Results**:

- Search returns relevant results
- Results include relevance scores
- Proper pagination information
- Search time reported

**Pass Criteria**: ✅ Advanced search returns intelligent results

---

#### **Test 3.2: Fuzzy Search Mode**

**Objective**: Test typo tolerance in search

**API Test**:

```bash
curl -X POST "http://127.0.0.1:8000/api/search/advanced" \
  -H "Content-Type: application/json" \
  -d '{
    "Query": "phython programing",
    "SearchMode": "fuzzy",
    "PageSize": 5
  }'
```

**Expected Results**:

- Search handles typos intelligently
- Returns results for "python programming" despite misspelling
- Fuzzy score included in results
- Reasonable relevance ranking

**Pass Criteria**: ✅ Fuzzy search handles typos and returns relevant results

---

#### **Test 3.3: Category-Based Search**

**Objective**: Test search filtering by categories

**Steps**:

1. Get available categories: `GET /api/search/categories`
2. Test category filtering:
   
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/search/advanced" \
   -H "Content-Type: application/json" \
   -d '{
    "Query": "web",
    "Categories": ["Web Development", "Computer Science"],
    "PageSize": 5
   }'
   ```

**Expected Results**:

- Categories endpoint returns 26 educational categories
- Category filtering works correctly
- Results limited to specified categories
- Category breakdown provided in response

**Pass Criteria**: ✅ Category-based search filtering works correctly

---

#### **Test 3.4: Search Suggestions**

**Objective**: Test contextual search suggestions

**API Test**:

```bash
curl "http://127.0.0.1:8000/api/search/suggestions?Query=prog"
```

**Expected Results**:

- Suggestions returned for partial query
- Relevant category suggestions included
- Proper suggestion format and ranking
- Performance within reasonable limits

**Pass Criteria**: ✅ Search suggestions provide helpful query completion

---

### **TEST SUITE 4: User Progress Tracking** ⭐ NEW FEATURE

#### **Test 4.1: Reading Session Management**

**Objective**: Test reading session start/end workflow

**Steps**:

1. Login as authenticated user
2. Start reading session:
   
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/progress/session/start" \
   -H "Authorization: Bearer YOUR_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{
    "book_id": 1,
    "book_title": "Python Programming Guide",
    "book_category": "Programming Languages",
    "device_type": "desktop"
   }'
   ```
3. Note session ID returned
4. End reading session:
   
   ```bash
   curl -X POST "http://127.0.0.1:8000/api/progress/session/end" \
   -H "Authorization: Bearer YOUR_TOKEN" \
   -H "Content-Type: application/json" \
   -d '{
    "session_id": "YOUR_SESSION_ID",
    "pages_read": 15,
    "completion_percentage": 25.0
   }'
   ```

**Expected Results**:

- Session starts with unique ID
- Session data recorded in database
- Session ends with statistics
- Progress metrics calculated correctly

**Pass Criteria**: ✅ Reading session tracking works end-to-end

---

#### **Test 4.2: User Progress Analytics**

**Objective**: Test comprehensive progress reporting

**API Test**:

```bash
curl "http://127.0.0.1:8000/api/progress/user" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Results**:

- User statistics displayed (books accessed, total time, sessions)
- Recent books list with progress information
- Learning analytics (favorite category, reading streak)
- Recent activity breakdown

**Pass Criteria**: ✅ Progress analytics provide comprehensive user insights

---

#### **Test 4.3: Bookmark System**

**Objective**: Test bookmarking functionality

**API Test**:

```bash
curl -X POST "http://127.0.0.1:8000/api/progress/bookmark" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1
  }'
```

**Expected Results**:

- Bookmark status toggles correctly
- Bookmarked books appear in user progress
- Multiple bookmark operations work
- Bookmark state persists across sessions

**Pass Criteria**: ✅ Bookmark system works with proper persistence

---

### **TEST SUITE 5: User Environment Isolation** ⭐ CRITICAL

#### **Test 5.1: Multi-User Installation Paths**

**Objective**: Verify user-specific installation directories

**Steps**:

1. Register multiple users with different usernames
2. Complete setup process for each user
3. Check installation paths are isolated
4. Verify no path conflicts between users

**Expected Results**:

- Each user gets isolated directory structure
- Paths follow OS conventions (LocalAppData/Application Support/.local/share)
- No conflicts between user installations
- Development environment remains separate

**Pass Criteria**: ✅ User environments properly isolated with no conflicts

---

#### **Test 5.2: User Setup Process**

**Objective**: Test complete user setup and database installation

**Steps**:

1. Login as verified user
2. Navigate to `/setup.html`
3. Complete setup process
4. Verify database installation
5. Test native app launch

**Expected Results**:

- Setup progress displays correctly
- Database copied to user-specific location
- Configuration files created in user directory
- Native app launches from user environment

**Pass Criteria**: ✅ User setup completes with proper isolation

---

### **TEST SUITE 6: Library Core Functionality** ⭐ CRITICAL

#### **Test 6.1: Book Categories and Search**

**Objective**: Test traditional library functionality

**Steps**:

1. Navigate to `/api/categories`
2. Verify all 26 categories returned
3. Test book search: `/api/books/search`
4. Verify search results include thumbnails

**Expected Results**:

- All educational categories available
- Book search returns relevant results
- Thumbnails display correctly (1,217+ available)
- Search performance acceptable

**Pass Criteria**: ✅ Core library functionality works correctly

---

#### **Test 6.2: Book Detail Views**

**Objective**: Test individual book information

**Steps**:

1. Get book list from search
2. Select specific book ID
3. Test book detail endpoint: `/api/books/{book_id}`
4. Verify book information completeness

**Expected Results**:

- Book details load correctly
- All metadata displayed (title, category, file info)
- Thumbnails accessible when available
- Proper error handling for invalid IDs

**Pass Criteria**: ✅ Book detail views work with complete information

---

### **TEST SUITE 7: Performance and Reliability** ⭐ IMPORTANT

#### **Test 7.1: Search Performance**

**Objective**: Verify search performance under load

**Steps**:

1. Run multiple search queries rapidly
2. Test with various query lengths and complexities
3. Monitor response times
4. Test with large result sets

**Expected Results**:

- Search responses under 1 second for typical queries
- No memory leaks or performance degradation
- Proper handling of complex queries
- Reasonable performance with fuzzy search

**Pass Criteria**: ✅ Search performance meets educational use requirements

---

#### **Test 7.2: Database Connection Reliability**

**Objective**: Test database stability under usage

**Steps**:

1. Perform multiple database operations rapidly
2. Test concurrent user scenarios
3. Verify connection pooling works
4. Test recovery from connection issues

**Expected Results**:

- Database connections stable under load
- No connection leaks or resource exhaustion
- Proper error handling for database issues
- Consistent performance across operations

**Pass Criteria**: ✅ Database operations reliable and performant

---

## 📊 TESTING RESULTS SUMMARY

### **Critical Path Tests** (Must Pass)

- [ ] Application startup and component initialization
- [ ] User registration and email verification workflow
- [ ] User authentication and session management
- [ ] Advanced search functionality (comprehensive mode)
- [ ] User progress tracking (session start/end)
- [ ] User environment isolation
- [ ] Core library functionality (categories, book search)

### **Advanced Feature Tests** (Should Pass)

- [ ] Fuzzy search with typo tolerance
- [ ] Category-based search filtering
- [ ] Search suggestions and autocomplete
- [ ] User progress analytics and reporting
- [ ] Bookmark system functionality
- [ ] Multi-user concurrent access

### **Performance Tests** (Should Pass)

- [ ] Search response times under 1 second
- [ ] Database connection stability
- [ ] Memory usage within reasonable limits
- [ ] Concurrent user handling

## 🎯 MANUAL TESTING SUCCESS CRITERIA

**System Ready for Production** when:

- ✅ **100% Critical Path Tests Pass** - All essential functionality working
- ✅ **90%+ Advanced Feature Tests Pass** - New features functional with minor acceptable issues
- ✅ **80%+ Performance Tests Pass** - System performs acceptably under normal load
- ✅ **User Experience Smooth** - Registration through library access works intuitively
- ✅ **Educational Mission Maintained** - All features serve educational accessibility goals

## 🚀 POST-TESTING ACTIONS

After successful manual testing:

1. **Document any issues found** with reproduction steps
2. **Verify educational mission compliance** - ensure all features remain accessible
3. **Update production deployment checklist** with any new requirements
4. **Prepare for production deployment** using existing guides
5. **Plan user acceptance testing** with real students (if applicable)

---

**🎓 Ready to validate AndyLibrary's advanced educational capabilities through comprehensive manual testing!**