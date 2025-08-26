# OurLibrary Rescue - Setup Guide

A clean, testable baseline of the 7-step user onboarding flow with enforced route guards, pluggable authentication, and comprehensive e2e testing.

## Architecture Overview

### 7-Step Flow
1. **Main Page** (`#/`) - Welcome with CTAs  
2. **Registration** (`#/register`) - Email + password form
3. **Registration Complete** (`#/registered`) - Email sent confirmation
4. **Email Verification** (`#/verify`) - Verify before proceeding  
5. **Setup: Consent** (`#/setup/consent`) - Permission for file scanning
6. **Setup: Filesystem** (`#/setup/filesystem`) - Choose library folder
7. **Desktop Library** (`#/app`) - Main application

### Key Features
- **Route Guards**: Enforces proper flow progression
- **Pluggable Auth**: Mock for dev/testing, Firebase for production
- **Test Coverage**: Complete Playwright e2e suite
- **Modern Stack**: Vite + Tailwind + ESM

## Quick Start

### Prerequisites
```bash
# Enable pnpm (recommended)
corepack enable && corepack prepare pnpm@latest --activate
```

### Development Setup
```bash
# 1. Install dependencies
pnpm i

# 2. Install Playwright browsers
pnpm exec playwright install

# 3. Start development server (uses mock auth)
pnpm dev
# Opens http://localhost:5173

# 4. Run e2e tests
pnpm test:e2e
```

## Authentication Modes

### Mock Mode (Default)
Perfect for development and testing:
- Deterministic behavior
- Email verification simulated (1s delay)
- No external dependencies
- All e2e tests pass reliably

### Firebase Mode (Production)
For real authentication:

```bash
# 1. Install Firebase SDK
pnpm add firebase

# 2. Create .env with your Firebase config
VITE_AUTH_MODE=firebase
VITE_FB_API_KEY=your_api_key
VITE_FB_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FB_PROJECT_ID=your_project_id
VITE_FB_APP_ID=your_app_id
```

**Firebase Setup Requirements:**
- Enable Email/Password authentication
- Configure email action URLs to point to your domain + `#/verify`
- Whitelist your domain in authorized domains

## Project Structure

```
src/
├── auth/
│   ├── AuthService.js      # Pluggable auth facade
│   ├── MockAdapter.js      # Development auth adapter
│   └── FirebaseAdapter.js  # Production auth adapter
├── pages/                  # Page components
├── ui/
│   └── dom.js             # DOM utilities
├── router.js              # Route management + guards
├── main.js                # App entry point
└── styles.css             # Tailwind + custom components
```

## Route Guards

The router automatically enforces the proper flow:

- **Unauthenticated** → Redirected to `#/register`
- **Authenticated + Unverified** → Redirected to `#/verify`  
- **Verified + No Setup** → Redirected to `#/setup/consent`
- **Setup Complete** → Can access `#/app`

## Testing

### E2E Test Suite
Tests cover all 7 steps:
```bash
# Run all tests
pnpm test:e2e

# Run with UI mode
pnpm test:ui

# Run specific test
pnpm exec playwright test tests/e2e/04_email_verification.spec.ts
```

### Test Structure
Each step has its own spec file:
- `01_main.spec.ts` - Home page loading
- `02_registration.spec.ts` - Account creation  
- `03_registration_complete.spec.ts` - Email sent confirmation
- `04_email_verification.spec.ts` - Full verification flow
- `05_setup_consent.spec.ts` - Consent requirement
- `06_setup_filesystem.spec.ts` - Folder selection
- `07_desktop_library.spec.ts` - Library access + signout

## Deployment

### Build
```bash
pnpm build
# Generates dist/ directory
```

### CI/CD
GitHub Actions workflow included:
- Installs dependencies
- Runs Playwright tests
- Builds for production

### Environment Variables
For production deployment, set:
```
VITE_AUTH_MODE=firebase
VITE_FB_API_KEY=...
VITE_FB_AUTH_DOMAIN=...
VITE_FB_PROJECT_ID=...
VITE_FB_APP_ID=...
```

## Development Notes

### State Management
- Uses `deriveState()` pattern for consistent auth state
- localStorage for setup completion tracking
- No external state management library needed

### Styling
- Tailwind CSS with proper content paths (no purge issues)
- Custom component classes in `src/styles.css`
- Dark theme with slate color palette

### Error Handling
- Route guards handle invalid states
- Mock adapter provides predictable behavior
- Firebase adapter includes proper error handling

## Troubleshooting

### Common Issues
1. **Tailwind styles not working**: Check `tailwind.config.cjs` content paths
2. **Tests failing**: Ensure Playwright browsers installed (`pnpm exec playwright install`)
3. **Firebase errors**: Verify all env vars are set and Firebase config is correct

### Debug Mode
```bash
# Run tests in headed mode
pnpm exec playwright test --headed

# Run dev server with debug
DEBUG=* pnpm dev
```

## Next Steps

1. **Customize Pages**: Modify components in `src/pages/`
2. **Add Features**: Extend the library functionality in `DesktopLibrary.js`  
3. **Styling**: Customize Tailwind theme and components
4. **Backend**: Add real file system integration for desktop app
5. **Authentication**: Configure Firebase for production use

This baseline provides a solid foundation for building the complete OurLibrary application with confidence that the core user flow is robust and well-tested.