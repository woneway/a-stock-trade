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

  // 大盘指数
  shIndex: string;
  szIndex: string;
  cyIndex: string;

  // 资金流向
  mainFlow: string;
  instBuy: string;
  instSell: string;

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

  // 大盘指数
  shIndex: '',
  szIndex: '',
  cyIndex: '',

  // 资金流向
  mainFlow: '',
  instBuy: '',
  instSell: '',

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

      // 从表单数据中提取热门板块和涨停股
      const hotSectors = extractHotSectors(data.focusStocks);
      const limitUpStocks = extractLimitUpStocks(data.focusStocks);

      const saveData = {
        trade_date: today,
        market_cycle: data.marketCycle,
        position_plan: data.focusStocks?.split('\n').slice(1, 4).join('; ') || '',
        status: 'completed',
        planned_stock_count: data.focusStocks?.split('\n').length - 1 || 0,
        // 新增的详细数据字段
        sentiment_score: parseInt(data.limitUpCount) || 0,
        up_count: 2000, // 从表单获取或留空
        down_count: 1000, // 从表单获取或留空
        limit_up_count: parseInt(data.limitUpCount) || 0,
        limit_down_count: parseInt(data.limitDownCount) || 0,
        break_up_count: parseInt(data.brokenPlateRatio) || 0,
        // 大盘指数
        sh_index: parseFloat(data.shIndex) || null,
        sz_index: parseFloat(data.szIndex) || null,
        cy_index: parseFloat(data.cyIndex) || null,
        // 资金流向
        main_flow: parseFloat(data.mainFlow) || null,
        inst_buy: parseFloat(data.instBuy) || null,
        inst_sell: parseFloat(data.instSell) || null,
        // JSON字段
        hot_sectors: hotSectors,
        limit_up_stocks: limitUpStocks,
        notes: data.sentimentLogic || ''
      };

      if (existingHistory) {
        // 更新历史计划
        await axios.put(`/api/plan/history/${existingHistory.id}`, saveData);
      } else {
        // 创建历史计划
        await axios.post('/api/plan/history', saveData);
      }
    } catch (err) {
      console.error('保存到数据库失败:', err);
    }
  };

  // 辅助函数：从focusStocks提取热门板块
  const extractHotSectors = (text: string): string => {
    if (!text) return '[]';
    // 简单解析：如果包含股票代码，返回空列表（需要用户手动填写）
    // 实际使用时可以从涨停板列表中提取
    return '[]';
  };

  // 辅助函数：从focusStocks提取涨停股列表
  const extractLimitUpStocks = (text: string): string => {
    if (!text) return '[]';
    // 解析格式：代码  名称  几连板  涨停原因
    const stocks: Array<{code: string, name: string, boards: number, reason: string}> = [];
    const lines = text.split('\n').filter(l => l.trim());
    for (const line of lines) {
      const parts = line.trim().split(/\s+/);
      if (parts.length >= 2 && /^\d{6}$/.test(parts[0])) {
        stocks.push({
          code: parts[0],
          name: parts[1] || '',
          boards: 1,
          reason: parts.slice(2).join(' ') || ''
        });
      }
    }
    return JSON.stringify(stocks);
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

### 大盘指数
- 上证指数：${data.shIndex || '-'}点
- 深证指数：${data.szIndex || '-'}点
- 创业板指：${data.cyIndex || '-'}点

### 资金流向
- 主力净流入：${data.mainFlow || '-'}亿
- 机构买入：${data.instBuy || '-'}亿
- 机构卖出：${data.instSell || '-'}亿

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

              {/* 大盘指数输入 */}
              <div className="quick-inputs" style={{ marginTop: '16px' }}>
                <div className="quick-input">
                  <label>上证指数</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.shIndex}
                    onChange={(e) => updateField('shIndex', e.target.value)}
                    placeholder="如: 3387.5"
                  />
                  <span className="unit">点</span>
                </div>
                <div className="quick-input">
                  <label>深证指数</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.szIndex}
                    onChange={(e) => updateField('szIndex', e.target.value)}
                    placeholder="如: 11015"
                  />
                  <span className="unit">点</span>
                </div>
                <div className="quick-input">
                  <label>创业板指</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.cyIndex}
                    onChange={(e) => updateField('cyIndex', e.target.value)}
                    placeholder="如: 2250.3"
                  />
                  <span className="unit">点</span>
                </div>
              </div>

              {/* 资金流向输入 */}
              <div className="quick-inputs" style={{ marginTop: '16px' }}>
                <div className="quick-input">
                  <label>主力净流入</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.mainFlow}
                    onChange={(e) => updateField('mainFlow', e.target.value)}
                    placeholder="如: 268.5"
                  />
                  <span className="unit">亿</span>
                </div>
                <div className="quick-input">
                  <label>机构买入</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.instBuy}
                    onChange={(e) => updateField('instBuy', e.target.value)}
                    placeholder="如: 52.3"
                  />
                  <span className="unit">亿</span>
                </div>
                <div className="quick-input">
                  <label>机构卖出</label>
                  <input
                    type="number"
                    step="0.01"
                    value={data.instSell}
                    onChange={(e) => updateField('instSell', e.target.value)}
                    placeholder="如: 30.1"
                  />
                  <span className="unit">亿</span>
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
                <p><strong>操作路径：</strong></p>
                <ol>
                  <li>打开开盘啦 APP/网页 → 首页顶部「情绪仪表盘」</li>
                  <li>点击「情绪指标」进入详情页</li>
                </ol>

                <p><strong>需要记录的关键数据：</strong></p>
                <div className="tips-box">
                  <table>
                    <thead>
                      <tr>
                        <th>指标</th>
                        <th>在哪里看</th>
                        <th>记录什么</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>涨停家数</td>
                        <td>情绪仪表盘/涨停板</td>
                        <td>今日涨停了多少只股票</td>
                      </tr>
                      <tr>
                        <td>跌停家数</td>
                        <td>情绪仪表盘</td>
                        <td>今日跌停了多少只股票</td>
                      </tr>
                      <tr>
                        <td>炸板率</td>
                        <td>情绪仪表盘/炸板分析</td>
                        <td>涨停被打开的比例（越高越危险）</td>
                      </tr>
                      <tr>
                        <td>最高板</td>
                        <td>情绪仪表盘/连板池</td>
                        <td>今日最高连板数（龙头高度）</td>
                      </tr>
                      <tr>
                        <td>昨日溢价</td>
                        <td>情绪仪表盘</td>
                        <td>昨日涨停股今日平均涨幅</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <p><strong>判断步骤：</strong></p>
                <ol>
                  <li><strong>第一步：</strong>看涨停家数（&gt;50高潮，30-50发酵，&lt;10冰点）</li>
                  <li><strong>第二步：</strong>看最高板（5板+龙头，3-4板发酵，1-2板退潮）</li>
                  <li><strong>第三步：</strong>看炸板率（&lt;15%安全，&gt;35%危险）</li>
                  <li><strong>第四步：</strong>对照周期表，确定今天是哪个周期</li>
                  <li><strong>第五步：</strong>根据周期决定仓位（高潮8-10成，冰点0成）</li>
                </ol>

                <div className="reminder-box">
                  <strong>💡 快捷入口：</strong>开盘啦首页顶部直接显示情绪仪表盘，可以快速看到所有关键指标
                </div>
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
                <h3>用涨停板分析功能筛选目标股</h3>
              </div>
              <div className="how-content">
                <p><strong>操作路径：</strong></p>
                <ol>
                  <li>开盘啦首页 → 点击「涨停板」</li>
                </ol>

                <p><strong>筛选步骤：</strong></p>
                <ol>
                  <li><strong>按涨停时间排序</strong>：越早越强（09:25最强，14:30最弱）</li>
                  <li><strong>按封单金额排序</strong>：越大说明资金越看好</li>
                  <li><strong>按流通市值排序</strong>：越小越容易炒作</li>
                  <li><strong>筛选连板股</strong>：5板以上是市场核心（重点关注）</li>
                  <li><strong>筛选首板</strong>：找新题材首次出现的股票</li>
                </ol>

                <div className="tips-box">
                  <p><strong>龙头识别标准：</strong></p>
                  <table>
                    <thead>
                      <tr>
                        <th>板数</th>
                        <th>市场地位</th>
                        <th>操作建议</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>7板+</td><td>市场总龙头</td><td>持股待涨，首次分歧可低吸</td></tr>
                      <tr><td>5-6板</td><td>板块龙头</td><td>强势可持有，注意分化</td></tr>
                      <tr><td>3-4板</td><td>跟风龙头</td><td>谨慎追高，注意炸板</td></tr>
                      <tr><td>1-2板</td><td>启动初期</td><td>观察为主</td></tr>
                    </tbody>
                  </table>
                </div>

                <p><strong>选出3-5只明日重点关注</strong>，记录到下方输入框</p>
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
                <h3>用炸板分析功能规避风险</h3>
              </div>
              <div className="how-content">
                <p><strong>操作路径：</strong></p>
                <ol>
                  <li>开盘啦首页 → 点击「炸板分析」</li>
                </ol>

                <p><strong>分析要点：</strong></p>
                <ol>
                  <li><strong>看炸板率</strong>：炸板率&gt;35%说明市场很弱，小心</li>
                  <li><strong>看炸板时间</strong>：越早炸板风险越大</li>
                  <li><strong>看炸板次数</strong>：多次炸板说明资金不坚定</li>
                  <li><strong>看回落幅度</strong>：从涨停跌下来越多，风险越大</li>
                </ol>

                <div className="tips-box warning">
                  <p><strong>炸板类型分析：</strong></p>
                  <table>
                    <thead>
                      <tr>
                        <th>类型</th>
                        <th>特征</th>
                        <th>风险</th>
                        <th>应对</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>跟风炸板</td><td>龙头已封，跟风被炸</td><td>高</td><td>立即放弃</td></tr>
                      <tr><td>板块炸板</td><td>整个板块回落</td><td>高</td><td>规避板块</td></tr>
                      <tr><td>量能不足</td><td>封板资金不够</td><td>中</td><td>观察量价</td></tr>
                      <tr><td>大盘拖累</td><td>大盘大跌拖累</td><td>中</td><td>等待修复</td></tr>
                    </tbody>
                  </table>
                </div>

                <p><strong>反思记录：</strong>为什么炸？是选的股不行还是买入时机不对？</p>
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
                <h3>用龙虎榜+资金流向跟主力操作</h3>
              </div>
              <div className="how-content">
                <p><strong>龙虎榜操作路径：</strong></p>
                <ol>
                  <li>开盘啦首页 → 点击「龙虎榜」</li>
                </ol>

                <p><strong>分析步骤：</strong></p>
                <ol>
                  <li><strong>筛选「机构买入」</strong>：记录净买入前5（机构看长线）</li>
                  <li><strong>筛选「游资买入」</strong>：记录知名游资席位动向（游资看短线）</li>
                  <li><strong>分析合力</strong>：机构+游资同时买入最佳</li>
                  <li><strong>排除问题股</strong>：对倒股、温州帮、高位出货股</li>
                </ol>

                <p><strong>资金流向操作路径：</strong></p>
                <ol>
                  <li>开盘啦首页 → 点击「资金流向」</li>
                  <li>点击「区间统计」看5日/10日/30日持续净流入</li>
                </ol>

                <div className="tips-box">
                  <p><strong>资金形态判断：</strong></p>
                  <table>
                    <thead>
                      <tr>
                        <th>资金形态</th>
                        <th>特征</th>
                        <th>信号含义</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>持续净流入</td><td>5日/10日连续流入</td><td>主线热点</td></tr>
                      <tr><td>首次净流入</td><td>今日首次大幅流入</td><td>启动信号</td></tr>
                      <tr><td>净流出</td><td>连续流出</td><td>行情结束</td></tr>
                      <tr><td>反复流入</td><td>时进时出</td><td>震荡行情</td></tr>
                    </tbody>
                  </table>
                </div>
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
