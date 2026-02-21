import { test, expect } from '@playwright/test';

interface PageConfig {
  path: string;
  name: string;
  verifyElements?: string[];
}

const pages: PageConfig[] = [
  {
    path: '/',
    name: 'Dashboard',
    verifyElements: ['.page', '.dashboard-hero', '.hero-value']
  },
  {
    path: '/today',
    name: 'TodayPlan',
    verifyElements: ['.page', '.plan-section', '.market-grid']
  },
  {
    path: '/strategy',
    name: 'Strategy',
    verifyElements: ['.page', '.strategy-card', '.strategy-name']
  },
  {
    path: '/plans',
    name: 'PlanList',
    verifyElements: ['.page', '.plan-item', '.calendar-header']
  },
  {
    path: '/settings',
    name: 'Settings',
    verifyElements: ['.page', '.review-tabs', '.card']
  },
];

pages.forEach(({ path, name, verifyElements }) => {
  test.describe(`页面: ${name}`, () => {
    test('页面加载成功', async ({ page }) => {
      const response = await page.goto(path, { waitUntil: 'networkidle' });
      expect(response?.status()).toBe(200);
    });

    test('关键元素存在', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle' });
      await expect(page.locator('.page')).toBeVisible();
    });

    test('侧边栏正常显示', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle' });
      await expect(page.locator('.sidebar')).toBeVisible();
      await expect(page.locator('.logo')).toContainText('A股交易系统');
    });

    test('导航菜单正常', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle' });
      const navItems = page.locator('.nav-item');
      await expect(navItems).toHaveCount(5);
    });

    test('截图保存', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);
      await page.screenshot({
        path: `test/screenshots/${name}.png`,
        fullPage: true
      });
    });
  });
});

test.describe('导航交互测试', () => {
  test('侧边栏导航切换正常', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const navItems = page.locator('.nav-item');

    await navItems.nth(1).click();
    await expect(page).toHaveURL('/today');
    await page.waitForTimeout(300);

    await navItems.nth(2).click();
    await expect(page).toHaveURL('/strategy');
    await page.waitForTimeout(300);

    await navItems.nth(3).click();
    await expect(page).toHaveURL('/plans');
    await page.waitForTimeout(300);
  });
});

test.describe('Dashboard 专项测试', () => {
  test('英雄区域渲染', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    await expect(page.locator('.dashboard-hero')).toBeVisible();
    await expect(page.locator('.hero-value')).toBeVisible();
  });

  test('持仓表格显示', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    await expect(page.locator('.page')).toBeVisible();
    const hasTable = await page.locator('table').count() > 0;
    const hasEmpty = await page.locator('.empty-state').count() > 0;
    expect(hasTable || hasEmpty).toBe(true);
  });
});

test.describe('今日计划 专项测试', () => {
  test('Tab导航显示', async ({ page }) => {
    await page.goto('/today', { waitUntil: 'networkidle' });
    await expect(page.locator('.market-tabs')).toBeVisible();
    await expect(page.locator('.market-tab')).toHaveCount(3);
    await expect(page.locator('.market-tab:has-text("盘前")')).toBeVisible();
    await expect(page.locator('.market-tab:has-text("盘中")')).toBeVisible();
    await expect(page.locator('.market-tab:has-text("盘后")')).toBeVisible();
  });

  test('盘前内容显示', async ({ page }) => {
    await page.goto('/today', { waitUntil: 'networkidle' });
    await expect(page.locator('.market-grid')).toBeVisible();
    await expect(page.locator('.flow-grid')).toBeVisible();
    await expect(page.locator('.sector-list')).toBeVisible();
  });

  test('Tab切换正常', async ({ page }) => {
    await page.goto('/today', { waitUntil: 'networkidle' });
    
    await page.locator('.market-tab:has-text("盘中")').click();
    await expect(page.locator('.stock-table')).toBeVisible();
    
    await page.locator('.market-tab:has-text("盘后")').click();
    await expect(page.locator('.executed-list')).toBeVisible();
    await expect(page.locator('.review-form')).toBeVisible();
  });
});

test.describe('策略页面 专项测试', () => {
  test('策略卡片显示', async ({ page }) => {
    await page.goto('/strategy', { waitUntil: 'networkidle' });
    await expect(page.locator('.strategy-card').first()).toBeVisible();
  });

  test('新建策略按钮存在', async ({ page }) => {
    await page.goto('/strategy', { waitUntil: 'networkidle' });
    await expect(page.locator('button:has-text("新建策略")')).toBeVisible();
  });
});

test.describe('计划列表 专项测试', () => {
  test('日历头部显示', async ({ page }) => {
    await page.goto('/plans', { waitUntil: 'networkidle' });
    await expect(page.locator('.calendar-header')).toBeVisible();
  });

  test('计划列表显示', async ({ page }) => {
    await page.goto('/plans', { waitUntil: 'networkidle' });
    await expect(page.locator('.plan-list')).toBeVisible();
  });
});

test.describe('Settings 页面专项测试', () => {
  test('设置Tab显示', async ({ page }) => {
    await page.goto('/settings', { waitUntil: 'networkidle' });
    await expect(page.locator('.review-tabs')).toBeVisible();
  });

  test('表单输入框存在', async ({ page }) => {
    await page.goto('/settings', { waitUntil: 'networkidle' });
    await expect(page.locator('input').first()).toBeVisible();
  });
});
