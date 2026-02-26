# 复盘与计划数据接入完整方案

> 更新日期: 2026-02-26

---

## 一、数据需求总览

### 1.1 复盘数据需求

复盘是为了**判断当前市场周期、总结当日交易、制定明日计划**。

| 数据项 | 用途 | 优先级 | 数据来源 |
|--------|------|--------|----------|
| **涨停家数** | 判断市场情绪强度 | ⭐⭐⭐⭐⭐ | AkShare/开盘啦 |
| **跌停家数** | 判断市场亏钱效应 | ⭐⭐⭐⭐⭐ | AkShare/开盘啦 |
| **炸板数量** | 判断做多失败率 | ⭐⭐⭐⭐⭐ | 开盘啦(特色) |
| **炸板亏损幅度** | 炸板后平均亏损 | ⭐⭐⭐⭐ | 开盘啦(特色) |
| **最高板** | 判断龙头高度 | ⭐⭐⭐⭐⭐ | AkShare/开盘啦 |
| **昨日溢价** | 昨日涨停股今日表现 | ⭐⭐⭐⭐ | AkShare |
| **涨跌家数** | 判断大盘整体强弱 | ⭐⭐⭐⭐⭐ | AkShare |
| **成交额** | 判断市场活跃度 | ⭐⭐⭐⭐ | AkShare |
| **涨停列表** | 选股池 | ⭐⭐⭐⭐⭐ | AkShare |
| **首板列表** | 找新题材 | ⭐⭐⭐⭐ | AkShare |
| **连板列表** | 识别龙头 | ⭐⭐⭐⭐ | AkShare |
| **炸板列表** | 规避风险 | ⭐⭐⭐⭐ | 开盘啦(特色) |
| **热门板块** | 判断主线 | ⭐⭐⭐⭐⭐ | AkShare |
| **资金流向** | 判断主力方向 | ⭐⭐⭐⭐ | AkShare |
| **龙虎榜** | 跟庄操作 | ⭐⭐⭐⭐ | AkShare |
| **北向资金** | 判断外资态度 | ⭐⭐⭐ | AkShare |

### 1.2 计划数据需求

计划是为了**确定买什么、买多少、怎么买、怎么卖**。

| 数据项 | 用途 | 优先级 | 数据来源 |
|--------|------|--------|----------|
| **情绪周期判断** | 决定仓位 | ⭐⭐⭐⭐⭐ | 复盘数据汇总 |
| **目标板块** | 选股方向 | ⭐⭐⭐⭐⭐ | AI分析 |
| **目标个股** | 具体标的 | ⭐⭐⭐⭐⭐ | AI分析+人工确认 |
| **买入条件** | 触发条件 | ⭐⭐⭐⭐⭐ | 手动填写 |
| **止损价位** | 风控线 | ⭐⭐⭐⭐⭐ | 手动填写 |
| **止盈计划** | 卖出策略 | ⭐⭐⭐⭐⭐ | 手动填写 |
| **仓位建议** | 仓位控制 | ⭐⭐⭐⭐ | AI分析 |
| **风险提示** | 风险预警 | ⭐⭐⭐⭐ | AI分析 |

---

## 二、数据来源与接入方式

### 2.1 AkShare（推荐）

**官网**: https://akshare.akfamily.xyz/

**优点**:
- ✅ 完全免费
- ✅ 无需注册
- ✅ Python 直接调用
- ✅ 数据种类丰富

**缺点**:
- ⚠️ 数据可能有几分钟延迟
- ⚠️ 部分历史数据有限

**接入方式**:

```python
import akshare as ak

# 1. 涨跌停数据
ak.stock_zt_pool_em()           # 涨停池详情
ak.stock_zt_pool_sub_em()       # 炸板池
ak.stock_zt_pool_strong_em()    # 强势股池

# 2. 大盘数据
ak.index_stock_cons_csindex()    # 大盘涨跌家数
ak.index_zh_a_hist()            # 大盘历史数据

# 3. 板块数据
ak.stock_board_industry_name_em()    # 板块排行
ak.stock_board_industry_hist_em()   # 板块历史

# 4. 龙虎榜
ak.stock_lhb_detail_em()        # 龙虎榜详情
ak.stock_lhb_sub_em()           # 每日龙虎榜

# 5. 资金流向
ak.stock_fund_flow_main_em()    # 主力资金流向
ak.stock_fund_flow_industry()   # 行业资金流向

# 6. 北向资金
ak.stock_hk_gt_index()          # 北向资金流入
```

### 2.2 开盘啦（特色数据）

