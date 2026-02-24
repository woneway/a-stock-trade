import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表页面...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 点击新建计划按钮...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);

console.log('3. 选择策略...');
await page.getByText('龙头战法').first().click();
await page.waitForTimeout(1000);
await page.screenshot({ path: 'step1-strategy-selected.png', fullPage: true });
console.log('   Saved step1-strategy-selected.png');

console.log('4. 点击扫描股票...');
try {
  const scanBtn = page.locator('button:has-text("扫描股票")').first();
  await scanBtn.click({ timeout: 5000 });
  console.log('   Clicked 扫描股票');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'step2-scanned.png', fullPage: true });
  console.log('   Saved step2-scanned.png');
} catch (e) {
  console.log('   Error or timeout:', e.message);
  await page.screenshot({ path: 'step2-error.png', fullPage: true });
}

console.log('Done!');
await browser.close();
