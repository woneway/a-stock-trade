import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface CandidateStock {
  code: string;
  name: string;
  buy_reason: string;
  sell_reason: string;
  priority: number;
}

interface PrePlan {
  id?: number;
  trade_date?: string;
  plan_date?: string;
  selected_strategy?: string;
  watch_indicators?: string;
  watch_messages?: string;
  candidate_stocks?: string;
  plan_basis?: string;
  entry_condition?: string;
  exit_condition?: string;
  status?: string;
  sentiment?: string;
  external_signals?: string;
}

interface Trade {
  id: number;
  stock_code: string;
  stock_name: string;
  trade_type: string;
  price: number;
  quantity: number;
  amount: number;
  fee: number;
  reason?: string;
  pnl?: number;
  trade_date: string;
}

const DEFAULT_INDICATORS = [
  '涨停数量', '跌停数量', '上涨家数', '下跌家数',
  '连板数量', '首板数量', '昨日涨停表现', '成交额',
];

const DEFAULT_MESSAGES = [
  '政策消息', '行业公告', '个股公告', '外围市场', '龙虎榜数据',
];

export default function TodayPlan() {
  const [activeTab, setActiveTab] = useState<'pre' | 'in' | 'post'>('pre');
  const [todayPlan, setTodayPlan] = useState<PrePlan | null>(null);
  const [candidateStocks, setCandidateStocks] = useState<CandidateStock[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  const today = dayjs().format('YYYY-MM-DD');

  useEffect(() => {
    loadTodayPlan();
    loadTrades();
  }, []);

  const loadTodayPlan = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/plan/pre', { params: { trade_date: today } });
      if (res.data) {
        setTodayPlan(res.data);
        if (res.data.candidate_stocks) {
          try {
            const parsed = typeof res.data.candidate_stocks === 'string'
              ? JSON.parse(res.data.candidate_stocks)
              : res.data.candidate_stocks;
            setCandidateStocks(parsed);
          } catch (e) {
            console.error('Parse candidate_stocks error:', e);
          }
        }
      }
    } catch (err) {
      console.error('Failed to load today plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTrades = async () => {
    try {
      const res = await axios.get('/api/trades');
      setTrades(res.data?.filter((t: Trade) => t.trade_date === today) || []);
    } catch (err) {
      console.error('Failed to load trades:', err);
    }
  };

  const watchIndicators = todayPlan?.watch_indicators?.split(',').filter(Boolean) || [];
  const watchMessages = todayPlan?.watch_messages?.split(',').filter(Boolean) || [];

  const toggleIndicator = async (indicator: string) => {
    if (!todayPlan?.id) return;
    const current = todayPlan?.watch_indicators?.split(',').filter(Boolean) || [];
    const updated = current.includes(indicator)
      ? current.filter(i => i !== indicator)
      : [...current, indicator];
    await savePlan({ watch_indicators: updated.join(',') });
  };

  const toggleMessage = async (message: string) => {
    if (!todayPlan?.id) return;
    const current = todayPlan?.watch_messages?.split(',').filter(Boolean) || [];
    const updated = current.includes(message)
      ? current.filter(m => m !== message)
      : [...current, message];
    await savePlan({ watch_messages: updated.join(',') });
  };

  const savePlan = async (updates: Partial<PrePlan>) => {
    if (!todayPlan?.id) return;
    try {
      await axios.put(`/api/plan/pre/${todayPlan.id}`, updates);
      setTodayPlan({ ...todayPlan, ...updates });
    } catch (err) {
      console.error('Failed to save plan:', err);
    }
  };

  const handleConfirmPlan = async () => {
    if (!todayPlan?.id) return;
    try {
      await axios.post(`/api/plan/pre/${todayPlan.id}/confirm`);
      setTodayPlan({ ...todayPlan, status: 'confirmed' });
      alert('计划已确认');
    } catch (err) {
      console.error('Failed to confirm plan:', err);
    }
  };

  const getStatusBadge = (status?: string) => {
    const statusMap: Record<string, { text: string; class: string }> = {
      'draft': { text: '草稿', class: 'draft' },
      'confirmed': { text: '已确认', class: 'confirmed' },
      'completed': { text: '已完成', class: 'completed' },
    };
    const s = statusMap[status || 'draft'];
    return <span className={`status-badge ${s.class}`}>{s.text}</span>;
  };

  const totalPnl = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
  const totalAmount = trades.reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>今日计划</h1>
          <span className="date">{today} {dayjs().format('dddd')}</span>
        </div>
        {todayPlan && getStatusBadge(todayPlan.status)}
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : !todayPlan ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div className="empty-text">今日暂无计划</div>
          <a href="/plans" className="btn btn-primary">去创建计划</a>
        </div>
      ) : (
        <>
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

          <div className="tab-content">
            {activeTab === 'pre' && (
              <div className="pre-market">
                <div className="plan-summary-card">
                  <div className="plan-summary-header">
                    <h3>🎯 今日策略: {todayPlan.selected_strategy || '未选择'}</h3>
                  </div>
                  {todayPlan.entry_condition && (
                    <div className="plan-condition">
                      <span className="condition-label">买入条件:</span>
                      <span className="condition-text">{todayPlan.entry_condition}</span>
                    </div>
                  )}
                  {todayPlan.exit_condition && (
                    <div className="plan-condition">
                      <span className="condition-label">卖出条件:</span>
                      <span className="condition-text">{todayPlan.exit_condition}</span>
                    </div>
                  )}
                  {todayPlan.plan_basis && (
                    <div className="plan-condition">
                      <span className="condition-label">计划依据:</span>
                      <span className="condition-text">{todayPlan.plan_basis}</span>
                    </div>
                  )}
                </div>

                <div className="plan-section">
                  <h3>📊 关注指标</h3>
                  <div className="indicator-tags">
                    {DEFAULT_INDICATORS.map(indicator => (
                      <span
                        key={indicator}
                        className={`tag ${watchIndicators.includes(indicator) ? 'active' : ''}`}
                        onClick={() => todayPlan?.id && toggleIndicator(indicator)}
                      >
                        {indicator}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="plan-section">
                  <h3>📰 关注消息</h3>
                  <div className="indicator-tags">
                    {DEFAULT_MESSAGES.map(message => (
                      <span
                        key={message}
                        className={`tag ${watchMessages.includes(message) ? 'active' : ''}`}
                        onClick={() => todayPlan?.id && toggleMessage(message)}
                      >
                        {message}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="plan-section">
                  <h3>📈 候选股票 ({candidateStocks.length})</h3>
                  {candidateStocks.length === 0 ? (
                    <div className="empty-tip">暂无候选股票</div>
                  ) : (
                    <div className="candidate-grid">
                      {candidateStocks.map((stock, idx) => (
                        <div key={idx} className="candidate-card">
                          <div className="candidate-header">
                            <span className="stock-name">{stock.name}</span>
                            <span className="stock-code">{stock.code}</span>
                          </div>
                          <div className="candidate-reason">
                            <span className="reason-label">买:</span> {stock.buy_reason}
                          </div>
                          {stock.sell_reason && (
                            <div className="candidate-reason">
                              <span className="reason-label">卖:</span> {stock.sell_reason}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {todayPlan.status === 'draft' && (
                  <div className="action-bar">
                    <a href="/plans" className="btn">编辑计划</a>
                    <button className="btn btn-primary" onClick={handleConfirmPlan}>
                      确认计划
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'in' && (
              <div className="in-market">
                <div className="candidate-section">
                  <h3>📈 候选股票池</h3>
                  {candidateStocks.length === 0 ? (
                    <div className="empty-tip">暂无候选股票</div>
                  ) : (
                    <div className="stock-table">
                      <table>
                        <thead>
                          <tr>
                            <th>股票</th>
                            <th>买入理由</th>
                            <th>状态</th>
                            <th>操作</th>
                          </tr>
                        </thead>
                        <tbody>
                          {candidateStocks.map((stock, idx) => (
                            <tr key={idx}>
                              <td>
                                <div className="stock-cell">
                                  <span className="stock-name">{stock.name}</span>
                                  <span className="stock-code">{stock.code}</span>
                                </div>
                              </td>
                              <td className="reason-cell">{stock.buy_reason}</td>
                              <td><span className="status-tag pending">待买</span></td>
                              <td>
                                <button className="btn-action buy">买入</button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                <div className="trades-section">
                  <h3>📋 今日成交 ({trades.length})</h3>
                  {trades.length === 0 ? (
                    <div className="empty-tip">今日暂无成交</div>
                  ) : (
                    <div className="stock-table">
                      <table>
                        <thead>
                          <tr>
                            <th>股票</th>
                            <th>操作</th>
                            <th>价格</th>
                            <th>数量</th>
                            <th>金额</th>
                            <th>理由</th>
                          </tr>
                        </thead>
                        <tbody>
                          {trades.map((trade, idx) => (
                            <tr key={idx}>
                              <td>
                                <div className="stock-cell">
                                  <span className="stock-name">{trade.stock_name}</span>
                                  <span className="stock-code">{trade.stock_code}</span>
                                </div>
                              </td>
                              <td>
                                <span className={`action-tag ${trade.trade_type === '买入' ? 'buy' : 'sell'}`}>
                                  {trade.trade_type}
                                </span>
                              </td>
                              <td>¥{trade.price}</td>
                              <td>{trade.quantity}</td>
                              <td>¥{trade.amount.toLocaleString()}</td>
                              <td>{trade.reason}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'post' && (
              <div className="post-market">
                <div className="trades-summary">
                  <h3>📊 今日交易汇总</h3>
                  <div className="summary-stats">
                    <div className="stat-card">
                      <span className="stat-value">{trades.length}</span>
                      <span className="stat-label">成交次数</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-value">
                        ¥{totalAmount.toLocaleString()}
                      </span>
                      <span className="stat-label">总成交金额</span>
                    </div>
                    <div className="stat-card">
                      <span className={`stat-value ${totalPnl >= 0 ? 'positive' : 'negative'}`}>
                        {totalPnl >= 0 ? '+' : ''}¥{totalPnl.toLocaleString()}
                      </span>
                      <span className="stat-label">总盈亏</span>
                    </div>
                  </div>
                </div>

                <div className="review-section">
                  <h3>📝 盘后复盘</h3>
                  <div className="review-form">
                    <div className="form-group">
                      <label>🌡️ 情绪记录</label>
                      <textarea placeholder="今日情绪波动: 开盘..." rows={2} />
                    </div>
                    <div className="form-group">
                      <label>❌ 失误记录</label>
                      <textarea placeholder="1. ...&#10;2. ..." rows={3} />
                    </div>
                    <div className="form-group">
                      <label>💡 心得体会</label>
                      <textarea placeholder="..." rows={3} />
                    </div>
                    <div className="form-group">
                      <label>🎯 明日计划</label>
                      <textarea placeholder="1. ...&#10;2. ..." rows={3} />
                    </div>
                    <button className="btn btn-primary">保存复盘</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
