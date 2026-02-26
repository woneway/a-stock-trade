import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import './Simplified.css';

interface PlanData {
  // 仓位计划
  marketCycle: string;
  positionPlan: string;
  positionLogic: string;

  // 标的计划
  targetStocks: string;
  targetPriority: string;
  targetLogic: string;

  // 买入条件
  entryCondition: string;
  entryTemplate: string;
  entryLogic: string;

  // 止损止盈
  stopLoss: string;
  takeProfit: string;
  exitLogic: string;
}

const DEFAULT_VALUES = {
  // 仓位计划
  marketCycle: '',
  positionPlan: '',
  positionLogic: `【为什么做】
不同周期赚钱难度不同，仓位也要不同。
- 情绪好（启动/发酵/高潮）：市场好赚钱容易，重仓
- 情绪差（分歧/退潮/冰点）：市场差赚钱难，轻仓/空仓

【仓位参考表】
| 周期 | 仓位 | 说明 |
|------|------|------|
| 启动 | 5-7成 | 试错 |
| 发酵 | 7-9成 | 积极参与 |
| 高潮 | 8-10成 | 持股待涨 |
| 分歧 | 3-5成 | 谨慎 |
| 退潮 | 0-2成 | 空仓休息 |
| 冰点 | 0成 | 等待 |

【核心原则】
计划你的交易，交易你的计划。
没有计划 = 临盘冲动 = 大概率亏钱`,

  // 标的计划
  targetStocks: `【目标股票】（按优先级排序）
1. 代码    名称    仓位    关注理由
2.
3.
4.`,
  targetPriority: `【优先级理由】
1.
2.
3.`,
  targetLogic: `【为什么做】
只做计划内的交易，不做计划外的操作。
- 计划内：有逻辑支撑，买卖有依据
- 计划外：冲动交易，大概率亏钱

【筛选原则】
- 龙头优先：选择板块内地位最高的股票
- 形态优先：选择技术形态好的股票（突破新高、放量）
- 资金优先：选择有资金关注的股票（龙虎榜、资金流向）
- 股性优先：选择股性活跃、成交额大的股票`,

  // 买入条件
  entryCondition: `【买入条件】（满足全部条件才买）
1. 竞价高开 ___% 以上
2. 竞价量能 ___ 万手以上
3. 大盘环境：___（好/一般/差）
4. 板块配合：有板块效应
5. 题材配合：有新题材/政策

【触发条件】
- □ 分时均价线上方横盘突破
- □ 直线拉升3%以上且封板
- □ 回调到均线支撑企稳
- □ 大单抢筹且量价配合
- □ 板块龙头率先涨停`,
  entryTemplate: `【买入条件模板】（可复制使用）
- 分时均价线上方横盘突破：价格在均价线上方横盘，突然放量突破
- 直线拉升3%以上且封板：强势股直线拉升，快速封板
- 回调到均线支撑企稳：回调到重要均线（如5日线）企稳回升
- 大单抢筹且量价配合：出现大单买入，量价齐升
- 板块龙头率先涨停：板块内龙头股率先涨停，带动板块
- 弱转强：竞价低开高走，突破分时可买`,
  entryLogic: `【为什么做】
模糊的买入条件 = 没有条件
- 「涨幅大了就买」→ 涨多少算大？
- 「感觉好了就买」→ 什么时候算好？

【明确条件的好处】
- 符合就买，不符合就不买
- 避免临时起意冲动交易
- 交易有纪律，亏钱也有数

【买入时机参考】
- 龙头首次分歧：龙头第一次炸板/回落，可低吸
- 龙头加速：涨停突破/封板，可板上确认
- 跟风启动：跟风股直线拉升，立即买入
- 板块爆发：板块批量涨停，选最强买
- 弱转强：竞价低开高走，突破分时可买`,

  // 止损止盈
  stopLoss: '-5%',
  takeProfit: `【止盈计划】
第一目标：+8% → 减仓1/3
第二目标：+15% → 再减1/3
第三目标：+20%+ → 剩1/3博取更大利润

【卖出时机】
- 触及止盈点 → 分批卖出
- 出现滞涨信号 → 卖出
- 跌破5日线 → 减半仓
- 大盘急跌-2%以上 → 卖出`,
  exitLogic: `【为什么做】
数学原理：亏50%需要赚100%才能回本
- 亏5%：赚5.26%回本
- 亏10%：赚11.11%回本
- 亏20%：赚25%回本
- 亏50%：赚100%回本

【风控原则】
- 止损要坚决：触及止损线必须无条件止损，不能犹豫
- 止盈要分批：分批止盈，不要一次性卖完
- 保护利润：盈利后移动止损到成本价上方
- 仓位控制：单只股票不超过3成仓，分散风险
- 不做计划外：严格按照计划执行，不临时起意

【十二字真言】
1. 资金在哪我在哪
2. 情绪好我就做
3. 情绪差我就走
4. 错了就止损`,
};

