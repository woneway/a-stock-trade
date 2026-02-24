import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表页面...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 点击新建计划按钮...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);

console.log('3. 选择策略 "龙头战法"...');
await page.getByText('龙头战法').first().click();
await page.waitForTimeout(500);

console.log('4. 截图保存...');
await page.screenshot({ path: 'test-plan-strategy-selected.png', fullPage: true });
console.log('   Saved to test-plan-strategy-selected.png');

console.log('5. 点击扫描股票按钮...');
const scanBtn = page.locator('button:has-text("扫描股票")').first();
if (await scanBtn.isVisible()) {
  await scanBtn.click();
  console.log('   Clicked 扫描股票');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'test-plan-scanned.png', fullPage: true });
  console.log('   Saved test-plan-scanned.png');
}

await browser.close();
console.log('Done!');
