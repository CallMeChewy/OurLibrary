import { expect, Frame, Locator, Page, test } from '@playwright/test';

const BASE = '/'; // uses baseURL from config

// ----- noisy logging (helps see if it's "doing something")
function wireLogging(page: Page) {
  page.on('console', msg => console.log('PAGE LOG:', msg.type(), msg.text()));
  page.on('request', req => console.log('➡️', req.method(), req.url()));
  page.on('response', res => console.log('⬅️', res.status(), res.url()));
}

// ----- debug helper: list frames & titles
async function logFrames(page: Page) {
  const frames = page.frames();
  console.log(`🧩 Frames (${frames.length}):`);
  for (const f of frames) console.log(' -', f.name() || '(no name)', '::', f.url());
}

// ----- try to find a visible locator across page + frames
async function firstVisibleAnywhere(page: Page, makeLocators: (ctx: Page|Frame) => Locator[], perTryTimeout = 2500) {
  // search main page first, then each frame
  const contexts: (Page|Frame)[] = [page, ...page.frames()];
  for (const ctx of contexts) {
    for (const loc of makeLocators(ctx)) {
      try {
        const el = loc.first();
        await el.waitFor({ state: 'visible', timeout: perTryTimeout });
        return el;
      } catch { /* try next */ }
    }
  }
  throw new Error('No matching visible locator found in page or frames.');
}

// ----- dump candidate inputs (for screenshots + selector tuning)
async function dumpTextInputs(ctx: Page|Frame, label: string) {
  const inputs = ctx.locator('input');
  const n = await inputs.count();
  console.log(`🔎 ${label}: found ${n} <input> elements`);
  for (let i = 0; i < Math.min(n, 20); i++) {
    const el = inputs.nth(i);
    const type = await el.getAttribute('type');
    const name = await el.getAttribute('name');
    const id = await el.getAttribute('id');
    const ph = await el.getAttribute('placeholder');
    console.log(`  [${i}] type=${type} name=${name} id=${id} placeholder=${ph}`);
  }
}

// ----- main test
test.describe('OurLibrary auth happy path', () => {
  test('register → capture 6‑digit code → verify → reach desktop library', async ({ page }) => {
    wireLogging(page);

    // 1) open landing
    await page.goto(BASE, { waitUntil: 'domcontentloaded' });
    await page.screenshot({ path: 'test-results/01-landing.png' });
    await logFrames(page);

    // 2) click "Get Started" (robust)
    const getStarted = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByRole('button', { name: /get started/i }),
      ctx.getByRole('link',   { name: /get started/i }),
      ctx.getByRole('button', { name: /sign up|create account|join/i }),
      ctx.locator('button:has-text("Get Started")'),
      ctx.locator('a:has-text("Get Started")')
    ]);
    await getStarted.click();
    await page.screenshot({ path: 'test-results/02-after-get-started.png' });
    await logFrames(page);

    // 3) choose email registration
    const emailReg = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByRole('button', { name: /register with email/i }),
      ctx.getByRole('button', { name: /continue with email|sign up with email/i }),
      ctx.locator('button:has-text("Email")'),
      ctx.locator('button:has([class*="email" i])')
    ]);
    await emailReg.click();
    await page.screenshot({ path: 'test-results/03-after-email-register.png' });
    await logFrames(page);

    // 4) fill the form (page + frames; multiple strategies)
    // dump inputs for both page and frames, helpful when it fails
    await dumpTextInputs(page, 'MAIN');
    for (const f of page.frames()) await dumpTextInputs(f, `FRAME:${f.name() || 'no-name'}`);

    const email = `demo.${Date.now()}@example.com`;

    // email
    const emailInput = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByLabel(/email/i),
      ctx.getByPlaceholder(/email/i),
      ctx.locator('input[type="email"]'),
      ctx.locator('input[name="email"]'),
      ctx.locator('input[id*="email" i]'),
      ctx.locator('input[autocomplete="email"]')
    ]);
    await emailInput.fill(email);

    // name
    const nameInput = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByLabel(/full name|name/i),
      ctx.getByPlaceholder(/full name|name/i),
      ctx.locator('input[name*="name" i]'),
      ctx.locator('input[id*="name" i]')
    ]);
    await nameInput.fill('Demo User');

    // password #1
    const pass1 = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByLabel(/^password$/i),
      ctx.getByPlaceholder(/password/i),
      ctx.locator('input[type="password"]').nth(0),
    ]);
    await pass1.fill('DemoPass!123');

    // password #2 (confirm)
    const pass2 = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByLabel(/confirm password|confirm/i),
      ctx.locator('input[type="password"]').nth(1),
    ]);
    await pass2.fill('DemoPass!123');

    // optional ZIP
    try {
      const zip = await firstVisibleAnywhere(page, (ctx) => [
        ctx.getByLabel(/zip|postal/i),
        ctx.getByPlaceholder(/zip|postal/i),
        ctx.locator('input[name*="zip" i]')
      ], 800);
      await zip.fill('12345');
    } catch { /* no zip, fine */ }

    // optional ToS
    try {
      const tos = await firstVisibleAnywhere(page, (ctx) => [
        ctx.getByRole('checkbox', { name: /terms|agree|accept/i }),
        ctx.locator('input[type="checkbox"]')
      ], 800);
      await tos.check();
    } catch { /* no tos, fine */ }

    await page.screenshot({ path: 'test-results/04-form-filled.png' });

    // 5) submit
    const submit = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByRole('button', { name: /create account|register|sign up|continue/i }),
      ctx.locator('button[type="submit"]')
    ]);
    await submit.click();

    // 6) capture 6-digit code from console (dev mode)
    let code = '';
    for (let i = 0; i < 60 && !code; i++) {
      await page.waitForTimeout(250);
      const last = page.context()._events?.console ? '' : ''; // noop – keep TS happy on older versions
      // Playwright console logs already wired; we’ll search page logs via event handler:
      // In practice, if your app emails instead of logging, swap this for mail-check.
    }
    // If your dev build does log the code, wire it like this:
    const buffered: string[] = [];
    page.on('console', msg => buffered.push(msg.text()));
    for (let i = 0; i < 60 && !code; i++) {
      await page.waitForTimeout(250);
      const hit = buffered.find(t => /\b(\d{6})\b/.test(t));
      if (hit) code = (hit.match(/\b(\d{6})\b/) || [])[1] || '';
    }
    expect.soft(code, 'verification code surfaced in console (dev mode)').toMatch(/^\d{6}$/);
    await page.screenshot({ path: 'test-results/05-code-screen.png' });

    // 7) enter code + verify
    const codeInput = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByLabel(/verification code|code/i),
      ctx.getByPlaceholder(/code/i),
      ctx.locator('input[name*="code" i]'),
      ctx.locator('input[type="text"]')
    ]);
    await codeInput.fill(code);

    const verifyBtn = await firstVisibleAnywhere(page, (ctx) => [
      ctx.getByRole('button', { name: /verify|continue|confirm/i }),
      ctx.locator('button[type="submit"]'),
    ]);
    await verifyBtn.click();

    // 8) arrive at desktop library
    await page.waitForLoadState('domcontentloaded');
    await expect(page).toHaveURL(/desktop-library/i, { timeout: 20_000 });
    await expect(page.getByText(/anderson.*enhanced.*edition/i)).toBeVisible({ timeout: 12_000 });
    await page.screenshot({ path: 'test-results/08-desktop-library.png' });
  });
});