**优点**:
- ✅ 独有数据：炸板亏钱效应、短线精灵
- ✅ 界面直观

**缺点**:
- ❌ 无公开 API
- ❌ 需要 OCR 或手动

**替代方案**:
- 炸板数据可通过 AkShare 的 `stock_zt_pool_sub_em()` 近似获取
- 短线精灵暂无可替代数据源

### 2.3 Tushare（备选）

**官网**: https://tushare.pro/

**优点**:
- ✅ 数据全面稳定
- ✅ 支持历史数据

**缺点**:
- ⚠️ 需要注册获取 token
- ⚠️ 部分数据付费

---

## 三、数据库模型设计

### 3.1 现有模型（可复用）

```python
# external_data.py 中已有
class LimitData:          # 涨跌停数据
class SectorData:         # 板块数据
class DragonListData:     # 龙虎榜数据
class CapitalFlowData:    # 资金流向数据
class NorthMoneyData:     # 北向资金数据
```

### 3.2 需要新增的模型

```python
# ========== 情绪指标汇总 ==========
class SentimentIndex(SQLModel, table=True):
    """每日情绪指标汇总"""
    __tablename__ = "sentiment_indexes"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(unique=True, index=True)

    # 大盘数据
    up_count: Optional[int] = Field(default=0)      # 上涨家数
    down_count: Optional[int] = Field(default=0)    # 下跌家数
    total_amount: Optional[float] = Field(default=0) # 成交额(亿)

    # 涨跌停数据
    limit_up_count: Optional[int] = Field(default=0)     # 涨停家数
    limit_down_count: Optional[int] = Field(default=0)   # 跌停家数
    break_up_count: Optional[int] = Field(default=0)     # 炸板家数
    break_up_rate: Optional[float] = Field(default=0)    # 炸板率

    # 最高板
    highest_board: Optional[int] = Field(default=0)      # 最高连板数

    # 昨日溢价
    yesterday_premium: Optional[float] = Field(default=0) # 昨日涨停股今日溢价

    # 情绪周期（AI判断）
    cycle: Optional[str] = Field(default=None)           # 周期(冰点/启动/发酵/高潮/分歧/退潮)
    cycle_confidence: Optional[float] = Field(default=0)  # 判断置信度
    position_advice: Optional[str] = Field(default=None)  # 仓位建议

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ========== 重点板块 ==========
class HotSector(SQLModel, table=True):
    """每日重点板块"""
    __tablename__ = "hot_sectors"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True)
    sector_name: str = Field(index=True)

    change: Optional[float] = Field(default=0)       # 涨幅
    stock_count: Optional[int] = Field(default=0)    # 涨停家数
    net_inflow: Optional[float] = Field(default=0)    # 净流入
    strength: Optional[int] = Field(default=0)       # 强度评分

    created_at: datetime = Field(default_factory=datetime.now)


# ========== 重点个股 ==========
class HotStock(SQLModel, table=True):
    """每日重点关注个股"""
    __tablename__ = "hot_stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True)

    code: str = Field(index=True)
    name: str

    # 基本信息
    sector: Optional[str] = Field(default=None)       # 所属板块
    market_cap: Optional[float] = Field(default=0)   # 流通市值

    # 涨停信息
    limit_up_time: Optional[str] = Field(default=None) # 涨停时间
    limit_up_type: Optional[str] = Field(default=None) # 涨停类型(首板/2连板/...)
    continue_board: Optional[int] = Field(default=0)   # 连续涨停数

    # 资金信息
    net_inflow: Optional[float] = Field(default=0)   # 主力净流入
    lhb_buy: Optional[float] = Field(default=0)      # 龙虎榜买入

    # 关注原因
    focus_reason: Optional[str] = Field(default=None)  # 关注理由

    # 优先级
    priority: Optional[int] = Field(default=0)        # 优先级(1-5)

    created_at: datetime = Field(default_factory=datetime.now)
```

---

## 四、API 接口设计

### 4.1 数据同步接口

```
POST /api/sync/sentiment      # 同步每日情绪指标
POST /api/sync/hot-sectors    # 同步热点板块
POST /api/sync/hot-stocks      # 同步热点个股
POST /api/sync/daily-summary   # 同步每日汇总(一键同步)
```

### 4.2 数据查询接口

```
GET /api/market/sentiment/{date}     # 获取情绪指标
GET /api/market/sentiment/latest     # 获取最新情绪指标
GET /api/market/hot-sectors          # 获取热点板块
GET /api/market/hot-stocks           # 获取热点个股
GET /api/market/cycle-analysis       # 获取周期分析
```

