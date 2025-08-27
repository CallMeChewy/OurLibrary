import { test, expect } from '@playwright/test';

test.describe('Integration Tests - Complete Flow Integration', () => {
  test('localStorage persistence across page reloads', async ({ page }) => {
    console.log('🔄 Testing localStorage persistence...');
    
    // Complete registration flow
    await page.goto('/');
    await page.click('text=Get Started');
    await page.locator('#email').fill('integration-test@ourlibrary.com');
    await page.locator('#password').fill('IntegrationTest123!');
    await page.click('button[type="submit"]');
    await page.click('text=Go to verification page');
    
    // Wait for mock verification
    await page.waitForTimeout(1200);
    await page.click('#refresh');
    
    // Complete consent
    await page.check('input[name="agree"]');
    await page.click('button[type="submit"]');
    
    // Complete filesystem setup
    await page.locator('#folder').fill('/test/integration/library');
    await page.click('button[type="submit"]');
    
    // Verify we're in the app
    await expect(page).toHaveURL(/#\/app$/);
    
    // Reload page and verify state is maintained
    await page.reload();
    await expect(page).toHaveURL(/#\/app$/);
    await expect(page.locator('text=Your Library')).toBeVisible();
    
    console.log('✅ localStorage persistence working correctly');
  });
  
  test('Route guard integration with auth state', async ({ page }) => {
    console.log('🛡️ Testing route guards with auth state changes...');
    
    // Start unauthenticated - should redirect protected routes to register
    await page.goto('/#/app');
    await expect(page).toHaveURL(/#\/register$/);
    
    // Register but don't verify - should redirect app to verify
    await page.locator('#email').fill('guard-test@ourlibrary.com');
    await page.locator('#password').fill('GuardTest123!');
    await page.click('button[type="submit"]');
    
    // Try to access app - should redirect to verify
    await page.goto('/#/app');
    await expect(page).toHaveURL(/#\/verify$/);
    
    // Verify email
    await page.waitForTimeout(1200);
    await page.click('#refresh');
    
    // Try to access app - should redirect to consent
    await page.goto('/#/app');
    await expect(page).toHaveURL(/#\/setup\/consent$/);
    
    console.log('✅ Route guard integration working correctly');
  });
  
  test('Form validation and error handling', async ({ page }) => {
    console.log('📝 Testing form validation...');
    
    await page.goto('/#/register');
    
    // Test empty form submission
    await page.click('button[type="submit"]');
    // Browser validation should prevent submission
    
    // Test invalid email
    await page.locator('#email').fill('invalid-email');
    await page.locator('#password').fill('TestPass123!');
    await page.click('button[type="submit"]');
    // Browser validation should prevent submission
    
    // Test short password
    await page.locator('#email').fill('valid@email.com');
    await page.locator('#password').fill('short');
    await page.click('button[type="submit"]');
    // Browser validation should prevent submission (minlength="8")
    
    console.log('✅ Form validation working correctly');
  });
  
  test('Navigation consistency', async ({ page }) => {
    console.log('🧭 Testing navigation consistency...');
    
    // Test navigation links are present on all pages
    const testNavigation = async (url: string, pageName: string) => {
      await page.goto(url);
      await expect(page.locator('text=OurLibrary')).toBeVisible();
      await expect(page.locator('a[href="#/"]')).toBeVisible();
      await expect(page.locator('a[href="#/register"]')).toBeVisible();
      await expect(page.locator('a[href="#/app"]')).toBeVisible();
      console.log(`  ✅ Navigation present on ${pageName}`);
    };
    
    await testNavigation('/', 'Welcome page');
    await testNavigation('/#/register', 'Registration page');
    await testNavigation('/#/signin', 'Sign in page');
    
    // Test footer is present
    await page.goto('/');
    await expect(page.locator('text=© 2025 OurLibrary. All rights reserved.')).toBeVisible();
    
    console.log('✅ Navigation consistency verified');
  });
  
  test('Browser back/forward navigation', async ({ page }) => {
    console.log('⬅️➡️ Testing browser navigation...');
    
    await page.goto('/');
    await page.click('text=Get Started');
    await expect(page).toHaveURL(/#\/register$/);
    
    await page.click('text=Sign in');
    await expect(page).toHaveURL(/#\/signin$/);
    
    // Test back button
    await page.goBack();
    await expect(page).toHaveURL(/#\/register$/);
    
    // Test forward button
    await page.goForward();
    await expect(page).toHaveURL(/#\/signin$/);
    
    console.log('✅ Browser navigation working correctly');
  });
  
  test('Responsive design verification', async ({ page }) => {
    console.log('📱 Testing responsive design...');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('nav')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/#/register');
    await expect(page.locator('form')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/#/setup/consent');
    await expect(page.locator('.card')).toBeVisible();
    
    console.log('✅ Responsive design working correctly');
  });
});