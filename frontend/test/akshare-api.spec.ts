import { test, expect, chromium, Browser, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface TestResult {
  category: string;
  functionName: string;
  params: Record<string, string>;
  status: 'success' | 'error';
  responseTime: number;
  error?: string;
  dataSample?: any;
}

const results: TestResult[] = [];
const screenshotDir = '/Users/lianwu/ai/projects/a-stock-trade/frontend/test-results/akshare-screenshots';

// 确保截图目录存在
if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir, { recursive: true });
}

async function getCategories(page: Page): Promise<{ name: string; functions: { name: string; description: string }[] }[]> {
  const categories = await page.evaluate(() => {
    // @ts-ignore
    return window.__CATEGORIES__ || [];
  });

  // 如果 window 上没有，通过 API 获取
  if (categories.length === 0) {
    const response = await page.request.get('http://localhost:8000/akshare/categories');
    const data = await response.json();
    return Object.entries(data).map(([name, funcs]: [string, any]) => ({
      name,
      functions: funcs
    }));
  }
  return categories;
}

async function getSchema(page: Page, funcName: string) {
  const response = await page.request.get(`http://localhost:8000/akshare/schema/${funcName}`);
  return await response.json();
}

async function callFunction(page: Page, funcName: string, params: Record<string, string>) {
  const queryString = new URLSearchParams(params).toString();
  const url = queryString
    ? `http://localhost:8000/akshare/functions/${funcName}?${queryString}`
    : `http://localhost:8000/akshare/functions/${funcName}`;

  const startTime = Date.now();
  try {
    const response = await page.request.get(url);
    const responseTime = Date.now() - startTime;
    const data = await response.json();
    return {
      status: response.status(),
      data,
      responseTime,
      error: response.status() >= 400 ? data.error || data.detail : undefined
    };
  } catch (e: any) {
    return {
      status: 0,
      data: null,
      responseTime: Date.now() - startTime,
      error: e.message
    };
  }
}

async function getDefaultParams(schema: any): Promise<Record<string, string>> {
  const params: Record<string, string> = {};

  if (!schema.params) return params;

  for (const param of schema.params) {
    if (param.default && param.default !== 'PydanticUndefined') {
      params[param.name] = param.default;
    } else if (param.required) {
      // 根据参数名设置默认值
      if (param.name.includes('date') || param.name === 'start_date' || param.name === 'end_date') {
        params[param.name] = '2025-01-01';
      } else if (param.name === 'symbol') {
        params[param.name] = '000001';
      } else if (param.name === 'stock') {
        params[param.name] = '000001';
      } else if (param.name === 'indicator') {
        params[param.name] = '今日';
      } else if (param.name === 'sector_type') {
        params[param.name] = '行业资金流';
      } else if (param.name === 'period') {
        params[param.name] = 'daily';
      } else if (param.name === 'adjust') {
        params[param.name] = '';
      }
    }
  }

  return params;
}

test.describe('AKShare API Testing', () => {
  test('should test all akshare functions', async ({ page }) => {
    // 访问测试页面
    await page.goto('http://localhost:5185/akshare-test');
    await page.waitForLoadState('networkidle');

    // 等待页面加载完成
    await page.waitForSelector('.tab-list', { timeout: 10000 });

    // 获取所有分类
    const response = await page.request.get('http://localhost:8000/akshare/categories');
    const categoriesData = await response.json();

    const categories = Object.entries(categoriesData).map(([name, funcs]: [string, any]) => ({
      name,
      functions: funcs
    }));

    console.log(`\n=== Found ${categories.length} categories ===`);

    // 遍历每个分类
    for (const category of categories) {
      console.log(`\n--- Category: ${category.name} (${category.functions.length} functions) ---`);

      // 点击分类 Tab
      const tabButton = page.locator(`.tab-btn:has-text("${category.name}")`);
      if (await tabButton.isVisible()) {
        await tabButton.click();
        await page.waitForTimeout(300);
      }

      // 遍历每个函数
      for (const func of category.functions) {
        console.log(`\nTesting: ${func.name}`);

        try {
          // 点击函数
          const funcItem = page.locator(`.func-item:has-text("${func.name}")`);
          if (await funcItem.isVisible()) {
            await funcItem.click();
            await page.waitForTimeout(500);
          }

          // 获取 schema
          const schema = await getSchema(page, func.name);

          // 获取默认参数
          const params = await getDefaultParams(schema);

          // 截图
          await page.screenshot({
            path: `${screenshotDir}/${category.name}_${func.name}_params.png`,
            fullPage: false
          });

          // 调用接口
          const result = await callFunction(page, func.name, params);

          // 记录结果
          const testResult: TestResult = {
            category: category.name,
            functionName: func.name,
            params,
            status: result.error ? 'error' : 'success',
            responseTime: result.responseTime,
            error: result.error,
            dataSample: result.data ? (Array.isArray(result.data) ? result.data.slice(0, 3) : result.data) : undefined
          };
          results.push(testResult);

          // 截图结果
          await page.screenshot({
            path: `${screenshotDir}/${category.name}_${func.name}_result.png`,
            fullPage: false
          });

          console.log(`  Status: ${result.status}, Time: ${result.responseTime}ms, Error: ${result.error || 'none'}`);

        } catch (e: any) {
          console.error(`  Error: ${e.message}`);
          results.push({
            category: category.name,
            functionName: func.name,
            params: {},
            status: 'error',
            responseTime: 0,
            error: e.message
          });
        }
      }
    }

    // 保存测试结果
    const report = {
      total: results.length,
      success: results.filter(r => r.status === 'success').length,
      error: results.filter(r => r.status === 'error').length,
      results
    };

    fs.writeFileSync(
      '/Users/lianwu/ai/projects/a-stock-trade/frontend/test-results/akshare-test-report.json',
      JSON.stringify(report, null, 2)
    );

    console.log('\n=== Test Complete ===');
    console.log(`Total: ${report.total}, Success: ${report.success}, Error: ${report.error}`);
    console.log(`Report saved to: /Users/lianwu/ai/projects/a-stock-trade/frontend/test-results/akshare-test-report.json`);

  });
});
