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
  const [candidateStocksEdit, setCandidateStocksEdit] = useState<CandidateStockInput[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategyIds, setSelectedStrategyIds] = useState<number[]>([]);
  const [creatingPlan, setCreatingPlan] = useState(false);

  useEffect(() => {
    loadPlans();
    loadStrategies();
  }, [currentMonth]);

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

  const handleCreatePlan = async () => {
    if (selectedStrategyIds.length === 0) {
      alert('请至少选择一个策略');
      return;
    }

    setCreatingPlan(true);
    try {
      const strategyIdsStr = selectedStrategyIds.join(',');
      await axios.post(`/api/plan/generate-from-strategies?strategy_ids=${strategyIdsStr}`);
      alert('计划已生成，请编辑候选股票');
      setShowCreateModal(false);
      setSelectedStrategyIds([]);
      loadPlans();
    } catch (err) {
      console.error('Failed to create plan:', err);
      alert('创建计划失败');
    } finally {
      setCreatingPlan(false);
    }
  };

  const toggleStrategy = (id: number) => {
    setSelectedStrategyIds(prev =>
      prev.includes(id)
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
  };

  const openEditModal = (plan: PlanRecord) => {
    if (!plan.prePlan) return;
    setEditingPlan(plan.prePlan);
    
    const stocks: CandidateStockInput[] = [];
    if (plan.prePlan.candidate_stocks) {
      try {
        const parsed = JSON.parse(plan.prePlan.candidate_stocks);
        stocks.push(...parsed.map((s: CandidateStock) => ({
          code: s.code || '',
          name: s.name || '',
          buy_reason: s.buy_reason || '',
          sell_reason: s.sell_reason || '',
          priority: s.priority || 0,
        })));
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
    
    try {
      await axios.put(`/api/plan/pre/${editingPlan.id}`, {
        candidate_stocks: JSON.stringify(candidateStocksEdit),
        sentiment: editingPlan.sentiment,
        external_signals: editingPlan.external_signals,
        sectors: editingPlan.sectors,
        plan_basis: editingPlan.plan_basis,
        entry_condition: editingPlan.entry_condition,
        exit_condition: editingPlan.exit_condition,
      });
      alert('计划已更新');
      setShowEditModal(false);
      loadPlans();
    } catch (err) {
      console.error('Failed to update plan:', err);
      alert('更新失败');
    }
  };

  const addCandidateStock = () => {
    setCandidateStocksEdit([
      ...candidateStocksEdit,
      { code: '', name: '', buy_reason: '', sell_reason: '', priority: candidateStocksEdit.length + 1 }
    ]);
  };

  const updateCandidateStock = (index: number, field: keyof CandidateStockInput, value: string | number) => {
    const updated = [...candidateStocksEdit];
    updated[index] = { ...updated[index], [field]: value };
    setCandidateStocksEdit(updated);
  };

  const removeCandidateStock = (index: number) => {
    setCandidateStocksEdit(candidateStocksEdit.filter((_, i) => i !== index));
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

  const tomorrow = dayjs().add(1, 'day').format('YYYY-MM-DD');
  const hasTomorrowPlan = plans.some(p => p.date === tomorrow);

  return (
    <div className="page">
      <div className="page-header">
        <h1>计划列表</h1>
        {!hasTomorrowPlan && (
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            + 创建明日计划
          </button>
        )}
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
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>创建明日计划</h2>
              <button onClick={() => setShowCreateModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <p className="modal-hint">选择策略，系统将自动生成候选股票和买卖思路</p>

              <div className="strategy-select-list">
                {strategies.map(strategy => (
                  <div
                    key={strategy.id}
                    className={`strategy-select-item ${selectedStrategyIds.includes(strategy.id) ? 'selected' : ''}`}
                    onClick={() => toggleStrategy(strategy.id)}
                  >
                    <div className="strategy-check">
                      {selectedStrategyIds.includes(strategy.id) && '✓'}
                    </div>
                    <div className="strategy-info">
                      <div className="strategy-name">{strategy.name}</div>
                      {strategy.description && <div className="strategy-desc">{strategy.description}</div>}
                      {strategy.stock_selection_logic && (
                        <div className="strategy-logic">{strategy.stock_selection_logic}</div>
                      )}
                      <div className="strategy-params">
                        <span>仓位: {strategy.position_size}%</span>
                        <span>止损: {strategy.stop_loss}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn" onClick={() => setShowCreateModal(false)}>取消</button>
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
          <div className="modal plan-edit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>编辑计划 - {editingPlan.trade_date}</h2>
              <button onClick={() => setShowEditModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="edit-section">
                <h4>候选股票</h4>
                <div className="candidate-stocks-list">
                  {candidateStocksEdit.map((stock, index) => (
                    <div key={index} className="candidate-stock-item">
                      <div className="stock-row">
                        <input
                          type="text"
                          placeholder="股票代码"
                          value={stock.code}
                          onChange={(e) => updateCandidateStock(index, 'code', e.target.value)}
                        />
                        <input
                          type="text"
                          placeholder="股票名称"
                          value={stock.name}
                          onChange={(e) => updateCandidateStock(index, 'name', e.target.value)}
                        />
                        <button className="btn-icon" onClick={() => removeCandidateStock(index)}>×</button>
                      </div>
                      <div className="reason-row">
                        <input
                          type="text"
                          placeholder="买入理由"
                          value={stock.buy_reason}
                          onChange={(e) => updateCandidateStock(index, 'buy_reason', e.target.value)}
                        />
                      </div>
                      <div className="reason-row">
                        <input
                          type="text"
                          placeholder="卖出理由"
                          value={stock.sell_reason}
                          onChange={(e) => updateCandidateStock(index, 'sell_reason', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                  <button className="btn btn-secondary" onClick={addCandidateStock}>
                    + 添加候选股票
                  </button>
                </div>
              </div>

              <div className="edit-section">
                <label>市场情绪</label>
                <input
                  type="text"
                  value={editingPlan.sentiment || ''}
                  onChange={(e) => setEditingPlan({ ...editingPlan, sentiment: e.target.value })}
                  placeholder="如：分歧、看多、看空"
                />
              </div>

              <div className="edit-section">
                <label>外部信号</label>
                <input
                  type="text"
                  value={editingPlan.external_signals || ''}
                  onChange={(e) => setEditingPlan({ ...editingPlan, external_signals: e.target.value })}
                  placeholder="如：美股走势、重大政策"
                />
              </div>

              <div className="edit-section">
                <label>计划依据</label>
                <textarea
                  value={editingPlan.plan_basis || ''}
                  onChange={(e) => setEditingPlan({ ...editingPlan, plan_basis: e.target.value })}
                  placeholder="制定计划的依据"
                  rows={3}
                />
              </div>

              <div className="edit-section">
                <label>买入条件</label>
                <textarea
                  value={editingPlan.entry_condition || ''}
                  onChange={(e) => setEditingPlan({ ...editingPlan, entry_condition: e.target.value })}
                  placeholder="什么条件下买入"
                  rows={2}
                />
              </div>

              <div className="edit-section">
                <label>卖出条件</label>
                <textarea
                  value={editingPlan.exit_condition || ''}
                  onChange={(e) => setEditingPlan({ ...editingPlan, exit_condition: e.target.value })}
                  placeholder="什么条件下卖出"
                  rows={2}
                />
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
