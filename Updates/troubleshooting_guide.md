# Playwright E2E Testing - Final Working Version

## What Was Actually Broken

**The Real Issue:** `page.goto('/')` failed because Playwright didn't know what website `"/"` referred to.

**Error Message You Probably Saw:**
```
Error: Invalid URL: /
```

**The Fix:** Added `baseURL` in `playwright.config.ts` so `"/"` automatically resolves to your live site.

## Correct File Structure

Create exactly this structure (case-sensitive!):

```
OurLibrary/                          # Your repo root
├── package.json                     # Root level
├── playwright.config.ts             # Root level  
└── Tests/                           # Capital T
    └── E2E/                         # Capital E2E
        └── auth-flow.spec.ts        # Exact filename
```

## Setup Commands (Copy/Paste)

```bash
# Navigate to your repo root
cd ~/Desktop/OurLibrary

# Install Playwright
npm install

# Install Chromium browser  
npm run pw:install

# Run test with visible browser (watch it work!)
npm run test:headed
```

## Key Fixes Applied

### 1. baseURL Configuration
**Before:** `page.goto('/')` → Invalid URL error
**After:** `page.goto('/')` → Goes to https://callmechewy.github.io/OurLibrary/

### 2. Simplified testDir
**Before:** `testDir: 'Tests'` + complex matching
**After:** `testDir: 'Tests/E2E'` + simple `['**/*.spec.ts']`

### 3. Cleaner Package Scripts
```json
{
  "test:headed": "playwright test --headed",    // Watch it run
  "test:ui": "playwright test --ui",            // Visual debugging
  "test": "playwright test"                     // Headless run
}
```

## Common Issues & Solutions

### "No tests found"
**Check:**
- File is at `Tests/E2E/auth-flow.spec.ts` (exact case and path)
- Filename ends with `.spec.ts` (not `_spec.ts`)
- `playwright.config.ts` is in repo root

### "Invalid URL" Error
**Check:**
- `playwright.config.ts` has `baseURL` set correctly
- You're running from repo root where `package.json` lives

### Test Finds Page But Fails
**Check:**
- Your demo/dev console logging is active on the live site
- Button text hasn't changed ("Get Started", "Register with Email", etc.)
- Use `npm run test:ui` to debug selectors visually

## Success Indicators

When working correctly, you should see:
```
✅ Running 1 test using 1 worker
✅ [chromium] › auth-flow.spec.ts:10:3 › OurLibrary auth happy path › register...
```

**Browser opens automatically and:**
1. Loads your GitHub Pages site
2. Clicks "Get Started"  
3. Fills registration form
4. Captures 6-digit code from console
5. Completes verification
6. Lands on library page

## Debug Commands

```bash
# Run specific test with browser visible
npx playwright test --headed -g "OurLibrary auth happy path"

# Visual debugging mode
npm run test:ui

# Generate detailed trace on failure
npm run test -- --trace on
```

## Test Artifacts

After running, check these folders for debugging info:
- `playwright-report/` - HTML reports
- `test-results/` - Screenshots, videos, traces on failure

**Pro Tip:** If selectors are failing, run `npm run test:ui`, click your test, and use the "Pick locator" tool to find the right element selectors for your current site structure.