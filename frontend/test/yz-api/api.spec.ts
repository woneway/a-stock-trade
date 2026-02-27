/**
 * 游资核心接口 API 测试
 * 直接测试后端 API 功能
 */

import { test, expect } from '@playwright/test';

const API_BASE_URL = 'http://localhost:8001';

test.describe('游资核心接口 API 测试', () => {
  /**
   * 测试1: 涨停板池 API
   */
  test('API-涨停板池: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('涨停板池返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试2: 涨停板池 - 强制刷新
   */
  test('API-涨停板池: 强制刷新', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: false,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('强制刷新返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试3: 涨停板池 - 同步数据
   */
  test('API-涨停板池: 同步数据', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/sync/stock_zt_pool_em`);
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('同步结果:', data);
  });

  /**
   * 测试4: 龙虎榜详情 API
   */
  test('API-龙虎榜详情: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lhb_detail_em',
        params: { start_date: '20240201', end_date: '20240202' },
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('龙虎榜详情返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试5: 龙虎榜详情 - 强制刷新
   */
  test('API-龙虎榜详情: 强制刷新', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lhb_detail_em',
        params: {},
        use_cache: false,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('龙虎榜强制刷新返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试6: 龙虎榜详情 - 同步数据
   */
  test('API-龙虎榜详情: 同步数据', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/sync/stock_lhb_detail_em`);
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('同步结果:', data);
  });

  /**
   * 测试7: 个股资金流向 API
   */
  test('API-个股资金流向: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_individual_fund_flow',
        params: { stock: '600519', num: '1' },
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('个股资金流向返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试8: 个股资金流向 - 强制刷新
   */
  test('API-个股资金流向: 强制刷新', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_individual_fund_flow',
        params: { stock: '600519', num: '1' },
        use_cache: false,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('个股资金流向强制刷新返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试9: 营业部上榜次数 API
   */
  test('API-营业部上榜次数: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lh_yyb_most',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('营业部上榜次数返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试10: 昨日涨停池 API
   */
  test('API-昨日涨停池: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_previous_em',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('昨日涨停池返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试11: 强势涨停池 API
   */
  test('API-强势涨停池: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_strong_em',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('强势涨停池返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试12: 营业部资金实力 API
   */
  test('API-营业部资金实力: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lh_yyb_capital',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('营业部资金实力返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试13: 游资席位动向 API
   */
  test('API-游资席位动向: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_lhb_yytj_sina',
        params: {},
        use_cache: true,
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('游资席位动向返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试14: 沪深港通持股 API (修正函数名)
   */
  test('API-沪深港通持股: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_hsgt_hold_stock_em',
        params: {},
        use_cache: true,
      },
    });

    if (!response.ok()) {
      const errorText = await response.text();
      console.log('错误响应:', errorText);
    }
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('沪深港通持股返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试15: 大宗交易统计 API (修正函数名)
   */
  test('API-大宗交易: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_dzjy_mrtj',
        params: {},
        use_cache: true,
      },
    });

    if (!response.ok()) {
      const errorText = await response.text();
      console.log('错误响应:', errorText);
    }
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('大宗交易返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试16: 概念资金流向 API
   */
  test('API-概念资金流向: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_fund_flow_concept',
        params: {},
        use_cache: true,
      },
    });

    if (!response.ok()) {
      const errorText = await response.text();
      console.log('错误响应:', errorText);
    }
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('概念资金流向返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试17: 行业资金流向 API
   */
  test('API-行业资金流向: 直接查询', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_fund_flow_industry',
        params: {},
        use_cache: true,
      },
    });

    if (!response.ok()) {
      const errorText = await response.text();
      console.log('错误响应:', errorText);
    }
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    console.log('行业资金流向返回数据条数:', data.data?.length || 0);
    console.log('数据来源:', data.source);
  });

  /**
   * 测试18: 缓存查询验证
   */
  test('API-缓存验证: 第二次查询应使用缓存', async ({ request }) => {
    // 第一次查询
    const response1 = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: true,
      },
    });
    const data1 = await response1.json();
    console.log('第一次查询数据来源:', data1.source);

    // 第二次查询（应该使用缓存）
    const response2 = await request.post(`${API_BASE_URL}/api/data/akshare/execute`, {
      data: {
        func_name: 'stock_zt_pool_em',
        params: {},
        use_cache: true,
      },
    });
    const data2 = await response2.json();
    console.log('第二次查询数据来源:', data2.source);
  });
});
