// File: auth-flow.spec.ts
// Path: OurLibrary/Tests/E2E/auth-flow.spec.ts
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-25
// Last Modified: 2025-08-25  01:40PM
// Symlink Pattern: PROJECT_TOOL
//
// Description: Live E2E of email+code flow on GitHub Pages.
// Assumes dev/demo mode logs the 6‑digit code to console.

import { expect, test } from '@playwright/test';

test.describe('OurLibrary auth happy path', () => {
  test('register → capture 6‑digit code from console → verify → reach desktop library', async ({ page }) => {
    const consoleMessages: string[] = [];
    page.on('console', msg => consoleMessages.push(msg.text()));

    // With baseURL set, "/" is the live site
    const BASE = 'https://callmechewy.github.io/OurLibrary/';
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });

    // Open registration modal ("Get Started" button)
    await page.getByRole('button', { name: /get started/i }).click();

    // Choose "Register with Email & Password"
    await page.getByRole('button', { name: /register with email/i }).click();

    // Fill form
    const email = `demo.${Date.now()}@example.com`;
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/full name/i).fill('Demo User');
    await page.getByLabel(/^password$/i).fill('DemoPass!123');
    await page.getByLabel(/confirm password/i).fill('DemoPass!123');

    const zip = page.getByLabel(/zip/i);
    if (await zip.isVisible()) await zip.fill('12345');

    const tos = page.getByRole('checkbox', { name: /terms/i });
    if (await tos.isVisible()) await tos.check();

    // Submit to trigger email code generation
    await page.getByRole('button', { name: /create account/i }).click();

    // Capture 6‑digit code from console logs (demo mode)
    let code = '';
    for (let i = 0; i < 40 && !code; i++) {
      await page.waitForTimeout(200);
      const hit = consoleMessages.find(t => /\b(\d{6})\b/.test(t));
      if (hit) code = (hit.match(/\b(\d{6})\b/) || [])[1] || '';
    }
    expect.soft(code, 'verification code surfaced in console').toMatch(/^\d{6}$/);

    // Enter code and confirm
    await page.getByLabel(/verification code/i).fill(code);
    await page.getByRole('button', { name: /verify/i }).click();

    // Expect redirect to the library app (enhanced desktop)
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveURL(/desktop-library/i);
    await expect(page.getByText(/Anderson.*Enhanced Edition/i)).toBeVisible();
  });
});