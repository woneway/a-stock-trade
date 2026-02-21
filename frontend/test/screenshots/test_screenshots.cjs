const { chromium } = require('playwright');

async function takeScreenshots() {
  const browser = await chromium.launch({ 
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  // Test TodayPlan tab switching
  console.log('Testing TodayPlan tab switching...');
  await page.goto('http://localhost:5173/today', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);
  
  // Click each tab and take screenshot
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test/screenshots/today_pre.png', fullPage: true });
  console.log('Pre-market tab');
  
  // Click 盘中 tab
  await page.click('.market-tab:nth-child(2)');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test/screenshots/today_in.png', fullPage: true });
  console.log('In-market tab');
  
  // Click 盘后 tab
  await page.click('.market-tab:nth-child(3)');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test/screenshots/today_post.png', fullPage: true });
  console.log('Post-market tab');
  
  // Test PlanList
  console.log('Testing PlanList...');
  await page.goto('http://localhost:5173/plans', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test/screenshots/plans_full.png', fullPage: true });
  
  // Click on a plan to open modal
  await page.click('.plan-item');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/Users/lianwu/ai/projects/a-stock-trade/frontend/test/screenshots/plans_modal.png', fullPage: true });

  await browser.close();
  console.log('Done!');
}

takeScreenshots().catch(console.error);
