import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface Strategy {
  id: number;
  name: string;
  description?: string;
  stock_selection_logic?: string;
  entry_condition?: string;
  exit_condition?: string;
  stop_loss: number;
  position_size: number;
  is_active: boolean;
}

interface CandidateStock {
  code: string;
  name: string;
  buy_reason: string;
  sell_reason: string;
  priority: number;
}

interface CandidateStockInput {
  code: string;
  name: string;
  buy_reason: string;
  sell_reason: string;
  priority: number;
}

interface ScannedStock {
  code: string;
  name: string;
  score: number;
  change?: number;
  limit_consecutive: number;
  entry_advice: { signal: string; trigger_type?: string };
}

interface StrategyStocks {
  strategyId: number;
  strategyName: string;
  stocks: ScannedStock[];
  selectedStocks: string[];
  scanning: boolean;
}

interface PrePlan {
  id?: number;
  strategy_ids?: string;
  selected_strategy?: string;
  sentiment?: string;
  external_signals?: string;
  sectors?: string;
  candidate_stocks?: string;
  plan_basis?: string;
  stop_loss?: number;
  position_size?: number;
  entry_condition?: string;
  exit_condition?: string;
  status?: string;
  plan_date?: string;
  trade_date?: string;
  created_at?: string;
  watch_indicators?: string;
  watch_messages?: string;
}

interface Trade {
  id: number;
  trade_date: string;
  stock_code: string;
  stock_name: string;
  trade_type: string;
  price: number;
  quantity: number;
  amount: number;
  fee: number;
  reason?: string;
  pnl?: number;
  pnl_percent?: number;
}

interface PlanRecord {
  id: number;
  date: string;
  tradeCount: number;
  profit: number;
  strategy?: string;
  stocks?: {
    code: string;
    name: string;
    signal?: 'buy' | 'sell' | 'watch' | 'none';
    reason?: string;
  }[];
  trades?: { time: string; stock: string; type: string; price: number; quantity: number; result?: number }[];
  prePlan?: PrePlan;
}

