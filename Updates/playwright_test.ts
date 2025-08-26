import { test, expect } from '@playwright/test';

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