export default function SimplifiedPlan() {
  const navigate = useNavigate();
  const [data, setPlanData] = useState<PlanData>({
    marketCycle: '',
    positionPlan: '',
    positionLogic: DEFAULT_VALUES.positionLogic,
    targetStocks: DEFAULT_VALUES.targetStocks,
    targetPriority: DEFAULT_VALUES.targetPriority,
    targetLogic: DEFAULT_VALUES.targetLogic,
    entryCondition: DEFAULT_VALUES.entryCondition,
    entryTemplate: DEFAULT_VALUES.entryTemplate,
    entryLogic: DEFAULT_VALUES.entryLogic,
    stopLoss: DEFAULT_VALUES.stopLoss,
    takeProfit: DEFAULT_VALUES.takeProfit,
    exitLogic: DEFAULT_VALUES.exitLogic,
  });

  const [activeStep, setActiveStep] = useState(1);
  const [saved, setSaved] = useState(false);

  const today = dayjs().format('YYYY-MM-DD');

  // 加载今日保存的数据
  useEffect(() => {
    const savedData = localStorage.getItem(`simplified-plan-${today}`);
    if (savedData) {
      try {
        setPlanData(JSON.parse(savedData));
      } catch (e) {
        console.error('加载保存数据失败', e);
      }
    }
  }, [today]);

  const updateField = (field: keyof PlanData, value: string) => {
    setPlanData(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    // 保存到 localStorage
    localStorage.setItem(`simplified-plan-${today}`, JSON.stringify(data));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);

    // 目标日期是明天
    const targetDate = dayjs().add(1, 'day').format('YYYY-MM-DD');

    // 保存到数据库
    try {
      const historyRes = await axios.get('/api/plan/history', {
        params: { start_date: today, end_date: today }
      });

      const existingHistory = historyRes.data?.[0];

      if (existingHistory) {
        await axios.put(`/api/plan/history/${existingHistory.id}`, {
          trade_date: today,
          market_cycle: data.marketCycle,
          position_plan: data.positionPlan,
          status: 'confirmed'
        });
      } else {
        await axios.post('/api/plan/history', {
          trade_date: today,
          market_cycle: data.marketCycle,
          position_plan: data.positionPlan,
          status: 'confirmed'
        });
      }
    } catch (err) {
      console.error('保存到数据库失败:', err);
    }
  };

  const handleGoToTodayPlan = async () => {
    // 先保存当前计划
    await handleSave();

    // 创建或获取今日计划（使用今天的日期）
    try {
      const todayStr = dayjs().format('YYYY-MM-DD');

      // 尝试获取今日计划
      const existingPlan = await axios.get('/api/plan/pre', {
        params: { trade_date: todayStr }
      });

      if (existingPlan.data && existingPlan.data.id) {
        // 计划已存在，更新它
        await axios.put(`/api/plan/pre/${existingPlan.data.id}`, {
          sentiment: data.marketCycle,
          position_size: data.positionPlan || '5',
          selected_strategy: data.marketCycle,
        });
      } else {
        // 如果不存在，创建一个新的今日计划
        await axios.post('/api/plan/pre', {
          plan_date: todayStr,
          trade_date: todayStr,
          selected_strategy: data.marketCycle,
          sentiment: data.marketCycle,
          position_size: data.positionPlan || '5',
          status: 'draft'
        });
      }
    } catch (err) {
      console.error('创建今日计划失败:', err);
    }

    // 跳转到今日计划
    navigate('/today');
  };

  const handleExport = () => {
    const content = `# 交易计划 - ${today}

## 一、仓位计划

### 做什么（任务）
- 情绪周期：${data.marketCycle}
- 仓位建议：${data.positionPlan}成

### 为什么做（逻辑）
${data.positionLogic}

---

## 二、标的计划

### 做什么（任务）
${data.targetStocks}

### 为什么做（逻辑）
${data.targetLogic}

### 优先级理由
${data.targetPriority}

---

## 三、买入条件

### 做什么（任务）
${data.entryCondition}

### 为什么做（逻辑）
${data.entryLogic}

### 参考模板
${data.entryTemplate}

---

## 四、止损止盈

### 做什么（任务）
- 止损线：${data.stopLoss}
- 止盈计划：${data.takeProfit}

### 为什么做（逻辑）
${data.exitLogic}
    `.trim();

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `交易计划-${today}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getPositionAdvice = (cycle: string): string => {
    const adviceMap: Record<string, string> = {
      '冰点': '0成',
      '启动': '5-7成',
      '发酵': '7-9成',
      '分歧': '3-5成',
      '高潮': '8-10成',
      '退潮': '0-2成',
    };
    return adviceMap[cycle] || '';
  };

  const getCycleFromStorage = () => {
    const savedReview = localStorage.getItem(`simplified-review-${today}`);
    if (savedReview) {
      try {
        const reviewData = JSON.parse(savedReview);
        return reviewData.marketCycle || '';
      } catch (e) {
        return '';
      }
    }
    return '';
  };

  // 自动从复盘获取周期
  useEffect(() => {
    if (!data.marketCycle) {
      const cycle = getCycleFromStorage();
      if (cycle) {
        updateField('marketCycle', cycle);
        updateField('positionPlan', getPositionAdvice(cycle));
      }
    }
  }, [today]);

  const steps = [
    { num: 1, title: '仓位计划', icon: '📊', desc: '根据情绪周期决定仓位' },
    { num: 2, title: '标的计划', icon: '🎯', desc: '确定目标股票' },
    { num: 3, title: '买入条件', icon: '✅', desc: '明确触发条件' },
    { num: 4, title: '止损止盈', icon: '🛡️', desc: '设定风控线' },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>简化计划</h1>
          <span className="date">{today} {dayjs().format('dddd')}</span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-outline" onClick={handleExport}>
            导出 Markdown
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            {saved ? '已保存 ✓' : '保存'}
          </button>
          <button className="btn btn-primary" onClick={handleGoToTodayPlan}>
            开始执行 →
          </button>
        </div>
      </div>

      {/* 步骤导航 */}
      <div className="steps-nav">
        {steps.map(step => (
          <button
            key={step.num}
            className={`step-btn ${activeStep === step.num ? 'active' : ''}`}
            onClick={() => setActiveStep(step.num)}
          >
            <span className="step-icon">{step.icon}</span>
            <span className="step-num">{step.num}</span>
            <span className="step-title">{step.title}</span>
          </button>
        ))}
      </div>

      {/* 步骤内容 */}
      <div className="step-content">
        {activeStep === 1 && (
          <div className="step-panel">
            {/* 做什么 */}
            <div className="card-section whattodo">
              <div className="card-header">
                <span className="card-tag">做什么</span>
                <h3>根据情绪周期决定仓位</h3>
              </div>
              <div className="quick-inputs">
                <div className="quick-input">
                  <label>今日情绪周期</label>
                  <select
                    value={data.marketCycle}
                    onChange={(e) => {
                      updateField('marketCycle', e.target.value);
                      updateField('positionPlan', getPositionAdvice(e.target.value));
                    }}
                  >
                    <option value="">选择周期（来自复盘）</option>
                    <option value="冰点">冰点</option>
                    <option value="启动">启动</option>
                    <option value="发酵">发酵</option>
                    <option value="分歧">分歧</option>
                    <option value="高潮">高潮</option>
                    <option value="退潮">退潮</option>
                  </select>
                </div>
                <div className="quick-input">
                  <label>建议仓位</label>
                  <input
                    type="text"
                    value={data.positionPlan}
                    onChange={(e) => updateField('positionPlan', e.target.value)}
                    placeholder="如: 5-8成"
                  />
                  <span className="unit">成</span>
                </div>
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>不同周期赚钱难度不同，仓位也要不同</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>情绪好（启动/发酵/高潮）重仓，情绪差（分歧/退潮/冰点）轻仓</p>
                <p className="formula"><strong>情绪好 → 重仓 → 多赚钱<br/>情绪差 → 轻仓 → 少亏钱</strong></p>
                <div className="cycle-table">
                  <table>
                    <thead>
                      <tr>
                        <th>周期</th>
                        <th>仓位</th>
                        <th>说明</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>启动</td><td>5-7成</td><td>试错龙头</td></tr>
                      <tr><td>发酵</td><td>7-9成</td><td>积极参与</td></tr>
                      <tr><td>高潮</td><td>8-10成</td><td>持股待涨</td></tr>
                      <tr><td>分歧</td><td>3-5成</td><td>谨慎追高</td></tr>
                      <tr><td>退潮</td><td>0-2成</td><td>空仓休息</td></tr>
                      <tr><td>冰点</td><td>0成</td><td>等待</td></tr>
                    </tbody>
                  </table>
                </div>
                <p className="highlight"><strong>十二字真言：资金在哪我在哪，情绪好我就做，情绪差我就走</strong></p>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>高潮8-10成，退潮0-2成</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>先完成今日复盘，获取情绪周期判断</li>
                  <li>根据周期选择对应仓位</li>
                  <li>记录仓位计划，说明理由</li>
                </ol>
                <div className="reminder-box">
                  <strong>提醒：</strong>没有计划 = 临盘冲动 = 大概率亏钱
                </div>
              </div>
            </div>

            {/* 详细输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>仓位计划说明</label>
                <textarea
                  value={data.positionLogic}
                  onChange={(e) => updateField('positionLogic', e.target.value)}
                  placeholder="输入仓位计划说明..."
                  rows={8}
                />
              </div>
            </div>
          </div>
        )}

        {activeStep === 2 && (
          <div className="step-panel">
            {/* 做什么 */}
            <div className="card-section whattodo">
              <div className="card-header">
                <span className="card-tag">做什么</span>
                <h3>从复盘选的股票中确定目标，按优先级排序</h3>
              </div>
              <div className="form-group">
                <label>目标股票（按优先级排序）</label>
                <textarea
                  value={data.targetStocks}
                  onChange={(e) => updateField('targetStocks', e.target.value)}
                  placeholder="输入目标股票..."
                  rows={8}
                />
              </div>
              <div className="form-group">
                <label>优先级理由</label>
                <textarea
                  value={data.targetPriority}
                  onChange={(e) => updateField('targetPriority', e.target.value)}
                  placeholder="输入优先级理由..."
                  rows={6}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>只做计划内的交易，不做计划外的操作</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>计划你的交易，交易你的计划</p>
                <ul>
                  <li>计划内：有逻辑支撑，买卖有依据</li>
                  <li>计划外：冲动交易，大概率亏钱</li>
                </ul>
                <p className="highlight"><strong>标的筛选原则</strong></p>
                <ul>
                  <li>龙头优先：选择板块内地位最高的股票</li>
                  <li>形态优先：选择技术形态好的股票（突破新高、放量）</li>
                  <li>资金优先：选择有资金关注的股票（龙虎榜、资金流向）</li>
                  <li>股性优先：选择股性活跃、成交额大的股票</li>
                </ul>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>按优先级排序，从复盘关注的股票中确定</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>从复盘选的3-5只关注股中确定目标</li>
                  <li>按优先级排序：最看好的排第一</li>
                  <li>记录每只股票的仓位配置</li>
                  <li>明确每只股票的买入理由</li>
                </ol>
              </div>
            </div>

            {/* 详细输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>标的计划详细说明</label>
                <textarea
                  value={data.targetLogic}
                  onChange={(e) => updateField('targetLogic', e.target.value)}
                  placeholder="输入标的计划详细说明..."
                  rows={6}
                />
              </div>
            </div>
          </div>
        )}

        {activeStep === 3 && (
          <div className="step-panel">
            {/* 做什么 */}
            <div className="card-section whattodo">
              <div className="card-header">
                <span className="card-tag">做什么</span>
                <h3>明确买入的触发条件，满足条件才买</h3>
              </div>
              <div className="form-group">
                <label>买入条件（满足全部条件才买）</label>
                <textarea
                  value={data.entryCondition}
                  onChange={(e) => updateField('entryCondition', e.target.value)}
                  placeholder="输入买入条件..."
                  rows={10}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>模糊条件=没有条件，明确条件才能执行</h3>
              </div>
              <div className="logic-content">
                <p><strong>模糊条件的问题</strong></p>
                <ul>
                  <li>「涨幅大了就买」→ 涨多少算大？</li>
                  <li>「感觉好了就买」→ 什么时候算好？</li>
                </ul>
                <p className="highlight"><strong>明确条件的好处</strong></p>
                <ul>
                  <li>符合就买，不符合就不买</li>
                  <li>避免临时起意冲动交易</li>
                  <li>交易有纪律，亏钱也有数</li>
                </ul>
                <p className="highlight"><strong>买入时机参考</strong></p>
                <ul>
                  <li>龙头首次分歧：龙头第一次炸板/回落，可低吸</li>
                  <li>龙头加速：涨停突破/封板，可板上确认</li>
                  <li>跟风启动：跟风股直线拉升，立即买入</li>
                  <li>板块爆发：板块批量涨停，选最强买</li>
                  <li>弱转强：竞价低开高走，突破分时可买</li>
                </ul>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>用输入框规范条件，不满足就不买</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>列出所有买入条件（越多越详细越好）</li>
                  <li>必须是可量化的条件</li>
                  <li>所有条件都满足才买入</li>
                  <li>有一个条件不满足就放弃</li>
                </ol>
              </div>
            </div>

            {/* 详细输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>买入条件详细说明</label>
                <textarea
                  value={data.entryLogic}
                  onChange={(e) => updateField('entryLogic', e.target.value)}
                  placeholder="输入买入条件详细说明..."
                  rows={6}
                />
              </div>
              <div className="form-group">
                <label>参考模板（可复制使用）</label>
                <textarea
                  value={data.entryTemplate}
                  onChange={(e) => updateField('entryTemplate', e.target.value)}
                  placeholder="参考模板..."
                  rows={6}
                  className="template-textarea"
                />
                <button
                  className="btn btn-sm btn-outline"
                  style={{ marginTop: '8px' }}
                  onClick={() => {
                    updateField('entryCondition', DEFAULT_VALUES.entryCondition + '\n\n' + data.entryTemplate);
                  }}
                >
                  复制模板到上方
                </button>
              </div>
            </div>
          </div>
        )}

        {activeStep === 4 && (
          <div className="step-panel">
            {/* 做什么 */}
            <div className="card-section whattodo">
              <div className="card-header">
                <span className="card-tag">做什么</span>
                <h3>设定止损线和止盈计划</h3>
              </div>
              <div className="quick-inputs">
                <div className="quick-input">
                  <label>止损线</label>
                  <input
                    type="text"
                    value={data.stopLoss}
                    onChange={(e) => updateField('stopLoss', e.target.value)}
                    placeholder="如: -5%"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>止盈计划</label>
                <textarea
                  value={data.takeProfit}
                  onChange={(e) => updateField('takeProfit', e.target.value)}
                  placeholder="输入止盈计划..."
                  rows={8}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>截断亏损，让利润奔跑</h3>
              </div>
              <div className="logic-content">
                <p><strong>数学原理：亏50%需要赚100%才能回本</strong></p>
                <div className="math-table">
                  <table>
                    <thead>
                      <tr>
                        <th>亏损</th>
                        <th>回本需要涨幅</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>-5%</td><td>+5.26%</td></tr>
                      <tr><td>-10%</td><td>+11.11%</td></tr>
                      <tr><td>-20%</td><td>+25%</td></tr>
                      <tr><td>-50%</td><td>+100%</td></tr>
                      <tr><td>-70%</td><td>+233%</td></tr>
                    </tbody>
                  </table>
                </div>
                <p className="highlight"><strong>风控原则</strong></p>
                <ul>
                  <li>止损要坚决：触及止损线必须无条件止损，不能犹豫</li>
                  <li>止盈要分批：分批止盈，不要一次性卖完</li>
                  <li>保护利润：盈利后移动止损到成本价上方</li>
                  <li>仓位控制：单只股票不超过3成仓，分散风险</li>
                  <li>不做计划外：严格按照计划执行，不临时起意</li>
                </ul>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>-5%止损，+10%分批卖</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>设定止损线：-5%必须走，不犹豫</li>
                  <li>设定止盈点：+8%、+15%、+20%分批卖</li>
                  <li>设定特殊情况的处理方式</li>
                  <li>坚持执行，不临时起意</li>
                </ol>
              </div>
            </div>

            {/* 详细输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>止损止盈详细说明</label>
                <textarea
                  value={data.exitLogic}
                  onChange={(e) => updateField('exitLogic', e.target.value)}
                  placeholder="输入止损止盈详细说明..."
                  rows={8}
                />
              </div>
              <div className="tips-box warning">
                <h4>⚠️ 十二字真言</h4>
                <ul>
                  <li><strong>资金在哪我在哪：</strong>资金流入 → 跟进，资金流出 → 回避</li>
                  <li><strong>情绪好我就做：</strong>高潮期 → 重仓，退潮期 → 空仓</li>
                  <li><strong>情绪差我就走：</strong>盘面危险 → 卖出，计划失败 → 止损</li>
                  <li><strong>错了就止损：</strong>-5%必走，不幻想，不死扛</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 底部操作栏 */}
      <div className="action-bar">
        <button
          className="btn"
          disabled={activeStep === 1}
          onClick={() => setActiveStep(activeStep - 1)}
        >
          上一步
        </button>
        <div className="step-indicator">
          {steps.map(s => (
            <span
              key={s.num}
              className={`indicator-dot ${activeStep >= s.num ? 'active' : ''}`}
              onClick={() => setActiveStep(s.num)}
            />
          ))}
        </div>
        {activeStep < 4 ? (
          <button
            className="btn btn-primary"
            onClick={() => setActiveStep(activeStep + 1)}
          >
            下一步
          </button>
        ) : (
          <button className="btn btn-primary" onClick={handleSave}>
            完成保存
          </button>
        )}
      </div>
    </div>
  );
}
