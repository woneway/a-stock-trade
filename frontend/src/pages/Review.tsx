import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import './Simplified.css';

interface ReviewData {
  // 情绪判断
  limitUpCount: string;
  brokenPlateRatio: string;
  limitDownCount: string;
  highestBoard: string;
  yesterdayLimitUp: string;
  marketCycle: string;
  sentimentLogic: string;

  // 涨停板复盘
  focusStocks: string;
  focusStocksLogic: string;
  limitUpAnalysis: string;

  // 炸板复盘
  brokenPlates: string;
  brokenPlatesAnalysis: string;
  brokenPlatesLesson: string;

  // 资金/龙虎榜
  capitalFlow: string;
  combinedStocks: string;
  combinedStocksLogic: string;
}

const DEFAULT_VALUES = {
  // 情绪判断
  limitUpCount: '',
  brokenPlateRatio: '',
  limitDownCount: '',
  highestBoard: '',
  yesterdayLimitUp: '',
  marketCycle: '',
  sentimentLogic: `【为什么做】
情绪是市场的「温度计」，决定赚钱难度。
- 牛市（高潮期）：80%的股票都在涨，你随便买都可能赚
- 熊市（退潮期）：80%的股票都在跌，你买什么都可能亏
情绪 → 决定赚钱难度 → 决定仓位 → 决定策略

【周期判断标准】
- 启动期：涨停20-30家，最高2-3板，炸板率25-35%
- 发酵期：涨停30-50家，最高3-4板，炸板率15-25%
- 高潮期：涨停50+家，最高5+板，炸板率<15%
- 分歧期：涨停30-50家，最高4-5板，炸板率25-35%
- 退潮期：涨停10-20家，最高2-3板，炸板率35-45%
- 冰点期：涨停<10家，最高1-2板，炸板率>45%`,

  // 涨停板复盘
  focusStocks: `【明日关注股】（3-5只）
1. 代码    名称    几连板    涨停原因
2.
3.
4.
5.`,
  focusStocksLogic: `【为什么做】
涨停板是市场最强信号。
- 涨停 = 资金用真金白银投票「这个股票值得买」
- 涨停板数量多 = 大量资金在积极做多 = 强势市场

【选股思路】
- 越早涨停 = 资金越看好（09:25最强，14:30最弱）
- 龙头涨停 → 带动板块 → 跟风跟着涨
- 跟风涨停 → 只是跟随 → 没有带动性
龙头70%继续涨，跟风只有30%`,
  limitUpAnalysis: `【怎么做】
1. 用开盘啦「涨停板分析」功能
2. 按「涨停时间」排序：越早越强
3. 按「封单金额」排序：越大越强
4. 按「流通市值」排序：越小越容易炒
5. 筛选连板股 → 识别龙头（5板以上是核心）
6. 筛选「首板」找新题材（新概念首次出现）`,

  // 炸板复盘
  brokenPlates: `【今日炸板股】
1. 代码    名称    炸板时间    回落幅度
2.
3.`,
  brokenPlatesAnalysis: `【炸板原因分析】
1. 跟风炸板：龙头已封住，跟风被炸 → 资金不认可
2. 板块炸板：整个板块回落 → 规避整个板块
3. 量能不足：封板资金不够 → 观察
4. 大盘拖累：大盘大跌拖累 → 等待反弹`,
  brokenPlatesLesson: `【反思总结】
1. 今天打板为什么炸？
2. 是选的股不行，还是买的时机不对？
3. 有什么经验教训？
4. 避免重复犯错的措施？`,

  // 资金/龙虎榜
  capitalFlow: `【主力资金动向】
- 今日净流入板块：
- 今日净流出板块：
- 资金态度：积极/观望/谨慎

【5日/10日持续净流入板块】
1.
2.
3.`,
  combinedStocks: `【合力股】（机构+游资合力）
1. 代码    名称    机构买入    游资买入    合力判断
2.
3.`,
  combinedStocksLogic: `【为什么做】
龙虎榜 = 主力资金动向的「监控摄像头」。
- 散户买卖：几百几千股，对股价影响微乎其微
- 主力买卖：几万几十万股，直接决定股价涨跌
- 跟踪主力 = 站在资金这一边

【合力股特征】
- 机构买入 = 基本面认可，长期看好
- 游资买入 = 技术面认可，短期要涨
- 两者合力 = 既要涨，又要涨得久

【避免问题股】
- 对倒股（买入≈卖出）
- 温州帮等操纵股
- 高位放量出货股`,
};

