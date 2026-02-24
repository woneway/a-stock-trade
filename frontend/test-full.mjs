import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('=== 完整测试流程 ===\n');

console.log('1. 删除旧计划...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 新建今日计划(2026-02-24)...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1500);
await page.screenshot({ path: 'step1-modal.png', fullPage: true });

console.log('3. 选择策略...');
await page.locator('.strategy-select-item').filter({ hasText: '龙头战法' }).click({ force: true });
await page.waitForTimeout(1000);

console.log('4. 扫描股票...');
await page.locator('button:has-text("扫描股票")').first().click({ force: true });
console.log('   等待扫描...');
await page.waitForTimeout(5000);
await page.screenshot({ path: 'step2-scanned.png', fullPage: true });

console.log('5. 选择股票...');
const checkboxes = page.locator('input[type="checkbox"]');
const count = await checkboxes.count();
console.log(`   找到 ${count} 个checkbox`);
if (count > 0) {
  await checkboxes.first().click({ force: true });
  await page.waitForTimeout(500);
}
await page.screenshot({ path: 'step3-selected.png', fullPage: true });

console.log('6. 生成计划...');
await page.locator('button:has-text("生成计划")').click({ force: true });
console.log('   等待保存...');
await page.waitForTimeout(3000);
await page.screenshot({ path: 'step4-done.png', fullPage: true });

console.log('7. 验证今日计划...');
await page.goto('http://localhost:5173/today');
await page.waitForTimeout(2000);
await page.screenshot({ path: 'step5-today.png', fullPage: true });

console.log('\n=== 测试完成 ===');
await browser.close();
