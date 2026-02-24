import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

console.log('1. 强制刷新页面...');
await page.goto('http://localhost:5173/plans', { waitUntil: 'networkidle' });

console.log('2. 点击新建计划...');
await page.getByRole('button', { name: '+ 新建计划' }).click();
await page.waitForTimeout(2000);

console.log('3. 检查默认日期...');
const modalTitle = await page.locator('h2').textContent();
console.log('   弹窗标题:', modalTitle);

console.log('Done!');
await browser.close();
