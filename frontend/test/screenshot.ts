import { chromium } from 'playwright-core';

const BASE_URL = 'http://localhost:5173';
const SCREENSHOT_DIR = './test/screenshots';

const pages = [
  { path: '/', name: 'Dashboard' },
  { path: '/plans', name: 'Plans' },
  { path: '/positions', name: 'Positions' },
  { path: '/trades', name: 'Trades' },
  { path: '/review', name: 'Review' },
  { path: '/monitor', name: 'Monitor' },
  { path: '/settings', name: 'Settings' },
];

async function takeScreenshots() {
  console.log('Starting screenshot capture...');

  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  for (const { path, name } of pages) {
    console.log(`Capturing ${name}...`);
    try {
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle', timeout: 10000 });
      await page.waitForTimeout(500);
      await page.screenshot({
        path: `${SCREENSHOT_DIR}/${name}.png`,
        fullPage: true
      });
      console.log(`✓ ${name} saved`);
    } catch (e) {
      console.error(`✗ ${name} failed: ${e.message}`);
    }
  }

  await browser.close();
  console.log('Done!');
}

takeScreenshots().catch(console.error);