export default function PlanList() {
  const [currentMonth, setCurrentMonth] = useState(dayjs());
  const [selectedPlan, setSelectedPlan] = useState<PlanRecord | null>(null);
  const [plans, setPlans] = useState<PlanRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState<PrePlan | null>(null);
  const [editingStrategyIds, setEditingStrategyIds] = useState<number[]>([]);
  const [editingStrategyStocks, setEditingStrategyStocks] = useState<StrategyStocks[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategyIds, setSelectedStrategyIds] = useState<number[]>([]);
  const [strategyStocks, setStrategyStocks] = useState<StrategyStocks[]>([]);
  const [creatingPlan, setCreatingPlan] = useState(false);
  const [createPlanDate, setCreatePlanDate] = useState(dayjs().format('YYYY-MM-DD'));
  const [createWatchIndicators, setCreateWatchIndicators] = useState<string[]>(['涨停数量', '下跌家数', '连板数量']);
  const [createWatchMessages, setCreateWatchMessages] = useState<string[]>(['政策消息', '外围市场']);

  useEffect(() => {
    loadPlans();
    loadStrategies();
  }, [currentMonth]);

  useEffect(() => {
    if (strategies.length > 0 && editingStrategyIds.length > 0) {
      setEditingStrategyStocks(prev => prev.map(s => {
        const strategy = strategies.find(str => str.id === s.strategyId);
        return { ...s, strategyName: strategy?.name || s.strategyName };
      }));
    }
  }, [strategies]);

  const loadStrategies = async () => {
    try {
      const res = await axios.get('/api/strategies');
      setStrategies(res.data.filter((s: Strategy) => s.is_active));
    } catch (err) {
      console.error('Failed to load strategies:', err);
    }
  };

  const loadPlans = async () => {
    setLoading(true);
    try {
      const startDate = currentMonth.startOf('month').format('YYYY-MM-DD');
      const endDate = currentMonth.endOf('month').format('YYYY-MM-DD');

      const [tradesRes, prePlansRes] = await Promise.all([
        axios.get('/api/trades'),
        axios.get('/api/plan/pre/list', {
          params: { start_date: startDate, end_date: endDate }
        }),
      ]);

      const trades: Trade[] = tradesRes.data || [];
      const prePlans: PrePlan[] = prePlansRes.data || [];

      const planMap = new Map<string, PlanRecord>();

      trades.forEach(trade => {
        const date = trade.trade_date;
        if (!planMap.has(date)) {
          planMap.set(date, {
            id: Date.now() + Math.random(),
            date,
            tradeCount: 0,
            profit: 0,
          });
        }
        const plan = planMap.get(date)!;
        plan.tradeCount++;
        plan.profit += trade.pnl || 0;
        if (!plan.trades) {
          plan.trades = [];
        }
        plan.trades.push({
          time: '',
          stock: trade.stock_name || trade.stock_code,
          type: trade.trade_type,
          price: trade.price,
          quantity: trade.quantity,
          result: trade.pnl,
        });
      });

      prePlans.forEach(prePlan => {
        const date = prePlan.trade_date || '';
        if (!planMap.has(date)) {
          planMap.set(date, {
            id: prePlan.id ?? 0,
            date,
            tradeCount: 0,
            profit: 0,
          });
        }
        const plan = planMap.get(date)!;
        plan.strategy = prePlan.selected_strategy;
        plan.prePlan = prePlan;
      });

      const sortedPlans = Array.from(planMap.values()).sort((a, b) =>
        dayjs(b.date).valueOf() - dayjs(a.date).valueOf()
      );

      setPlans(sortedPlans);
    } catch (err) {
      console.error('Failed to load plans:', err);
      setPlans([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleStrategy = (id: number) => {
    setSelectedStrategyIds(prev =>
      prev.includes(id)
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
  };

  const scanStrategyStocks = async (strategyId: number, strategyName: string) => {
    setStrategyStocks(prev => prev.map(s => 
      s.strategyId === strategyId ? { ...s, scanning: true } : s
    ));
    try {
      const res = await axios.post('/api/strategy/scan', { strategy_id: strategyId });
      const results = res.data.results || [];
      setStrategyStocks(prev => prev.map(s => 
        s.strategyId === strategyId ? { ...s, stocks: results, scanning: false } : s
      ));
    } catch (err) {
      console.error('Scan failed:', err);
      setStrategyStocks(prev => prev.map(s => 
        s.strategyId === strategyId ? { ...s, scanning: false } : s
      ));
    }
  };

  const toggleStockSelection = (strategyId: number, code: string) => {
    setStrategyStocks(prev => prev.map(s => {
      if (s.strategyId !== strategyId) return s;
      const selected = s.selectedStocks.includes(code)
        ? s.selectedStocks.filter(c => c !== code)
        : [...s.selectedStocks, code];
      return { ...s, selectedStocks: selected };
    }));
  };

  const toggleEditingStrategy = (id: number) => {
    setEditingStrategyIds(prev =>
      prev.includes(id)
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
    if (!editingStrategyIds.includes(id)) {
      const strategy = strategies.find(s => s.id === id);
      setEditingStrategyStocks(prev => [...prev, { strategyId: id, strategyName: strategy?.name || '', stocks: [], selectedStocks: [], scanning: false }]);
    } else {
      setEditingStrategyStocks(prev => prev.filter(s => s.strategyId !== id));
    }
  };

  const scanEditingStrategyStocks = async (strategyId: number, strategyName: string) => {
    setEditingStrategyStocks(prev => prev.map(s =>
      s.strategyId === strategyId ? { ...s, scanning: true } : s
    ));
    try {
      const res = await axios.post('/api/strategy/scan', { strategy_id: strategyId });
      const results = res.data.results || [];
      setEditingStrategyStocks(prev => prev.map(s =>
        s.strategyId === strategyId ? { ...s, stocks: results, scanning: false } : s
      ));
    } catch (err) {
      console.error('Scan failed:', err);
      setEditingStrategyStocks(prev => prev.map(s =>
        s.strategyId === strategyId ? { ...s, scanning: false } : s
      ));
    }
  };

  const toggleEditingStockSelection = (strategyId: number, code: string) => {
    setEditingStrategyStocks(prev => prev.map(s => {
      if (s.strategyId !== strategyId) return s;
      const selected = s.selectedStocks.includes(code)
        ? s.selectedStocks.filter(c => c !== code)
        : [...s.selectedStocks, code];
      return { ...s, selectedStocks: selected };
    }));
  };

  const handleCreatePlan = async () => {
    if (selectedStrategyIds.length === 0) {
      alert('请至少选择一个策略');
      return;
    }

    const allSelectedStocks = strategyStocks.flatMap(s => 
      s.selectedStocks.map(code => {
        const stock = s.stocks.find(st => st.code === code);
        return {
          code,
          name: stock?.name || '',
          buy_reason: stock?.entry_advice?.signal || '',
          sell_reason: '',
          priority: 1,
        };
      })
    );

    setCreatingPlan(true);
    try {
      const strategyIdsStr = selectedStrategyIds.join(',');
      await axios.post(`/api/plan/generate-from-strategies?strategy_ids=${strategyIdsStr}&trade_date=${createPlanDate}`);
      
      if (allSelectedStocks.length > 0) {
        const today = dayjs().format('YYYY-MM-DD');
        const planRes = await axios.get('/api/plan/pre', { params: { trade_date: createPlanDate } });
        if (planRes.data?.id) {
          await axios.put(`/api/plan/pre/${planRes.data.id}`, {
            candidate_stocks: JSON.stringify(allSelectedStocks),
            watch_indicators: createWatchIndicators.join(','),
            watch_messages: createWatchMessages.join(','),
          });
        }
      }
      
      alert('计划已生成');
      setShowCreateModal(false);
      setSelectedStrategyIds([]);
      setStrategyStocks([]);
      loadPlans();
    } catch (err) {
      console.error('Failed to create plan:', err);
      alert('创建计划失败');
    } finally {
      setCreatingPlan(false);
    }
  };

  const openEditModal = (plan: PlanRecord) => {
    if (!plan.prePlan) return;
    setEditingPlan(plan.prePlan);

    const strategyIds: number[] = [];
    if (plan.prePlan.strategy_ids) {
      try {
        let parsed = plan.prePlan.strategy_ids;
        if (typeof parsed === 'string') {
          parsed = parsed.trim();
          if (parsed.startsWith('[')) {
            parsed = JSON.parse(parsed);
          } else {
            parsed = parsed.split(',').map((s: string) => s.trim()).filter(Boolean);
          }
        }
        if (Array.isArray(parsed)) {
          strategyIds.push(...parsed.map((id: string | number) => typeof id === 'number' ? id : parseInt(id)).filter((id: number) => !isNaN(id)));
        }
      } catch (e) {
        console.error('Failed to parse strategy_ids:', e);
      }
    }
    setEditingStrategyIds(strategyIds);

    const strategyStocksData = strategyIds.map(id => {
      const strategy = strategies.find(s => s.id === id);
      return { strategyId: id, strategyName: strategy?.name || `策略${id}`, stocks: [], selectedStocks: [], scanning: false };
    });
    setEditingStrategyStocks(strategyStocksData);

    const stocks: CandidateStockInput[] = [];
    if (plan.prePlan.candidate_stocks) {
      try {
        let parsed = plan.prePlan.candidate_stocks;
        if (typeof parsed === 'string') {
          parsed = JSON.parse(parsed);
        }
        if (Array.isArray(parsed)) {
          stocks.push(...parsed.map((s: CandidateStock) => ({
            code: s.code || '',
            name: s.name || '',
            buy_reason: s.buy_reason || '',
            sell_reason: s.sell_reason || '',
            priority: s.priority || 0,
          })));
        }
      } catch (e) {
        console.error('Failed to parse candidate_stocks:', e);
      }
    }
    setCandidateStocksEdit(stocks);
    setShowEditModal(true);
  };

  const handleConfirmPlan = async () => {
    if (!editingPlan?.id) return;
    
    try {
      await axios.post(`/api/plan/pre/${editingPlan.id}/confirm`);
      alert('计划已确认');
      setShowEditModal(false);
      loadPlans();
    } catch (err) {
      console.error('Failed to confirm plan:', err);
      alert('确认失败');
    }
  };

  const handleSaveEdit = async () => {
    if (!editingPlan?.id) return;

    const allSelectedStocks = editingStrategyStocks.flatMap(s =>
      s.selectedStocks.map(code => {
        const stock = s.stocks.find(st => st.code === code);
        return {
          code,
          name: stock?.name || '',
          buy_reason: stock?.entry_advice?.signal || '',
          sell_reason: '',
          priority: 1,
        };
      })
    );

    try {
      await axios.put(`/api/plan/pre/${editingPlan.id}`, {
        strategy_ids: JSON.stringify(editingStrategyIds),
        candidate_stocks: JSON.stringify(allSelectedStocks),
        sentiment: editingPlan.sentiment,
        external_signals: editingPlan.external_signals,
        sectors: editingPlan.sectors,
        plan_basis: editingPlan.plan_basis,
        entry_condition: editingPlan.entry_condition,
        exit_condition: editingPlan.exit_condition,
        watch_indicators: editingPlan.watch_indicators,
        watch_messages: editingPlan.watch_messages,
      });
      alert('计划已更新');
      setShowEditModal(false);
      loadPlans();
    } catch (err) {
      console.error('Failed to update plan:', err);
      alert('更新失败');
    }
  };

  const daysInMonth = currentMonth.daysInMonth();
  const monthStart = currentMonth.startOf('month');
  const startDay = monthStart.day();

  const getPlansForDay = (day: number) => {
    const date = currentMonth.date(day).format('YYYY-MM-DD');
    return plans.filter(p => p.date === date);
  };

  const prevMonth = () => setCurrentMonth(currentMonth.subtract(1, 'month'));
  const nextMonth = () => setCurrentMonth(currentMonth.add(1, 'month'));

  return (
    <div className="page">
      <div className="page-header">
        <h1>计划列表</h1>
        <button className="btn btn-primary" onClick={() => {
          setCreatePlanDate(dayjs().format('YYYY-MM-DD'));
          setShowCreateModal(true);
        }}>
          + 新建计划
        </button>
      </div>

      <div className="calendar-header">
        <button className="calendar-nav" onClick={prevMonth}>‹</button>
        <span className="calendar-title">{currentMonth.format('YYYY年MM月')}</span>
        <button className="calendar-nav" onClick={nextMonth}>›</button>
      </div>

      <div className="plan-list">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className="plan-item"
            onClick={() => setSelectedPlan(plan)}
          >
            <div className="plan-date">
              <span className="plan-day">{dayjs(plan.date).format('MM/DD')}</span>
              <span className="plan-weekday">{dayjs(plan.date).format('ddd')}</span>
            </div>
            <div className="plan-info">
              <span className="plan-count">{plan.tradeCount}笔交易</span>
              {plan.strategy && <span className="plan-strategy">{plan.strategy}</span>}
              {plan.prePlan?.status && (
                <span className={`plan-status ${plan.prePlan.status}`}>
                  {plan.prePlan.status === 'draft' ? '草稿' :
                   plan.prePlan.status === 'confirmed' ? '已确认' : '已完成'}
                </span>
              )}
            </div>
            <div className={`plan-profit ${plan.profit >= 0 ? 'positive' : 'negative'}`}>
              {plan.profit >= 0 ? '+' : ''}¥{plan.profit.toLocaleString()}
            </div>
            <span className="plan-arrow">›</span>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal modal-fullscreen" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>新建计划 - {createPlanDate}</h2>
              <button className="modal-close" onClick={() => { setShowCreateModal(false); setSelectedStrategyIds([]); setStrategyStocks([]); }}>×</button>
            </div>

            <div className="modal-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <div>
                <div className="form-section">
                  <div className="form-section-title">📊 通用关注指标</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                    {['涨停数量', '跌停数量', '上涨家数', '下跌家数', '连板数量', '首板数量', '昨日涨停表现', '成交额'].map(item => (
                      <span
                        key={item}
                        style={{
                          padding: '4px 12px',
                          borderRadius: '16px',
                          background: createWatchIndicators.includes(item) ? '#3b82f6' : '#f1f5f9',
                          color: createWatchIndicators.includes(item) ? 'white' : '#475569',
                          cursor: 'pointer',
                          fontSize: '13px',
                        }}
                        onClick={() => setCreateWatchIndicators(prev => prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item])}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <div className="form-section-title">📰 关注消息</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                    {['政策消息', '行业公告', '个股公告', '外围市场', '龙虎榜数据'].map(item => (
                      <span
                        key={item}
                        style={{
                          padding: '4px 12px',
                          borderRadius: '16px',
                          background: createWatchMessages.includes(item) ? '#3b82f6' : '#f1f5f9',
                          color: createWatchMessages.includes(item) ? 'white' : '#475569',
                          cursor: 'pointer',
                          fontSize: '13px',
                        }}
                        onClick={() => setCreateWatchMessages(prev => prev.includes(item) ? prev.filter(i => i !== item) : [...prev, item])}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <div className="form-section">
                  <div className="form-section-title">🎯 选择策略</div>
                  <div className="strategy-select-list" style={{ marginTop: '8px', maxHeight: '400px', overflowY: 'auto' }}>
                    {strategies.map(strategy => (
                      <div
                        key={strategy.id}
                        className={`strategy-select-item ${selectedStrategyIds.includes(strategy.id) ? 'selected' : ''}`}
                        onClick={() => {
                          if (selectedStrategyIds.includes(strategy.id)) {
                            toggleStrategy(strategy.id);
                            setStrategyStocks(prev => prev.filter(s => s.strategyId !== strategy.id));
                          } else {
                            toggleStrategy(strategy.id);
                            setStrategyStocks(prev => [...prev, { strategyId: strategy.id, strategyName: strategy.name, stocks: [], selectedStocks: [], scanning: false }]);
                          }
                        }}
                      >
                        <div className="strategy-check">
                          {selectedStrategyIds.includes(strategy.id) && '✓'}
                        </div>
                        <div className="strategy-info">
                          <div className="strategy-name">{strategy.name}</div>
                          {strategy.description && <div className="strategy-desc">{strategy.description}</div>}
                          <div className="strategy-params">
                            <span>仓位: {strategy.position_size}%</span>
                            <span>止损: {strategy.stop_loss}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <div className="form-section">
                  <div className="form-section-title">📈 策略选股</div>
                  {selectedStrategyIds.length === 0 ? (
                    <div style={{ color: '#94a3b8', padding: '20px', textAlign: 'center' }}>请先选择中间列的策略</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
                      {selectedStrategyIds.map(strategyId => {
                        const strategyStock = strategyStocks.find(s => s.strategyId === strategyId);
                        const strategy = strategies.find(s => s.id === strategyId);
                        return (
                          <div key={strategyId} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                              <span style={{ fontWeight: '600' }}>{strategy?.name}</span>
                              <button
                                className="btn btn-secondary"
                                style={{ padding: '4px 12px', fontSize: '12px' }}
                                onClick={() => scanStrategyStocks(strategyId, strategy?.name || '')}
                                disabled={strategyStock?.scanning}
                              >
                                {strategyStock?.scanning ? '扫描中...' : '🔍 扫描股票'}
                              </button>
                            </div>
                            {strategyStock && strategyStock.stocks.length > 0 && (
                              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                {strategyStock.stocks.slice(0, 8).map((stock, idx) => (
                                  <div
                                    key={stock.code}
                                    style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '8px',
                                      padding: '6px 8px',
                                      background: strategyStock.selectedStocks.includes(stock.code) ? '#dbeafe' : 'transparent',
                                      borderRadius: '4px',
                                      cursor: 'pointer',
                                    }}
                                    onClick={() => toggleStockSelection(strategyId, stock.code)}
                                  >
                                    <input
                                      type="checkbox"
                                      checked={strategyStock.selectedStocks.includes(stock.code)}
                                      onChange={() => {}}
                                    />
                                    <span style={{ flex: 1 }}>{stock.code} {stock.name}</span>
                                    <span style={{ color: stock.score >= 70 ? '#16a34a' : stock.score >= 50 ? '#ca8a04' : '#94a3b8', fontWeight: '500' }}>
                                      {stock.score}分
                                    </span>
                                    <span style={{ fontSize: '12px', color: '#64748b' }}>[{stock.entry_advice?.signal}]</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn" onClick={() => { setShowCreateModal(false); setSelectedStrategyIds([]); setStrategyStocks([]); }}>取消</button>
              <button
                className="btn btn-primary"
                onClick={handleCreatePlan}
                disabled={creatingPlan || selectedStrategyIds.length === 0}
              >
                {creatingPlan ? '生成中...' : '生成计划'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showEditModal && editingPlan && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal modal-fullscreen" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>编辑计划 - {editingPlan.trade_date}</h2>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>

            <div className="modal-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <div>
                <div className="form-section">
                  <div className="form-section-title">📊 通用关注指标</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                    {['涨停数量', '跌停数量', '上涨家数', '下跌家数', '连板数量', '首板数量', '昨日涨停表现', '成交额'].map(item => (
                      <span
                        key={item}
                        style={{
                          padding: '4px 12px',
                          borderRadius: '16px',
                          background: editingPlan.watch_indicators?.includes(item) ? '#3b82f6' : '#f1f5f9',
                          color: editingPlan.watch_indicators?.includes(item) ? 'white' : '#475569',
                          cursor: 'pointer',
                          fontSize: '13px',
                        }}
                        onClick={() => {
                          const current = editingPlan.watch_indicators?.split(',').filter(Boolean) || [];
                          const updated = current.includes(item) ? current.filter(i => i !== item) : [...current, item];
                          setEditingPlan({ ...editingPlan, watch_indicators: updated.join(',') });
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <div className="form-section-title">📰 关注消息</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                    {['政策消息', '行业公告', '个股公告', '外围市场', '龙虎榜数据'].map(item => (
                      <span
                        key={item}
                        style={{
                          padding: '4px 12px',
                          borderRadius: '16px',
                          background: editingPlan.watch_messages?.includes(item) ? '#3b82f6' : '#f1f5f9',
                          color: editingPlan.watch_messages?.includes(item) ? 'white' : '#475569',
                          cursor: 'pointer',
                          fontSize: '13px',
                        }}
                        onClick={() => {
                          const current = editingPlan.watch_messages?.split(',').filter(Boolean) || [];
                          const updated = current.includes(item) ? current.filter(i => i !== item) : [...current, item];
                          setEditingPlan({ ...editingPlan, watch_messages: updated.join(',') });
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <div className="form-section-title">📝 计划信息</div>
                  <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>市场情绪</label>
                      <input
                        type="text"
                        value={editingPlan.sentiment || ''}
                        onChange={(e) => setEditingPlan({ ...editingPlan, sentiment: e.target.value })}
                        placeholder="如：分歧、看多、看空"
                        style={{ width: '100%', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>外部信号</label>
                      <input
                        type="text"
                        value={editingPlan.external_signals || ''}
                        onChange={(e) => setEditingPlan({ ...editingPlan, external_signals: e.target.value })}
                        placeholder="如：美股走势、重大政策"
                        style={{ width: '100%', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '6px' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>计划依据</label>
                      <textarea
                        value={editingPlan.plan_basis || ''}
                        onChange={(e) => setEditingPlan({ ...editingPlan, plan_basis: e.target.value })}
                        placeholder="制定计划的依据"
                        rows={3}
                        style={{ width: '100%', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '6px', resize: 'vertical' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>买入条件</label>
                      <textarea
                        value={editingPlan.entry_condition || ''}
                        onChange={(e) => setEditingPlan({ ...editingPlan, entry_condition: e.target.value })}
                        placeholder="什么条件下买入"
                        rows={2}
                        style={{ width: '100%', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '6px', resize: 'vertical' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>卖出条件</label>
                      <textarea
                        value={editingPlan.exit_condition || ''}
                        onChange={(e) => setEditingPlan({ ...editingPlan, exit_condition: e.target.value })}
                        placeholder="什么条件下卖出"
                        rows={2}
                        style={{ width: '100%', padding: '8px', border: '1px solid #e2e8f0', borderRadius: '6px', resize: 'vertical' }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <div className="form-section">
                  <div className="form-section-title">🎯 选择策略</div>
                  <div className="strategy-select-list" style={{ marginTop: '8px', maxHeight: '400px', overflowY: 'auto' }}>
                    {strategies.map(strategy => (
                      <div
                        key={strategy.id}
                        className={`strategy-select-item ${editingStrategyIds.includes(strategy.id) ? 'selected' : ''}`}
                        onClick={() => toggleEditingStrategy(strategy.id)}
                      >
                        <div className="strategy-check">
                          {editingStrategyIds.includes(strategy.id) && '✓'}
                        </div>
                        <div className="strategy-info">
                          <div className="strategy-name">{strategy.name}</div>
                          {strategy.description && <div className="strategy-desc">{strategy.description}</div>}
                          <div className="strategy-params">
                            <span>仓位: {strategy.position_size}%</span>
                            <span>止损: {strategy.stop_loss}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <div className="form-section">
                  <div className="form-section-title">📈 策略选股</div>
                  {editingStrategyIds.length === 0 ? (
                    <div style={{ color: '#94a3b8', padding: '20px', textAlign: 'center' }}>请先选择中间列的策略</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
                      {editingStrategyIds.map(strategyId => {
                        const strategyStock = editingStrategyStocks.find(s => s.strategyId === strategyId);
                        const strategy = strategies.find(s => s.id === strategyId);
                        return (
                          <div key={strategyId} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                              <span style={{ fontWeight: '600' }}>{strategy?.name}</span>
                              <button
                                className="btn btn-secondary"
                                style={{ padding: '4px 12px', fontSize: '12px' }}
                                onClick={() => scanEditingStrategyStocks(strategyId, strategy?.name || '')}
                                disabled={strategyStock?.scanning}
                              >
                                {strategyStock?.scanning ? '扫描中...' : '🔍 扫描股票'}
                              </button>
                            </div>
                            {strategyStock && strategyStock.stocks.length > 0 && (
                              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                {strategyStock.stocks.slice(0, 8).map((stock, idx) => (
                                  <div
                                    key={stock.code}
                                    style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '8px',
                                      padding: '6px 8px',
                                      background: strategyStock.selectedStocks.includes(stock.code) ? '#dbeafe' : 'transparent',
                                      borderRadius: '4px',
                                      cursor: 'pointer',
                                    }}
                                    onClick={() => toggleEditingStockSelection(strategyId, stock.code)}
                                  >
                                    <input
                                      type="checkbox"
                                      checked={strategyStock.selectedStocks.includes(stock.code)}
                                      onChange={() => {}}
                                    />
                                    <span style={{ flex: 1 }}>{stock.code} {stock.name}</span>
                                    <span style={{ color: stock.score >= 70 ? '#16a34a' : stock.score >= 50 ? '#ca8a04' : '#94a3b8', fontWeight: '500' }}>
                                      {stock.score}分
                                    </span>
                                    <span style={{ fontSize: '12px', color: '#64748b' }}>[{stock.entry_advice?.signal}]</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn" onClick={() => setShowEditModal(false)}>取消</button>
              {editingPlan?.status === 'draft' && (
                <button className="btn btn-primary" onClick={handleSaveEdit}>
                  保存草稿
                </button>
              )}
              {editingPlan?.status === 'draft' && (
                <button className="btn btn-success" onClick={handleConfirmPlan}>
                  确认计划
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {selectedPlan && (
        <div className="modal-overlay" onClick={() => setSelectedPlan(null)}>
          <div className="modal plan-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedPlan.date} 计划详情</h2>
              <button onClick={() => setSelectedPlan(null)}>×</button>
            </div>

            <div className="execution-flow">
              <div className="flow-step completed">
                <span className="step-icon">📋</span>
                <span className="step-label">计划</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.strategy ? 'completed' : ''}`}>
                <span className="step-icon">🎯</span>
                <span className="step-label">策略</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.stocks?.length ? 'completed' : ''}`}>
                <span className="step-icon">📈</span>
                <span className="step-label">选股</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.trades?.length ? 'completed' : ''}`}>
                <span className="step-icon">✅</span>
                <span className="step-label">执行</span>
              </div>
            </div>

            {selectedPlan.strategy && (
              <div className="detail-section">
                <h4>引用策略</h4>
                <p>{selectedPlan.strategy}</p>
              </div>
            )}

            {selectedPlan.trades && selectedPlan.trades.length > 0 && (
              <div className="detail-section">
                <h4>执行记录</h4>
                <div className="trade-list">
                  {selectedPlan.trades.map((trade, i) => (
                    <div key={i} className="trade-item">
                      <span className={`trade-type ${trade.type === '买入' ? 'buy' : 'sell'}`}>{trade.type}</span>
                      <span className="trade-stock">{trade.stock}</span>
                      <span className="trade-quantity">{trade.quantity}股</span>
                      <span className="trade-price">@{trade.price}</span>
                      {trade.result !== undefined && (
                        <span className={`trade-result ${trade.result >= 0 ? 'positive' : 'negative'}`}>
                          {trade.result >= 0 ? '+' : ''}¥{trade.result}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="modal-footer">
              {selectedPlan.prePlan?.status === 'draft' && (
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setSelectedPlan(null);
                    openEditModal(selectedPlan);
                  }}
                >
                  编辑计划
                </button>
              )}
              <button className="btn" onClick={() => setSelectedPlan(null)}>关闭</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
