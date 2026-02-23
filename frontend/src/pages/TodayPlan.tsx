import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface HotStock {
  code: string;
  name: string;
  reason: string;
  institution: string;
}

interface LimitUpData {
  total: number;
  yesterday: number;
  newHigh: number;
  continuation: number;
}

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

interface SectorStrength {
  name: string;
  strength: number;
  trend: string;
  avgChange: number;
}

interface WatchStock {
  code: string;
  name: string;
  price: number;
  change: number;
  strategy: string;
  status: 'observing' | 'pending' | 'holding';
  quantity?: number;
  entryPrice?: number;
  signal?: string;
  signal_reason?: string;
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

interface TradeRecord {
  code: string;
  name: string;
  action: '买入' | '卖出';
  price: number;
  quantity: number;
  amount: number;
  fee: number;
  reason: string;
  entryPrice?: number;
  exitPrice?: number;
  pnl?: number;
  pnlPercent?: number;
}

interface Review {
  preMarket: {
    sentiment: string;
    sectors: string[];
    targetStocks: string[];
    planBasis: string;
  };
  postMarket: {
    mistakes: string;
    lessons: string;
    tradeAnalysis: string;
    emotionRecord: string;
    tomorrowPlan: string;
  };
}

interface StrategyItem {
  id: number;
  name: string;
  description?: string;
  watch_signals?: string;
  stop_loss?: number;
  position_size?: number;
  entry_condition?: string;
  exit_condition?: string;
}

interface PrePlanData {
  id?: number;
  strategyId?: number;
  stopLoss?: number;
  positionSize?: number;
  entryCondition?: string;
  exitCondition?: string;
}

interface PostReviewAnalysis {
  planned_stocks: string[];
  actual_traded_stocks: string[];
  planned_executed: string[];
  unplanned_executed: string[];
  execution_rate: number;
  planned_pnl: number;
  unplanned_pnl: number;
  total_pnl: number;
}

interface StrategyStats {
  strategy_name: string;
  trade_count: number;
  win_count: number;
  loss_count: number;
  win_rate: number;
  total_pnl: number;
  avg_pnl: number;
  avg_win: number;
  avg_loss: number;
}

interface IntelligentAnalysis {
  today_analysis: PostReviewAnalysis;
  weekly_stats: {
    trade_count: number;
    win_count: number;
    loss_count: number;
    win_rate: number;
    total_pnl: number;
    avg_pnl: number;
  };
  monthly_stats: {
    trade_count: number;
    win_count: number;
    loss_count: number;
    win_rate: number;
    total_pnl: number;
    avg_pnl: number;
  };
  strategy_stats: StrategyStats[];
  recommendations: string[];
}

export default function TodayPlan() {
  const [strategy, setStrategy] = useState<string>('首板');
  const [strategies, setStrategies] = useState<StrategyItem[]>([]);
  const [activeTab, setActiveTab] = useState<'pre' | 'in' | 'post'>('pre');
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [showAddStockModal, setShowAddStockModal] = useState(false);
  const [newStock, setNewStock] = useState({ code: '', name: '', strategy: '追涨' });
  const [prePlanData, setPrePlanData] = useState<PrePlanData>({});
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [selectedStock, setSelectedStock] = useState<WatchStock | null>(null);
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  
  const [marketData] = useState<MarketData[]>([
    { index: '上证指数', points: 3200, change: 0.5, support: 3150, resistance: 3250 },
    { index: '创业板', points: 2100, change: 1.2, support: 2050, resistance: 2200 },
  ]);

  const [limitUpData] = useState<LimitUpData>({
    total: 45,
    yesterday: 38,
    newHigh: 12,
    continuation: 33,
  });

  const [dragonList] = useState<{top: HotStock[]; second: HotStock[]}>({
    top: [
      { code: '600519', name: '贵州茅台', reason: '机构买入', institution: '沪股通' },
      { code: '002594', name: '比亚迪', reason: '大单买入', institution: '深股通' },
    ],
    second: [
      { code: '300750', name: '宁德时代', reason: '游资买入', institution: '华鑫证券' },
      { code: '688981', name: '中芯国际', reason: '跟风买入', institution: '东财拉萨' },
    ],
  });

  const [sectorStrength] = useState<SectorStrength[]>([
    { name: '芯片', strength: 95, trend: '上升', avgChange: 5.8 },
    { name: '新能源', strength: 75, trend: '上升', avgChange: 3.2 },
    { name: 'AI', strength: 60, trend: '震荡', avgChange: 1.5 },
  ]);

  const [sectors] = useState<Sector[]>([
    { name: '芯片', change: 3.5, type: 'main', leader: '中芯国际' },
    { name: '新能源', change: 1.2, type: 'rotation' },
    { name: 'AI', change: -0.5, type: 'watch' },
  ]);

  useEffect(() => {
    axios.get('/api/watch-stocks').then(res => {
      if (res.data && res.data.length > 0) {
        setWatchStocks(res.data.map((s: any) => ({
          ...s,
          status: s.status || 'observing'
        })));
      }
    });
  }, []);

  useEffect(() => {
    axios.get('/api/strategies').then(res => {
      if (res.data && res.data.length > 0) {
        setStrategies(res.data);
        if (!strategy || strategy === '首板') {
          setStrategy(res.data[0].name);
        }
      }
    });
  }, []);

  useEffect(() => {
    axios.get('/api/plan/pre/today').then(res => {
      if (res.data && (res.data.status === 'confirmed' || res.data.status === 'executed')) {
        setReview({
          preMarket: {
            sentiment: res.data.sentiment || '分歧',
            sectors: res.data.sectors ? res.data.sectors.split(',').filter(Boolean) : [],
            targetStocks: res.data.candidate_stocks ? JSON.parse(res.data.candidate_stocks).filter((s: any) => s.code).map((s: any) => s.code) : [],
            planBasis: res.data.plan_basis || '',
          },
          postMarket: {
            mistakes: '',
            lessons: '',
            tradeAnalysis: '',
            emotionRecord: '',
            tomorrowPlan: '',
          },
        });

        if (res.data.selected_strategy) {
          setStrategy(res.data.selected_strategy);
        }

        if (res.data.stop_loss) {
          setPrePlanData({
            id: res.data.id,
            strategyId: res.data.strategy_ids ? parseInt(res.data.strategy_ids.split(',')[0]) : undefined,
            stopLoss: res.data.stop_loss,
            positionSize: res.data.position_size,
            entryCondition: res.data.entry_condition,
            exitCondition: res.data.exit_condition,
          });
        }
      }
    }).catch(() => {
    });
  }, []);

  useEffect(() => {
    if (activeTab === 'post') {
      setLoadingAnalysis(true);
      axios.get('/api/plan/intelligent-analysis?days=30')
        .then(res => {
          setIntelligentAnalysis(res.data);
        })
        .catch(err => {
          console.error('Failed to load intelligent analysis:', err);
        })
        .finally(() => {
          setLoadingAnalysis(false);
        });
    }
  }, [activeTab]);

  const [watchStocks, setWatchStocks] = useState<WatchStock[]>([
    { code: '600519', name: '贵州茅台', price: 1850, change: 2.8, strategy: '追涨', status: 'observing' },
    { code: '300750', name: '宁德时代', price: 275, change: -1.8, strategy: '低吸', status: 'pending' },
    { code: '002594', name: '比亚迪', price: 268, change: 3.1, strategy: '追涨', status: 'holding', quantity: 100, entryPrice: 260 },
  ]);

  const handleAddStock = () => {
    if (newStock.code && newStock.name) {
      setWatchStocks([...watchStocks, { ...newStock, price: 0, change: 0, status: 'observing' } as WatchStock]);
      setNewStock({ code: '', name: '', strategy: '追涨' });
      setShowAddStockModal(false);
    }
  };

  const handleGenerateFromStrategy = async (strategyId: number) => {
    setGeneratingPlan(true);
    try {
      const res = await axios.post(`/api/plan/generate-from-strategies?strategy_ids=${strategyId}`);
      const data = res.data;
      setPrePlanData({
        id: data.id,
        strategyId: data.strategy_ids ? parseInt(data.strategy_ids.split(',')[0]) : undefined,
        stopLoss: data.stop_loss,
        positionSize: data.position_size,
        entryCondition: data.entry_condition,
        exitCondition: data.exit_condition,
      });
      setStrategy(data.selected_strategy || strategy);
      setReview({
        ...review,
        preMarket: {
          ...review.preMarket,
          sentiment: data.sentiment || '分歧',
          planBasis: data.plan_basis || review.preMarket.planBasis,
        }
      });
      alert('已从策略生成计划！');
    } catch (err) {
      console.error('Failed to generate plan from strategy:', err);
      alert('生成失败');
    } finally {
      setGeneratingPlan(false);
    }
  };

  const handleSavePrePlan = async () => {
    const today = new Date().toISOString().split('T')[0];
    try {
      await axios.post('/api/plan/pre', {
        trade_date: today,
        plan_date: today,
        strategy_ids: prePlanData.strategyId?.toString(),
        sentiment: review.preMarket.sentiment,
        selected_strategy: strategy,
        sectors: review.preMarket.sectors.join(','),
        candidate_stocks: JSON.stringify(review.preMarket.targetStocks.map(code => ({ code, name: code, buy_reason: '', sell_reason: '', priority: 1 }))),
        plan_basis: review.preMarket.planBasis,
        stop_loss: prePlanData.stopLoss,
        position_size: prePlanData.positionSize,
        entry_condition: prePlanData.entryCondition,
        exit_condition: prePlanData.exitCondition,
        status: 'draft',
      });
      alert('盘前计划已保存！');
    } catch (err) {
      console.error('Failed to save pre-plan:', err);
      alert('保存失败');
    }
  };

  const handleSavePostReview = async () => {
    const today = new Date().toISOString().split('T')[0];
    try {
      const existingPlan = prePlanData.id ? null : (await axios.get(`/api/plan/pre?trade_date=${today}`)).data;
      const prePlanId = prePlanData.id || existingPlan?.id;
      
      await axios.post('/api/plan/post', {
        trade_date: today,
        pre_plan_id: prePlanId,
        emotion_record: review.postMarket.emotionRecord,
        mistakes: review.postMarket.mistakes,
        lessons: review.postMarket.lessons,
        trade_analysis: review.postMarket.tradeAnalysis,
        tomorrow_plan: review.postMarket.tomorrowPlan,
        planned_stocks: review.preMarket.targetStocks.join(','),
        actual_trades_json: JSON.stringify(trades.map(t => ({
          code: t.code,
          name: t.name,
          action: t.action,
          price: t.price,
          quantity: t.quantity,
          pnl: t.pnl,
        }))),
      });
      alert('盘后总结已保存！');
    } catch (err) {
      console.error('Failed to save post-review:', err);
      alert('保存失败');
    }
  };

  const [news] = useState([
    { type: '政策', content: 'XXX会议召开，利好AI板块' },
    { type: '公告', content: 'XX公司业绩预增' },
  ]);

  const [trades, setTrades] = useState<TradeRecord[]>([
    { code: '600519', name: '贵州茅台', action: '买入', price: 1800, quantity: 100, amount: 180000, fee: 135, reason: '突破前高' },
    { code: '300750', name: '宁德时代', action: '卖出', price: 278, quantity: 200, amount: 55600, fee: 41.7, reason: '触及止损', entryPrice: 282, exitPrice: 278, pnl: -800, pnlPercent: -1.42 },
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
    preMarket: { sentiment: '分歧', sectors: [], targetStocks: [], planBasis: '' },
    postMarket: {
      mistakes: '',
      lessons: '',
      tradeAnalysis: '',
      emotionRecord: '',
      tomorrowPlan: ''
    },
  });

  const [intelligentAnalysis, setIntelligentAnalysis] = useState<IntelligentAnalysis | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const handleTrade = (stock: WatchStock, type: 'buy' | 'sell') => {
    setSelectedStock(stock);
    setTradeType(type);
    setShowTradeModal(true);
  };

  const confirmTrade = async () => {
    if (!selectedStock) return;

    const tradeData = {
      stock_code: selectedStock.code,
      stock_name: selectedStock.name,
      trade_type: tradeType === 'buy' ? '买入' : '卖出',
      price: selectedStock.price,
      quantity: 100,
      amount: selectedStock.price * 100,
      fee: selectedStock.price * 100 * 0.00075,
      reason: tradeType === 'buy' ? '盘中买入' : '盘中卖出',
      trade_date: new Date().toISOString().split('T')[0],
      pre_plan_id: prePlanData.id || null,
      is_planned: !!prePlanData.id,
    };

    try {
      await axios.post('/api/trades', tradeData);
      const newTrade: TradeRecord = {
        code: selectedStock.code,
        name: selectedStock.name,
        action: tradeType === 'buy' ? '买入' : '卖出',
        price: selectedStock.price,
        quantity: 100,
        amount: selectedStock.price * 100,
        fee: selectedStock.price * 100 * 0.00075,
        reason: tradeType === 'buy' ? '盘中买入' : '盘中卖出',
      };
      setTrades([...trades, newTrade]);
      alert(`${tradeType === 'buy' ? '买入' : '卖出'}成功！${prePlanData.id ? '(已关联计划)' : ''}`);
    } catch (err) {
      console.error('Failed to record trade:', err);
      alert('交易记录失败');
    }

    setShowTradeModal(false);
    setSelectedStock(null);
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

  const totalPnl = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
  const totalFee = trades.reduce((sum, t) => sum + t.fee, 0);

  return (
    <div className="page">
      <div className="page-header">
        <h1>今日计划</h1>
        <span className="date">{dayjs().format('YYYY-MM-DD')}</span>
      </div>

      <div className="strategy-selector">
        <span className="strategy-label">当前策略:</span>
        <div className="strategy-buttons">
          {strategies.length > 0 ? (
            <>
              <button
                className="btn btn-sm"
                style={{ marginRight: '8px' }}
                onClick={() => {
                  const s = strategies.find(x => x.name === strategy);
                  if (s) handleGenerateFromStrategy(s.id);
                }}
                disabled={generatingPlan}
              >
                {generatingPlan ? '生成中...' : '📥 从策略生成'}
              </button>
              {strategies.map(s => (
                <button
                  key={s.id}
                  className={`strategy-btn ${strategy === s.name ? 'active' : ''}`}
                  onClick={() => {
                    setStrategy(s.name);
                    setPrePlanData({
                      strategyId: s.id,
                      stopLoss: s.stop_loss,
                      positionSize: s.position_size,
                      entryCondition: s.entry_condition,
                      exitCondition: s.exit_condition,
                    });
                  }}
                >
                  {s.name}
                </button>
              ))}
            </>
          ) : (
            <>
              <button className={`strategy-btn ${strategy === '龙头' ? 'active' : ''}`} onClick={() => setStrategy('龙头')}>🐲 龙头</button>
              <button className={`strategy-btn ${strategy === '首板' ? 'active' : ''}`} onClick={() => setStrategy('首板')}>🔥 首板</button>
              <button className={`strategy-btn ${strategy === '龙回头' ? 'active' : ''}`} onClick={() => setStrategy('龙回头')}>🐉 龙回头</button>
              <button className={`strategy-btn ${strategy === '趋势' ? 'active' : ''}`} onClick={() => setStrategy('趋势')}>📈 趋势</button>
            </>
          )}
        </div>
      </div>
      {prePlanData.strategyId && (
        <div className="strategy-params" style={{ padding: '12px', background: '#f5f5f5', borderRadius: '8px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {prePlanData.positionSize && (
              <div><strong>仓位:</strong> {prePlanData.positionSize}%</div>
            )}
            {prePlanData.stopLoss && (
              <div><strong>止损:</strong> {prePlanData.stopLoss}%</div>
            )}
            {prePlanData.entryCondition && (
              <div><strong>买入条件:</strong> {prePlanData.entryCondition}</div>
            )}
            {prePlanData.exitCondition && (
              <div><strong>卖出条件:</strong> {prePlanData.exitCondition}</div>
            )}
          </div>
        </div>
      )}

      <div className="strategy-hint">
        {(() => {
          const selected = strategies.find(s => s.name === strategy);
          if (selected && selected.watch_signals) {
            return <span>{selected.description || selected.name}: {selected.watch_signals}</span>;
          }
          return (
            <>
              {strategy === '龙头' && <span>🐲 龙头战法: 关注换手率排行、板块强度、资金流向</span>}
              {strategy === '首板' && <span>🔥 首板战法: 关注首板→二板晋级率、封板质量</span>}
              {strategy === '龙回头' && <span>🐉 龙回头: 关注回调幅度、均线支撑</span>}
              {strategy === '趋势' && <span>📈 趋势低吸: 关注均线周期、成交量萎缩</span>}
            </>
          );
        })()}
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
            <h3>涨停板</h3>
            <div className="limit-up-grid">
              <div className="limit-up-card">
                <span className="limit-up-num">{limitUpData.total}</span>
                <span className="limit-up-label">今日涨停</span>
              </div>
              <div className="limit-up-card">
                <span className="limit-up-num">{limitUpData.continuation}</span>
                <span className="limit-up-label">连板</span>
              </div>
              <div className="limit-up-card">
                <span className="limit-up-num">{limitUpData.newHigh}</span>
                <span className="limit-up-label">首板</span>
              </div>
              <div className="limit-up-card">
                <span className="limit-up-num">{limitUpData.total - limitUpData.yesterday > 0 ? '+' : ''}{limitUpData.total - limitUpData.yesterday}</span>
                <span className="limit-up-label">较昨日</span>
              </div>
            </div>
          </div>

          <div className="plan-section">
            <h3>龙虎榜</h3>
            <div className="dragon-list">
              <div className="dragon-section">
                <h4>🏆 机构榜</h4>
                {dragonList.top.map((stock, i) => (
                  <div key={i} className="dragon-item">
                    <span className="dragon-name">{stock.name}</span>
                    <span className="dragon-code">{stock.code}</span>
                    <span className="dragon-reason">{stock.reason}</span>
                    <span className="dragon-inst">{stock.institution}</span>
                  </div>
                ))}
              </div>
              <div className="dragon-section">
                <h4>🐉 游资榜</h4>
                {dragonList.second.map((stock, i) => (
                  <div key={i} className="dragon-item">
                    <span className="dragon-name">{stock.name}</span>
                    <span className="dragon-code">{stock.code}</span>
                    <span className="dragon-reason">{stock.reason}</span>
                    <span className="dragon-inst">{stock.institution}</span>
                  </div>
                ))}
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
            <h3>板块强度</h3>
            <div className="sector-strength-list">
              {sectorStrength.map((sector, i) => (
                <div key={i} className="sector-strength-item">
                  <div className="sector-strength-header">
                    <span className="sector-strength-name">{sector.name}</span>
                    <span className={`sector-strength-trend ${sector.trend}`}>{sector.trend}</span>
                  </div>
                  <div className="sector-strength-bar">
                    <div className="sector-strength-fill" style={{ width: `${sector.strength}%` }}></div>
                  </div>
                  <div className="sector-strength-info">
                    <span>强度: {sector.strength}</span>
                    <span>均涨幅: {sector.avgChange}%</span>
                  </div>
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
            <h3>📋 {strategy}策略重点</h3>
            <div className="strategy-focus">
              {strategy === '龙头' && (
                <div className="focus-items">
                  <div className="focus-item">
                    <span className="focus-icon">📊</span>
                    <span className="focus-label">换手率排行</span>
                    <span className="focus-desc">前排高换手往往是资金聚集地</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">💪</span>
                    <span className="focus-label">板块强度</span>
                    <span className="focus-desc">板块强度&amp;gt;80%考虑介入</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">💰</span>
                    <span className="focus-label">资金流向</span>
                    <span className="focus-desc">主力持续流入板块可关注</span>
                  </div>
                </div>
              )}
              {strategy === '首板' && (
                <div className="focus-items">
                  <div className="focus-item">
                    <span className="focus-icon">🔥</span>
                    <span className="focus-label">首板→二板晋级率</span>
                    <span className="focus-desc">历史晋级率&amp;gt;50%可尝试</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">⚡</span>
                    <span className="focus-label">封板质量</span>
                    <span className="focus-desc">首次封板时间越早越好</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">🏭</span>
                    <span className="focus-label">板块轮动</span>
                    <span className="focus-desc">新启动板块首板更具持续性</span>
                  </div>
                </div>
              )}
              {strategy === '龙回头' && (
                <div className="focus-items">
                  <div className="focus-item">
                    <span className="focus-icon">📉</span>
                    <span className="focus-label">回调幅度</span>
                    <span className="focus-desc">回调20-30%是低吸区间</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">📈</span>
                    <span className="focus-label">均线支撑</span>
                    <span className="focus-desc">10日均线附近考虑低吸</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">🔄</span>
                    <span className="focus-label">反抽信号</span>
                    <span className="focus-desc">缩量十字星可能是反转信号</span>
                  </div>
                </div>
              )}
              {strategy === '趋势' && (
                <div className="focus-items">
                  <div className="focus-item">
                    <span className="focus-icon">📊</span>
                    <span className="focus-label">均线周期</span>
                    <span className="focus-desc">多头排列是重要信号</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">📉</span>
                    <span className="focus-label">成交量萎缩</span>
                    <span className="focus-desc">回调缩量是洗盘特征</span>
                  </div>
                  <div className="focus-item">
                    <span className="focus-icon">🎯</span>
                    <span className="focus-label">支撑位</span>
                    <span className="focus-desc">前期高点突破后转为支撑</span>
                  </div>
                </div>
              )}
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
                    {sentimentPhases.map((s) => (
                      <option key={s.phase} value={s.phase}>{s.phase}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>选用策略</label>
                  <select
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                  >
                    {strategies.length > 0 ? (
                      strategies.map((s) => (
                        <option key={s.id} value={s.name}>{s.name}</option>
                      ))
                    ) : (
                      <>
                        <option value="龙头">🐲 龙头战法</option>
                        <option value="首板">🔥 首板战法</option>
                        <option value="龙回头">🐉 龙回头</option>
                        <option value="趋势">📈 趋势低吸</option>
                      </>
                    )}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>策略外观察信号</label>
                <input
                  placeholder="外围市场、政策消息、特殊盘面信号..."
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>关注板块</label>
                  <input
                    value={review.preMarket.sectors.join(', ')}
                    onChange={(e) => setReview({ ...review, preMarket: { ...review.preMarket, sectors: e.target.value.split(',').map(s => s.trim()) } })}
                    placeholder="芯片,新能源,AI"
                  />
                </div>
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
                  placeholder="1. 芯片板块持续强势，关注龙头股&#10;2. 情绪周期处于分歧，控制仓位&#10;3. 只做首板，不追高位"
                  rows={4}
                />
              </div>
              <button className="btn btn-primary" onClick={handleSavePrePlan}>保存盘前计划</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'in' && (
        <div className="tab-content">
          <div className="plan-section">
            <div className="section-header">
              <h3>关注股票</h3>
              <button className="btn btn-sm" onClick={() => setShowAddStockModal(true)}>+ 添加股票</button>
            </div>
            <div className="stock-table">
              <table>
                <thead>
                  <tr>
                    <th>股票</th>
                    <th>现价</th>
                    <th>涨跌幅</th>
                    <th>策略</th>
                    <th>持仓/成本</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {watchStocks.map((stock, i) => (
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
                        {stock.status === 'holding' && stock.entryPrice && stock.quantity ? (
                          <div>
                            <div>{stock.quantity}股</div>
                            <div className="text-sm text-gray">成本¥{stock.entryPrice}</div>
                            <div className={stock.price >= stock.entryPrice ? 'positive' : 'negative'}>
                              {((stock.price - stock.entryPrice) / stock.entryPrice * 100).toFixed(2)}%
                            </div>
                          </div>
                        ) : '-'}
                      </td>
                      <td>
                        <span className={`status-tag ${getStatusClass(stock.status)}`}>
                          {getStatusLabel(stock.status)}
                        </span>
                        {stock.signal && (
                          <span className={`signal-tag ${stock.signal === 'second_board' ? 'hot' : 'dragon'}`}>
                            {stock.signal === 'second_board' ? '🔥 二板' : '🐉 龙回头'}
                          </span>
                        )}
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
            <h3>今日操作记录</h3>
            <div className="trade-summary">
              <div className="trade-summary-item">
                <span className="summary-label">交易次数</span>
                <span className="summary-value">{trades.length}次</span>
              </div>
              <div className="trade-summary-item">
                <span className="summary-label">总手续费</span>
                <span className="summary-value">¥{totalFee.toFixed(2)}</span>
              </div>
              <div className="trade-summary-item">
                <span className="summary-label">总盈亏</span>
                <span className={`summary-value ${totalPnl >= 0 ? 'positive' : 'negative'}`}>
                  {totalPnl >= 0 ? '+' : ''}¥{totalPnl}
                </span>
              </div>
            </div>
            <div className="trade-table">
              <table>
                <thead>
                  <tr>
                    <th>股票</th>
                    <th>操作</th>
                    <th>价格</th>
                    <th>数量</th>
                    <th>金额</th>
                    <th>手续费</th>
                    <th>买入理由</th>
                    {trades[0]?.pnl !== undefined && <th>盈亏</th>}
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade, i) => (
                    <tr key={i}>
                      <td>
                        <div className="stock-cell">
                          <span className="stock-name">{trade.name}</span>
                          <span className="stock-code">{trade.code}</span>
                        </div>
                      </td>
                      <td>
                        <span className={`action-tag ${trade.action === '买入' ? 'buy' : 'sell'}`}>
                          {trade.action}
                        </span>
                      </td>
                      <td>¥{trade.price}</td>
                      <td>{trade.quantity}</td>
                      <td>¥{trade.amount.toLocaleString()}</td>
                      <td>¥{trade.fee.toFixed(2)}</td>
                      <td>{trade.reason}</td>
                      {trade.pnl !== undefined && (
                        <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                          {trade.pnl >= 0 ? '+' : ''}¥{trade.pnl} ({trade.pnlPercent?.toFixed(2)}%)
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="plan-section">
            <h3>盘后复盘</h3>
            <div className="review-form">
              <div className="form-group">
                <label>🌡️ 情绪记录</label>
                <textarea
                  value={review.postMarket.emotionRecord}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, emotionRecord: e.target.value } })}
                  placeholder="今日情绪波动: 开盘兴奋，盘中恐慌，尾盘平静..."
                  rows={2}
                />
              </div>
              <div className="form-group">
                <label>❌ 失误记录</label>
                <textarea
                  value={review.postMarket.mistakes}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, mistakes: e.target.value } })}
                  placeholder="1. 追高被套&#10;2. 止损不够果断&#10;3. 仓位过重"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>📈 买卖点分析</label>
                <textarea
                  value={review.postMarket.tradeAnalysis}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, tradeAnalysis: e.target.value } })}
                  placeholder="600519: 买入点不佳，应等回踩再买&#10;300750: 卖出及时，止损正确"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>💡 心得体会</label>
                <textarea
                  value={review.postMarket.lessons}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, lessons: e.target.value } })}
                  placeholder="今日操作总结..."
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>🎯 明日计划</label>
                <textarea
                  value={review.postMarket.tomorrowPlan}
                  onChange={(e) => setReview({ ...review, postMarket: { ...review.postMarket, tomorrowPlan: e.target.value } })}
                  placeholder="1. 关注芯片板块持续性&#10;2. 只做首板&#10;3. 控制仓位不超过50%"
                  rows={3}
                />
              </div>
              <button className="btn btn-primary" onClick={handleSavePostReview}>保存盘后总结</button>
            </div>
          </div>

          {loadingAnalysis ? (
            <div className="plan-section">
              <div className="loading">加载智能分析中...</div>
            </div>
          ) : intelligentAnalysis && (
            <>
              <div className="plan-section">
                <h3>📊 智能分析</h3>
                <div className="analysis-grid">
                  <div className="analysis-card">
                    <div className="analysis-card-header">
                      <span className="analysis-card-title">今日执行</span>
                    </div>
                    <div className="analysis-card-content">
                      <div className="analysis-stat">
                        <span className="stat-label">计划执行率</span>
                        <span className={`stat-value ${intelligentAnalysis.today_analysis.execution_rate >= 50 ? 'positive' : 'negative'}`}>
                          {intelligentAnalysis.today_analysis.execution_rate}%
                        </span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">计划内盈利</span>
                        <span className={`stat-value ${intelligentAnalysis.today_analysis.planned_pnl >= 0 ? 'positive' : 'negative'}`}>
                          ¥{intelligentAnalysis.today_analysis.planned_pnl}
                        </span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">计划外盈利</span>
                        <span className={`stat-value ${intelligentAnalysis.today_analysis.unplanned_pnl >= 0 ? 'positive' : 'negative'}`}>
                          ¥{intelligentAnalysis.today_analysis.unplanned_pnl}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="analysis-card">
                    <div className="analysis-card-header">
                      <span className="analysis-card-title">本周统计</span>
                    </div>
                    <div className="analysis-card-content">
                      <div className="analysis-stat">
                        <span className="stat-label">交易次数</span>
                        <span className="stat-value">{intelligentAnalysis.weekly_stats.trade_count}次</span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">胜率</span>
                        <span className={`stat-value ${intelligentAnalysis.weekly_stats.win_rate >= 50 ? 'positive' : 'negative'}`}>
                          {intelligentAnalysis.weekly_stats.win_rate}%
                        </span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">总盈亏</span>
                        <span className={`stat-value ${intelligentAnalysis.weekly_stats.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                          ¥{intelligentAnalysis.weekly_stats.total_pnl}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="analysis-card">
                    <div className="analysis-card-header">
                      <span className="analysis-card-title">本月统计</span>
                    </div>
                    <div className="analysis-card-content">
                      <div className="analysis-stat">
                        <span className="stat-label">交易次数</span>
                        <span className="stat-value">{intelligentAnalysis.monthly_stats.trade_count}次</span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">胜率</span>
                        <span className={`stat-value ${intelligentAnalysis.monthly_stats.win_rate >= 50 ? 'positive' : 'negative'}`}>
                          {intelligentAnalysis.monthly_stats.win_rate}%
                        </span>
                      </div>
                      <div className="analysis-stat">
                        <span className="stat-label">总盈亏</span>
                        <span className={`stat-value ${intelligentAnalysis.monthly_stats.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                          ¥{intelligentAnalysis.monthly_stats.total_pnl}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {intelligentAnalysis.strategy_stats.length > 0 && (
                <div className="plan-section">
                  <h3>🎯 策略效果</h3>
                  <div className="strategy-stats-table">
                    <table>
                      <thead>
                        <tr>
                          <th>策略</th>
                          <th>交易次数</th>
                          <th>胜率</th>
                          <th>总盈亏</th>
                          <th>平均盈亏</th>
                          <th>平均盈利</th>
                          <th>平均亏损</th>
                        </tr>
                      </thead>
                      <tbody>
                        {intelligentAnalysis.strategy_stats.map((stat, index) => (
                          <tr key={index} className={index === 0 ? 'best-strategy' : ''}>
                            <td>{stat.strategy_name}</td>
                            <td>{stat.trade_count}</td>
                            <td className={stat.win_rate >= 50 ? 'positive' : 'negative'}>{stat.win_rate}%</td>
                            <td className={stat.total_pnl >= 0 ? 'positive' : 'negative'}>{stat.total_pnl >= 0 ? '+' : ''}¥{stat.total_pnl}</td>
                            <td className={stat.avg_pnl >= 0 ? 'positive' : 'negative'}>{stat.avg_pnl >= 0 ? '+' : ''}¥{stat.avg_pnl}</td>
                            <td className="positive">+¥{stat.avg_win}</td>
                            <td className="negative">-¥{Math.abs(stat.avg_loss)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {intelligentAnalysis.recommendations.length > 0 && (
                <div className="plan-section">
                  <h3>💡 智能建议</h3>
                  <div className="recommendations-list">
                    {intelligentAnalysis.recommendations.map((rec, index) => (
                      <div key={index} className="recommendation-item">
                        <span className="rec-icon">→</span>
                        <span className="rec-text">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {showAddStockModal && (
        <div className="modal-overlay" onClick={() => setShowAddStockModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>添加关注股票</h3>
              <button className="modal-close" onClick={() => setShowAddStockModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>股票代码</label>
                <input
                  type="text"
                  placeholder="如: 600519"
                  value={newStock.code}
                  onChange={e => setNewStock({ ...newStock, code: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>股票名称</label>
                <input
                  type="text"
                  placeholder="如: 贵州茅台"
                  value={newStock.name}
                  onChange={e => setNewStock({ ...newStock, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>策略</label>
                <select
                  value={newStock.strategy}
                  onChange={e => setNewStock({ ...newStock, strategy: e.target.value })}
                >
                  <option value="追涨">追涨</option>
                  <option value="低吸">低吸</option>
                  <option value="首板">首板</option>
                  <option value="龙头">龙头</option>
                  <option value="反包">反包</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn" onClick={() => setShowAddStockModal(false)}>取消</button>
              <button className="btn btn-primary" onClick={handleAddStock}>添加</button>
            </div>
          </div>
        </div>
      )}

      {showTradeModal && selectedStock && (
        <div className="modal-overlay" onClick={() => setShowTradeModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{tradeType === 'buy' ? '买入' : '卖出'} {selectedStock.name}</h3>
              <button className="modal-close" onClick={() => setShowTradeModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="trade-info">
                <div className="trade-info-item">
                  <span className="label">股票代码</span>
                  <span className="value">{selectedStock.code}</span>
                </div>
                <div className="trade-info-item">
                  <span className="label">当前价格</span>
                  <span className="value">¥{selectedStock.price}</span>
                </div>
                <div className="trade-info-item">
                  <span className="label">涨跌幅</span>
                  <span className={`value ${selectedStock.change >= 0 ? 'positive' : 'negative'}`}>
                    {selectedStock.change >= 0 ? '+' : ''}{selectedStock.change}%
                  </span>
                </div>
                <div className="trade-info-item">
                  <span className="label">策略</span>
                  <span className="value">{selectedStock.strategy}</span>
                </div>
                {tradeType === 'sell' && selectedStock.status === 'holding' && selectedStock.entryPrice && selectedStock.quantity && (
                  <>
                    <div className="trade-info-item">
                      <span className="label">持仓数量</span>
                      <span className="value">{selectedStock.quantity}股</span>
                    </div>
                    <div className="trade-info-item">
                      <span className="label">成本价</span>
                      <span className="value">¥{selectedStock.entryPrice}</span>
                    </div>
                    <div className="trade-info-item">
                      <span className="label">持仓盈亏</span>
                      <span className={`value ${(selectedStock.price - selectedStock.entryPrice) >= 0 ? 'positive' : 'negative'}`}>
                        {(selectedStock.price - selectedStock.entryPrice) >= 0 ? '+' : ''}{((selectedStock.price - selectedStock.entryPrice) / selectedStock.entryPrice * 100).toFixed(2)}%
                        (¥{((selectedStock.price - selectedStock.entryPrice) * selectedStock.quantity).toLocaleString()})
                      </span>
                    </div>
                  </>
                )}
              </div>
              <div className="form-group">
                <label>{tradeType === 'sell' ? '卖出数量' : '买入数量'}(手)</label>
                <input type="number" placeholder="1手=100股" defaultValue={tradeType === 'sell' && selectedStock.quantity ? Math.floor(selectedStock.quantity / 100) : 1} />
              </div>
              <div className="trade-calc">
                <div className="calc-item">
                  <span>预估金额:</span>
                  <span>¥{(selectedStock.price * 100).toLocaleString()}</span>
                </div>
                <div className="calc-item">
                  <span>预估手续费:</span>
                  <span>¥{(selectedStock.price * 100 * 0.00075).toFixed(2)}</span>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn" onClick={() => setShowTradeModal(false)}>取消</button>
              <button className={`btn ${tradeType === 'buy' ? 'btn-success' : 'btn-danger'}`} onClick={confirmTrade}>
                确认{tradeType === 'buy' ? '买入' : '卖出'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
