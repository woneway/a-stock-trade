import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './test',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test-reports/html' }],
    ['json', { outputFile: 'test-reports/results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:5194',
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'on',
    channel: 'chrome',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5194',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
