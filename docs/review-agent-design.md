# 游资复盘 LLM Agent 设计方案

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     游资复盘 Agent 迭代流程                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                              │
│   │  1. 启动   │                                              │
│   └──────┬──────┘                                              │
│          ↓                                                      │
│   ┌─────────────┐    数据有问题？    ┌─────────────┐           │
│   │ 2. 获取数据 │ ──────────────>  │  重新获取   │           │
│   └──────┬──────┘   ←否           └──────┬──────┘           │
│          ↓                                │                     │
│   ┌─────────────┐    缺新闻？       ┌─────────────┐           │
│   │  3. 初步分析 │ ──────────────>  │  查询新闻   │           │
│   └──────┬──────┘   ←否           └──────┬──────┘           │
│          ↓                                │                     │
│   ┌─────────────┐    需要更多数据？  ┌─────────────┐           │
│   │  4. 深度分析 │ ──────────────>  │ 补充数据   │           │
│   └──────┬──────┘   ←否           └──────┬──────┘           │
│          ↓                                │                     │
│   ┌─────────────┐                                              │
│   │  5. 输出报告│                                              │
│   └─────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 二、核心概念

### Agent 模式：ReAct (Reasoning + Acting)
- **Reasoning**: LLM 根据当前状态进行分析
- **Acting**: 根据分析结果决定下一步行动
- **迭代**: 循环执行直到分析完成

### 关键特征
1. **按需获取数据**: 不是一次性获取所有数据，而是按需获取
2. **自动发现缺失**: 发现缺少新闻/数据时主动补充
3. **错误处理**: 发现数据问题时主动重试
4. **逐步深入**: 从概览到细节，层层深入

## 三、状态机设计

### AgentState 枚举
```python
class AgentState(Enum):
    IDLE = "idle"                    # 空闲
    FETCHING_DATA = "fetching_data"  # 获取数据中
    ANALYZING = "analyzing"          # 分析中
    FETCHING_NEWS = "fetching_news"  # 获取新闻中
    FETCHING_MORE_DATA = "fetching_more_data"  # 获取更多数据中
    COMPLETED = "completed"          # 完成
    ERROR = "error"                  # 错误
```

### 决策动作
```python
class Action(Enum):
    complete = "complete"           # 分析完成，输出报告
    fetch_news = "fetch_news"       # 需要查询新闻
    fetch_more_data = "fetch_more_data"  # 需要更多数据
    retry = "retry"                # 数据有问题，重新获取
```

## 四、数据结构

### ReviewContext（复盘上下文）
```python
class ReviewContext(BaseModel):
    date: str                               # 复盘日期
    steps: List[ReviewStep] = []           # 执行步骤记录

    # 收集的数据
    market_emotion: Optional[dict] = None  # 市场情绪
    zt_pool: Optional[List[dict]] = None   # 涨停板
    dtgc: Optional[List[dict]] = None      # 跌停板
    zbgc: Optional[List[dict]] = None     # 炸板股
    fund_flow: Optional[dict] = None       # 资金流向
    lhb: Optional[List[dict]] = None      # 龙虎榜
    margin: Optional[dict] = None         # 两融数据
    sectors: Optional[List[dict]] = None  # 板块数据
    news: Optional[List[dict]] = None     # 新闻数据

    # 分析结果
    analysis: Optional[dict] = None
    final_report: Optional[str] = None
```

### ReviewStep（执行步骤）
```python
class ReviewStep(BaseModel):
    step: int               # 步骤序号
    state: AgentState       # 当前状态
    action: str            # 执行的动作
    result: str           # 执行结果
    data_used: List[str]  # 使用了哪些数据
    next_action: Optional[str] = None  # 下一步建议
```

## 五、迭代决策 Prompt

### DECISION_PROMPT
```
## 当前分析状态
已完成的数据收集：
{completed_data}

当前分析进度：
{analysis_progress}

## 你的任务
根据当前的分析进度，决定下一步行动。

## 可选行动
1. **complete** - 分析已完成，可以输出报告
2. **fetch_news** - 需要查询新闻，补充市场情绪/板块动量信息
3. **fetch_more_data** - 需要更多数据（如具体个股详情、板块资金流等）
4. **retry** - 当前数据有问题，需要重新获取

## 输出格式
{
  "action": "complete/fetch_news/fetch_more_data/retry",
  "reason": "为什么做这个决定",
  "params": {
    // 需要的具体数据或参数
  },
  "analysis_update": "当前分析结论的更新"
}
```

## 六、迭代示例

