import { test, expect } from '@playwright/test';

test.describe('游资视角完整功能体验', () => {
  test('游资一日交易流程', async ({ page }) => {
    // 第一步：开盘前看首页 Dashboard，了解市场概况
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('首页');
    console.log('✅ 1. 进入首页 Dashboard');

    // 查看当日市场数据卡片
    const dashboardCards = page.locator('.dashboard-cards, .stats-grid, .card');
    const hasCards = await dashboardCards.first().isVisible().catch(() => false);
    if (hasCards) {
      console.log('✅ 2. 查看市场概览数据');
    }

    // 第二步：看热度榜，了解热点板块
    await page.click('a[href="/heat"]');
    await expect(page.locator('h1, h2')).toContainText('热度');
    console.log('✅ 3. 进入热度页面，分析热点板块');

    // 查看热度数据
    await page.waitForTimeout(500);
    const heatItems = page.locator('.heat-item, .sector-item, .hot-stock');
    const hasHeatData = await heatItems.first().isVisible().catch(() => false);
    if (hasHeatData) {
      console.log('✅ 4. 查看热点板块和个股');
    }

    // 第三步：去策略页面选股
    await page.click('a[href="/strategy"]');
    await expect(page.locator('h1')).toContainText('策略管理');
    console.log('✅ 5. 进入策略管理页面');

    // 查看现有策略
    const strategyCards = page.locator('.strategy-card');
    const strategyCount = await strategyCards.count();
    console.log(`✅ 6. 找到 ${strategyCount} 个策略`);

    // 展开第一个策略查看详情
    if (strategyCount > 0) {
      const firstExpand = page.locator('.expand-icon').first();
      if (await firstExpand.isVisible()) {
        await firstExpand.click();
        await page.waitForTimeout(300);
        const hasContent = await page.locator('.strategy-content').first().isVisible();
        if (hasContent) {
          console.log('✅ 7. 展开策略查看详情（选股思路、买卖条件、风控参数）');
        }
      }
    }

    // 第四步：使用策略选股
    const scanButton = page.locator('.strategy-actions .action-btn').filter({ hasText: '选股' }).first();
    if (await scanButton.isVisible()) {
      await scanButton.click();
      await page.waitForTimeout(1000);
      const scanModal = page.locator('.modal');
      if (await scanModal.isVisible()) {
        console.log('✅ 8. 打开选股弹窗，扫描符合条件的股票');
        
        // 查看选股结果
        const scanResults = page.locator('.scan-result-item, .result-item');
        const resultCount = await scanResults.count();
        console.log(`✅ 9. 找到 ${resultCount} 只符合条件的股票`);
        
        // 关闭弹窗
        await page.click('.modal-header button, .modal-footer button:has-text("关闭")');
      }
    }

    // 第五步：制定今日计划
    await page.click('a[href="/today"]');
    await expect(page.locator('h1, h2')).toContainText('今日计划');
    console.log('✅ 10. 进入今日计划页面');

    // 查看今日计划内容
    const todayPlanContent = page.locator('.plan-content, .today-content, .content');
    const hasPlanContent = await todayPlanContent.first().isVisible().catch(() => false);
    if (hasPlanContent) {
      console.log('✅ 11. 查看今日交易计划');
    }

    // 第六步：查看计划列表
    await page.click('a[href="/plans"]');
    await expect(page.locator('h1, h2')).toContainText('计划列表');
    console.log('✅ 12. 进入计划列表页面');

    const planCards = page.locator('.plan-card, .plan-item');
    const planCount = await planCards.count();
    console.log(`✅ 13. 历史计划数量: ${planCount}`);

    // 第七步：查看设置
    await page.click('a[href="/settings"]');
    await expect(page.locator('h1, h2')).toContainText('设置');
    console.log('✅ 14. 进入设置页面');

    // 查看设置选项
    const settingsSections = page.locator('.settings-section, .section');
    const settingsCount = await settingsSections.count();
    console.log(`✅ 15. 设置分类数量: ${settingsCount}`);

    console.log('\n🎉 游资一日交易流程体验完成！');
  });

  test('策略管理完整流程', async ({ page }) => {
    await page.goto('/strategy');
    
    // 创建新策略
    await page.click('button:has-text("创建策略")');
    await expect(page.locator('.modal h2')).toContainText('新建策略');
    console.log('✅ 创建策略弹窗打开');

    // 填写策略基本信息
    await page.fill('input[placeholder*="龙头战法"]', '测试游资策略');
    await page.fill('input[placeholder*="市场龙头"]', '追涨强势股');
    await page.fill('textarea[placeholder*="板块首板"]', '选取当日板块涨幅第一的龙头股');
    console.log('✅ 填写策略基本信息');

    // 设置风控参数
    await page.fill('input[type="number"] >> nth=0', '6'); // 止损
    await page.fill('input[type="number"] >> nth=1', '20'); // 仓位
    console.log('✅ 设置止损和仓位');

    // 保存策略
    await page.click('button:has-text("保存")');
    await page.waitForTimeout(500);
    console.log('✅ 策略创建成功');

    // 验证策略已创建
    await expect(page.locator('.strategy-name:has-text("测试游资策略")').first()).toBeVisible();
  });
});
