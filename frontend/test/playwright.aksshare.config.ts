import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './test',
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:5185',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    channel: 'chrome',
    headless: false,
  },
});