### 第一次迭代
- **获取数据**: 市场情绪、涨停板、炸板、两融
- **分析**: "涨停92只，跌停1只，情绪较强。电力板块涨停较多，需要确认是否有政策/新闻驱动。"
- **决策**: fetch_news（需要确认电力板块驱动因素）

### 第二次迭代
- **获取新闻**: "电力板块受益于能源政策"
- **分析**: "政策驱动 + 业绩预期 + 资金涌入 = 电力是主线。炸板率17%较高，需要看具体炸板股分布。"
- **决策**: fetch_more_data（需要炸板股详情）

### 第三次迭代
- **获取炸板详情**: 云天励飞炸14次，沃尔德13次
- **分析**: "AI股炸板率高，是被动炸板而非情绪崩溃。电力板块良性，炸板主要是跟风小票。结论：市场健康，可看多。"
- **决策**: complete（分析完成）

## 七、工具层设计

### MCP 服务配置

#### 1. AKShare MCP
```json
// 已配置的 MCP 服务
{
  "akshare": {
    "command": "python3",
    "args": ["/Users/lianwu/ai/mcp/mcp_akshare/run.py"]
  }
}
```

#### 2. MiniMax MCP
```json
{
  "MiniMax": {
    "command": "uvx",
    "args": ["minimax-coding-plan-mcp", "-y"],
    "env": {
      "MINIMAX_API_HOST": "https://api.minimaxi.com",
      "MINIMAX_API_KEY": "sk-cp-***"
    }
  }
}
```

### 数据获取工具（使用 AKShare MCP）

| 工具函数 | MCP 调用 | 说明 |
|----------|----------|------|
| `get_market_emotion()` | `ak_call("stock_em_market_activity", {})` | 市场情绪 |
| `get_zt_pool(date)` | `ak_call("stock_zt_pool_em", {"date": date})` | 涨停板 |
| `get_dtgc(date)` | `ak_call("stock_zt_pool_dtgc_em", {"date": date})` | 跌停板 |
| `get_zbgc(date)` | `ak_call("stock_zt_pool_zbgc_em", {"date": date})` | 炸板股 |
| `get_fund_flow()` | `ak_call("stock_fund_flow_em", {})` | 资金流向 |
| `get_lhb_detail(date)` | `ak_call("stock_lhb_detail_em", {"start_date": date, "end_date": date})` | 龙虎榜详情 |
| `get_margin(date)` | `ak_call("margin_sse", {"start_date": date, "end_date": date})` | 两融数据 |
| `get_sectors()` | `ak_call("stock_fund_flow_rank_em", {"indicator": "今日", "sector_type": "行业资金流"})` | 板块资金流 |

### 新闻获取工具（使用 MiniMax MCP）

| 工具函数 | MCP 调用 | 说明 |
|----------|----------|------|
| `search_news(keywords, date)` | `web_search(query)` | 搜索相关新闻 |
| `get_market_news(date)` | `web_search(query)` | 获取市场新闻 |

### Agent 内部工具封装

```python
class MCPTools:
    """MCP 工具封装"""

    def __init__(self, akshare_mcp, minimax_mcp):
        self.akshare = akshare_mcp
        self.minimax = minimax_mcp

    async def get_market_emotion(self) -> dict:
        """获取市场情绪"""
        result = await self.akshare.ak_call(
            "stock_em_market_activity",
            "{}"
        )
        return json.loads(result)

    async def get_zt_pool(self, date: str) -> List[dict]:
        """获取涨停板"""
        result = await self.akshare.ak_call(
            "stock_zt_pool_em",
            json.dumps({"date": date})
        )
        return json.loads(result)

    async def search_news(self, keywords: List[str], date: str) -> List[dict]:
        """搜索新闻"""
        query = " ".join(keywords) + " " + date + " 股市 财经"
        result = await self.minimax.web_search({
            "query": query,
            "max_results": 10
        })
        return result
```

## 八、API 接口设计

### POST /api/review/analyze
```json
// Request
{
  "date": "2026-02-27",    // 可选，默认今天
  "max_iterations": 15     // 可选，最大迭代次数（默认15）
}

// Response
{
  "code": 0,
  "msg": "success",
  "data": {
    "date": "2026-02-27",
    "iterations_used": 3,
    "steps": [
      {
        "step": 1,
        "state": "fetching_data",
        "action": "获取基础数据",
        "result": "成功获取6项数据"
      },
      {
        "step": 2,
        "state": "fetching_news",
        "action": "获取新闻",
        "result": "获取到5条相关新闻"
      },
      {
        "step": 3,
        "state": "analyzing",
        "action": "分析+决策",
        "result": "分析完成"
      }
    ],
    "analysis": {
      "emotion_score": 4.5,
      "direction": "看多",
      "position": 70,
      "hot_sectors": ["电力", "小金属"],
      "risks": ["炸板率偏高"]
    },
    "final_report": "## 游资复盘分析报告\n\n**日期**: 2026-02-27\n\n..."
  }
}
```

