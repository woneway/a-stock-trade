import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('=== 测试编辑计划功能 ===\n');

console.log('1. 打开计划列表...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 点击 02/24 计划打开详情...');
await page.locator('.plan-item').filter({ hasText: '02/24' }).click();
await page.waitForTimeout(1000);

console.log('3. 点击编辑计划按钮...');
await page.locator('button:has-text("编辑计划")').click();
await page.waitForTimeout(2000);
await page.screenshot({ path: 'edit-plan-test.png', fullPage: true });

console.log('4. 检查股票是否加载...');
const stockText = await page.locator('body').textContent();
if (stockText.includes('300308') || stockText.includes('中际旭创')) {
  console.log('   ✅ 股票 300308 已加载');
} else {
  console.log('   ❌ 股票未加载');
}

console.log('\n=== 测试完成 ===');
await browser.close();
