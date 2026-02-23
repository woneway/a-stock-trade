# AI-Driven Frontend Visual Testing & Optimization Skills

## Overview

This document captures the methodology and skills developed during the A股交易系统 frontend optimization project. The approach combines Playwright for screenshot capture with AI vision models (MiniMax VLM / Claude) for visual analysis and iterative improvements.

## Methodology

### Core Workflow

```
Screenshot → AI Analysis → Problem Identification → Code Fix → Verify → Repeat
```

### Key Steps

1. **Capture Screenshots**: Use Playwright to capture all frontend pages
2. **AI Visual Analysis**: Submit screenshots to VLM for comprehensive analysis
3. **Extract Issues**: Parse AI feedback into actionable problems
4. **Implement Fixes**: Modify code to address identified issues
5. **Verify Changes**: Re-capture and re-analyze to confirm improvements
6. **Iterate**: Continue until quality meets standards

## Tools & Setup

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './test',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    channel: 'chrome', // Use system Chrome
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
});
```

### Screenshot Capture Script

```typescript
// test/screenshot.ts
import { chromium } from 'playwright-core';

async function captureScreenshots() {
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  const pages = ['/', '/plans', '/positions', '/trades', '/review', '/monitor', '/settings'];
  
  for (const path of pages) {
    await page.goto(`http://localhost:5173${path}`);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `test/screenshots${path}.png`, fullPage: true });
  }
  
  await browser.close();
}
```

### AI Visual Analysis Prompt

```
分析这张A股交易系统的前端页面截图，从以下维度给出改进建议：

1. **布局结构**：导航、侧边栏、内容区的比例和位置
2. **视觉设计**：颜色搭配、对比度、层次感
3. **组件一致性**：按钮、卡片、表格、输入框的样式统一性
4. **交互体验**：鼠标悬停效果、点击反馈、过渡动画
5. **细节处理**：间距、圆角、阴影、图标使用
6. **响应式适配**：不同屏幕尺寸下的表现
7. **整体印象**：是否现代、时尚、专业

请列出具体的问题和对应的优化建议，用JSON格式输出：
{
  "issues": [
    {"severity": "high/medium/low", "description": "问题描述", "suggestion": "优化建议"}
  ],
  "summary": "总体评价",
  "priority_fixes": ["优先修复项1", "优先修复项2"]
}
```

## Optimization Categories

### 1. Layout & Structure
- Consistent sidebar width and styling
- Proper content area padding/margins
- Grid-based responsive layouts
- Card-based content organization

### 2. Visual Design
- Define CSS variables for theme colors
- Use accent colors consistently (pink #e91e63)
- Ensure sufficient contrast ratios
- Apply subtle shadows and borders

### 3. Component Styling
- Unified button styles (primary, secondary, danger)
- Consistent card styling (padding, border-radius, background)
- Table styling with proper alignment and spacing
- Form input styling with focus states

### 4. Interactions
- Hover effects on interactive elements
- Transition animations for state changes
- Loading states for async operations
- Toast notifications for user feedback

### 5. Details
- Proper spacing (8px grid system)
- Consistent border-radius
- Icon usage for visual cues
- Status badges with semantic colors

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Layout wrapper in wrong place | Wrap all routes in Layout component in App.tsx |
| Inconsistent colors | Define CSS variables and use throughout |
| Missing hover states | Add :hover styles for interactive elements |
| Poor contrast | Adjust color values for accessibility |
| Unstyled inputs | Apply global input reset and custom styles |
| No loading states | Add loading spinner/ skeleton components |

## CSS Variables Best Practices

```css
:root {
  /* Colors */
  --color-primary: #e91e63;
  --color-bg: #0f0f17;
  --color-bg-secondary: #1a1b2e;
  --color-text: #ffffff;
  --color-text-muted: #9ca3af;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  
  /* Border */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
}
```

## File Organization

```
frontend/
├── src/
│   ├── components/     # Reusable components (Layout, etc.)
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── types/          # TypeScript types
│   ├── App.tsx         # Root with routes
│   └── App.css         # Global styles & CSS variables
├── test/
│   ├── screenshots/    # Captured screenshots
│   ├── screenshot.ts  # Screenshot script
│   └── ...
└── playwright.config.ts
```

## Running the Workflow

```bash
# 1. Start dev server
npm run dev

# 2. Capture screenshots
npx tsx test/screenshot.ts

# 3. Analyze with AI (use mcp__MiniMax__understand_image)
# Submit each screenshot and parse the feedback

# 4. Implement fixes based on AI suggestions

# 5. Re-capture and verify
```

## Key Takeaways

1. **Iterative Process**: AI analysis reveals issues incrementally - don't try to fix everything at once
2. **Visual Verification**: Always capture screenshots after changes to verify
3. **Consistency Matters**: CSS variables ensure consistency across components
4. **Component Patterns**: Reusable components reduce duplication
5. **Human Review**: AI suggestions are guidance - validate with human judgment

## Troubleshooting

- **Playwright browser not found**: Use `channel: 'chrome'` to use system Chrome
- **Screenshots timing out**: Add `waitForLoadState('networkidle')` before capture
- **AI seeing old screenshots**: Ensure screenshot was re-captured after changes
- **Dev server not responding**: Check port 5173 is available, restart if needed
