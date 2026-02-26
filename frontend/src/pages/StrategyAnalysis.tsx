import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './StrategyAnalysis.css';
import StrategyModal from './StrategyModal';

// 类型定义
interface StrategyParam {
  name: string;
  label: string;
  default: number;
  min: number;
  max: number;
  type?: string;
}

interface Strategy {
  id: string;
  name: string;
  description: string;
  strategy_type?: string;
  params: StrategyParam[];
  is_builtin?: boolean;
}

interface BacktestStrategy {
  id: number;
  name: string;
  description?: string;
  code: string;
  strategy_type: string;
  params_definition: StrategyParam[];
  is_builtin: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface BacktestResult {
  initial_capital: number;
  final_value: number;
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  best_trade: number;
  worst_trade: number;
  avg_trade: number;
  trades: { entry_time: string; exit_time: string; entry_price: number; exit_price: number; pnl: number; pnl_pct: number }[];
  equity_curve: { equity: number }[];
  indicators: Record<string, number[]>;
}

interface OptimizeResult {
  best_params: Record<string, number>;
  best_metrics: {
    total_return: number;
    annual_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
    final_value: number;
  };
  total_combinations: number;
  objective: string;
  top_10: {
    rank: number;
    params: Record<string, number>;
    metrics: Record<string, number>;
  }[];
}

interface KlineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function StrategyAnalysis() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'config' | 'optimize' | 'backtest'>('config');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [customStrategies, setCustomStrategies] = useState<BacktestStrategy[]>([]);
  const [showStrategyModal, setShowStrategyModal] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<BacktestStrategy | null>(null);

  const [popularStocks, setPopularStocks] = useState<{code: string; name: string}[]>([]);
  const [klineData, setKlineData] = useState<KlineData[]>([]);

  const [formData, setFormData] = useState({
    stockCode: '600519',
    stockName: '贵州茅台',
    startDate: '2023-01-01',
    endDate: '2024-12-31',
    initialCash: 100000,
    strategyType: 'ma_cross',
    strategyId: null as number | null,
    // MA Cross
    fastPeriod: 10,
    slowPeriod: 20,
    // RSI
    rsiPeriod: 14,
    rsiUpper: 70,
    rsiLower: 30,
    // MACD
    macdFast: 12,
    macdSlow: 26,
    macdSignal: 9,
    // Bollinger
    bbPeriod: 20,
    bbStd: 2.0,
    // Stop loss/profit
    stopLossPct: 10,
    stopProfitPct: 10,
  });

  const [optimizeMethod, setOptimizeMethod] = useState<'grid' | 'random'>('grid');
  const [optimizeObjective, setOptimizeObjective] = useState('sharpe_ratio');
  const [optimizeIterations, setOptimizeIterations] = useState(50);

