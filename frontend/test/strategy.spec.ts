import { test, expect } from '@playwright/test';

test.describe('策略模块测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/strategy');
  });

  test('策略页面加载', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('策略管理');
    await expect(page.getByRole('button', { name: '+ 创建策略' })).toBeVisible();
  });

  test('创建策略', async ({ page }) => {
    await page.getByRole('button', { name: '+ 创建策略' }).click();
    
    await expect(page.locator('.modal h2')).toContainText('新建策略');
    
    await page.locator('input[placeholder="如: 龙头战法"]').fill('测试策略');
    await page.locator('input[placeholder="如: 市场龙头/空间板"]').fill('测试描述');
    await page.locator('textarea[placeholder="板块首板涨停后第二天的二板确认..."]').fill('测试选股思路');
    await page.locator('input[placeholder="🔥二板,🐉龙回头,📈板块强度"]').fill('二板');
    
    await page.getByRole('button', { name: '保存' }).click();
  });

  test('策略卡片展开/收起', async ({ page }) => {
    const firstExpandIcon = page.locator('.expand-icon').first();
    if (await firstExpandIcon.isVisible()) {
      await firstExpandIcon.click();
      await expect(page.locator('.strategy-content').first()).toBeVisible();
      
      await firstExpandIcon.click();
      await expect(page.locator('.strategy-content').first()).not.toBeVisible();
    }
  });

  test('策略搜索功能', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="搜索策略"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('测试');
      await page.waitForTimeout(500);
    }
  });

  test('策略筛选功能', async ({ page }) => {
    await page.getByRole('button', { name: '启用中' }).click();
    await page.waitForTimeout(300);
    
    await page.getByRole('button', { name: '已停用' }).click();
    await page.waitForTimeout(300);
    
    await page.getByRole('button', { name: '全部' }).click();
  });

  test('策略复制功能', async ({ page }) => {
    const copyButton = page.locator('.strategy-actions .action-btn').filter({ hasText: '复制' }).first();
    if (await copyButton.isVisible()) {
      await copyButton.click();
      await expect(page.locator('.modal h2')).toContainText('新建策略');
      await expect(page.locator('input[value*="副本"]')).toBeVisible();
    }
  });

  test('策略编辑功能', async ({ page }) => {
    const editButton = page.locator('.strategy-actions .action-btn').filter({ hasText: '编辑' }).first();
    if (await editButton.isVisible()) {
      await editButton.click();
      await expect(page.locator('.modal h2')).toContainText('编辑策略');
    }
  });

  test('策略启用/停用功能', async ({ page }) => {
    const toggleButton = page.locator('.strategy-actions .action-btn.warning, .strategy-actions .action-btn.success').first();
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      await page.waitForTimeout(500);
    }
  });
});
