import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 点击新建计划...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);
await page.screenshot({ path: 's1-modal.png', fullPage: true });

console.log('3. 选择策略(强制点击)...');
const strategyItem = page.locator('.strategy-select-item').filter({ hasText: '龙头战法' }).first();
await strategyItem.click({ force: true });
await page.waitForTimeout(1000);
await page.screenshot({ path: 's2-strategy-selected.png', fullPage: true });

console.log('4. 点击扫描股票...');
const scanBtn = page.locator('button:has-text("扫描股票")').first();
await scanBtn.click({ force: true });
console.log('   等待扫描结果...');
await page.waitForTimeout(5000);
await page.screenshot({ path: 's3-scanned.png', fullPage: true });

console.log('Done!');
await browser.close();