  const [optimizeResult, setOptimizeResult] = useState<OptimizeResult | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);

  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStrategies();
    fetchPopularStocks();
  }, []);

  const fetchStrategies = async () => {
    try {
      const res = await axios.get('/api/backtest/strategies');
      // 兼容新旧格式
      if (res.data.all) {
        setStrategies(res.data.all);
      } else {
        setStrategies(res.data);
      }

      // 获取自定义策略
      const customRes = await axios.get('/api/backtest/strategies/list');
      setCustomStrategies(customRes.data);
    } catch (err) {
      console.error('Failed to fetch strategies:', err);
    }
  };

  const fetchPopularStocks = async () => {
    try {
      const res = await axios.get('/api/data/stocks/popular');
      setPopularStocks(res.data);
    } catch (err) {
      console.error('Failed to fetch popular stocks:', err);
    }
  };

  const fetchKlineData = async () => {
    try {
      const res = await axios.get(`/api/data/klines/${formData.stockCode}`, {
        params: {
          start_date: formData.startDate,
          end_date: formData.endDate
        }
      });
      setKlineData(res.data.data || []);
    } catch (err) {
      console.error('Failed to fetch kline data:', err);
    }
  };

  const handleStockChange = (code: string) => {
    const stock = popularStocks.find(s => s.code === code);
    setFormData({
      ...formData,
      stockCode: code,
      stockName: stock?.name || code
    });
  };

  const getCurrentParams = () => {
    // 如果是自定义策略，收集所有参数
    if (formData.strategyId && customStrategies.length > 0) {
      const customStrategy = customStrategies.find(s => s.id === formData.strategyId);
      if (customStrategy && customStrategy.params_definition) {
        const params: any = {};
        customStrategy.params_definition.forEach((param: any) => {
          const formKey = param.name.charAt(0).toUpperCase() + param.name.slice(1);
          if (formData[formKey as keyof typeof formData] !== undefined) {
            params[param.name] = formData[formKey as keyof typeof formData];
          } else if (param.default !== undefined) {
            params[param.name] = param.default;
          }
        });
        return params;
      }
    }

    switch (formData.strategyType) {
      case 'ma_cross':
        return { fast_period: formData.fastPeriod, slow_period: formData.slowPeriod };
      case 'rsi':
        return { rsi_period: formData.rsiPeriod, rsi_upper: formData.rsiUpper, rsi_lower: formData.rsiLower };
      case 'macd':
        return { macd_fast: formData.macdFast, macd_slow: formData.macdSlow, macd_signal: formData.macdSignal };
      case 'bollinger':
        return { bb_period: formData.bbPeriod, bb_std: formData.bbStd };
      case 'stop_loss_profit':
        return { stop_loss_pct: formData.stopLossPct, stop_profit_pct: formData.stopProfitPct };
      default:
        return {};
    }
  };

  const handleStrategySelect = (strategy: Strategy) => {
    // 清除之前的自定义策略选择
    setFormData(prev => ({
      ...prev,
      strategyType: strategy.id,
      strategyId: null,
    }));
  };

  const handleCustomStrategySelect = (strategyId: number) => {
    const strategy = customStrategies.find(s => s.id === strategyId);
    if (strategy) {
      setFormData(prev => ({
        ...prev,
        strategyType: 'custom',
        strategyId: strategyId,
      }));
    }
  };

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setBacktestResult(null);

    try {
      const params = getCurrentParams();
      const requestData: any = {
        stock_code: formData.stockCode,
        start_date: formData.startDate,
        end_date: formData.endDate,
        initial_capital: formData.initialCash,
        strategy_type: formData.strategyType,
        ...params,
      };

      // 如果选择了自定义策略
      if (formData.strategyId) {
        requestData.strategy_id = formData.strategyId;
        requestData.strategy_params = params;
      }

      const res = await axios.post('/api/backtest/run', requestData);

      setBacktestResult(res.data);
      setActiveTab('backtest');

      // 获取K线数据用于图表
      fetchKlineData();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '回测失败');
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    setOptimizeResult(null);

    try {
      const res = await axios.post('/api/optimizer/run', {
        stock_code: formData.stockCode,
        start_date: formData.startDate,
        end_date: formData.endDate,
        strategy_type: formData.strategyType,
        initial_capital: formData.initialCash,
        method: optimizeMethod,
        n_iter: optimizeIterations,
        objective: optimizeObjective,
      });

      setOptimizeResult(res.data);
      setActiveTab('optimize');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '优化失败');
    } finally {
      setLoading(false);
    }
  };

  const applyBestParams = () => {
    if (!optimizeResult) return;
    const best = optimizeResult.best_params;

    setFormData(prev => {
      const newData = { ...prev };
      if (best.fast_period) newData.fastPeriod = best.fast_period;
      if (best.slow_period) newData.slowPeriod = best.slow_period;
      if (best.rsi_period) newData.rsiPeriod = best.rsi_period;
      if (best.rsi_upper) newData.rsiUpper = best.rsi_upper;
      if (best.rsi_lower) newData.rsiLower = best.rsi_lower;
      if (best.macd_fast) newData.macdFast = best.macd_fast;
      if (best.macd_slow) newData.macdSlow = best.macd_slow;
      if (best.macd_signal) newData.macdSignal = best.macd_signal;
      if (best.bb_period) newData.bbPeriod = best.bb_period;
      if (best.bb_std) newData.bbStd = best.bb_std;
      if (best.stop_loss_pct) newData.stopLossPct = best.stop_loss_pct;
      if (best.stop_profit_pct) newData.stopProfitPct = best.stop_profit_pct;
      return newData;
    });
  };

  // 渲染策略参数表单
  const renderStrategyParams = () => {
    // 自定义策略参数
    if (formData.strategyId && customStrategies.length > 0) {
      const customStrategy = customStrategies.find(s => s.id === formData.strategyId);
      if (customStrategy && customStrategy.params_definition && customStrategy.params_definition.length > 0) {
        return (
          <>
            {customStrategy.params_definition.map((param: any) => (
              <div key={param.name} className="form-row">
                <div className="form-group">
                  <label>{param.label}</label>
                  <input
                    type={param.type === 'float' ? 'number' : 'number'}
                    step={param.step || (param.type === 'float' ? 0.1 : 1)}
                    value={(formData as any)[param.name.charAt(0).toUpperCase() + param.name.slice(1)] || param.default}
                    onChange={e => setFormData({
                      ...formData,
                      [param.name.charAt(0).toUpperCase() + param.name.slice(1)]: param.type === 'float' ? parseFloat(e.target.value) : parseInt(e.target.value)
                    })}
                    min={param.min}
                    max={param.max}
                  />
                </div>
              </div>
            ))}
          </>
        );
      }
      return <p className="strategy-hint">该策略无需参数配置</p>;
    }

    switch (formData.strategyType) {
      case 'ma_cross':
        return (
          <>
            <div className="form-row">
              <div className="form-group">
                <label>快速均线周期</label>
                <input type="number" value={formData.fastPeriod}
                  onChange={e => setFormData({ ...formData, fastPeriod: Number(e.target.value) })} min={5} max={50} />
              </div>
              <div className="form-group">
                <label>慢速均线周期</label>
                <input type="number" value={formData.slowPeriod}
                  onChange={e => setFormData({ ...formData, slowPeriod: Number(e.target.value) })} min={10} max={200} />
              </div>
            </div>
          </>
        );
      case 'rsi':
        return (
          <>
            <div className="form-row">
              <div className="form-group">
                <label>RSI周期</label>
                <input type="number" value={formData.rsiPeriod}
                  onChange={e => setFormData({ ...formData, rsiPeriod: Number(e.target.value) })} min={5} max={30} />
              </div>
              <div className="form-group">
                <label>超买阈值</label>
                <input type="number" value={formData.rsiUpper}
                  onChange={e => setFormData({ ...formData, rsiUpper: Number(e.target.value) })} min={50} max={90} />
              </div>
              <div className="form-group">
                <label>超卖阈值</label>
                <input type="number" value={formData.rsiLower}
                  onChange={e => setFormData({ ...formData, rsiLower: Number(e.target.value) })} min={10} max={50} />
              </div>
            </div>
          </>
        );
      case 'macd':
        return (
          <>
            <div className="form-row">
              <div className="form-group">
                <label>快线周期</label>
                <input type="number" value={formData.macdFast}
                  onChange={e => setFormData({ ...formData, macdFast: Number(e.target.value) })} min={5} max={30} />
              </div>
              <div className="form-group">
                <label>慢线周期</label>
                <input type="number" value={formData.macdSlow}
                  onChange={e => setFormData({ ...formData, macdSlow: Number(e.target.value) })} min={15} max={50} />
              </div>
              <div className="form-group">
                <label>信号线周期</label>
                <input type="number" value={formData.macdSignal}
                  onChange={e => setFormData({ ...formData, macdSignal: Number(e.target.value) })} min={5} max={20} />
              </div>
            </div>
          </>
        );
      case 'bollinger':
        return (
          <>
            <div className="form-row">
              <div className="form-group">
                <label>布林带周期</label>
                <input type="number" value={formData.bbPeriod}
                  onChange={e => setFormData({ ...formData, bbPeriod: Number(e.target.value) })} min={10} max={50} />
              </div>
              <div className="form-group">
                <label>标准差倍数</label>
                <input type="number" value={formData.bbStd}
                  onChange={e => setFormData({ ...formData, bbStd: Number(e.target.value) })} min={1.5} max={3.0} step={0.1} />
              </div>
            </div>
          </>
        );
      case 'stop_loss_profit':
        return (
          <>
            <div className="form-row">
              <div className="form-group">
                <label>止损比例 (%)</label>
                <input type="number" value={formData.stopLossPct}
                  onChange={e => setFormData({ ...formData, stopLossPct: Number(e.target.value) })} min={1} max={30} />
              </div>
              <div className="form-group">
                <label>止盈比例 (%)</label>
                <input type="number" value={formData.stopProfitPct}
                  onChange={e => setFormData({ ...formData, stopProfitPct: Number(e.target.value) })} min={1} max={50} />
              </div>
            </div>
          </>
        );
      case 'simple_trend':
        return <p className="strategy-hint">简单趋势策略：阳线买入，阴线卖出，无需参数配置</p>;
      default:
        return null;
    }
  };

  // 渲染回测结果
  const renderBacktestResults = () => {
    if (!backtestResult) return null;

    return (
      <div className="backtest-results">
        <div className="result-header">
          <h3>回测结果</h3>
          <div className="result-summary">
            <span>{formData.stockName} ({formData.stockCode})</span>
            <span>{formData.startDate} ~ {formData.endDate}</span>
            <span>初始资金: ¥{formData.initialCash.toLocaleString()}</span>
          </div>
        </div>

        {/* 收益指标 */}
        <div className="metrics-section">
          <h4>收益指标</h4>
          <div className="metrics-grid">
            <div className="metric-card large">
              <span className="metric-label">最终资金</span>
              <span className={`metric-value huge ${backtestResult.final_value >= formData.initialCash ? 'positive' : 'negative'}`}>
                ¥{backtestResult.final_value.toLocaleString()}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">总收益率</span>
              <span className={`metric-value ${backtestResult.total_return >= 0 ? 'positive' : 'negative'}`}>
                {backtestResult.total_return.toFixed(2)}%
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">年化收益</span>
              <span className={`metric-value ${backtestResult.annual_return >= 0 ? 'positive' : 'negative'}`}>
                {backtestResult.annual_return.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        {/* 风险指标 */}
        <div className="metrics-section">
          <h4>风险指标</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">夏普比率</span>
              <span className="metric-value">{backtestResult.sharpe_ratio.toFixed(2)}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">最大回撤</span>
              <span className="metric-value negative">-{backtestResult.max_drawdown.toFixed(2)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">胜率</span>
              <span className="metric-value">{backtestResult.win_rate.toFixed(2)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">交易次数</span>
              <span className="metric-value">{backtestResult.total_trades}</span>
            </div>
          </div>
        </div>

        {/* 交易统计 */}
        <div className="metrics-section">
          <h4>交易统计</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">最佳交易</span>
              <span className="metric-value positive">+{backtestResult.best_trade.toFixed(2)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">最差交易</span>
              <span className="metric-value negative">{backtestResult.worst_trade.toFixed(2)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">平均交易</span>
              <span className={`metric-value ${backtestResult.avg_trade >= 0 ? 'positive' : 'negative'}`}>
                {backtestResult.avg_trade.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        {/* 交易记录 */}
        {backtestResult.trades && backtestResult.trades.length > 0 && (
          <div className="trades-section">
            <h4>交易记录</h4>
            <div className="trades-table-wrapper">
              <table className="trades-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>买入价</th>
                    <th>卖出价</th>
                    <th>盈亏</th>
                    <th>盈亏%</th>
                  </tr>
                </thead>
                <tbody>
                  {backtestResult.trades.slice(0, 20).map((trade, idx) => (
                    <tr key={idx} className={trade.pnl >= 0 ? 'profit' : 'loss'}>
                      <td>{idx + 1}</td>
                      <td>¥{trade.entry_price?.toFixed(2) || '-'}</td>
                      <td>¥{trade.exit_price?.toFixed(2) || '-'}</td>
                      <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                        {trade.pnl ? (trade.pnl >= 0 ? '+' : '') + trade.pnl.toFixed(2) : '-'}
                      </td>
                      <td className={trade.pnl_pct >= 0 ? 'positive' : 'negative'}>
                        {trade.pnl_pct ? (trade.pnl_pct >= 0 ? '+' : '') + trade.pnl_pct.toFixed(2) + '%' : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  // 渲染优化结果
  const renderOptimizeResults = () => {
    if (!optimizeResult) return null;

    const { best_params, best_metrics, total_combinations, top_10 } = optimizeResult;

    return (
      <div className="optimize-results">
        <div className="optimize-summary">
          <h3>优化完成</h3>
          <p>共测试 {total_combinations} 种参数组合</p>
        </div>

        <div className="best-section">
          <h4>最佳参数</h4>
          <div className="params-grid">
            {Object.entries(best_params).map(([key, value]) => (
              <div key={key} className="param-item">
                <span className="param-name">{key}</span>
                <span className="param-value">{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="best-metrics">
          <h4>最佳收益指标</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">总收益</span>
              <span className={`metric-value ${best_metrics.total_return >= 0 ? 'positive' : 'negative'}`}>
                {best_metrics.total_return.toFixed(2)}%
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">夏普比率</span>
              <span className="metric-value">{best_metrics.sharpe_ratio.toFixed(2)}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">最大回撤</span>
              <span className="metric-value negative">-{best_metrics.max_drawdown.toFixed(2)}%</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">胜率</span>
              <span className="metric-value">{best_metrics.win_rate.toFixed(2)}%</span>
            </div>
          </div>
        </div>

        <div className="top-10">
          <h4>Top 10 参数组合</h4>
          <table className="top-10-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>参数</th>
                <th>收益</th>
                <th>夏普</th>
                <th>回撤</th>
                <th>胜率</th>
              </tr>
            </thead>
            <tbody>
              {top_10.map((item) => (
                <tr key={item.rank} className={item.rank === 1 ? 'best' : ''}>
                  <td>#{item.rank}</td>
                  <td className="params-cell">
                    {Object.entries(item.params).map(([k, v]) => (
                      <span key={k} className="param-tag">{k}: {v}</span>
                    ))}
                  </td>
                  <td className={item.metrics.total_return >= 0 ? 'positive' : 'negative'}>
                    {item.metrics.total_return.toFixed(2)}%
                  </td>
                  <td>{item.metrics.sharpe_ratio.toFixed(2)}</td>
                  <td className="negative">-{item.metrics.max_drawdown.toFixed(2)}%</td>
                  <td>{item.metrics.win_rate.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="optimize-actions">
          <button className="btn btn-primary" onClick={applyBestParams}>应用最佳参数</button>
          <button className="btn btn-secondary" onClick={() => setActiveTab('config')}>修改配置</button>
          <button className="btn btn-success" onClick={runBacktest}>使用最佳参数回测</button>
        </div>
      </div>
    );
  };

  return (
    <div className="strategy-analysis-page">
      <div className="page-header">
        <h1>策略分析</h1>
        <button className="btn btn-secondary" onClick={() => navigate('/settings')}>
          返回设置
        </button>
      </div>

      <div className="tabs">
        <button className={`tab ${activeTab === 'config' ? 'active' : ''}`} onClick={() => setActiveTab('config')}>
          1. 策略配置
        </button>
        <button className={`tab ${activeTab === 'optimize' ? 'active' : ''}`} onClick={() => setActiveTab('optimize')}>
          2. 参数优化
        </button>
        <button className={`tab ${activeTab === 'backtest' ? 'active' : ''}`} onClick={() => setActiveTab('backtest')}>
          3. 回测结果
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="tab-content">
        {activeTab === 'config' && (
          <div className="config-panel">
            <div className="form-section">
              <h3>基础参数</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>选择股票</label>
                  <select value={formData.stockCode} onChange={e => handleStockChange(e.target.value)}>
                    <option value="">选择热门股票</option>
                    {popularStocks.map(stock => (
                      <option key={stock.code} value={stock.code}>{stock.code} - {stock.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>或输入代码</label>
                  <input type="text" value={formData.stockCode}
                    onChange={e => setFormData({ ...formData, stockCode: e.target.value })} placeholder="如: 600519" />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>开始日期</label>
                  <input type="date" value={formData.startDate}
                    onChange={e => setFormData({ ...formData, startDate: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>结束日期</label>
                  <input type="date" value={formData.endDate}
                    onChange={e => setFormData({ ...formData, endDate: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>初始资金</label>
                  <input type="number" value={formData.initialCash}
                    onChange={e => setFormData({ ...formData, initialCash: Number(e.target.value) })} />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>
                选择策略
                <button
                  className="btn btn-sm btn-secondary"
                  style={{ marginLeft: 'auto' }}
                  onClick={() => setShowStrategyModal(true)}
                >
                  + 新建策略
                </button>
              </h3>

              {/* 内置策略 */}
              <div className="strategy-group">
                <h4>内置策略</h4>
                <div className="strategy-cards">
                  {strategies.filter(s => !s.strategy_type || s.strategy_type === 'builtin').map(s => (
                    <div
                      key={s.id}
                      className={`strategy-card ${formData.strategyType === s.id && !formData.strategyId ? 'selected' : ''}`}
                      onClick={() => handleStrategySelect(s)}
                    >
                      <div className="strategy-name">{s.name}</div>
                      <div className="strategy-desc">{s.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 自定义策略 */}
              {customStrategies.length > 0 && (
                <div className="strategy-group">
                  <h4>自定义策略</h4>
                  <div className="strategy-cards">
                    {customStrategies.map(s => (
                      <div
                        key={s.id}
                        className={`strategy-card ${formData.strategyId === s.id ? 'selected' : ''}`}
                        onClick={() => handleCustomStrategySelect(s.id)}
                      >
                        <div className="strategy-name">{s.name}</div>
                        <div className="strategy-desc">{s.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {renderStrategyParams()}
            </div>

            <div className="form-actions">
              <button className="btn btn-primary" onClick={runBacktest} disabled={loading}>
                {loading ? '回测中...' : '直接回测'}
              </button>
              <button className="btn btn-success" onClick={runOptimization} disabled={loading}>
                {loading ? '优化中...' : '开始参数优化'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'optimize' && (
          <div className="optimize-panel">
            {!optimizeResult ? (
              <div className="optimize-config">
                <h3>优化配置</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>优化方法</label>
                    <select value={optimizeMethod} onChange={e => setOptimizeMethod(e.target.value as 'grid' | 'random')}>
                      <option value="grid">网格搜索</option>
                      <option value="random">随机搜索</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>优化目标</label>
                    <select value={optimizeObjective} onChange={e => setOptimizeObjective(e.target.value)}>
                      <option value="sharpe_ratio">夏普比率</option>
                      <option value="total_return">总收益率</option>
                      <option value="max_drawdown">最大回撤</option>
                      <option value="win_rate">胜率</option>
                    </select>
                  </div>
                  {optimizeMethod === 'random' && (
                    <div className="form-group">
                      <label>迭代次数</label>
                      <input type="number" value={optimizeIterations}
                        onChange={e => setOptimizeIterations(Number(e.target.value))} min={10} max={200} />
                    </div>
                  )}
                </div>
                <div className="form-actions">
                  <button className="btn btn-primary" onClick={runOptimization} disabled={loading}>
                    {loading ? '优化中...' : '开始优化'}
                  </button>
                  <button className="btn btn-secondary" onClick={() => setActiveTab('config')}>返回配置</button>
                </div>
              </div>
            ) : renderOptimizeResults()}
          </div>
        )}

        {activeTab === 'backtest' && (
          <div className="backtest-panel">
            {!backtestResult ? (
              <div className="empty-result">
                <p>暂无回测结果</p>
                <button className="btn btn-primary" onClick={() => setActiveTab('config')}>去配置</button>
              </div>
            ) : renderBacktestResults()}
          </div>
        )}
      </div>

      {/* 新建/编辑策略弹窗 */}
      {showStrategyModal && (
        <StrategyModal
          strategy={editingStrategy}
          onClose={() => {
            setShowStrategyModal(false);
            setEditingStrategy(null);
          }}
          onSave={() => {
            setShowStrategyModal(false);
            setEditingStrategy(null);
            fetchStrategies();
          }}
        />
      )}
    </div>
  );
}
