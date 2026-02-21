import { useState } from 'react';
import dayjs from 'dayjs';

interface MarketData {
  index: string;
  points: number;
  change: number;
  support: number;
  resistance: number;
}

interface Sector {
  name: string;
  change: number;
  type: 'main' | 'rotation' | 'watch';
  leader?: string;
}

interface Stock {
  code: string;
  name: string;
  price: number;
  change: number;
  strategy: string;
  status: 'observing' | 'pending' | 'holding';
}

interface Alert {
  stock: string;
  type: 'warning' | 'success';
  message: string;
}

interface CapitalFlow {
  mainInflow: { sector: string; amount: string; stocks: string[] }[];
  mainOutflow: { sector: string; amount: string }[];
  northMoney: { in: number; out: number; net: number };
}

interface SentimentPhase {
  phase: string;
  description: string;
  advice: string;
}

interface Review {
  preMarket: {
    sentiment: string;
    sectors: string[];
    targetStocks: string[];
    planBasis: string;
  };
  postMarket: {
    executed: { stock: string; action: string; result: string }[];
    mistakes: string;
    lessons: string;
  };
}

export default function TodayPlan() {
  const [activeTab, setActiveTab] = useState<'pre' | 'in' | 'post'>('pre');
  const [marketData] = useState<MarketData[]>([
    { index: '上证指数', points: 3200, change: 0.5, support: 3150, resistance: 3250 },
    { index: '创业板', points: 2100, change: 1.2, support: 2050, resistance: 2200 },
  ]);
  const [sectors] = useState<Sector[]>([
    { name: '芯片', change: 3.5, type: 'main', leader: '中芯国际' },
    { name: '新能源', change: 1.2, type: 'rotation' },
    { name: 'AI', change: -0.5, type: 'watch' },
  ]);
  const [news] = useState([
    { type: '政策', content: 'XXX会议召开，利好AI板块' },
    { type: '公告', content: 'XX公司业绩预增' },
  ]);
  const [stocks] = useState<Stock[]>([
    { code: '600519', name: '贵州茅台', price: 1850, change: 2.8, strategy: '追涨', status: 'observing' },
    { code: '300750', name: '宁德时代', price: 275, change: -1.8, strategy: '低吸', status: 'pending' },
    { code: '002594', name: '比亚迪', price: 268, change: 3.1, strategy: '追涨', status: 'holding' },
  ]);
  const [alerts] = useState<Alert[]>([
    { stock: '300750', type: 'warning', message: '接近止损价 272 (现价275)' },
    { stock: '600519', type: 'success', message: '触发止盈条件 1850×1.05' },
  ]);
  const [capitalFlow] = useState<CapitalFlow>({
    mainInflow: [
      { sector: '芯片', amount: '28亿', stocks: ['中芯国际', '寒武纪'] },
      { sector: '新能源车', amount: '15亿', stocks: ['比亚迪', '宁德时代'] },
    ],
    mainOutflow: [
      { sector: '房地产', amount: '5.2亿' },
      { sector: '医药', amount: '3.8亿' },
    ],
    northMoney: { in: 45.6, out: 32.1, net: 13.5 },
  });
  const [sentimentPhase, setSentimentPhase] = useState<SentimentPhase>({
    phase: '分歧',
    description: '龙头分歧加大，跟风股分化',
    advice: '控制仓位，低吸为主，避免追高',
  });
  const sentimentPhases = [
    { phase: '冰点', description: '市场情绪最低迷', advice: '等待企稳，关注逆势抗跌股' },
    { phase: '回暖', description: '资金开始试探', advice: '小仓位试错，观察持续性' },
    { phase: '高潮', description: '普涨行情', advice: '持股待涨，不宜追新' },
    { phase: '分歧', description: '高位震荡，分歧加大', advice: '控制仓位，边打边撤' },
    { phase: '退潮', description: '亏钱效应扩散', advice: '空仓休息，避免抄底' },
  ];
  const [review, setReview] = useState<Review>({
    preMarket: { sentiment: '', sectors: [], targetStocks: [], planBasis: '' },
    postMarket: { executed: [], mistakes: '', lessons: '' },
  });

  const handleTrade = (stock: Stock, type: 'buy' | 'sell') => {
    console.log(`${type} ${stock.name}`);
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      observing: '观察中',
      pending: '待买',
      holding: '持仓中',
    };
    return labels[status] || status;
  };

  const getStatusClass = (status: string) => {
    const classes: Record<string, string> = {
      observing: 'observing',
      pending: 'pending',
      holding: 'holding',
    };
    return classes[status] || '';
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>今日计划</h1>
        <span className="date">{dayjs().format('YYYY-MM-DD')}</span>
      </div>

      <div className="market-tabs">
        <button
          className={`market-tab ${activeTab === 'pre' ? 'active' : ''}`}
          onClick={() => setActiveTab('pre')}
        >
          <span className="tab-icon">🌅</span>
          <span className="tab-label">盘前</span>
          <span className="tab-desc">制定计划</span>
        </button>
        <button
          className={`market-tab ${activeTab === 'in' ? 'active' : ''}`}
          onClick={() => setActiveTab('in')}
        >
          <span className="tab-icon">⚡</span>
          <span className="tab-label">盘中</span>
          <span className="tab-desc">执行监控</span>
        </button>
        <button
          className={`market-tab ${activeTab === 'post' ? 'active' : ''}`}
          onClick={() => setActiveTab('post')}
        >
          <span className="tab-icon">📊</span>
          <span className="tab-label">盘后</span>
          <span className="tab-desc">复盘总结</span>
        </button>
      </div>

      {activeTab === 'pre' && (
        <div className="tab-content">
          <div className="plan-section">
            <h3>大盘</h3>
            <div className="market-grid">
              {marketData.map((market, i) => (
                <div key={i} className="market-card">
                  <div className="market-header">
                    <span className="market-name">{market.index}</span>
                    <span className={`market-change ${market.change >= 0 ? 'positive' : 'negative'}`}>
                      {market.change >= 0 ? '+' : ''}{market.change}%
                    </span>
                  </div>
                  <div className="market-points">{market.points}</div>
                  <div className="market-range">
                    <span>支撑 {market.support}</span>
                    <span>压力 {market.resistance}</span>
                  </div>
                </div>
              ))}
              <div className="market-card sentiment-card">
                <div className="market-header">
                  <span className="market-name">情绪周期</span>
                  <span className="sentiment-phase">{sentimentPhase.phase}</span>
                </div>
                <div className="sentiment-info">
                  <p className="sentiment-desc">{sentimentPhase.description}</p>
                  <p className="sentiment-advice">{sentimentPhase.advice}</p>
                </div>
                <select
                  className="sentiment-select"
                  value={sentimentPhase.phase}
                  onChange={(e) => {
                    const phase = sentimentPhases.find(p => p.phase === e.target.value);
                    if (phase) setSentimentPhase(phase);
                  }}
                >
                  {sentimentPhases.map((s) => (
                    <option key={s.phase} value={s.phase}>{s.phase}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="plan-section">
            <h3>资金流向</h3>
            <div className="flow-grid">
              <div className="flow-card inflow">
                <h4>主力流入</h4>
                {capitalFlow.mainInflow.map((flow, i) => (
                  <div key={i} className="flow-item">
                    <span className="flow-sector">{flow.sector}</span>
                    <span className="flow-amount">{flow.amount}</span>
                    <span className="flow-stocks">{flow.stocks.join(', ')}</span>
                  </div>
                ))}
              </div>
              <div className="flow-card outflow">
                <h4>主力流出</h4>
                {capitalFlow.mainOutflow.map((flow, i) => (
                  <div key={i} className="flow-item">
                    <span className="flow-sector">{flow.sector}</span>
                    <span className="flow-amount negative">{flow.amount}</span>
                  </div>
                ))}
              </div>
              <div className="flow-card north-money">
                <h4>北向资金</h4>
                <div className="north-summary">
                  <span>流入 <b className="positive">{capitalFlow.northMoney.in}亿</b></span>
                  <span>流出 <b className="negative">{capitalFlow.northMoney.out}亿</b></span>
                  <span>净流入 <b className={capitalFlow.northMoney.net >= 0 ? 'positive' : 'negative'}>
                    {capitalFlow.northMoney.net >= 0 ? '+' : ''}{capitalFlow.northMoney.net}亿
                  </b></span>
                </div>
              </div>
            </div>
          </div>

          <div className="plan-section">
            <h3>板块</h3>
            <div className="sector-list">
              {sectors.map((sector, i) => (
                <div key={i} className={`sector-item sector-${sector.type}`}>
                  <span className="sector-name">{sector.name}</span>
                  <span className={`sector-change ${sector.change >= 0 ? 'positive' : 'negative'}`}>
                    {sector.change >= 0 ? '+' : ''}{sector.change}%
                  </span>
                  {sector.leader && <span className="sector-leader">龙头: {sector.leader}</span>}
                  {sector.type === 'main' && <span className="sector-tag">主线</span>}
                  {sector.type === 'rotation' && <span className="sector-tag">轮动</span>}
                  {sector.type === 'watch' && <span className="sector-tag">观察</span>}
                </div>
              ))}
            </div>
          </div>

          <div className="plan-section">
            <h3>消息面</h3>
            <div className="news-list">
              {news.map((item, i) => (
                <div key={i} className="news-item">
                  <span className={`news-type ${item.type}`}>{item.type}</span>
                  <span className="news-content">{item.content}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="plan-section">
            <h3>盘前计划</h3>
            <div className="review-form">
              <div className="form-row">
                <div className="form-group">
                  <label>情绪周期</label>
                  <select
                    value={review.preMarket.sentiment}
                    onChange={(e) => setReview({ ...review, preMarket: { ...review.preMarket, sentiment: e.target.value } })}
                  >
                    <option value="">请选择</option>
                    {sentimentPhases.map((s) => (
                      <option key={s.phase} value={s.phase}>{s.phase}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>关注板块</label>
                  <input
                    value={review.preMarket.sectors.join(', ')}
                    onChange={(e) => setReview({ ...review, preMarket: { ...review.preMarket, sectors: e.target.value.split(',').map(s => s.trim()) } })}
                    placeholder="芯片,新能源,AI"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>目标股票</label>
                  <input
                    value={review.preMarket.targetStocks.join(', ')}
                    onChange={(e) => setReview({ ...review, preMarket: { ...review.preMarket, targetStocks: e.target.value.split(',').map(s => s.trim()) } })}
                    placeholder="600519,300750"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>计划依据</label>
                <textarea
                  value={review.preMarket.planBasis}
                  onChange={(e) => setReview({ ...review, preMarket: { ...review.preMarket, planBasis: e.target.value } })}
                  placeholder="今日操作计划依据..."
                  rows={3}
                />
              </div>
              <button className="btn btn-primary">保存盘前计划</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'in' && (
        <div className="tab-content">
          <div className="plan-section">
            <h3>关注股票</h3>
            <div className="stock-table">
              <table>
                <thead>
                  <tr>
                    <th>股票</th>
                    <th>现价</th>
                    <th>涨跌幅</th>
                    <th>策略</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {stocks.map((stock, i) => (
                    <tr key={i}>
                      <td>
                        <div className="stock-cell">
                          <span className="stock-name">{stock.name}</span>
                          <span className="stock-code">{stock.code}</span>
                        </div>
                      </td>
                      <td>¥{stock.price}</td>
                      <td className={stock.change >= 0 ? 'positive' : 'negative'}>
                        {stock.change >= 0 ? '+' : ''}{stock.change}%
                      </td>
                      <td>{stock.strategy}</td>
                      <td>
                        <span className={`status-tag ${getStatusClass(stock.status)}`}>
                          {getStatusLabel(stock.status)}
                        </span>
                      </td>
                      <td>
                        <div className="action-btns">
                          {stock.status !== 'holding' && (
                            <button className="action-btn success" onClick={() => handleTrade(stock, 'buy')}>
                              买
                            </button>
                          )}
                          {stock.status === 'holding' && (
                            <button className="action-btn danger" onClick={() => handleTrade(stock, 'sell')}>
                              卖
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {alerts.length > 0 && (
            <div className="plan-section">
              <h3>监控提醒</h3>
              <div className="alert-list">
                {alerts.map((alert, i) => (
                  <div key={i} className={`alert-item alert-${alert.type}`}>
                    <span className="alert-icon">{alert.type === 'warning' ? '⚠️' : '✓'}</span>
                    <span className="alert-stock">{alert.stock}</span>
                    <span className="alert-message">{alert.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'post' && (
        <div className="tab-content">
          <div className="plan-section">
            <h3>操作记录</h3>
            <div className="executed-list">
              <div className="executed-item">
                <span className="executed-stock">600519 贵州茅台</span>
                <span className="executed-action">买入</span>
                <span className="executed-result positive">+2.8%</span>
              </div>
              <div className="executed-item">
                <span className="executed-stock">300750 宁德时代</span>
                <span className="executed-action">卖出</span>
                <span className="executed-result negative">-1.2%</span>
              </div>
            </div>
          </div>

          <div className="plan-section">
            <h3>盘后复盘</h3>
            <div className="review-form">
              <div className="form-group">
                <label>失误记录</label>
                <textarea
                  value={review.postMarket.mistakes}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, mistakes: e.target.value } })}
                  placeholder="今日操作中的失误..."
                  rows={2}
                />
              </div>
              <div className="form-group">
                <label>心得体会</label>
                <textarea
                  value={review.postMarket.lessons}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, lessons: e.target.value } })}
                  placeholder="今日操作总结..."
                  rows={3}
                />
              </div>
              <button className="btn btn-primary">保存盘后总结</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