### GET /api/review/history
获取历史复盘记录

### POST /api/review/compare
与历史相似日期对比

## 九、代码结构

```
backend/app/agents/
├── __init__.py
├── review_agent.py        # 主 Agent 类（迭代循环 + 状态机）
├── config.py              # MCP 配置
├── tools/
│   ├── __init__.py
│   ├── mcp_client.py     # MCP 客户端封装
│   ├── akshare_tool.py   # AKShare 数据获取工具
│   └── news_tool.py      # 新闻获取工具
├── prompts/
│   ├── __init__.py
│   ├── system_prompt.py  # 系统提示词
│   ├── decision_prompt.py # 决策提示词
│   └── report_prompt.py  # 报告生成提示词
└── models.py             # 数据模型
```

### MCP 客户端封装

```python
# tools/mcp_client.py
from mcp import ClientSession, StdioServerParameters

class MCPClient:
    """MCP 客户端"""

    def __init__(self):
        self.akshare_server = StdioServerParameters(
            command="python3",
            args=["/Users/lianwu/ai/mcp/mcp_akshare/run.py"]
        )
        self.minimax_server = StdioServerParameters(
            command="uvx",
            args=["minimax-coding-plan-mcp", "-y"],
            env={
                "MINIMAX_API_HOST": "https://api.minimaxi.com",
                "MINIMAX_API_KEY": os.getenv("MINIMAX_API_KEY")
            }
        )

    async def call_akshare(self, function: str, params: dict) -> Any:
        """调用 AKShare MCP"""
        async with ClientSession(self.akshare_server) as session:
            await session.initialize()
            result = await session.call_tool("ak_call", {
                "function": function,
                "params": json.dumps(params)
            })
            return result

    async def search_news(self, query: str, max_results: int = 10) -> Any:
        """调用 MiniMax MCP 搜索新闻"""
        async with ClientSession(self.minimax_server) as session:
            await session.initialize()
            result = await session.call_tool("web_search", {
                "query": query,
                "max_results": max_results
            })
            return result
```

## 十、LLM 选择

| 模型 | 用途 | 特点 |
|------|------|------|
| Claude 4 Sonnet | 主力分析 | 中文好，理解力强 |
| GPT-4o mini | 快速分析 | 便宜快速 |

## 十一、关键决策（已确认）

| 决策项 | 方案 | 说明 |
|--------|------|------|
| 数据获取失败 | 超过3次则跳过 | 避免无限重试 |
| 迭代终止条件 | LLM 自行判断 | 由 LLM 决定何时完成 |
| 迭代绝对上限 | 15次 | 防止无限循环 |
| 新闻来源 | MiniMax MCP | 使用 MiniMax 的 MCP 服务 |
| 缓存策略 | 暂不需要 | 简化实现 |
| 输出格式 | Markdown | 人类可读的报告格式 |

## 十二、重试机制设计

```python
class RetryConfig:
    """重试配置"""
    MAX_RETRIES = 3           # 最大重试次数
    MAX_ITERATIONS = 15       # 迭代绝对上限
    RETRY_DELAY = 1           # 重试间隔（秒）
    RETRY_ON_ERRORS = [
        "Connection aborted",
        "RemoteDisconnected",
        "timeout",
        "Internal Server Error"
    ]

async def fetch_with_retry(fetch_func, *args, **kwargs):
    """带重试的数据获取"""
    retry_count = 0
    last_error = None

    while retry_count < RetryConfig.MAX_RETRIES:
        try:
            result = await fetch_func(*args, **kwargs)
            # 检查结果是否有效
            if result is not None and result != []:
                return result
            retry_count += 1
            last_error = "Empty result"
        except Exception as e:
            retry_count += 1
            last_error = str(e)

        if retry_count < RetryConfig.MAX_RETRIES:
            await asyncio.sleep(RetryConfig.RETRY_DELAY)

    # 超过3次失败，返回 None 或空值，让 LLM 处理
    return None
```

## 十三、迭代终止判断

```python
# LLM 决策时，自行判断是否可以完成
DECISION_PROMPT = """
## 迭代终止条件
你（Llm）需要自行判断当前分析是否足够完成报告。

判断标准：
1. 核心数据已获取（市场情绪、涨跌停）
2. 关键问题已解答
3. 不需要更多数据/新闻补充

如果满足以下条件，选择 **complete**：
- 已明确市场情绪判断
- 已识别主线板块
- 已完成风险评估
- 已给出策略建议

否则继续 **fetch_news** 或 **fetch_more_data**
"""
```

