import { test, expect } from '@playwright/test';

test.describe('OurLibrary - Complete 7-Step User Flow with Screenshots', () => {
  test('Complete user journey from welcome to library app', async ({ page }) => {
    // Set up screenshot directory
    const testName = 'complete-flow';
    
    // PHASE 1: Welcome/Landing Page
    console.log('📸 PHASE 1: Testing Welcome/Landing Page...');
    await page.goto('/');
    
    // Verify main elements
    await expect(page.locator('h1')).toHaveText('OurLibrary');
    await expect(page.locator('text=Welcome to OurLibrary')).toBeVisible();
    await expect(page.locator('text=Get Started')).toBeVisible();
    await expect(page.locator('a:has-text("Sign In")')).toBeVisible();
    
    // Take screenshot of Phase 1
    await page.screenshot({ 
      path: `screenshots/${testName}-01-welcome-page.png`,
      fullPage: true 
    });
    
    // PHASE 2: Registration Form
    console.log('📸 PHASE 2: Testing Registration Form...');
    await page.click('text=Get Started');
    await expect(page).toHaveURL(/#\/register$/);
    
    // Verify registration form elements
    await expect(page.locator('h2:has-text("Register")')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toHaveText('Create account');
    
    // Take screenshot of Phase 2
    await page.screenshot({ 
      path: `screenshots/${testName}-02-registration-form.png`,
      fullPage: true 
    });
    
    // Fill registration form
    await page.locator('#email').fill('test-user@ourlibrary.com');
    await page.locator('#password').fill('SecurePassword123!');
    await page.locator('button[type="submit"]').click();
    
    // PHASE 3: Route guard redirects to verification (no registration complete page)
    console.log('📸 PHASE 3: Redirected to Email Verification...');
    await expect(page).toHaveURL(/#\/verify$/);
    
    // Take screenshot of Phase 3 (verification page initially)
    await page.screenshot({ 
      path: `screenshots/${testName}-03-email-verification-initial.png`,
      fullPage: true 
    });
    
    // PHASE 4: Email Verification
    console.log('📸 PHASE 4: Testing Email Verification...');
    await expect(page).toHaveURL(/#\/verify$/);
    await expect(page.locator('text=Email Verification')).toBeVisible();
    await expect(page.locator('text=Please verify your email')).toBeVisible();
    await expect(page.locator('#refresh')).toBeVisible();
    await expect(page.locator('#resend')).toBeVisible();
    
    // Take screenshot of Phase 4 (unverified state)
    await page.screenshot({ 
      path: `screenshots/${testName}-04-email-verification-pending.png`,
      fullPage: true 
    });
    
    // Mock verification process (wait for mock to verify)
    await page.waitForTimeout(1200); // Mock takes 1 second + buffer
    await page.click('#refresh');
    
    // PHASE 5: Setup - Terms and Consent
    console.log('📸 PHASE 5: Testing Terms and Consent...');
    await expect(page).toHaveURL(/#\/setup\/consent$/);
    await expect(page.locator('text=Terms of Service & Privacy')).toBeVisible();
    await expect(page.locator('text=Data Storage')).toBeVisible();
    await expect(page.locator('h3:has-text("Privacy")')).toBeVisible();
    await expect(page.locator('text=Educational Use')).toBeVisible();
    
    // Take screenshot of Phase 5
    await page.screenshot({ 
      path: `screenshots/${testName}-05-terms-consent.png`,
      fullPage: true 
    });
    
    // Accept terms
    await page.check('input[name="agree"]');
    await page.click('button[type="submit"]');
    
    // PHASE 6: Setup - Filesystem Configuration
    console.log('📸 PHASE 6: Testing Filesystem Setup...');
    await expect(page).toHaveURL(/#\/setup\/filesystem$/);
    await expect(page.locator('text=Set Up Your Personal Library')).toBeVisible();
    await expect(page.locator('text=What we\'ll create:')).toBeVisible();
    await expect(page.locator('text=📚 Books/')).toBeVisible();
    await expect(page.locator('text=🖼️ Covers/')).toBeVisible();
    await expect(page.locator('text=💾 Database/')).toBeVisible();
    
    // Take screenshot of Phase 6
    await page.screenshot({ 
      path: `screenshots/${testName}-06-filesystem-setup.png`,
      fullPage: true 
    });
    
    // Configure filesystem
    await page.locator('#folder').fill('/Users/testuser/OurLibrary');
    await page.click('button[type="submit"]');
    
    // PHASE 7: Library Application (Final Destination)
    console.log('📸 PHASE 7: Testing Library Application...');
    await expect(page).toHaveURL(/#\/app$/);
    await expect(page.locator('h2:has-text("Your Library")')).toBeVisible();
    await expect(page.locator('text=Manage your educational content')).toBeVisible();
    await expect(page.locator('text=Library Statistics')).toBeVisible();
    await expect(page.locator('text=Quick Actions')).toBeVisible();
    await expect(page.locator('text=Recent Books')).toBeVisible();
    
    // Verify action buttons
    await expect(page.locator('text=Add New Books')).toBeVisible();
    await expect(page.locator('text=Scan Directory')).toBeVisible();
    await expect(page.locator('text=Import from URL')).toBeVisible();
    await expect(page.locator('text=Manage Categories')).toBeVisible();
    await expect(page.locator('#signOut')).toBeVisible();
    
    // Take screenshot of Phase 7
    await page.screenshot({ 
      path: `screenshots/${testName}-07-library-application.png`,
      fullPage: true 
    });
    
    // Test sign out functionality
    console.log('🔄 Testing Sign Out...');
    await page.click('#signOut');
    await expect(page).toHaveURL(/#\/$/);
    await expect(page.locator('text=Welcome to OurLibrary')).toBeVisible();
    
    // Take final screenshot showing return to welcome
    await page.screenshot({ 
      path: `screenshots/${testName}-08-signed-out-welcome.png`,
      fullPage: true 
    });
    
    console.log('✅ All 7 phases completed successfully with screenshots!');
  });
  
  test('Route guard enforcement - cannot skip steps', async ({ page }) => {
    console.log('🛡️ Testing Route Guards...');
    
    // Try to access protected routes directly
    await page.goto('/#/app');
    await expect(page).toHaveURL(/#\/register$/); // Should redirect to register
    
    await page.goto('/#/setup/consent');
    await expect(page).toHaveURL(/#\/register$/); // Should redirect to register
    
    await page.goto('/#/verify');  
    await expect(page).toHaveURL(/#\/register$/); // Should redirect to register
    
    console.log('✅ Route guards working correctly!');
  });
  
  test('Authentication state management', async ({ page }) => {
    console.log('🔐 Testing Authentication State...');
    
    // Test sign in flow
    await page.goto('/#/signin');
    await expect(page.locator('h2:has-text("Sign In")')).toBeVisible();
    
    await page.locator('#email').fill('existing-user@ourlibrary.com');
    await page.locator('#password').fill('ExistingPassword123!');
    await page.click('button[type="submit"]');
    
    // Mock sign in goes straight to setup (email already verified)
    await expect(page).toHaveURL(/#\/setup\/consent$/);
    
    console.log('✅ Sign in flow working correctly!');
  });
});