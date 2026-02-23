import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

// Collect console errors
const errors = [];
page.on('console', msg => {
  if (msg.type() === 'error') errors.push(msg.text());
});
page.on('pageerror', err => errors.push(err.message));

const pages = [
  { url: 'http://localhost:5174/', name: 'Dashboard' },
  { url: 'http://localhost:5174/today', name: 'TodayPlan' },
  { url: 'http://localhost:5174/strategy', name: 'Strategy' },
  { url: 'http://localhost:5174/plans', name: 'PlanList' },
  { url: 'http://localhost:5174/settings', name: 'Settings' },
];

console.log('Testing pages...\n');

for (const p of pages) {
  try {
    await page.goto(p.url, { waitUntil: 'networkidle', timeout: 10000 });
    await page.waitForTimeout(1000);
    console.log(`✅ ${p.name}: OK`);
  } catch (e) {
    console.log(`❌ ${p.name}: ${e.message}`);
  }
}

console.log('\nConsole Errors:', errors.length ? errors : 'None');
await browser.close();
