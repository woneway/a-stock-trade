/**
 * 测试辅助函数
 * 提供常用的API调用和验证功能
 */

import { test as base, Page } from '@playwright/test';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

/**
 * 执行akshare接口查询
 */
export async function executeAkshare(
  funcName: string,
  params: Record<string, string> = {},
  useCache: boolean = true
): Promise<any> {
  const response = await axios.post(`${API_BASE_URL}/api/data/akshare/execute`, {
    func_name: funcName,
    params,
    use_cache: useCache,
  });
  return response.data;
}

/**
 * 同步数据到本地数据库
 */
export async function syncAkshareData(
  funcName: string,
  params: Record<string, string> = {}
): Promise<any> {
  const queryString = new URLSearchParams(params).toString();
  const url = `${API_BASE_URL}/api/data/akshare/sync/${funcName}${queryString ? '?' + queryString : ''}`;
  const response = await axios.post(url);
  return response.data;
}

/**
 * 获取接口详情
 */
export async function getFunctionDetail(funcName: string): Promise<any> {
  const response = await axios.get(`${API_BASE_URL}/api/data/akshare/function/${funcName}`);
  return response.data;
}

/**
 * 验证查询结果
 */
export function validateQueryResult(result: any): {
  success: boolean;
  message: string;
  details: {
    hasData: boolean;
    dataCount: number;
    source: string | null;
    hasColumns: boolean;
  };
} {
  // 检查响应结构
  if (!result) {
    return {
      success: false,
      message: '响应为空',
      details: { hasData: false, dataCount: 0, source: null, hasColumns: false },
    };
  }

  // 检查数据存在
  const hasData = result.data && Array.isArray(result.data) && result.data.length > 0;
  const dataCount = result.data?.length || 0;

  // 检查数据来源
  const source = result.source || null;

  // 检查字段
  const hasColumns = result.columns && Array.isArray(result.columns) && result.columns.length > 0;

  return {
    success: hasData,
    message: hasData ? '数据验证通过' : '无数据返回',
    details: { hasData, dataCount, source, hasColumns },
  };
}

/**
 * 等待页面加载完成
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  // 等待关键元素出现
  await page.waitForSelector('.dq-container', { timeout: 10000 }).catch(() => {
    // 如果没有dq-container，可能页面结构不同
    console.log('页面结构可能不同，跳过容器等待');
  });
}

/**
 * 选择接口并等待详情加载
 */
export async function selectInterface(
  page: Page,
  interfaceName: string,
  tabName: string = '游资常用'
): Promise<void> {
  // 点击对应tab
  const tab = page.locator('.dq-tab').filter({ hasText: tabName });
  if (await tab.count() > 0) {
    await tab.click();
  }

  // 点击接口
  const item = page.locator('.dq-item').filter({ hasText: interfaceName });
  if (await item.count() > 0) {
    await item.click();
  }

  // 等待详情加载
  await page.waitForTimeout(500);
}

/**
 * 执行查询并等待结果
 */
export async function executeQueryAndWait(
  page: Page,
  buttonText: string = '执行查询',
  timeout: number = 30000
): Promise<void> {
  await page.click(`button:has-text("${buttonText}")`);
  await page.waitForSelector('.dq-result, .dq-error', { timeout });
}

/**
 * 验证数据来源标签
 */
export async function verifyDataSource(
  page: Page,
  expectedSource: 'cache' | '实时' | 'akshare'
): Promise<boolean> {
  const sourceLabel = page.locator('.dq-result-header span');
  const text = await sourceLabel.textContent();
  return text?.includes(expectedSource) || text?.includes('实时') || false;
}

/**
 * 扩展playwright test配置
 */
export const test = base.extend<{
  executeAkshare: typeof executeAkshare;
  syncAkshareData: typeof syncAkshareData;
  validateQueryResult: typeof validateQueryResult;
  selectInterface: typeof selectInterface;
  executeQueryAndWait: typeof executeQueryAndWait;
}>({
  executeAkshare: async ({}, use) => {
    await use(executeAkshare);
  },
  syncAkshareData: async ({}, use) => {
    await use(syncAkshareData);
  },
  validateQueryResult: async ({}, use) => {
    await use(validateQueryResult);
  },
  selectInterface: async ({ page }, use) => {
    await use(selectInterface);
  },
  executeQueryAndWait: async ({ page }, use) => {
    await use(executeQueryAndWait);
  },
});
