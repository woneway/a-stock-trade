import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表页面...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');
console.log('   Page title:', await page.title());

console.log('2. 点击新建计划按钮...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);

console.log('3. 截图保存...');
await page.screenshot({ path: 'test-plan-modal.png', fullPage: true });
console.log('   Saved to test-plan-modal.png');

await browser.close();
console.log('Done!');
