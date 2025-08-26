import { test, expect } from '@playwright/test';

test('application loads correctly', async ({ page }) => {
  await page.goto('/');
  
  // Check main elements are present
  await expect(page.locator('h1')).toHaveText('OurLibrary');
  await expect(page.locator('main')).toBeVisible();
  
  // Check navigation works
  await expect(page.locator('a[href="#/"]')).toBeVisible();
  await expect(page.locator('a[href="#/register"]')).toBeVisible();
});

test('navigation between pages', async ({ page }) => {
  await page.goto('/');
  
  // Should show main page by default
  await expect(page.locator('text=Welcome to OurLibrary')).toBeVisible();
  
  // Navigate to register
  await page.click('a[href="#/register"]');
  await expect(page.locator('text=Register')).toBeVisible();
  await expect(page.locator('#email')).toBeVisible();
  
  // Navigate to sign in
  await page.click('a[href="#/signin"]');
  await expect(page.locator('text=Sign In')).toBeVisible();
});

test('email verification progression', async ({ page }) => {
  // Start registration flow
  await page.goto('/#/register');
  await page.locator('#email').fill('dev@example.com');
  await page.locator('#password').fill('Himalaya123!');
  await page.locator('button[type="submit"]').click();

  // Go to verification page
  await page.getByRole('link', { name: 'Go to verification page' }).click();
  await expect(page).toHaveURL(/#\/verify$/);

  // Mock auth flips to verified after 1s, so wait and refresh
  await page.locator('#refresh').click();
  await page.waitForTimeout(1200); // Give mock time to verify
  await page.locator('#refresh').click();

  // Should redirect to setup/consent automatically by guard
  await page.waitForURL(/#\/setup\/consent$/);
});