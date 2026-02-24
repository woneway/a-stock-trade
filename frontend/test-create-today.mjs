import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 新建计划(今天是2026-02-24)...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);
await page.screenshot({ path: 'c1-modal.png', fullPage: true });

console.log('3. 检查默认日期...');
const modalTitle = await page.locator('h2').textContent();
console.log('   弹窗标题:', modalTitle);

console.log('4. 选择策略...');
await page.locator('.strategy-select-item').filter({ hasText: '龙头战法' }).click({ force: true });
await page.waitForTimeout(1000);

console.log('5. 扫描股票...');
await page.locator('button:has-text("扫描股票")').first().click({ force: true });
await page.waitForTimeout(5000);
await page.screenshot({ path: 'c2-scanned.png', fullPage: true });

console.log('6. 选择第一只股票...');
await page.locator('input[type="checkbox"]').first().click({ force: true });
await page.waitForTimeout(500);

console.log('7. 生成计划...');
await page.locator('button:has-text("生成计划")').click({ force: true });
await page.waitForTimeout(3000);
await page.screenshot({ path: 'c3-done.png', fullPage: true });

console.log('8. 验证今日计划...');
await page.goto('http://localhost:5173/today');
await page.waitForTimeout(2000);
await page.screenshot({ path: 'c4-today.png', fullPage: true });

console.log('Done!');
await browser.close();
