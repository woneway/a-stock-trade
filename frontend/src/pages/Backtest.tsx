import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface BacktestStrategy {
  id: string;
  name: string;
  description: string;
  params: {
    name: string;
    label: string;
    type: string;
    default: number;
  }[];
}

interface BacktestStats {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_win: number;
  avg_loss: number;
}

interface EquityCurvePoint {
  date: string;
  equity: number;
  return_pct: number;
}

export default function Backtest() {
  const navigate = useNavigate();
  const [strategies, setStrategies] = useState<BacktestStrategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    stockCode: '600519',
    stockName: '贵州茅台',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    initialCash: 100000,
    strategyType: 'double_ma',
    fastPeriod: 5,
    slowPeriod: 20,
    period: 20,
    period_me1: 12,
    period_me2: 26,
    period_signal: 9,
    rsiPeriod: 14,
    rsiUpper: 70,
    rsiLower: 30,
  });

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const res = await axios.get('/api/strategies');
      setStrategies(res.data);
    } catch (err) {
      console.error('Failed to fetch strategies:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let strategyParams = null;
      if (formData.strategyType === 'double_ma') {
        strategyParams = {
          type: 'double_ma',
          fast_period: formData.fastPeriod,
          slow_period: formData.slowPeriod,
        };
      } else if (formData.strategyType === 'macd') {
        strategyParams = {
          type: 'macd',
          period_me1: formData.period_me1,
          period_me2: formData.period_me2,
          period_signal: formData.period_signal,
        };
      } else if (formData.strategyType === 'rsi') {
        strategyParams = {
          type: 'rsi',
          period: formData.rsiPeriod,
          upper: formData.rsiUpper,
          lower: formData.rsiLower,
        };
      }

      const res = await axios.post('/api/backtest/run', {
        stock_code: formData.stockCode,
        stock_name: formData.stockName,
        start_date: formData.startDate,
        end_date: formData.endDate,
        initial_cash: formData.initialCash,
        strategy_params: strategyParams,
      });

      if (res.data.success) {
        setResult(res.data.data);
      } else {
        setError(res.data.message || '回测失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || '回测失败');
    } finally {
      setLoading(false);
    }
  };

  const renderStrategyParams = () => {
    switch (formData.strategyType) {
      case 'double_ma':
        return (
          <>
            <div className="form-group">
              <label>快速均线周期</label>
              <input
                type="number"
                value={formData.fastPeriod}
                onChange={(e) => setFormData({ ...formData, fastPeriod: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>慢速均线周期</label>
              <input
                type="number"
                value={formData.slowPeriod}
                onChange={(e) => setFormData({ ...formData, slowPeriod: Number(e.target.value) })}
              />
            </div>
          </>
        );
      case 'momentum':
        return (
          <div className="form-group">
            <label>均线周期</label>
            <input
              type="number"
              value={formData.period}
              onChange={(e) => setFormData({ ...formData, period: Number(e.target.value) })}
            />
          </div>
        );
      case 'macd':
        return (
          <>
            <div className="form-group">
              <label>快线周期</label>
              <input
                type="number"
                value={formData.period_me1}
                onChange={(e) => setFormData({ ...formData, period_me1: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>慢线周期</label>
              <input
                type="number"
                value={formData.period_me2}
                onChange={(e) => setFormData({ ...formData, period_me2: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>信号线周期</label>
              <input
                type="number"
                value={formData.period_signal}
                onChange={(e) => setFormData({ ...formData, period_signal: Number(e.target.value) })}
              />
            </div>
          </>
        );
      case 'rsi':
        return (
          <>
            <div className="form-group">
              <label>RSI周期</label>
              <input
                type="number"
                value={formData.rsiPeriod}
                onChange={(e) => setFormData({ ...formData, rsiPeriod: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>超买阈值</label>
              <input
                type="number"
                value={formData.rsiUpper}
                onChange={(e) => setFormData({ ...formData, rsiUpper: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>超卖阈值</label>
              <input
                type="number"
                value={formData.rsiLower}
                onChange={(e) => setFormData({ ...formData, rsiLower: Number(e.target.value) })}
              />
            </div>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="backtest-page">
      <div className="page-header">
        <h1>策略回测</h1>
        <button className="btn-secondary" onClick={() => navigate('/strategy')}>
          返回策略
        </button>
      </div>

      <div className="backtest-container">
        <div className="backtest-form-section">
          <h2>回测参数</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>股票代码</label>
              <input
                type="text"
                value={formData.stockCode}
                onChange={(e) => setFormData({ ...formData, stockCode: e.target.value })}
                placeholder="如: 600519"
              />
            </div>
            <div className="form-group">
              <label>股票名称</label>
              <input
                type="text"
                value={formData.stockName}
                onChange={(e) => setFormData({ ...formData, stockName: e.target.value })}
                placeholder="如: 贵州茅台"
              />
            </div>
            <div className="form-group">
              <label>开始日期</label>
              <input
                type="date"
                value={formData.startDate}
                onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>结束日期</label>
              <input
                type="date"
                value={formData.endDate}
                onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>初始资金</label>
              <input
                type="number"
                value={formData.initialCash}
                onChange={(e) => setFormData({ ...formData, initialCash: Number(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>选择策略</label>
              <select
                value={formData.strategyType}
                onChange={(e) => setFormData({ ...formData, strategyType: e.target.value })}
              >
                {strategies.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            {renderStrategyParams()}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? '回测中...' : '开始回测'}
            </button>
          </form>
        </div>

        <div className="backtest-result-section">
          {error && (
            <div className="error-message">
              <h3>错误</h3>
              <p>{error}</p>
            </div>
          )}

          {result && (
            <>
              <h2>回测结果</h2>

              <div className="result-summary">
                <div className="summary-item">
                  <span className="label">股票</span>
                  <span className="value">{result.stock_name} ({result.stock_code})</span>
                </div>
                <div className="summary-item">
                  <span className="label">回测区间</span>
                  <span className="value">{result.start_date} ~ {result.end_date}</span>
                </div>
                <div className="summary-item">
                  <span className="label">初始资金</span>
                  <span className="value">¥{result.initial_cash.toLocaleString()}</span>
                </div>
                <div className="summary-item">
                  <span className="label">最终资金</span>
                  <span className="value highlight">¥{result.final_value.toLocaleString()}</span>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-label">总收益率</div>
                  <div className={`stat-value ${result.stats.total_return >= 0 ? 'positive' : 'negative'}`}>
                    {result.stats.total_return}%
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">年化收益率</div>
                  <div className={`stat-value ${result.stats.annual_return >= 0 ? 'positive' : 'negative'}`}>
                    {result.stats.annual_return}%
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">夏普比率</div>
                  <div className="stat-value">{result.stats.sharpe_ratio}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">最大回撤</div>
                  <div className="stat-value negative">-{result.stats.max_drawdown_pct}%</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">胜率</div>
                  <div className="stat-value">{result.stats.win_rate}%</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">盈亏比</div>
                  <div className="stat-value">{result.stats.profit_factor}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">交易次数</div>
                  <div className="stat-value">{result.stats.total_trades}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">盈利次数</div>
                  <div className="stat-value positive">{result.stats.winning_trades}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">亏损次数</div>
                  <div className="stat-value negative">{result.stats.losing_trades}</div>
                </div>
              </div>

              <div className="equity-curve">
                <h3>收益曲线</h3>
                <div className="curve-chart">
                  {result.equity_curve && result.equity_curve.length > 0 && (
                    <div className="simple-chart">
                      {result.equity_curve.map((point: EquityCurvePoint, index: number) => (
                        <div
                          key={index}
                          className="chart-point"
                          style={{
                            height: `${Math.min(100, Math.max(0, (point.equity / result.initial_cash) * 50))}%`,
                            backgroundColor: point.equity >= result.initial_cash ? '#52c41a' : '#ff4d4f',
                          }}
                          title={`${point.date}: ¥${point.equity.toLocaleString()}`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {!result && !error && (
            <div className="empty-result">
              <p>请设置回测参数并点击"开始回测"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
