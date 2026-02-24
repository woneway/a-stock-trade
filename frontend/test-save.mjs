import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 访问计划列表...');
await page.goto('http://localhost:5173/plans');
await page.waitForLoadState('networkidle');

console.log('2. 点击新建计划...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(1000);

console.log('3. 选择策略...');
const strategyItem = page.locator('.strategy-select-item').filter({ hasText: '龙头战法' }).first();
await strategyItem.click({ force: true });
await page.waitForTimeout(1000);

console.log('4. 扫描股票...');
const scanBtn = page.locator('button:has-text("扫描股票")').first();
await scanBtn.click({ force: true });
console.log('   等待扫描...');
await page.waitForTimeout(5000);
await page.screenshot({ path: 't1-scanned.png', fullPage: true });

console.log('5. 选择第一只股票...');
const firstStockCheckbox = page.locator('input[type="checkbox"]').first();
await firstStockCheckbox.click({ force: true });
await page.waitForTimeout(500);
await page.screenshot({ path: 't2-stock-selected.png', fullPage: true });

console.log('6. 点击生成计划...');
const generateBtn = page.locator('button:has-text("生成计划")');
await generateBtn.click({ force: true });
console.log('   等待保存...');
await page.waitForTimeout(3000);
await page.screenshot({ path: 't3-generated.png', fullPage: true });

console.log('7. 验证结果...');
const pageContent = await page.content();
if (pageContent.includes('02/25') || pageContent.includes('计划已生成')) {
  console.log('   ✓ 计划创建成功!');
} else {
  console.log('   ✗ 计划创建可能失败');
}

console.log('Done!');
await browser.close();
