import { test, expect } from '@playwright/test';

test.describe('页面功能测试', () => {
  test('首页加载', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/A股交易系统/);
  });

  test('游资看板页面加载', async ({ page }) => {
    await page.goto('/trader-dashboard');
    await expect(page.getByRole('heading', { name: '游资看板' })).toBeVisible();
  });

  test('接口调试页面加载', async ({ page }) => {
    await page.goto('/data-query');
    await expect(page.getByRole('heading', { name: 'AKShare 接口调试' })).toBeVisible();
  });

  test('接口列表显示', async ({ page }) => {
    await page.goto('/data-query');
    // 使用更具体的选择器
    await expect(page.locator('.func-name').first()).toBeVisible();
    await expect(page.locator('.func-desc').first()).toBeVisible();
  });

  test('选择接口', async ({ page }) => {
    await page.goto('/data-query');
    // 点击列表中的第一项
    await page.locator('.func-item').first().click();
    // 验证参数面板显示
    await expect(page.locator('.current-func code')).toBeVisible();
  });
});
