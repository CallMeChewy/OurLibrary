const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Listen for console messages to capture the verification code
  page.on('console', msg => {
    console.log('BROWSER CONSOLE:', msg.text());
  });
  
  try {
    console.log('Navigating to auth demo...');
    await page.goto('https://callmechewy.github.io/OurLibrary/BowersWorld.com/auth-demo.html');
    
    console.log('Filling registration form...');
    await page.fill('#fullName', 'Test User');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'testpass123');
    await page.fill('#confirmPassword', 'testpass123');
    
    console.log('Submitting form...');
    await page.click('button[type="submit"]');
    
    // Wait for the verification screen to appear
    await page.waitForSelector('#verificationCode', { timeout: 10000 });
    
    console.log('Verification screen appeared!');
    
    // Check for status messages
    const statusContainer = await page.locator('#statusContainer').innerHTML();
    console.log('Status messages:', statusContainer);
    
    // Take a screenshot
    await page.screenshot({ path: 'verification_screen.png' });
    
    // Check if verification code is in the page somewhere
    const pageContent = await page.content();
    const codeMatch = pageContent.match(/DEMO MODE.*?([A-Z0-9]{6})/);
    if (codeMatch) {
      console.log('Found verification code:', codeMatch[1]);
    } else {
      console.log('No verification code found in page content');
    }
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();
