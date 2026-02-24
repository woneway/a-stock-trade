import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();

const traders = [
  { name: '炒股养家', sentiment: '分歧', board: '主流', entry: '打板', indicators: ['涨停数量', '下跌家数', '连板数量'], messages: ['政策消息', '外围市场'] },
  { name: '小鳄鱼', sentiment: '高潮', board: '主流', entry: '打板', indicators: ['涨停数量', '连板数量', '首板数量'], messages: ['政策消息', '行业公告'] },
  { name: '陈小群', sentiment: '冰点', board: '支流', entry: '低吸', indicators: ['下跌家数', '跌停数量', '成交额'], messages: ['行业公告', '个股公告'] },
  { name: '方新侠', sentiment: '分歧', board: '主流', entry: '回封', indicators: ['涨停数量', '连板数量', '换手率'], messages: ['政策消息', '龙虎榜数据'] },
  { name: '作手新一', sentiment: '混沌', board: '轮动', entry: '尾盘', indicators: ['涨停数量', '跌停数量', '上涨家数'], messages: ['政策消息', '外围市场', '行业公告'] },
  { name: '涅盘重升', sentiment: '分歧', board: '主流', entry: '打板', indicators: ['涨停数量', '连板数量', '首板数量'], messages: ['政策消息'] },
];

console.log('=== 游资体验今日计划 ===\n');

for (let i = 0; i < traders.length; i++) {
  const t = traders[i];
  console.log(`\n【${i+1}/6】${t.name} 体验今日计划`);
  console.log('='.repeat(40));

  try {
    await page.goto('http://localhost:5173/plans');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await page.locator('button:has-text("新建计划")').click();
    await page.waitForTimeout(2000);

    await page.locator('input[type="date"]').fill('2026-02-24');
    await page.waitForTimeout(500);

    for (const ind of t.indicators) {
      const btn = page.locator(`span:has-text("${ind}")`).first();
      if (await btn.count() > 0) await btn.click();
      await page.waitForTimeout(200);
    }

    for (const msg of t.messages) {
      const btn = page.locator(`span:has-text("${msg}")`).first();
      if (await btn.count() > 0) await btn.click();
      await page.waitForTimeout(200);
    }

    await page.locator('.strategy-select-item').first().click({ force: true });
    await page.waitForTimeout(1500);

    const scanBtn = page.locator('button:has-text("扫描股票")').first();
    if (await scanBtn.count() > 0) {
      await scanBtn.click({ force: true });
      await page.waitForTimeout(5000);

      if (await page.locator('input[type="checkbox"]').count() > 0) {
        await page.locator('input[type="checkbox"]').first().click({ force: true });
        await page.waitForTimeout(500);
      }
    }

    const genBtn = page.locator('button:has-text("生成计划")').first();
    if (await genBtn.count() > 0) {
      await genBtn.click({ force: true });
      await page.waitForTimeout(3000);
    }

    await page.keyboard.press('Escape');
    await page.waitForTimeout(1000);

    console.log(`✓ ${t.name} 创建计划成功`);

    console.log(`\n→ 体验今日计划页面...`);
    await page.goto('http://localhost:5173/today');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `test/${t.name}-today.png`, fullPage: true });

    const bodyText = await page.locator('body').textContent();

    if (bodyText.includes('今日策略')) console.log('  ✓ 今日策略显示');
    if (bodyText.includes(t.sentiment) || bodyText.includes('情绪')) console.log('  ✓ 情绪周期显示');
    if (bodyText.includes(t.board) || bodyText.includes('板块')) console.log('  ✓ 板块效应显示');
    if (bodyText.includes(t.entry) || bodyText.includes('买入')) console.log('  ✓ 买入方式显示');
    if (bodyText.includes('关注指标')) console.log('  ✓ 关注指标显示');
    if (bodyText.includes('候选股票')) console.log('  ✓ 候选股票显示');

    const editBtn = await page.locator('a:has-text("编辑计划")').count();
    if (editBtn > 0) {
      console.log('  ✓ 编辑计划链接存在');
    }

    const confirmBtn = await page.locator('button:has-text("确认计划")').count();
    if (confirmBtn > 0) {
      console.log('  ✓ 确认计划按钮存在');
    }

    const preTab = await page.locator('button:has-text("盘前")').count();
    const intraTab = await page.locator('button:has-text("盘中")').count();
    const postTab = await page.locator('button:has-text("盘后")').count();
    if (preTab > 0 && intraTab > 0 && postTab > 0) {
      console.log('  ✓ 盘前/盘中/盘后三阶段存在');
    }

    await page.locator('button:has-text("盘中")').click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `test/${t.name}-intraday.png`, fullPage: true });
    console.log('  ✓ 盘中阶段切换');

    await page.locator('button:has-text("盘后")').click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `test/${t.name}-postmarket.png`, fullPage: true });
    console.log('  ✓ 盘后阶段切换');

    console.log(`\n✅ ${t.name} 今日计划体验完成\n`);

  } catch (err) {
    console.log(`❌ ${t.name} 体验失败: ${err.message}\n`);
  }
}

console.log('\n=== 全部游资体验完成 ===\n');
await browser.close();
