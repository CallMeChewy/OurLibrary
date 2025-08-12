# File: CLAUDE.md

# Path: /home/herb/Desktop/OurLibrary/CLAUDE.md

# Standard: AIDEV-PascalCase-2.1

# Created: 2025-08-05

# Last Modified: 2025-08-05 05:54PM

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project OurLibrary - Educational Library Platform

An AI-powered educational library management system focused on providing equitable access to educational content for students in developing regions.

## Development Commands

### Primary Entry Points

- `python StartOurLibrary.py`: Start the main web server with smart port detection and environment validation
- `python RunStableMode.py`: Start in stable mode (if available)

### Testing and Validation

- `python -m pytest Tests/`: Run complete test suite with comprehensive markers
- `python -m pytest Tests/ -m unit`: Run unit tests only
- `python -m pytest Tests/ -m integration`: Run integration tests only
- `python Scripts/ValidateRighteousArchitecture.py`: Validate system architecture compliance
- `python Scripts/TestWorkflows.py`: Test complete user workflows
- `python Scripts/CreateUserTestEnvironment.py`: Create isolated test environment

### Development Tools

- `python Scripts/SimulateUserStartup.py`: Simulate user startup scenarios
- `pytest Tests/test_startup.py`: Test application startup logic

## Architecture Overview

This is a FastAPI-based web application with modern OAuth 2.0 authentication, intelligent search capabilities, and progressive web app features.

### Core Components

**Authentication & Security (`Source/Core/`)**:

- `ModernSocialAuthManager.py`: OAuth 2.0 with PKCE, multi-provider support
- `SocialAuthManager.py`: Legacy social authentication fallback
- Uses Fernet encryption for token security, comprehensive security headers

**Intelligence Layer (`Source/Core/`)**:

- `IntelligentSearchEngine.py`: 7-type learning intent recognition, semantic search
- `UserJourneyManager.py`: 5-stage educational journey management
- `UserProgressManager.py`: Learning analytics and progress tracking

**Data Layer (`Source/Core/`)**:

- `DatabaseManager.py`: SQLite with async support, connection pooling
- `Data/Databases/MyLibrary.db`: Main database with educational content metadata
- `DriveManager.py` & `StudentGoogleDriveAPI.py`: Google Drive integration

**Web Interface (`WebPages/`)**:

- `auth.html`: Modern authentication interface with educational mission focus
- `desktop-library-enhanced.html`: Main library interface with PWA features
- `JS/GoogleDriveAuth.js`: Modern Google Identity Services integration
- Progressive Web App with offline capabilities

### Key Architecture Patterns

**Multi-Layered Security**:

- PKCE OAuth 2.0 flow with state validation
- Token encryption and secure storage
- Input validation and SQL injection prevention
- Privacy-first analytics (GDPR/CCPA compliant)

**Educational Intelligence**:

- Learning intent classification (7 types: Discovery, Comprehension, Practice, etc.)
- Academic level detection (Elementary through Graduate)
- Multi-factor relevance scoring (educational value + accessibility)
- Contextual adaptation based on user behavior

**Robust Data Management**:

- Async database operations with connection pooling
- Comprehensive backup and recovery systems
- Cross-platform compatibility (Windows/Linux)
- Standalone deployment with PyInstaller

## Testing Strategy

### Test Categories (pytest markers)

- `unit`: Core logic and component tests
- `integration`: Cross-component workflow tests  
- `api`: FastAPI endpoint testing
- `database`: SQLite operations and integrity
- `google_drive`: External API integration
- `auth`: OAuth flow and security
- `educational_mission`: Mission-critical educational features
- `performance`: Benchmarking and optimization

### Critical Test Areas

- **OAuth Security**: PKCE flow, token handling, multi-provider auth
- **Intelligent Search**: Intent recognition, semantic matching, relevance scoring
- **Database Integrity**: Transaction safety, backup/recovery, cross-platform compatibility
- **User Journey**: 5-stage progression, contextual adaptation, privacy compliance
- **Performance**: < 3s startup, < 100ms search, < 2s auth flow

## Configuration Management

### Environment Configuration (`Config/`)

- `ourlibrary_config.json`: Core application settings
- `oauth_security_config.json`: OAuth provider credentials and security settings
- `google_credentials.json.template`: Template for Google API credentials
- `email_config.json`: Email service configuration for notifications

### Development vs Production

- Environment-specific configuration loading via `Source/Utils/EnvironmentConfig.py`
- Secure credential management with multiple backend support
- Production deployment with comprehensive security headers

## Development Workflow

### Before Making Changes

1. Run architecture validation: `python Scripts/ValidateRighteousArchitecture.py`
2. Ensure test environment: `python Scripts/CreateUserTestEnvironment.py`
3. Check startup scenarios: `python Scripts/SimulateUserStartup.py`

### After Making Changes

1. Run full test suite: `python -m pytest Tests/`
2. Test specific areas: `python -m pytest Tests/ -m <marker>`
3. Validate workflows: `python Scripts/TestWorkflows.py`
4. Performance check: `python -m pytest Tests/ -m performance`

### Key Implementation Notes

- Follow AIDEV-PascalCase-2.1 standard for file headers and naming
- All OAuth implementations must use PKCE for security
- Educational features must maintain privacy-first approach
- Database operations must be async-compatible for performance
- All user interfaces must work on $50 tablets (performance constraint)

## Project Rebrand Information

**Former Names**: AndyLibrary → WorldLibrary → **OurLibrary**
**Mission**: "Getting education into the hands of people who can least afford it"
**Email**: HimalayaProject1@gmail.com
**Domain**: BowersWorld.com (production deployment target)

## Production Architecture

**Frontend**: GitHub Pages (https://callmechewy.github.io/BowersWorld-com/)
**Backend**: Cloud deployment (Heroku/Railway/Render)
**Email**: HimalayaProject1@gmail.com with SMTP credentials configured
**Social OAuth**: Google/Facebook/GitHub integration ready
**Database**: SQLite with cloud backup, Google Drive integration

## Current Status

✅ **Registration/Login System**: Fully functional with email verification
✅ **Social OAuth Infrastructure**: Google/Facebook/GitHub ready
✅ **Frontend Deployment**: Live on GitHub Pages with fixed viewport layout
✅ **Backend API**: Tested and working (needs cloud deployment)
✅ **Email Integration**: HimalayaProject1@gmail.com configured

## Next Steps

1. Deploy backend to cloud platform (Heroku/Railway/Render)
2. Update frontend API URLs to production backend
3. Test complete user workflow: registration → verification → login → setup
4. Enable social login providers (Google/Facebook/GitHub)
5. Test database download and desktop application installation

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.