export default function SimplifiedReview() {
  const navigate = useNavigate();
  const [data, setData] = useState<ReviewData>({
    ...DEFAULT_VALUES,
  });

  const [activeStep, setActiveStep] = useState(1);
  const [saved, setSaved] = useState(false);

  const today = dayjs().format('YYYY-MM-DD');

  // 加载今日保存的数据
  useEffect(() => {
    const savedData = localStorage.getItem(`simplified-review-${today}`);
    if (savedData) {
      try {
        setData(JSON.parse(savedData));
      } catch (e) {
        console.error('加载保存数据失败', e);
      }
    }
  }, [today]);

  const updateField = (field: keyof ReviewData, value: string) => {
    setData(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    // 保存到 localStorage
    localStorage.setItem(`simplified-review-${today}`, JSON.stringify(data));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);

    // 保存到数据库：创建/更新历史计划
    try {
      // 检查是否已有今日的历史计划
      const historyRes = await axios.get('/api/plan/history', {
        params: { start_date: today, end_date: today }
      });

      const existingHistory = historyRes.data?.[0];

      if (existingHistory) {
        // 更新历史计划
        await axios.put(`/api/plan/history/${existingHistory.id}`, {
          trade_date: today,
          market_cycle: data.marketCycle,
          position_plan: data.focusStocks?.split('\n').slice(1, 4).join('; ') || '',
          status: 'completed'
        });
      } else {
        // 创建历史计划
        await axios.post('/api/plan/history', {
          trade_date: today,
          market_cycle: data.marketCycle,
          position_plan: data.focusStocks?.split('\n').slice(1, 4).join('; ') || '',
          status: 'completed',
          planned_stock_count: data.focusStocks?.split('\n').length - 1 || 0
        });
      }
    } catch (err) {
      console.error('保存到数据库失败:', err);
    }
  };

  const handleGoToPlan = () => {
    // 先保存
    handleSave();
    // 跳转到计划页面
    navigate('/simplified-plan');
  };

  const handleExport = () => {
    const content = `# 复盘 - ${today}

## 一、情绪判断

### 做什么（任务）
- 涨停家数：${data.limitUpCount}
- 炸板率：${data.brokenPlateRatio}%
- 跌停家数：${data.limitDownCount}
- 最高板：${data.highestBoard}板
- 昨日涨停溢价：${data.yesterdayLimitUp}%
- 周期判断：${data.marketCycle}

### 为什么做（逻辑）
${data.sentimentLogic}

---

## 二、涨停板复盘

### 做什么（任务）
${data.focusStocks}

### 为什么做（逻辑）
${data.focusStocksLogic}

### 怎么做（操作）
${data.limitUpAnalysis}

---

## 三、炸板复盘

### 做什么（任务）
${data.brokenPlates}

### 为什么做（逻辑）
${data.brokenPlatesAnalysis}

### 反思总结
${data.brokenPlatesLesson}

---

## 四、资金/龙虎榜

### 做什么（任务）
${data.capitalFlow}

### 为什么做（逻辑）
${data.combinedStocksLogic}

### 合力股
${data.combinedStocks}
    `.trim();

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `复盘-${today}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getCycleAdvice = (limitUp: string, highestBoard: string, brokenRatio: string, limitDown: string): string => {
    const limitUpNum = parseInt(limitUp) || 0;
    const highestBoardNum = parseInt(highestBoard) || 0;
    const brokenRatioNum = parseFloat(brokenRatio) || 0;
    const limitDownNum = parseInt(limitDown) || 0;

    if (limitUpNum >= 50 && highestBoardNum >= 5 && brokenRatioNum < 15 && limitDownNum <= 2) {
      return '高潮';
    } else if (limitUpNum >= 30 && limitUpNum <= 50 && highestBoardNum >= 3 && brokenRatioNum >= 15 && brokenRatioNum <= 35 && limitDownNum <= 15) {
      return '分歧';
    } else if (limitUpNum >= 20 && limitUpNum < 30 && highestBoardNum >= 2 && brokenRatioNum >= 25 && brokenRatioNum <= 35) {
      return '启动';
    } else if (limitUpNum >= 30 && limitUpNum <= 50 && highestBoardNum >= 3 && brokenRatioNum >= 15 && brokenRatioNum <= 25 && limitDownNum <= 5) {
      return '发酵';
    } else if (limitUpNum >= 10 && limitUpNum <= 20 && highestBoardNum >= 2 && brokenRatioNum >= 35 && limitDownNum >= 15) {
      return '退潮';
    } else if (limitUpNum < 10 && highestBoardNum <= 2 && brokenRatioNum > 45 && limitDownNum > 30) {
      return '冰点';
    }
    return '';
  };

  const steps = [
    { num: 1, title: '情绪判断', icon: '🌡️', desc: '判断市场周期' },
    { num: 2, title: '涨停板复盘', icon: '🚀', desc: '选出明日关注股' },
    { num: 3, title: '炸板复盘', icon: '💥', desc: '反思炸板原因' },
    { num: 4, title: '资金/龙虎榜', icon: '💰', desc: '记录主力动向' },
  ];

  // 自动判断周期
  useEffect(() => {
    const cycle = getCycleAdvice(data.limitUpCount, data.highestBoard, data.brokenPlateRatio, data.limitDownCount);
    if (cycle && !data.marketCycle) {
      updateField('marketCycle', cycle);
    }
  }, [data.limitUpCount, data.highestBoard, data.brokenPlateRatio, data.limitDownCount]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>简化复盘</h1>
          <span className="date">{today} {dayjs().format('dddd')}</span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-outline" onClick={handleExport}>
            导出 Markdown
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            {saved ? '已保存 ✓' : '保存'}
          </button>
          <button className="btn btn-primary" onClick={handleGoToPlan}>
            制定明日计划 →
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
                <h3>记录情绪指标，判断市场周期</h3>
              </div>
              <div className="quick-inputs">
                <div className="quick-input">
                  <label>涨停家数</label>
                  <input
                    type="number"
                    value={data.limitUpCount}
                    onChange={(e) => updateField('limitUpCount', e.target.value)}
                    placeholder="如: 85"
                  />
                  <span className="unit">家</span>
                </div>
                <div className="quick-input">
                  <label>炸板率</label>
                  <input
                    type="number"
                    step="0.1"
                    value={data.brokenPlateRatio}
                    onChange={(e) => updateField('brokenPlateRatio', e.target.value)}
                    placeholder="如: 15.5"
                  />
                  <span className="unit">%</span>
                </div>
                <div className="quick-input">
                  <label>跌停家数</label>
                  <input
                    type="number"
                    value={data.limitDownCount}
                    onChange={(e) => updateField('limitDownCount', e.target.value)}
                    placeholder="如: 12"
                  />
                  <span className="unit">家</span>
                </div>
                <div className="quick-input">
                  <label>最高板</label>
                  <input
                    type="number"
                    value={data.highestBoard}
                    onChange={(e) => updateField('highestBoard', e.target.value)}
                    placeholder="如: 7"
                  />
                  <span className="unit">板</span>
                </div>
                <div className="quick-input">
                  <label>昨日涨停溢价</label>
                  <input
                    type="number"
                    step="0.1"
                    value={data.yesterdayLimitUp}
                    onChange={(e) => updateField('yesterdayLimitUp', e.target.value)}
                    placeholder="如: 3.5"
                  />
                  <span className="unit">%</span>
                </div>
                <div className="quick-input">
                  <label>周期判断</label>
                  <select
                    value={data.marketCycle}
                    onChange={(e) => updateField('marketCycle', e.target.value)}
                  >
                    <option value="">选择周期</option>
                    <option value="冰点">冰点</option>
                    <option value="启动">启动</option>
                    <option value="发酵">发酵</option>
                    <option value="分歧">分歧</option>
                    <option value="高潮">高潮</option>
                    <option value="退潮">退潮</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>情绪是市场温度计，决定赚钱难度</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>情绪是市场的「温度计」，决定赚钱难度</p>
                <ul>
                  <li>牛市（高潮期）：80%的股票都在涨，你随便买都可能赚</li>
                  <li>熊市（退潮期）：80%的股票都在跌，你买什么都可能亏</li>
                </ul>
                <p className="formula"><strong>情绪 → 决定赚钱难度 → 决定仓位 → 决定策略</strong></p>
                <div className="cycle-table">
                  <table>
                    <thead>
                      <tr>
                        <th>周期</th>
                        <th>涨停家数</th>
                        <th>最高板</th>
                        <th>炸板率</th>
                        <th>仓位策略</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>启动</td><td>20-30</td><td>2-3板</td><td>25-35%</td><td>试错龙头</td></tr>
                      <tr><td>发酵</td><td>30-50</td><td>3-4板</td><td>15-25%</td><td>积极参与</td></tr>
                      <tr><td>高潮</td><td>50+</td><td>5+板</td><td>&lt;15%</td><td>持股待涨</td></tr>
                      <tr><td>分歧</td><td>30-50</td><td>4-5板</td><td>25-35%</td><td>谨慎追高</td></tr>
                      <tr><td>退潮</td><td>10-20</td><td>2-3板</td><td>35-45%</td><td>空仓休息</td></tr>
                      <tr><td>冰点</td><td>&lt;10</td><td>1-2板</td><td>&gt;45%</td><td>等待</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>用开盘啦情绪指标查看</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>打开开盘啦 → 首页顶部查看「情绪仪表盘」</li>
                  <li>记录关键数据：涨停家数、炸板率、跌停家数、最高板</li>
                  <li>根据数据对照周期判断标准</li>
                  <li>根据周期决定今日仓位策略</li>
                </ol>
              </div>
            </div>

            {/* 详细分析输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>情绪分析（详细记录）</label>
                <textarea
                  value={data.sentimentLogic}
                  onChange={(e) => updateField('sentimentLogic', e.target.value)}
                  placeholder="输入你的情绪分析..."
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
                <h3>选出3-5只明日关注股</h3>
              </div>
              <div className="form-group">
                <label>明日关注股（3-5只）</label>
                <textarea
                  value={data.focusStocks}
                  onChange={(e) => updateField('focusStocks', e.target.value)}
                  placeholder="输入明日关注股..."
                  rows={8}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>涨停板是最强信号，龙头溢价最高</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>涨停板是市场最强信号</p>
                <ul>
                  <li>涨停 = 资金用真金白银投票「这个股票值得买」</li>
                  <li>涨停板数量多 = 大量资金在积极做多 = 强势市场</li>
                </ul>
                <p className="highlight"><strong>越早涨停 = 资金越看好</strong></p>
                <ul>
                  <li>09:25涨停：开盘就涨停，资金一开盘就迫不及待要买</li>
                  <li>14:30涨停：到尾盘才涨停，资金是没办法才拉的</li>
                </ul>
                <p className="highlight"><strong>龙头 vs 跟风</strong></p>
                <ul>
                  <li>龙头涨停 → 带动板块 → 跟风跟着涨（70%继续涨）</li>
                  <li>跟风涨停 → 只是跟随 → 没有带动性（只有30%）</li>
                </ul>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>用涨停板分析，按时间排序找最早的涨停</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>开盘啦首页 → 点击「涨停板」</li>
                  <li>按「涨停时间」排序：越早越强</li>
                  <li>按「封单金额」排序：越大越强</li>
                  <li>按「流通市值」排序：越小越容易炒</li>
                  <li>筛选连板股：5板以上是市场核心（重点关注）</li>
                  <li>筛选首板找新题材：首次出现的概念</li>
                  <li>选出3-5只明日重点关注</li>
                </ol>
              </div>
            </div>

            {/* 详细分析输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>涨停板分析（详细记录）</label>
                <textarea
                  value={data.limitUpAnalysis}
                  onChange={(e) => updateField('limitUpAnalysis', e.target.value)}
                  placeholder="输入涨停板分析..."
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
                <h3>记录炸板股，反思炸板原因</h3>
              </div>
              <div className="form-group">
                <label>今日炸板股</label>
                <textarea
                  value={data.brokenPlates}
                  onChange={(e) => updateField('brokenPlates', e.target.value)}
                  placeholder="输入今日炸板股..."
                  rows={6}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>炸板=做多失败，避免重复犯错</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>炸板 = 资金做多失败</p>
                <ul>
                  <li>本来看好要涨停 → 结果没封住 → 资金跑了</li>
                  <li>炸板后第二天低开是大概率事件</li>
                </ul>
                <p className="highlight"><strong>跟风炸板为什么不能买？</strong></p>
                <ul>
                  <li>龙头涨停 → 跟风涨停</li>
                  <li>龙头没封住 → 跟风先炸</li>
                  <li>跟风炸了说明：资金不认可这个股票</li>
                  <li>第二天低开是大概率事件（70%以上）</li>
                </ul>
                <div className="warning-box">
                  <table>
                    <thead>
                      <tr>
                        <th>炸板类型</th>
                        <th>特征</th>
                        <th>风险等级</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>跟风炸板</td><td>龙头已封住，跟风被炸</td><td>高</td></tr>
                      <tr><td>板块炸板</td><td>整个板块回落</td><td>高</td></tr>
                      <tr><td>量能不足</td><td>封板资金不够</td><td>中</td></tr>
                      <tr><td>大盘拖累</td><td>大盘大跌拖累</td><td>中</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>用炸板分析功能</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>开盘啦首页 → 点击「炸板分析」</li>
                  <li>查看炸板股列表：炸板时间、次数、回落幅度</li>
                  <li>分析炸板原因：跟风/板块/量能/大盘</li>
                  <li>记录反思：为什么炸？选的股不行还是时机不对？</li>
                </ol>
              </div>
            </div>

            {/* 详细分析输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>炸板原因分析</label>
                <textarea
                  value={data.brokenPlatesAnalysis}
                  onChange={(e) => updateField('brokenPlatesAnalysis', e.target.value)}
                  placeholder="输入炸板原因分析..."
                  rows={6}
                />
              </div>
              <div className="form-group">
                <label>反思总结</label>
                <textarea
                  value={data.brokenPlatesLesson}
                  onChange={(e) => updateField('brokenPlatesLesson', e.target.value)}
                  placeholder="输入反思总结..."
                  rows={6}
                />
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
                <h3>记录主力资金动向，选合力股</h3>
              </div>
              <div className="form-group">
                <label>主力资金动向</label>
                <textarea
                  value={data.capitalFlow}
                  onChange={(e) => updateField('capitalFlow', e.target.value)}
                  placeholder="输入主力资金动向..."
                  rows={6}
                />
              </div>
              <div className="form-group">
                <label>合力股（机构+游资）</label>
                <textarea
                  value={data.combinedStocks}
                  onChange={(e) => updateField('combinedStocks', e.target.value)}
                  placeholder="输入合力股..."
                  rows={6}
                />
              </div>
            </div>

            {/* 为什么做 */}
            <div className="card-section whylogic">
              <div className="card-header">
                <span className="card-tag why">为什么做</span>
                <h3>跟主力资金站在一起</h3>
              </div>
              <div className="logic-content">
                <p><strong>核心原理：</strong>龙虎榜 = 主力资金动向的「监控摄像头」</p>
                <ul>
                  <li>散户买卖：几百几千股，对股价影响微乎其微</li>
                  <li>主力买卖：几万几十万股，直接决定股价涨跌</li>
                  <li>跟踪主力 = 站在资金这一边</li>
                </ul>
                <p className="highlight"><strong>机构 vs 游资</strong></p>
                <ul>
                  <li>机构资金：价值投资，持有几周-几个月，缓慢推升</li>
                  <li>游资资金：趋势投机，持有几天-几周，快速拉升</li>
                </ul>
                <p className="highlight"><strong>为什么机构+游资合力最好？</strong></p>
                <ul>
                  <li>机构买入 = 基本面认可，长期看好</li>
                  <li>游资买入 = 技术面认可，短期要涨</li>
                  <li>两者合力 = 既要涨，又要涨得久</li>
                </ul>
              </div>
            </div>

            {/* 怎么做 */}
            <div className="card-section howtodo">
              <div className="card-header">
                <span className="card-tag how">怎么做</span>
                <h3>用龙虎榜+资金流向功能</h3>
              </div>
              <div className="how-content">
                <ol>
                  <li>开盘啦首页 → 点击「龙虎榜」</li>
                  <li>筛选「机构买入」：记录净买入前5</li>
                  <li>筛选「游资买入」：记录知名游资席位动向</li>
                  <li>分析合力：机构+游资同时买入最佳</li>
                  <li>排除问题股：对倒股、温州帮、高位出货股</li>
                  <li>用「资金流向」→「区间统计」看5日/10日持续净流入</li>
                </ol>
              </div>
            </div>

            {/* 详细分析输入 */}
            <div className="card-section input-section">
              <div className="form-group">
                <label>合力理由分析</label>
                <textarea
                  value={data.combinedStocksLogic}
                  onChange={(e) => updateField('combinedStocksLogic', e.target.value)}
                  placeholder="输入合力理由分析..."
                  rows={6}
                />
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
