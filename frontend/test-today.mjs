import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问今日计划页面...');
await page.goto('http://localhost:5173/today');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: 'today1.png', fullPage: true });

console.log('2. 检查是否有今日计划...');
const hasPlan = await page.getByText('02/25').count();
if (hasPlan > 0) {
  console.log('   ✓ 找到今日计划');
} else {
  console.log('   ✗ 未找到今日计划');
}

console.log('3. 访问计划列表...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: 'plans1.png', fullPage: true });

console.log('4. 点击02/25计划进入详情...');
await page.getByText('02/25').first().click();
await page.waitForTimeout(1000);
await page.screenshot({ path: 'detail1.png', fullPage: true });

console.log('5. 点击编辑计划...');
await page.getByRole('button', { name: '编辑计划' }).click();
await page.waitForTimeout(1000);
await page.screenshot({ path: 'edit1.png', fullPage: true });

console.log('Done!');
await browser.close();