### 4.3 智能分析接口

```
GET /api/ai/cycle-judge          # AI判断情绪周期
GET /api/ai/position-advice     # AI仓位建议
GET /api/ai/target-sectors       # AI推荐板块
GET /api/ai/target-stocks        # AI推荐个股
```

---

## 五、数据接入流程

### 5.1 每日收盘后数据同步流程

```
┌─────────────────────────────────────────────────────────┐
│  15:00 收盘后                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1: 获取基础行情数据                               │
│  - 调用 AkShare 接口获取涨跌停、板块、资金等            │
│  - 存储到对应数据表                                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: 计算情绪指标                                   │
│  - 汇总涨停家数、炸板率、最高板等                       │
│  - 存储到 sentiment_indexes 表                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: 筛选热点板块和个股                            │
│  - 按涨幅、涨停数、资金流入排序                         │
│  - 存储到 hot_sectors 和 hot_stocks 表                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: AI 周期判断                                   │
│  - 基于情绪指标判断周期                                 │
│  - 生成仓位建议                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  完成: 复盘页面可查看当日数据                          │
└─────────────────────────────────────────────────────────┘
```

### 5.2 定时任务配置

建议配置定时任务（每日 15:30 执行）:

```python
# celery 任务示例
@app.task
def sync_daily_data():
    """每日数据同步"""
    # 1. 同步涨跌停数据
    sync_limit_data()

    # 2. 同步板块数据
    sync_sector_data()

    # 3. 同步资金流向
    sync_capital_flow()

    # 4. 同步龙虎榜
    sync_dragon_list()

    # 5. 计算情绪指标
    calc_sentiment_index()

    # 6. 筛选热点
    calc_hot_sectors()
    calc_hot_stocks()
```

---

## 六、前端数据展示

### 6.1 复盘页面数据流

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  后端API     │────▶│  复盘页面    │────▶│  用户查看   │
│  /api/market │     │  Review.tsx  │     │  填写复盘   │
└──────────────┘     └──────────────┘     └──────────────┘
      │                    │
      │                    ▼
      │            ┌──────────────┐
      └───────────▶│  自动填充   │
                   │  表单数据   │
                   └──────────────┘
```

### 6.2 需要在前端展示的数据

| 页面位置 | 展示数据 |
|----------|----------|
| 情绪指标 | 涨停家数、跌停家数、炸板率、最高板、昨日溢价 |
| 周期判断 | 当前周期、仓位建议 |
| 涨停板分析 | 涨停列表（可按时间/市值排序） |
| 炸板分析 | 炸板列表、炸板原因 |
| 板块分析 | 热点板块、资金流向 |
| 龙虎榜 | 机构/游资买入、合力股 |

---

## 七、实施计划

### Phase 1: 基础数据接入（1-2天）

- [ ] 新增 SentimentIndex 数据模型
- [ ] 新增 HotSector 数据模型
- [ ] 新增 HotStock 数据模型
- [ ] 实现 AkShare 数据同步
- [ ] 创建数据同步 API

### Phase 2: 前端展示（1-2天）

- [ ] 修改复盘页面，调用 API 获取数据
- [ ] 自动填充部分表单数据
- [ ] 展示热点板块和个股

### Phase 3: AI 智能分析（2-3天）

- [ ] 实现情绪周期判断算法
- [ ] 实现仓位建议生成
- [ ] 实现目标板块/个股推荐

### Phase 4: 定时任务（1天）

- [ ] 配置每日定时同步任务
- [ ] 添加数据校验和监控

---

## 八、总结

| 数据类型 | 来源 | 优先级 | 状态 |
|----------|------|--------|------|
| 涨跌停数据 | AkShare | ⭐⭐⭐⭐⭐ | 待实现 |
| 板块数据 | AkShare | ⭐⭐⭐⭐⭐ | 待实现 |
| 资金流向 | AkShare | ⭐⭐⭐⭐ | 待实现 |
| 龙虎榜 | AkShare | ⭐⭐⭐⭐ | 待实现 |
| 北向资金 | AkShare | ⭐⭐⭐ | 待实现 |
| 炸板详细 | 开盘啦/手动 | ⭐⭐⭐⭐ | 待补充 |
| 情绪周期 | AI分析 | ⭐⭐⭐⭐⭐ | 待实现 |
| 仓位建议 | AI分析 | ⭐⭐⭐⭐⭐ | 待实现 |

**核心思路**: 优先使用 AkShare 满足大部分数据需求，复盘页面先展示基础数据，后期逐步增加 AI 智能分析能力。

---

*文档创建时间: 2026-02-26*
