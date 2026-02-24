import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface CandidateStock {
  code: string;
  name: string;
  buy_reason: string;
  sell_reason: string;
  priority: number;
  strategy_id?: number;
  strategy_name?: string;
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

interface StockStatus {
  code: string;
  status: 'pending' | 'bought' | 'abandoned';
  price?: number;
  quantity?: number;
}

export default function TodayPlan() {
  const [activeTab, setActiveTab] = useState<'pre' | 'in' | 'post'>('pre');
  const [todayPlan, setTodayPlan] = useState<PrePlan | null>(null);
  const [candidateStocks, setCandidateStocks] = useState<CandidateStock[]>([]);
  const [stockStatuses, setStockStatuses] = useState<Record<string, StockStatus>>({});
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  const [postReview, setPostReview] = useState({
    sentiment_record: '',
    mistake_record: '',
    insights: '',
    tomorrow_plan: '',
  });
  const [savingReview, setSavingReview] = useState(false);

  const [tradeModal, setTradeModal] = useState<{
    show: boolean;
    type: 'buy' | 'sell';
    stock: CandidateStock | null;
    price: string;
    quantity: string;
    loading: boolean;
  }>({
    show: false,
    type: 'buy',
    stock: null,
    price: '',
    quantity: '',
    loading: false,
  });

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
            const uniqueStocks = Array.from<unknown>(
              new Map(parsed.map((s: CandidateStock) => [s.code, s])).values()
            ) as CandidateStock[];
            setCandidateStocks(uniqueStocks);
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

  const loadPostReview = async () => {
    try {
      const res = await axios.get('/api/plan/post', { params: { trade_date: today } });
      if (res.data) {
        setPostReview({
          sentiment_record: res.data.sentiment_record || '',
          mistake_record: res.data.mistake_record || '',
          insights: res.data.insights || '',
          tomorrow_plan: res.data.tomorrow_plan || '',
        });
      }
    } catch (err) {
      console.error('Failed to load post review:', err);
    }
  };

  const savePostReview = async () => {
    setSavingReview(true);
    try {
      await axios.put('/api/plan/post', {
        trade_date: today,
        ...postReview,
      });
      alert('复盘已保存');
    } catch (err) {
      console.error('Failed to save post review:', err);
      alert('保存失败');
    } finally {
      setSavingReview(false);
    }
  };

  const openBuyModal = (stock: CandidateStock) => {
    setTradeModal({
      show: true,
      type: 'buy',
      stock,
      price: '',
      quantity: '',
      loading: false,
    });
  };

  const openSellModal = (stock: CandidateStock) => {
    setTradeModal({
      show: true,
      type: 'sell',
      stock,
      price: '',
      quantity: '',
      loading: false,
    });
  };

  const handleTrade = async () => {
    if (!tradeModal.stock || !tradeModal.price || !tradeModal.quantity) {
      alert('请填写价格和数量');
      return;
    }
    const price = parseFloat(tradeModal.price);
    const quantity = parseInt(tradeModal.quantity);
    if (isNaN(price) || isNaN(quantity) || price <= 0 || quantity <= 0) {
      alert('请输入有效的价格和数量');
      return;
    }

    const amount = price * quantity;
    const fee = amount * 0.0003;
    const reason = tradeModal.type === 'buy' 
      ? tradeModal.stock.buy_reason 
      : tradeModal.stock.sell_reason || '手动卖出';

    setTradeModal(prev => ({ ...prev, loading: true }));
    try {
      await axios.post('/api/trades', {
        stock_code: tradeModal.stock.code,
        stock_name: tradeModal.stock.name,
        trade_type: tradeModal.type === 'buy' ? '买入' : '卖出',
        price,
        quantity,
        amount,
        fee,
        reason,
        trade_date: today,
        trade_time: dayjs().format('HH:mm:ss'),
      });

      if (tradeModal.type === 'buy') {
        updateStockStatus(tradeModal.stock.code, 'bought', price, quantity);
      } else {
        updateStockStatus(tradeModal.stock.code, 'abandoned', price, quantity);
      }

      setTradeModal(prev => ({ ...prev, show: false }));
      loadTrades();
      alert(tradeModal.type === 'buy' ? '买入成功' : '卖出成功');
    } catch (err) {
      console.error('Failed to record trade:', err);
      alert('操作失败');
    } finally {
      setTradeModal(prev => ({ ...prev, loading: false }));
    }
  };

  const updateStockStatus = (code: string, status: 'pending' | 'bought' | 'abandoned', price?: number, quantity?: number) => {
    setStockStatuses(prev => ({
      ...prev,
      [code]: { code, status, price, quantity }
    }));
  };

  useEffect(() => {
    if (activeTab === 'post') {
      loadPostReview();
    }
  }, [activeTab]);

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
                <div className="market-env-section">
                  <div className="env-card">
                    <h4>📊 关注指标</h4>
                    <div className="indicator-tags compact">
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
                  <div className="env-card">
                    <h4>📰 关注消息</h4>
                    <div className="indicator-tags compact">
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
                </div>

                <div className="plan-section">
                  <h3>📈 候选股票 ({candidateStocks.length})</h3>
                  <div className="plan-meta-row">
                    {todayPlan.sentiment && (
                      <span className="meta-tag sentiment">情绪: {todayPlan.sentiment}</span>
                    )}
                    {todayPlan.external_signals && (
                      <span className="meta-tag board">板块: {todayPlan.external_signals}</span>
                    )}
                    {todayPlan.entry_condition && (
                      <span className="meta-tag entry">买入: {todayPlan.entry_condition}</span>
                    )}
                    {todayPlan.exit_condition && (
                      <span className="meta-tag exit">卖出: {todayPlan.exit_condition}</span>
                    )}
                  </div>
                  {candidateStocks.length === 0 ? (
                    <div className="empty-tip">暂无候选股票</div>
                  ) : (() => {
                    const grouped = candidateStocks.reduce((acc, stock) => {
                      const key = stock.strategy_name || '未分组';
                      if (!acc[key]) acc[key] = [];
                      acc[key].push(stock);
                      return acc;
                    }, {} as Record<string, CandidateStock[]>);
                    return Object.entries(grouped).map(([strategyName, stocks]) => (
                      <div key={strategyName} className="strategy-group">
                        <h4 className="strategy-group-title">📋 {strategyName}</h4>
                        <div className="candidate-grid">
                          {stocks.map((stock, idx) => (
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
                      </div>
                    ));
                  })()}
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
                {candidateStocks.length === 0 ? (
                  <div className="empty-tip">暂无候选股票</div>
                ) : (() => {
                  const grouped = candidateStocks.reduce((acc, stock) => {
                    const key = stock.strategy_name || '未分组';
                    if (!acc[key]) acc[key] = [];
                    acc[key].push(stock);
                    return acc;
                  }, {} as Record<string, CandidateStock[]>);
                  return Object.entries(grouped).map(([strategyName, stocks]) => (
                    <div key={strategyName} className="candidate-section">
                      <h3>📈 {strategyName} - 盘中执行</h3>
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
                            {stocks.map((stock, idx) => {
                              const status = stockStatuses[stock.code]?.status || 'pending';
                              return (
                              <tr key={idx}>
                                <td>
                                  <div className="stock-cell">
                                    <span className="stock-name">{stock.name}</span>
                                    <span className="stock-code">{stock.code}</span>
                                  </div>
                                </td>
                                <td className="reason-cell">{stock.buy_reason}</td>
                                <td>
                                  <span className={`status-tag ${status}`}>
                                    {status === 'pending' ? '待买' : status === 'bought' ? '已买' : '放弃'}
                                  </span>
                                </td>
                                <td style={{ display: 'flex', gap: '4px' }}>
                                  {status === 'pending' && (
                                    <>
                                      <button
                                        className="btn-action buy"
                                        onClick={() => openBuyModal(stock)}
                                      >
                                        买入
                                      </button>
                                      <button
                                        className="btn-action abandon"
                                        onClick={() => updateStockStatus(stock.code, 'abandoned')}
                                      >
                                        放弃
                                      </button>
                                    </>
                                  )}
                                  {status === 'bought' && (
                                    <button
                                      className="btn-action sell"
                                      onClick={() => openSellModal(stock)}
                                    >
                                      卖出
                                    </button>
                                  )}
                                  {status === 'abandoned' && (
                                    <button
                                      className="btn-action"
                                      onClick={() => updateStockStatus(stock.code, 'pending')}
                                      style={{ fontSize: '11px', padding: '4px 8px' }}
                                    >
                                      恢复
                                    </button>
                                  )}
                                </td>
                              </tr>
                              )})}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ));
                })()}

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

                <div className="plan-vs-actual">
                  <h3>📋 计划 vs 实际</h3>
                  <div className="plan-vs-table">
                    <table>
                      <thead>
                        <tr>
                          <th>股票</th>
                          <th>计划买入</th>
                          <th>实际买入</th>
                          <th>状态</th>
                        </tr>
                      </thead>
                      <tbody>
                        {candidateStocks.map((stock, idx) => {
                          const status = stockStatuses[stock.code]?.status;
                          const isPlanned = true;
                          const isBought = status === 'bought';
                          const isAbandoned = status === 'abandoned';
                          return (
                            <tr key={idx}>
                              <td>
                                <div className="stock-cell">
                                  <span className="stock-name">{stock.name}</span>
                                  <span className="stock-code">{stock.code}</span>
                                </div>
                              </td>
                              <td>
                                <span className="plan-status planned">计划</span>
                              </td>
                              <td>
                                {isBought && <span className="plan-status bought">已买</span>}
                                {isAbandoned && <span className="plan-status abandoned">放弃</span>}
                                {!isBought && !isAbandoned && <span className="plan-status pending">未买</span>}
                              </td>
                              <td>
                                {isBought && <span className="exec-status success">✓</span>}
                                {isAbandoned && <span className="exec-status abandoned">✗</span>}
                                {!isBought && !isAbandoned && <span className="exec-status missed">-</span>}
                              </td>
                            </tr>
                          );
                        })}
                        {candidateStocks.length === 0 && (
                          <tr>
                            <td colSpan={4} className="empty-tip">暂无计划</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                  <div className="plan-summary-row">
                    <span>计划买入: {candidateStocks.length}</span>
                    <span>实际买入: {Object.values(stockStatuses).filter(s => s.status === 'bought').length}</span>
                    <span>放弃: {Object.values(stockStatuses).filter(s => s.status === 'abandoned').length}</span>
                    <span>未执行: {candidateStocks.length - Object.values(stockStatuses).filter(s => s.status === 'bought' || s.status === 'abandoned').length}</span>
                  </div>
                </div>

                <div className="review-section">
                  <h3>📝 盘后复盘</h3>
                  <div className="review-form">
                    <div className="form-group">
                      <label>🌡️ 情绪记录</label>
                      <textarea 
                        placeholder="今日情绪波动: 开盘..."
                        rows={2}
                        value={postReview.sentiment_record}
                        onChange={(e) => setPostReview({ ...postReview, sentiment_record: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>❌ 失误记录</label>
                      <textarea 
                        placeholder="1. ...&#10;2. ..."
                        rows={3}
                        value={postReview.mistake_record}
                        onChange={(e) => setPostReview({ ...postReview, mistake_record: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>💡 心得体会</label>
                      <textarea 
                        placeholder="..."
                        rows={3}
                        value={postReview.insights}
                        onChange={(e) => setPostReview({ ...postReview, insights: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label>🎯 明日计划</label>
                      <textarea 
                        placeholder="1. ...&#10;2. ..."
                        rows={3}
                        value={postReview.tomorrow_plan}
                        onChange={(e) => setPostReview({ ...postReview, tomorrow_plan: e.target.value })}
                      />
                    </div>
                    <button 
                      className="btn btn-primary" 
                      onClick={savePostReview}
                      disabled={savingReview}
                    >
                      {savingReview ? '保存中...' : '保存复盘'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {tradeModal.show && (
            <div className="modal-overlay" onClick={() => setTradeModal(prev => ({ ...prev, show: false }))}>
              <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                  <h2>{tradeModal.type === 'buy' ? '买入' : '卖出'} {tradeModal.stock?.name}</h2>
                  <button className="modal-close" onClick={() => setTradeModal(prev => ({ ...prev, show: false }))}>×</button>
                </div>
                <div className="modal-body">
                  <div className="form-group">
                    <label>股票代码</label>
                    <input type="text" value={tradeModal.stock?.code || ''} disabled />
                  </div>
                  <div className="form-group">
                    <label>价格</label>
                    <input
                      type="number"
                      step="0.01"
                      value={tradeModal.price}
                      onChange={(e) => setTradeModal(prev => ({ ...prev, price: e.target.value }))}
                      placeholder="请输入价格"
                      autoFocus
                    />
                  </div>
                  <div className="form-group">
                    <label>数量(股)</label>
                    <input
                      type="number"
                      value={tradeModal.quantity}
                      onChange={(e) => setTradeModal(prev => ({ ...prev, quantity: e.target.value }))}
                      placeholder="请输入数量"
                    />
                  </div>
                  {tradeModal.price && tradeModal.quantity && (
                    <div className="trade-preview">
                      <span>预估金额: ¥{(parseFloat(tradeModal.price) * parseInt(tradeModal.quantity)).toLocaleString()}</span>
                    </div>
                  )}
                </div>
                <div className="modal-footer">
                  <button className="btn" onClick={() => setTradeModal(prev => ({ ...prev, show: false }))}>取消</button>
                  <button
                    className={`btn ${tradeModal.type === 'buy' ? 'btn-primary' : 'btn-danger'}`}
                    onClick={handleTrade}
                    disabled={tradeModal.loading}
                  >
                    {tradeModal.loading ? '提交中...' : (tradeModal.type === 'buy' ? '确认买入' : '确认卖出')}
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
