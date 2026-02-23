import { useState, useEffect } from 'react';
import axios from 'axios';

interface Strategy {
  id: number;
  name: string;
  description?: string;
  stock_selection_logic?: string;
  watch_signals?: string;
  stop_loss: number;
  take_profit_1?: number;
  take_profit_2?: number;
  trailing_stop?: number;
}

interface Stock {
  id: number;
  code: string;
  name: string;
  sector?: string;
  price?: number;
  change?: number;
  turnover_rate?: number;
  volume_ratio?: number;
  market_cap?: number;
  limit_consecutive: number;
}

interface MatchDetail {
  field: string;
  matched: boolean;
  detail: string;
  score: number;
}

interface EntryAdvice {
  can_enter: boolean;
  signal: string;
  risk?: string;
  trigger_type?: string;
}

interface ExitAdvice {
  stop_loss: string;
  take_profit_1: string;
  take_profit_2: string;
  trailing_stop: string;
  advice: string;
}

interface ScanResult {
  stock_id: number;
  code: string;
  name: string;
  sector?: string;
  price?: number;
  change?: number;
  turnover_rate?: number;
  volume_ratio?: number;
  market_cap?: number;
  limit_consecutive: number;
  score: number;
  max_score: number;
  match_details: MatchDetail[];
  entry_advice: EntryAdvice;
  exit_advice: ExitAdvice;
}

