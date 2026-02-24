import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('=== 测试确认计划功能 ===\n');

console.log('1. 打开今日计划...');
await page.goto('http://localhost:5173/today');
await page.waitForLoadState('networkidle');
await page.waitForTimeout(2000);

console.log('2. 点击确认计划按钮...');
const confirmBtn = page.locator('button:has-text("确认计划")');
if (await confirmBtn.count() > 0) {
  await confirmBtn.click();
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'confirm-plan-test.png', fullPage: true });
  console.log('   ✅ 确认计划按钮已点击');
} else {
  console.log('   ❌ 未找到确认计划按钮');
}

console.log('\n=== 测试完成 ===');
await browser.close();
