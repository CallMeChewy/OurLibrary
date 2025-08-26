# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# OurLibrary - Educational Library Platform

An educational library management system with secure authentication focused on providing equitable access to educational content for students in developing regions.

## Mission & Context

**Mission**: "Getting education into the hands of people who can least afford it"
**Email**: HimalayaProject1@gmail.com / ProjectHimalaya@BowersWorld.com  
**Live Demo**: https://callmechewy.github.io/OurLibrary/

## Current Development Phase

This is a **clean restart** project focusing on secure authentication as the foundation. All previous development artifacts have been moved to `..Exclude/` to provide a fresh starting point while preserving development history.

**Core Focus**: Secure authentication and user registration system
**Future Phases**: Library components will be added modularly from archived materials

## Architecture & Technology Stack

### Frontend
- **Hosting**: GitHub Pages (static HTML/CSS/JS)
- **Styling**: Tailwind CSS for responsive design
- **Authentication UI**: Multi-step verification workflow

### Backend 
- **Cloud Functions**: Firebase Functions v2 (Node.js v22)
- **Authentication**: Firebase Auth with custom email verification
- **Email Service**: Nodemailer with SMTP via Misk.com hosting

### Email Infrastructure
- **Sender**: ProjectHimalaya@BowersWorld.com
- **SMTP**: smtp.misk.com:587 (business domain for deliverability)
- **Authentication Strategy**: Manual verification codes (no clickable links for security)

### Security Model
- **Anti-Phishing**: Manual verification codes instead of email links
- **Account Creation Flow**: Email registration → Verification code → THEN Firebase account creation
- **Google OAuth**: Direct Firebase creation (Google pre-verified)

## Development Commands

### Testing
```bash
# Run all tests (when test suite exists)
cd Tests
python -m pytest

# Run specific test categories
python -m pytest Tests/ -m unit
python -m pytest Tests/ -m integration  
python -m pytest Tests/ -m security
```

### Firebase Functions (when functions/ directory exists)
```bash
cd functions
npm install
firebase login
firebase use our-library-d7b60
firebase deploy --only functions
```

### Live Demo Testing
Available pages for testing:
- `index.html` - Main landing page
- `auth-demo.html` - Complete signup/login workflow
- `test-smtp.html` - Email service testing interface

## Project Structure

```
OurLibrary/
├── Config/
│   └── google_credentials.json.template  # OAuth configuration template
├── Docs/
│   ├── README.md                          # Project documentation  
│   └── Standards/                         # Design standards (v2.3)
├── Scripts/
│   ├── Common/                            # Shared utilities (symlinked)
│   │   ├── GitHub/                        # Git automation scripts
│   │   ├── FinderDisplay/                 # File search utilities
│   │   ├── System/                        # Project management
│   │   └── Tools/                         # Development tools
│   └── README.md                          # Scripts documentation
├── README.md                              # Main project documentation
└── LICENSE                                # MIT license
```

**Note**: Web files (HTML/CSS/JS) and Firebase functions are currently in `..Exclude/` and can be restored as needed for development.

## Development Standards

### File Headers (AIDEV-PascalCase-2.3)
All files must include standardized headers:
```python
# File: [EXACT FILENAME WITH EXTENSION]
# Path: [EXACT ABSOLUTE DEPLOYMENT PATH] 
# Standard: AIDEV-PascalCase-2.3
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD HH:MM[AM|PM]
```

### Naming Conventions
- **Python Files**: PascalCase (`AuthManager.py`)
- **Directories**: PascalCase (`Scripts/Common/`)
- **Variables/Functions**: PascalCase (`GetUserData()`)

### Symlink-Aware Development
Scripts in `Scripts/Common/` are designed to be symlinked across projects. All scripts must:
- Detect their execution context (not their file location)
- Work correctly when invoked via symlinks
- Use `os.getcwd()` for project context, not `__file__` location

## Authentication System Architecture

### Email Verification Flow
1. **User Registration**: Email entered → Validation
2. **Code Generation**: 6-digit verification code created
3. **Email Delivery**: Professional HTML email sent via business SMTP
4. **Manual Verification**: User enters code (no clickable links)
5. **Account Creation**: Firebase account created ONLY after verification

### Firebase Functions
- `sendVerificationEmail` - Handles registration verification codes  
- `sendPasswordResetEmail` - Handles password reset tokens

### Configuration Management
- Email service configuration in `Config/email_config.json` (when present)
- Application settings in `Config/ourlibrary_config.json` (when present)
- OAuth credentials in `Config/oauth_security_config.json` (when present)

## Key Development Notes

### Project History
- **Previous Names**: AndyLibrary → WorldLibrary → **OurLibrary**
- **Development Artifacts**: All previous work preserved in `..Exclude/` including comprehensive test suite, configurations, and web files
- **Clean Restart**: Current structure optimized for next development phase

### Available Resources in `..Exclude/`
- Complete test suite with multiple categories (unit, integration, security, browser, live)
- Working Firebase Cloud Functions  
- Professional email templates
- Web interface files (HTML/CSS/JS)
- Configuration files with SMTP settings
- Development and debugging utilities

### Next Development Priorities
1. Restore essential web files from `..Exclude/` as needed
2. Re-establish Firebase Functions deployment
3. Implement comprehensive test suite
4. Add library components modularly
5. Establish user dashboard and content management

## Important Context

This project represents a **foundation-first approach** to educational software development. The authentication system is production-ready and battle-tested, providing a secure base for future library management features. All development artifacts are preserved but organized to provide a clean starting point for continued development.