export default function StrategyScan() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategyId, setSelectedStrategyId] = useState<number | null>(null);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedStockIds, setSelectedStockIds] = useState<number[]>([]);
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState<Stock[]>([]);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    fetchStrategies();
    fetchStocks();
  }, []);

  const fetchStrategies = async () => {
    try {
      const res = await axios.get('/api/strategies?is_active=true');
      setStrategies(res.data);
      if (res.data.length > 0) {
        setSelectedStrategyId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch strategies:', err);
    }
  };

  const fetchStocks = async () => {
    try {
      const res = await axios.get('/api/stocks');
      setStocks(res.data);
    } catch (err) {
      console.error('Failed to fetch stocks:', err);
    }
  };

  const searchStocks = async (keyword: string) => {
    if (!keyword) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await axios.get(`/api/stocks/search?keyword=${keyword}&limit=10`);
      setSearchResults(res.data);
    } catch (err) {
      console.error('Failed to search stocks:', err);
    }
  };

  const handleSearchChange = (keyword: string) => {
    setSearchKeyword(keyword);
    if (keyword.length >= 1) {
      searchStocks(keyword);
      setShowSearch(true);
    } else {
      setShowSearch(false);
    }
  };

  const addStock = async (stock: Stock) => {
    try {
      await axios.post('/api/stocks', stock);
      fetchStocks();
      setSearchKeyword('');
      setShowSearch(false);
    } catch (err: any) {
      if (err.response?.status === 400) {
        alert('股票已存在');
      }
    }
  };

  const addNewStock = async () => {
    if (!searchKeyword) return;
    // 尝试解析股票代码和名称
    const code = searchKeyword.replace(/\D/g, '').slice(0, 6).padStart(6, '0');
    if (code.length !== 6) {
      alert('请输入有效的股票代码');
      return;
    }
    try {
      await axios.post('/api/stocks', {
        code,
        name: searchKeyword,
        sector: '其他'
      });
      fetchStocks();
      setSearchKeyword('');
      setShowSearch(false);
    } catch (err) {
      console.error('Failed to add stock:', err);
    }
  };

  const deleteStock = async (id: number) => {
    try {
      await axios.delete(`/api/stocks/${id}`);
      fetchStocks();
      setSelectedStockIds(prev => prev.filter(sid => sid !== id));
    } catch (err) {
      console.error('Failed to delete stock:', err);
    }
  };

  const clearStocks = async () => {
    if (!confirm('确定清空股票池?')) return;
    try {
      await axios.delete('/api/stocks');
      setStocks([]);
      setSelectedStockIds([]);
      setScanResults([]);
    } catch (err) {
      console.error('Failed to clear stocks:', err);
    }
  };

  const handleScan = async () => {
    if (!selectedStrategyId) {
      alert('请选择策略');
      return;
    }
    if (stocks.length === 0) {
      alert('请先添加股票到股票池');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('/api/strategy/scan', {
        strategy_id: selectedStrategyId,
        stock_ids: stocks.map(s => s.id)
      });
      setScanResults(res.data.results);
    } catch (err) {
      console.error('Failed to scan:', err);
      alert('扫描失败');
    } finally {
      setLoading(false);
    }
  };

  const toggleStockSelection = (stockId: number) => {
    setSelectedStockIds(prev =>
      prev.includes(stockId)
        ? prev.filter(id => id !== stockId)
        : [...prev, stockId]
    );
  };

  const selectedStrategy = strategies.find(s => s.id === selectedStrategyId);

  return (
    <div className="page">
      <div className="page-header">
        <h1>策略选股 <span className="time-hint">盘前/盘后使用</span></h1>
        <p className="page-desc">收盘后复盘制定计划，次日盘前确认选股</p>
      </div>

      {/* 步骤1: 选择策略 */}
      <div className="section">
        <h3>步骤1: 选择策略</h3>
        <div className="strategy-select">
          <select
            value={selectedStrategyId || ''}
            onChange={e => setSelectedStrategyId(Number(e.target.value))}
          >
            {strategies.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={handleScan} disabled={loading}>
            {loading ? '扫描中...' : '重新扫描'}
          </button>
        </div>

        {selectedStrategy && (
          <div className="strategy-params">
            <div className="param-tag">止损: {selectedStrategy.stop_loss}%</div>
            <div className="param-tag">止盈1: {selectedStrategy.take_profit_1}%</div>
            <div className="param-tag">止盈2: {selectedStrategy.take_profit_2}%</div>
            <div className="param-tag">移动止损: {selectedStrategy.trailing_stop}%</div>
          </div>
        )}
      </div>

      {/* 步骤2: 股票池管理 */}
      <div className="section">
        <h3>步骤2: 股票池 ({stocks.length}只)</h3>
        <div className="stock-pool">
          <div className="stock-search">
            <input
              type="text"
              placeholder="搜索股票代码/名称..."
              value={searchKeyword}
              onChange={e => handleSearchChange(e.target.value)}
              onFocus={() => searchKeyword && setShowSearch(true)}
            />
            <button className="btn btn-sm" onClick={addNewStock}>手动添加</button>
            <button className="btn btn-sm btn-danger" onClick={clearStocks}>清空</button>

            {showSearch && searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map(stock => (
                  <div
                    key={stock.id}
                    className="search-result-item"
                    onClick={() => addStock(stock)}
                  >
                    {stock.code} {stock.name}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="stock-tags">
            {stocks.map(stock => (
              <span key={stock.id} className="stock-tag">
                {stock.code} {stock.name}
                <button onClick={() => deleteStock(stock.id)}>×</button>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* 步骤3: 扫描结果 */}
      {scanResults.length > 0 && (
        <div className="section">
          <h3>扫描结果</h3>
          <div className="results-header">
            <span>共 {scanResults.length} 只股票匹配</span>
            <button
              className="btn btn-primary"
              disabled={selectedStockIds.length === 0}
            >
              已选 {selectedStockIds.length} 只
            </button>
          </div>

          <div className="results-list">
            {scanResults.map((result, index) => (
              <div key={result.stock_id} className="result-card">
                <div className="result-header">
                  <div className="result-rank">{index + 1}</div>
                  <div className="result-info">
                    <span className="result-name">{result.code} {result.name}</span>
                    <span className={`result-score ${result.score >= 80 ? 'high' : result.score >= 60 ? 'mid' : 'low'}`}>
                      {result.score}分
                    </span>
                    <span className="result-change">
                      {result.change !== undefined ? `${result.change > 0 ? '+' : ''}${result.change.toFixed(2)}%` : '-'}
                    </span>
                    {result.limit_consecutive > 0 && (
                      <span className="result-limit">{result.limit_consecutive}连板</span>
                    )}
                  </div>
                  <div className="result-select">
                    <input
                      type="checkbox"
                      checked={selectedStockIds.includes(result.stock_id)}
                      onChange={() => toggleStockSelection(result.stock_id)}
                    />
                  </div>
                </div>

                <div className="result-details">
                  <div className="detail-section">
                    <div className="detail-title">选股匹配:</div>
                    <div className="detail-tags">
                      {result.match_details.filter(d => d.matched).slice(0, 4).map((d, i) => (
                        <span key={i} className="detail-tag matched">{d.detail}</span>
                      ))}
                      {result.match_details.filter(d => !d.matched).slice(0, 2).map((d, i) => (
                        <span key={i} className="detail-tag unmatched">{d.detail}</span>
                      ))}
                    </div>
                  </div>

                  <div className="detail-section">
                    <div className="detail-title">买入建议:</div>
                    <div className={`entry-signal ${result.entry_advice.can_enter ? 'can' : 'cannot'}`}>
                      {result.entry_advice.trigger_type && (
                        <span className="signal-type">[{result.entry_advice.trigger_type}]</span>
                      )}
                      {result.entry_advice.signal}
                      {result.entry_advice.risk && (
                        <span className="signal-risk"> ({result.entry_advice.risk})</span>
                      )}
                    </div>
                  </div>

                  <div className="detail-section">
                    <div className="detail-title">卖出建议:</div>
                    <div className="exit-advice">
                      止损: {result.exit_advice.stop_loss} |
                      止盈1: {result.exit_advice.take_profit_1} |
                      止盈2: {result.exit_advice.take_profit_2}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {stocks.length > 0 && scanResults.length === 0 && !loading && (
        <div className="section">
          <button className="btn btn-primary btn-lg" onClick={handleScan}>
            开始扫描
          </button>
        </div>
      )}

      {stocks.length === 0 && (
        <div className="empty-state">
          <p>请先在股票池中添加股票</p>
        </div>
      )}

      <style>{`
        .page-header h1 {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .time-hint {
          font-size: 12px;
          font-weight: normal;
          color: #666;
          background: #f5f5f5;
          padding: 4px 10px;
          border-radius: 4px;
        }

        .page-desc {
          margin: 8px 0 0 0;
          font-size: 13px;
          color: #999;
        }

        .section {
          margin-bottom: 24px;
          padding: 16px;
          background: var(--card-bg, #fff);
          border-radius: 8px;
        }

        .section h3 {
          margin: 0 0 12px 0;
          font-size: 14px;
          color: #666;
        }

        .strategy-select {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .strategy-select select {
          flex: 1;
          max-width: 300px;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
        }

        .strategy-params {
          display: flex;
          gap: 8px;
          margin-top: 12px;
          flex-wrap: wrap;
        }

        .param-tag {
          padding: 4px 10px;
          background: #f0f0f0;
          border-radius: 4px;
          font-size: 12px;
          color: #666;
        }

        .stock-pool {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .stock-search {
          position: relative;
          display: flex;
          gap: 8px;
        }

        .stock-search input {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
        }

        .search-results {
          position: absolute;
          top: 100%;
          left: 0;
          right: 80px;
          background: white;
          border: 1px solid #ddd;
          border-radius: 6px;
          max-height: 200px;
          overflow-y: auto;
          z-index: 100;
        }

        .search-result-item {
          padding: 8px 12px;
          cursor: pointer;
          border-bottom: 1px solid #f0f0f0;
        }

        .search-result-item:hover {
          background: #f5f5f5;
        }

        .stock-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .stock-tag {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          background: #e3f2fd;
          border-radius: 4px;
          font-size: 13px;
        }

        .stock-tag button {
          background: none;
          border: none;
          color: #999;
          cursor: pointer;
          padding: 0;
          font-size: 14px;
        }

        .stock-tag button:hover {
          color: #f00;
        }

        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .results-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .result-card {
          padding: 12px;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          background: #fafafa;
        }

        .result-header {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .result-rank {
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #1976d2;
          color: white;
          border-radius: 50%;
          font-weight: bold;
          font-size: 14px;
        }

        .result-info {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .result-name {
          font-weight: 500;
        }

        .result-score {
          padding: 2px 8px;
          border-radius: 4px;
          font-weight: bold;
          font-size: 13px;
        }

        .result-score.high {
          background: #4caf50;
          color: white;
        }

        .result-score.mid {
          background: #ff9800;
          color: white;
        }

        .result-score.low {
          background: #9e9e9e;
          color: white;
        }

        .result-change {
          font-size: 13px;
          color: #666;
        }

        .result-limit {
          padding: 2px 6px;
          background: #ff5722;
          color: white;
          border-radius: 4px;
          font-size: 12px;
        }

        .result-select input {
          width: 18px;
          height: 18px;
        }

        .result-details {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #e0e0e0;
        }

        .detail-section {
          margin-bottom: 8px;
        }

        .detail-title {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .detail-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .detail-tag {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
        }

        .detail-tag.matched {
          background: #e8f5e9;
          color: #2e7d32;
        }

        .detail-tag.unmatched {
          background: #fff3e0;
          color: #ef6c00;
        }

        .entry-signal {
          font-size: 13px;
          padding: 6px 10px;
          border-radius: 4px;
        }

        .entry-signal.can {
          background: #e3f2fd;
          color: #1565c0;
        }

        .entry-signal.cannot {
          background: #fce4ec;
          color: #c62828;
        }

        .signal-type {
          font-weight: bold;
          margin-right: 4px;
        }

        .signal-risk {
          color: #f00;
          font-size: 12px;
        }

        .exit-advice {
          font-size: 13px;
          color: #666;
        }

        .empty-state {
          text-align: center;
          padding: 40px;
          color: #999;
        }

        .btn-lg {
          padding: 12px 32px;
          font-size: 16px;
        }

        .btn-danger {
          background: #f44336;
          color: white;
        }
      `}</style>
    </div>
  );
}
