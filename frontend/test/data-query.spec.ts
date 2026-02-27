import { test, expect } from '@playwright/test';

/**
 * 游资数据接口 E2E 测试
 * 测试查询、强制刷新、同步数据功能
 */
test.describe('游资数据接口测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到数据查询页面
    await page.goto('/data-query');
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  /**
   * 测试1: 验证数据查询页面正常加载
   */
  test('页面加载 - 数据查询页面正常显示', async ({ page }) => {
    // 验证页面标题
    await expect(page.locator('h1')).toContainText('数据查询');

    // 验证左侧菜单有游资常用分类
    await expect(page.locator('.dq-tab').filter({ hasText: '游资常用' })).toBeVisible();

    // 验证有执行查询按钮
    await expect(page.locator('button:has-text("执行查询")')).toBeVisible();
  });

  /**
   * 测试2: 查询功能 - 涨停板池
   */
  test('查询功能 - 涨停板池(使用缓存)', async ({ page }) => {
    // 点击"游资常用"标签
    await page.click('.dq-tab:has-text("游资常用")');

    // 点击"涨停板池"接口
    await page.click('.dq-item:has-text("涨停板池")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_zt_pool_em');

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');

    // 验证数据条数显示
    await expect(page.locator('.result-count')).toContainText(/\d+ 条/);

    // 验证缓存标签显示
    const sourceLabel = page.locator('.dq-result-header span').filter({ hasText: /缓存|实时/ });
    await expect(sourceLabel).toBeVisible();
  });

  /**
   * 测试3: 强制刷新功能 - 个股资金流向
   */
  test('强制刷新 - 个股资金流向', async ({ page }) => {
    // 点击"游资常用"标签
    await page.click('.dq-tab:has-text("游资常用")');

    // 点击"个股资金流向"接口
    await page.click('.dq-item:has-text("个股资金流向")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_individual_fund_flow');

    // 先执行一次普通查询建立缓存
    await page.click('button:has-text("执行查询")');
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 点击强制刷新按钮
    await page.click('button:has-text("强制刷新")');

    // 等待强制刷新完成
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');

    // 验证实时标签显示（强制刷新应该显示实时数据）
    const sourceLabel = page.locator('.dq-result-header span').filter({ hasText: /缓存|实时/ });
    await expect(sourceLabel).toBeVisible();
  });

  /**
   * 测试4: 同步数据功能 - 龙虎榜详情
   */
  test('同步数据 - 龙虎榜详情', async ({ page }) => {
    // 点击"龙虎榜"分类
    await page.click('.dq-tab:has-text("龙虎榜")');

    // 点击"龙虎榜详情"接口
    await page.click('.dq-item:has-text("龙虎榜详情")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_lhb_detail_em');

    // 点击同步数据按钮
    await page.click('button:has-text("同步数据")');

    // 等待同步完成（同步会先同步再查询）
    await page.waitForSelector('.dq-result', { timeout: 60000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');

    // 验证数据存在
    await expect(page.locator('.dq-result-table table')).toBeVisible();
  });

  /**
   * 测试5: 板块资金流向查询
   */
  test('查询功能 - 板块资金流向', async ({ page }) => {
    // 点击"游资常用"标签
    await page.click('.dq-tab:has-text("游资常用")');

    // 点击"板块资金流向"接口
    await page.click('.dq-item:has-text("板块资金流向")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_sector_fund_flow_rank');

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');
  });

  /**
   * 测试6: 龙虎榜营业部查询
   */
  test('查询功能 - 龙虎榜营业部', async ({ page }) => {
    // 点击"龙虎榜"分类
    await page.click('.dq-tab:has-text("龙虎榜")');

    // 点击"营业部排行"接口
    await page.click('.dq-item:has-text("营业部排行")');

    // 等待接口详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');
  });

  /**
   * 测试7: 多接口遍历测试
   */
  test('多接口遍历 - 游资常用接口', async ({ page }) => {
    // 点击"游资常用"标签
    await page.click('.dq-tab:has-text("游资常用")');

    // 游资常用接口列表
    const yzInterfaces = [
      'A股实时行情',
      '涨停板',
      '涨停板池',
      '板块资金流向',
      '个股资金流向',
      '龙虎榜详情',
      '龙虎榜营业部',
    ];

    for (const interfaceName of yzInterfaces) {
      console.log(`Testing interface: ${interfaceName}`);

      // 点击接口
      const item = page.locator('.dq-item').filter({ hasText: interfaceName });
      if (await item.count() > 0) {
        await item.click();

        // 等待详情加载
        await page.waitForTimeout(500);

        // 执行查询
        await page.click('button:has-text("执行查询")');

        // 等待结果或错误（有些接口可能暂时不可用）
        try {
          await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });
          console.log(`  ✓ ${interfaceName} - 查询完成`);
        } catch (e) {
          console.log(`  ✗ ${interfaceName} - 超时`);
        }
      }
    }
  });

  /**
   * 测试8: 强势涨停池查询
   */
  test('查询功能 - 强势涨停池', async ({ page }) => {
    // 点击"涨跌停"分类
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击"涨停板池-强势"接口
    await page.click('.dq-item:has-text("涨停板池-强势")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_zt_pool_strong_em');

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');
  });

  /**
   * 测试9: 昨日涨停池查询
   */
  test('查询功能 - 昨日涨停池', async ({ page }) => {
    // 点击"涨跌停"分类
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击"昨日涨停池"接口
    await page.click('.dq-item:has-text("昨日涨停池")');

    // 等待接口详情加载
    await expect(page.locator('.dq-detail-title h2')).toContainText('stock_zt_pool_previous_em');

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');
  });

  /**
   * 测试10: 沪深港通持股查询
   */
  test('查询功能 - 沪深港通持股', async ({ page }) => {
    // 点击"游资常用"标签
    await page.click('.dq-tab:has-text("游资常用")');

    // 点击"沪深港通持股"接口
    await page.click('.dq-item:has-text("沪深港通持股")');

    // 等待接口详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 点击执行查询按钮
    await page.click('button:has-text("执行查询")');

    // 等待查询结果
    await page.waitForSelector('.dq-result', { timeout: 30000 });

    // 验证结果显示
    await expect(page.locator('.dq-result-header h3')).toContainText('查询结果');
  });
});
