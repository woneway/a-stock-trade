import { chromium } from 'playwright';

async function screenshot() {
  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('http://localhost:5175/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test-reports/dashboard.png', fullPage: true });
  await browser.close();
  console.log('Screenshot saved');
}

screenshot().catch(console.error);