## 十四、新闻获取（MiniMax MCP）

### MiniMax MCP 配置
```json
{
  "MiniMax": {
    "command": "uvx",
    "args": ["minimax-coding-plan-mcp", "-y"],
    "env": {
      "MINIMAX_API_HOST": "https://api.minimaxi.com",
      "MINIMAX_API_KEY": "sk-cp-***"  // 实际使用时从环境变量获取
    }
  }
}
```

### 使用方式
```python
from mcp import ClientSession, StdioServerParameters

class NewsService:
    """新闻服务 - 使用 MiniMax MCP"""

    def __init__(self):
        self.server_params = StdioServerParameters(
            command="uvx",
            args=["minimax-coding-plan-mcp", "-y"],
            env={
                "MINIMAX_API_HOST": os.getenv("MINIMAX_API_HOST"),
                "MINIMAX_API_KEY": os.getenv("MINIMAX_API_KEY")
            }
        )

    async def search_news(self, keywords: List[str], date: str) -> List[dict]:
        """使用 MiniMax MCP 搜索新闻"""
        async with ClientSession(self.server_params) as session:
            await session.initialize()
            result = await session.call_tool(
                "web_search",
                {
                    "query": f"{keywords} {date} 股市 财经 政策",
                    "max_results": 10
                }
            )
            return result

    async def get_market_news(self, date: str) -> dict:
        """获取市场新闻"""
        return await self.search_news(["A股", "收盘", "政策"], date)
```

### MCP 工具清单
| 工具 | 功能 |
|------|------|
| web_search | 网页搜索 |
| web_fetch | 网页内容抓取 |
| ... | ... |

## 十五、数据获取失败处理流程

```
┌─────────────────────────────────────────────────────┐
│              数据获取失败处理流程                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  获取数据                                           │
│     │                                              │
│     ▼                                              │
│  成功？ ──是──> 存入 Context，继续                  │
│     │                                              │
│     否                                              │
│     ▼                                              │
│  重试计数 +1                                       │
│     │                                              │
│     ▼                                              │
│  超过3次？ ──是──> 标记为空，继续（不阻塞）         │
│     │                                              │
│     否                                              │
│     ▼                                              │
│  等待1秒，重试                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 十六、输出格式（Markdown）

### 报告模板
```markdown
# 游资复盘分析报告

**日期**: {date}
**分析时间**: {analysis_time}

---

## 一、盘面概览

| 指标 | 数值 | 解读 |
|------|------|------|
| 上涨 | {up_count}家 | {up_ratio} |
| 下跌 | {down_count}家 | |
| 涨停 | {zt_count}只 | |
| 跌停 | {dt_count}只 | |
| 炸板 | {zbgc_count}只 | 炸板率{zbgc_rate}% |
| 活跃度 | {activity}% | |

**情绪评分**: {emotion_score}/5 分

---

## 二、热点板块

### 主线板块
| 板块 | 涨停数 | 龙头股 |
|------|--------|--------|
| {sector1} | {count1} | {leader1} |
| {sector2} | {count2} | {leader2} |

### 支线板块
- {sector3}: {count3}只
- {sector4}: {count4}只

---

## 三、资金流向

- 融资余额: {margin_balance}亿
- 融资买入: {margin_buy}亿
- 趋势: {margin_trend}

---

## 四、风险预警

{risks}

---

## 五、明日策略

| 项目 | 建议 |
|------|------|
| 方向 | {direction} |
| 仓位 | {position}% |
| 关注方向 | {focus_sectors} |
| 关注标的 | {focus_stocks} |

---

## 六、分析步骤

{analysis_steps}

---

*本报告由 AI 自动生成，仅供参考，不构成投资建议。*
```

## 十七、开发计划

### Phase 1: MCP 工具封装
- [ ] 实现 MCP 客户端封装（akshare + minimax）
- [ ] 测试 MCP 调用连通性
- [ ] 封装数据获取工具函数
- [ ] 封装新闻获取工具函数

### Phase 2: Agent 核心框架
- [ ] 实现状态机
- [ ] 实现迭代循环
- [ ] 实现决策 Prompt
- [ ] 实现重试机制（3次跳过）

### Phase 3: LLM 集成
- [ ] 接入 MiniMax MCP
- [ ] 实现分析 Prompt
- [ ] 实现报告生成（Markdown）

### Phase 4: 调试
- [ ] 端到端测试
- [ ] 错误处理优化
- [ ] 性能优化
