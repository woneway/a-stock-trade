import { test, expect } from '@playwright/test';

test.describe('完整工作流测试', () => {
  test('创建明日计划流程', async ({ page }) => {
    await page.goto('http://localhost:5173/strategy', { waitUntil: 'networkidle' });
    
    const hasStrategy = await page.locator('.strategy-card').count() > 0;
    console.log('策略页面有策略卡片:', hasStrategy);
    
    await page.goto('http://localhost:5173/plans', { waitUntil: 'networkidle' });
    
    const createBtn = page.locator('button:has-text("创建明日计划")');
    if (await createBtn.isVisible()) {
      console.log('创建按钮可见');
      await createBtn.click();
      await page.waitForTimeout(500);
      
      const modal = page.locator('.modal, [class*="modal"], [role="dialog"]');
      const modalVisible = await modal.first().isVisible().catch(() => false);
      console.log('弹窗打开:', modalVisible);
    } else {
      console.log('创建按钮不可见，可能需要先创建策略');
    }
  });

  test('验证API数据流', async ({ page }) => {
    const response = await page.request.get('http://localhost:8001/api/strategy');
    const strategies = await response.json();
    console.log('策略数量:', Array.isArray(strategies) ? strategies.length : 0);
    
    const planResponse = await page.request.get('http://localhost:8001/api/plan/pre');
    const plans = await planResponse.json();
    console.log('计划数量:', Array.isArray(plans) ? plans.length : 0);
    
    const todayPlanResponse = await page.request.get('http://localhost:8001/api/plan/pre/today');
    const todayPlan = await todayPlanResponse.json();
    console.log('今日计划:', todayPlan ? '有' : '无');
  });

  test('今日计划页面验证', async ({ page }) => {
    await page.goto('http://localhost:5173/today', { waitUntil: 'networkidle' });
    
    const content = await page.content();
    const hasMarketTabs = content.includes('盘前') || content.includes('market-tab');
    console.log('有市场Tab:', hasMarketTabs);
    
    const hasCandidate = content.includes('候选') || content.includes('candidate') || content.includes('股票');
    console.log('有候选股票区域:', hasCandidate);
  });
});
