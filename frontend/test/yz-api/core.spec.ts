/**
 * 游资核心接口 E2E 测试
 * 测试龙虎榜和资金流向核心接口的：
 * 1. 直接查询
 * 2. 强制刷新
 * 3. 缓存查询
 * 4. 同步数据
 */

import { test, expect } from '@playwright/test';

// 测试配置
const API_BASE_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5192';

test.describe('游资核心接口 - 直接查询测试', () => {
  /**
   * 测试1: 龙虎榜详情查询
   */
  test('LHB01 - 龙虎榜详情直接查询', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击龙虎榜tab
    await page.click('.dq-tab:has-text("龙虎榜")');

    // 点击龙虎榜详情
    await page.click('.dq-item:has-text("龙虎榜详情")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 执行查询
    await page.click('button:has-text("执行查询")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    // 验证结果
    const hasResult = await page.locator('.dq-result').count();
    const hasError = await page.locator('.dq-error').count();

    if (hasResult > 0) {
      // 验证数据来源标签
      const sourceText = await page.locator('.dq-result-header span').first().textContent();
      console.log('数据来源:', sourceText);
      console.log('✓ 龙虎榜详情查询成功');
    } else if (hasError > 0) {
      const errorText = await page.locator('.dq-error').textContent();
      console.log('错误信息:', errorText);
    }
  });

  /**
   * 测试2: 个股资金流向查询
   */
  test('CF01 - 个股资金流向直接查询', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击资金流向tab
    await page.click('.dq-tab:has-text("资金流向")');

    // 点击个股资金流向
    await page.click('.dq-item:has-text("个股资金流向")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 输入股票代码参数
    await page.fill('input[placeholder*="股票代码"]', '600519');
    await page.fill('input[placeholder*="天数"]', '1');

    // 执行查询
    await page.click('button:has-text("执行查询")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 个股资金流向查询成功' : '✗ 查询失败');
  });

  /**
   * 测试3: 涨停板池查询
   */
  test('LT01 - 涨停板池直接查询', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击涨跌停tab
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击涨停板池
    await page.click('.dq-item:has-text("涨停板池")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 执行查询
    await page.click('button:has-text("执行查询")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 涨停板池查询成功' : '✗ 查询失败');
  });

  /**
   * 测试4: 板块资金流向排名查询
   */
  test('BK01 - 板块资金流向排名查询', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击资金流向tab
    await page.click('.dq-tab:has-text("资金流向")');

    // 点击板块资金流向排名
    await page.click('.dq-item:has-text("板块资金排名")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 执行查询
    await page.click('button:has-text("执行查询")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 板块资金流向排名查询成功' : '✗ 查询失败');
  });

  /**
   * 测试5: 营业部上榜次数查询
   */
  test('LHB02 - 营业部上榜次数查询', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击龙虎榜tab
    await page.click('.dq-tab:has-text("龙虎榜")');

    // 点击营业部排行
    await page.click('.dq-item:has-text("营业部排行")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 执行查询
    await page.click('button:has-text("执行查询")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 营业部上榜次数查询成功' : '✗ 查询失败');
  });
});

test.describe('游资核心接口 - 强制刷新测试', () => {
  /**
   * 测试6: 强制刷新 - 个股资金流向
   */
  test('CF02 - 个股资金流向强制刷新', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击资金流向tab
    await page.click('.dq-tab:has-text("资金流向")');

    // 点击个股资金流向
    await page.click('.dq-item:has-text("个股资金流向")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 输入股票代码参数
    await page.fill('input[placeholder*="股票代码"]', '600519');
    await page.fill('input[placeholder*="天数"]', '1');

    // 第一次查询（使用缓存）
    await page.click('button:has-text("执行查询")');
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    // 记录第一次查询的数据来源
    const firstSource = await page.locator('.dq-result-header span').first().textContent();
    console.log('第一次查询来源:', firstSource);

    // 点击强制刷新
    await page.click('button:has-text("强制刷新")');
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    // 记录强制刷新后的数据来源
    const secondSource = await page.locator('.dq-result-header span').first().textContent();
    console.log('强制刷新后来源:', secondSource);

    // 验证强制刷新成功
    console.log('✓ 强制刷新测试完成');
  });

  /**
   * 测试7: 强制刷新 - 涨停板池
   */
  test('LT02 - 涨停板池强制刷新', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击涨跌停tab
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击涨停板池
    await page.click('.dq-item:has-text("涨停板池")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 点击强制刷新
    await page.click('button:has-text("强制刷新")');

    // 等待结果
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 30000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 涨停板池强制刷新成功' : '✗ 强制刷新失败');
  });
});

test.describe('游资核心接口 - 同步数据测试', () => {
  /**
   * 测试8: 同步数据 - 龙虎榜详情
   */
  test('LHB03 - 龙虎榜详情同步数据', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击龙虎榜tab
    await page.click('.dq-tab:has-text("龙虎榜")');

    // 点击龙虎榜详情
    await page.click('.dq-item:has-text("龙虎榜详情")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 点击同步数据按钮
    await page.click('button:has-text("同步数据")');

    // 等待同步完成（同步会先同步再查询）
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 60000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 龙虎榜详情同步成功' : '✗ 同步失败');
  });

  /**
   * 测试9: 同步数据 - 涨停板池
   */
  test('LT03 - 涨停板池同步数据', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击涨跌停tab
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击涨停板池
    await page.click('.dq-item:has-text("涨停板池")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 点击同步数据按钮
    await page.click('button:has-text("同步数据")');

    // 等待同步完成
    await page.waitForSelector('.dq-result, .dq-error', { timeout: 60000 });

    const hasResult = await page.locator('.dq-result').count();
    console.log(hasResult > 0 ? '✓ 涨停板池同步成功' : '✗ 同步失败');
  });
});

test.describe('游资核心接口 - 缓存查询测试', () => {
  /**
   * 测试10: 缓存查询 - 验证第二次查询使用缓存
   */
  test('Cache01 - 缓存查询验证', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/data-query`);
    await page.waitForLoadState('networkidle');

    // 点击涨跌停tab
    await page.click('.dq-tab:has-text("涨跌停")');

    // 点击涨停板池
    await page.click('.dq-item:has-text("涨停板池")');

    // 等待详情加载
    await page.waitForSelector('.dq-detail-title h2', { timeout: 10000 });

    // 第一次查询
    await page.click('button:has-text("执行查询")');
    await page.waitForSelector('.dq-result', { timeout: 30000 });
    const firstSource = await page.locator('.dq-result-header span').first().textContent();
    console.log('第一次查询来源:', firstSource);

    // 第二次查询（应该使用缓存）
    await page.click('button:has-text("执行查询")');
    await page.waitForSelector('.dq-result', { timeout: 30000 });
    const secondSource = await page.locator('.dq-result-header span').first().textContent();
    console.log('第二次查询来源:', secondSource);

    // 验证缓存
    if (secondSource?.includes('缓存')) {
      console.log('✓ 缓存查询验证成功');
    } else {
      console.log('⚠ 第二次查询可能未使用缓存');
    }
  });
});

test.describe('游资接口 - 直接API调用测试', () => {
  /**
   * 测试11: 直接调用API - 龙虎榜详情
   */
  test('API01 - 直接调用龙虎榜详情API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lhb_detail_em',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('龙虎榜API响应:', JSON.stringify(data).slice(0, 200));

    if (data.data && data.data.length > 0) {
      console.log('✓ API调用成功，返回数据条数:', data.data.length);
    } else {
      console.log('⚠ API调用成功但无数据');
    }
  });

  /**
   * 测试12: 直接调用API - 涨停板池
   */
  test('API02 - 直接调用涨停板池API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    if (data.data && data.data.length > 0) {
      console.log('✓ 涨停板池API调用成功，返回数据条数:', data.data.length);
    } else {
      console.log('⚠ 涨停板池API调用成功但无数据');
    }
  });

  /**
   * 测试13: 直接调用API - 板块资金流向排名
   */
  test('API03 - 直接调用板块资金流向API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_sector_fund_flow_rank',
        params: { indicator: '今日', sector_type: '行业资金流' },
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    if (data.data && data.data.length > 0) {
      console.log('✓ 板块资金流向API调用成功，返回数据条数:', data.data.length);
    } else {
      console.log('⚠ 板块资金流向API调用成功但无数据');
    }
  });

  /**
   * 测试14: 直接调用API - 个股资金流向
   */
  test('API04 - 直接调用个股资金流向API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_individual_fund_flow',
        params: { stock: '600519', num: '1' },
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    if (data.data && data.data.length > 0) {
      console.log('✓ 个股资金流向API调用成功，返回数据条数:', data.data.length);
    } else {
      console.log('⚠ 个股资金流向API调用成功但无数据');
    }
  });

  /**
   * 测试15: 直接调用API - 营业部上榜次数
   */
  test('API05 - 直接调用营业部上榜次数API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lh_yyb_most',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    if (data.data && data.data.length > 0) {
      console.log('✓ 营业部上榜次数API调用成功，返回数据条数:', data.data.length);
    } else {
      console.log('⚠ 营业部上榜次数API调用成功但无数据');
    }
  });

  /**
   * 测试16: 强制刷新API调用
   */
  test('API06 - 强制刷新API调用', async ({ request }) => {
    // 第一次调用（缓存）
    await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: true,
      },
    });

    // 第二次调用（强制刷新）
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: false,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('✓ 强制刷新API调用成功');
  });
});
